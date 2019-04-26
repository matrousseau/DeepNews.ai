import tensorflow as tf
import tensorflow_hub as hub
import time
import pandas as pd
import  numpy as np
import contractions
from bs4 import BeautifulSoup
import unicodedata
import re
from keras.models import Model
from keras.layers import Input, Dense, Lambda
from keras.regularizers import l2
from keras.backend import set_session

def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    [s.extract() for s in soup(['iframe', 'script'])]
    stripped_text = soup.get_text()
    stripped_text = re.sub(r'[\r|\n|\r\n]+', '\n', stripped_text)
    return stripped_text

def remove_accented_chars(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text

def expand_contractions(text):
    return contractions.fix(text)

def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-Z0-9\s]' if not remove_digits else r'[^a-zA-Z\s]'
    text = re.sub(pattern, '', text)
    return text

def pre_process_document(document):
    # strip HTML
    document = strip_html_tags(document)
    # lower case
    document = document.lower()
    # remove extra newlines (often might be present in really noisy text)
    document = document.translate(document.maketrans("\n\t\r", "   "))
    # remove accented characters
    document = remove_accented_chars(document)
    # expand contractions
    document = expand_contractions(document)
    # remove special characters and\or digits
    # insert spaces between special characters to isolate them
    special_char_pattern = re.compile(r'([{.(-)!}])')
    document = special_char_pattern.sub(" \\1 ", document)
    document = remove_special_characters(document, remove_digits=True)
    # remove extra whitespace
    document = re.sub(' +', ' ', document)
    document = document.strip()

    return document


df = pd.read_csv('total_db.csv', encoding='utf-8')

X = df.Title.values
y = df.Y.values
# articles_to_predict = df.Title.values

pre_process_corpus = np.vectorize(pre_process_document)
print(pre_process_corpus(X))

embed = hub.Module("module_elmo2/")

def ELMoEmbedding(x):
    return embed(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["default"]

def build_model():
    input_text = Input(shape=(1,), dtype="string")
    embedding = Lambda(ELMoEmbedding, output_shape=(1024, ))(input_text)
    dense = Dense(256, activation='relu', kernel_regularizer=l2(0.001))(embedding)
    pred = Dense(1, activation='sigmoid')(dense)
    model = Model(inputs=[input_text], outputs=pred)
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    return model

model_elmo = build_model()

with tf.Session() as session:
    set_session(session)
    session.run(tf.global_variables_initializer())
    session.run(tf.tables_initializer())
    history = model_elmo.fit(X, y, epochs=5, batch_size=256, validation_split = 0.2)
    model_elmo.save_weights('model_elmo_weights.h5')

print('Prediction')

dfarticles = pd.read_csv('AI_articles_dataset.csv')
articles_to_predict = dfarticles.Title.values

with tf.Session() as session:
    set_session(session)
    session.run(tf.global_variables_initializer())
    session.run(tf.tables_initializer())
    model_elmo = build_model()
    model_elmo.load_weights('model_elmo_weights.h5')
    import time
    t = time.time()
    predicts = model_elmo.predict(articles_to_predict)
    print("time: ", time.time() - t)
    print(predicts)
