import numpy as np
import pandas as pd


class DailyData:

    ''' -------------------- DailyData ------------------

    Nettoyage des données : chaque jour à 9h00 on crawl une centaine d'articles.

    On nettoie ces données :

     - clean_csv1 : preprocessing des données, mise en forme
     - clean_csv2 : ajout des url par défaut + preprocessing des données, mise en forme
     - export_updated_articles : exportation du dataframe

    '''

    def __init__(self):

        try:
            self.alltime_articles = pd.read_csv('UserData/Default_Data/AI_articles_dataset.csv')
            self.alltime_articles.columns = ['Title', 'Link', 'Date']
            print('Base de données chargée')
        except:
            print('Base de données créée')
            self.alltime_articles = pd.DataFrame({'Title': [], 'Link': [], 'Date': []})

    def clean_csv_1(self, path):
        print(path)
        today_articles = pd.read_csv(path)
        titles = list(today_articles['Title'])[0].split(',')
        links = list(today_articles['Link'])[0].split(',')
        dates = np.full((len(links)), today_articles['Date'][0])

        if len(titles) == len(links) == len(dates):

            for title, link, date in zip(titles, links, dates):
                self.alltime_articles = self.arrange_df([title, link, date], self.alltime_articles)

    def clean_csv_2(self, path, default_url):
        print(path)
        today_articles = pd.read_csv(path)
        titles = list(today_articles['Title'])[0].split(',')
        links = list(today_articles['Link'])[0].split(',')
        dates = np.full((len(links)), today_articles['Date'][0])

        complete_link = [default_url + link for link in links]

        if len(titles) == len(complete_link) == len(dates):

            for title, link, date in zip(titles, complete_link, dates):
                self.alltime_articles = self.arrange_df([title, link, date], self.alltime_articles)

    def export_updated_articles(self):
        self.alltime_articles = self.alltime_articles.drop_duplicates(subset=['Title'], keep='first')
        self.alltime_articles.to_csv('UserData/Default_Data/AI_articles_dataset.csv', index=False)
        print("Nouvelles données ajoutées à AI_articles_dataset")

    def arrange_df(self, ligne, df):
        clean_line = pd.DataFrame(ligne).T
        clean_line.columns = ['Title', 'Link', 'Date']
        df = pd.concat([df, clean_line], axis=0, ignore_index=True, sort=True)
        return df
