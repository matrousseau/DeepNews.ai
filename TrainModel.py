import re
import unicodedata

import contractions
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
from bs4 import BeautifulSoup
from keras.backend import set_session
from keras.layers import Input, Dense, Lambda
from keras.models import Model
from keras.regularizers import l2

from S3Manager import load_answer_from_S3, load_previous_articles_from_S3, upload_selected_articles_to_S3

''' -------------------- TrainModel ------------------

Model predictif : en récupérant les données de la veille sur AWS S3, on réentraine chaque jour le
Deep Neural Network

 - update_labels : on ajoute à la base de données totale les données labélisées de la veille
 - trainDNN : Entrainement d'un DNN [256, 64] avec les données de total_db.csv + transfer learning pour
   la couche d'embedding (universal-sentence-encoder 2)
 - select_articles : Récupération d'un dictionnaire puis traitement pour récupérer les 3 meilleurs prédictions

'''


class DNN:

    def __init__(self, user_id):
        try:
            self.total_database = pd.read_csv('UserData/' + user_id + '/total_db.csv', encoding='utf-8')
            self.all_title = self.total_database.Title.values
            self.daily_articles = pd.read_csv('UserData/Default_Data/AI_articles_dataset.csv')
            self.daily_titles = self.daily_articles.Title.values
            self.previous_answer = load_answer_from_S3(user_id).T
            self.previous_answer.columns = ['Y']
            self.previous_articles = load_previous_articles_from_S3(user_id)
            self.user_id = user_id
            self.X = []
            self.y = []
            self.dnn = []
        except:
            pass

    def update_labels(self):
        df_to_add = pd.DataFrame({'Date': [], 'Link': [], 'Title': []})
        df_to_add = df_to_add.append(self.previous_articles.reset_index(drop=True))
        df_to_add = pd.concat([df_to_add, self.previous_answer], axis=1)
        self.total_database = self.total_database.append(df_to_add)
        self.total_database.to_csv('UserData/' + self.user_id + '/total_db.csv', index=False)

    def build_model(self):
        input_text = Input(shape=(1,), dtype="string")
        embedding = Lambda(self.ELMoEmbedding, output_shape=(1024,))(input_text)
        dense = Dense(256, activation='relu', kernel_regularizer=l2(0.001))(embedding)
        pred = Dense(1, activation='sigmoid')(dense)
        model = Model(inputs=[input_text], outputs=pred)
        model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        return model

    def ELMoEmbedding(self, x):
        return self.embed(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["default"]

    def trainDNN(self):

        pre_process_corpus = np.vectorize(self.pre_process_document)
        self.X = self.total_database.Title.values
        self.y = self.total_database.Y.values
        self.X = pre_process_corpus(self.X)
        self.embed = hub.Module("UserData/Default_Data/module_elmo2/")

        model_elmo = self.build_model()

        with tf.Session() as session:
            set_session(session)
            session.run(tf.global_variables_initializer())
            session.run(tf.tables_initializer())
            history = model_elmo.fit(self.X, self.y, epochs=2, batch_size=8)
            model_elmo.save_weights('UserData/' + self.user_id + '/Model/model_elmo_weights.h5')
            session.close()

    def prediction(self):
        with tf.Session() as session:
            set_session(session)
            session.run(tf.global_variables_initializer())
            session.run(tf.tables_initializer())
            model_elmo = self.build_model()
            model_elmo.load_weights('UserData/' + self.user_id + '/Model/model_elmo_weights.h5')
            predicts = model_elmo.predict(self.daily_titles)
            session.close()
            return predicts

    def select_articles(self):

        indexs = []
        self.total_database = pd.read_csv('UserData/' + self.user_id + '/total_db.csv', encoding='utf-8')
        self.all_title = self.total_database.Title.values
        pre_process_corpus = np.vectorize(self.pre_process_document)
        scores_predicted = self.prediction()
        index = [i for i in range(0, len(scores_predicted))]
        dict_scores = dict(zip(index, scores_predicted))
        dict_scores_sorted = [(k, dict_scores[k]) for k in sorted(dict_scores, key=dict_scores.get, reverse=True)]


        for i in range(0, len(dict_scores_sorted)):
            if self.daily_titles[dict_scores_sorted[i][0]] not in list(self.all_title) and len(
                    indexs) < 3:
                indexs.append(dict_scores_sorted[i][0])

        articles_selected = self.daily_articles.iloc[indexs]
        articles_selected.to_json('UserData/' + self.user_id + '/today_selected_articles.json')
        upload_selected_articles_to_S3(self.user_id)

    def strip_html_tags(self, text):
        soup = BeautifulSoup(text, "html.parser")
        [s.extract() for s in soup(['iframe', 'script'])]
        stripped_text = soup.get_text()
        stripped_text = re.sub(r'[\r|\n|\r\n]+', '\n', stripped_text)
        return stripped_text

    def remove_accented_chars(self, text):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        return text

    def expand_contractions(self, text):
        return contractions.fix(text)

    def remove_special_characters(self, text, remove_digits=False):
        pattern = r'[^a-zA-Z0-9\s]' if not remove_digits else r'[^a-zA-Z\s]'
        text = re.sub(pattern, '', text)
        return text

    def pre_process_document(self, document):
        # strip HTML
        document = self.strip_html_tags(document)
        # lower case
        document = document.lower()
        # remove extra newlines (often might be present in really noisy text)
        document = document.translate(document.maketrans("\n\t\r", "   "))
        # remove accented characters
        document = self.remove_accented_chars(document)
        # expand contractions
        document = self.expand_contractions(document)
        # remove special characters and\or digits
        # insert spaces between special characters to isolate them
        special_char_pattern = re.compile(r'([{.(-)!}])')
        document = special_char_pattern.sub(" \\1 ", document)
        document = self.remove_special_characters(document, remove_digits=True)
        # remove extra whitespace
        document = re.sub(' +', ' ', document)
        document = document.strip()

        return document
