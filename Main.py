import DailyData
import TrainModel
from S3Manager import load_all_ids, upload_selected_articles_to_S3, reset_answer

import os
from os import listdir
from os.path import isfile, join

import pandas as pd

''' -------------------- DeepNews.ai ------------------

Objectif du projet : Récupérer des articles de différentes sources puis développer un
système de recommandation pour envoyer quotidiennement ces données via un bot Messenger.


1. On charge et nettoie les données précemment crawlées
2. On récupère les derniers users et on leur créé une session s'ils sont nouveaux
3. On charge les données de chaque user et on réentraine le DNN
4. On prédit quels sont les articles les plus adaptés à chaque user
5. On update les données sur S3

-------------------------- Main.py ------------------

Classe principale : on importe toutes les classes / fonctions pour charger les nouveaux articles,
les nettoyer, puis effectuer des prédictions sur ces articles.

'''


def load_data():
    mediumstartup_path = 'IACrawler/MediumCrawler.csv'
    mediumtech_path = 'IACrawler/MediumTech.csv'
    mediumML_path = 'IACrawler/MediumML.csv'
    mediumDS_path = 'IACrawler/MediumDS.csv'
    mediumAI_path = 'IACrawler/MediumAI.csv'
    actuia_path = 'IACrawler/actuia.csv'
    itsocial_path = 'IACrawler/itsocial.csv'
    approximatelycorrect_path = 'IACrawler/approximatelycorrect.csv'
    kdnuggets_path = 'IACrawler/kdnuggets.csv'
    dscentral_path = 'IACrawler/dscentral.csv'

    print('------- CREATION DE LA BASE DE DONNEES DU JOUR -------')
    database = DailyData.DailyData()

    print('------- Nettoyage des articles récupérés -------')
    database.clean_csv_1(mediumstartup_path)
    database.clean_csv_1(mediumtech_path)
    database.clean_csv_1(mediumAI_path)
    database.clean_csv_1(mediumML_path)
    database.clean_csv_1(mediumDS_path)
    database.clean_csv_1(actuia_path)
    database.clean_csv_1(dscentral_path)
    database.clean_csv_1(itsocial_path)
    database.clean_csv_1(approximatelycorrect_path)
    database.clean_csv_2(kdnuggets_path, 'https://www.kdnuggets.com/')

    print('------- Enregistrement des données -------')
    database.export_updated_articles()


def init_users():
    ids = load_all_ids()
    default_db = pd.read_csv('UserData\\Default_Data\\total_db.csv')
    default_json = pd.read_json('UserData\\Default_Data\\today_selected_articles.json')
    for i in range(len(ids)):
        user_id = str(ids.iloc[i][0])
        if not os.path.isdir('UserData/' + user_id):
            print('New user')
            os.mkdir('UserData/' + user_id)
            os.mkdir('UserData/' + user_id + '/Model')
            default_db.to_csv('UserData/' + user_id + '/total_db.csv', index=False)
            default_json.to_json('UserData/' + user_id + '/today_selected_articles.json')


def train_and_predict():
    ids = load_all_ids()
    for i in range(len(ids)):
        user_id = str(ids.iloc[i][0])
        print('train model')
        dnn = TrainModel.DNN(user_id)
        print('update label')
        dnn.update_labels()
        print('train DNN')
        dnn.trainDNN()
        print('select articles')
        dnn.select_articles()
        print('Training done')


def update_files_S3():
    ids = load_all_ids()
    for i in range(len(ids)):
        user_id = str(ids.iloc[i][0])
        upload_selected_articles_to_S3(user_id)

def end_daily_task():
    mypath = 'IACrawler'
    os.remove('UserData/Default_Data/AI_articles_dataset.csv')
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in files:
        extension = file.split('.')[1]
        if extension == 'csv':
            os.remove('IACrawler/' + file)


# 1. Chargement de la base de données

load_data()

# 2. Chargement des données de la veille et entrainement

init_users()

# 3. Réentrainement du model et selection des 3 meilleurs articles

train_and_predict()

# 4. Actualisation des articles sélectionnés sur S3

update_files_S3()

# 5. Préparation des fichiers pour l'entrainement de demain

end_daily_task()