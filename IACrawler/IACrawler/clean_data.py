import pandas as pd
load_list_of_words = pd.read_csv('Data/word_labels.csv')
load_list_of_words.columns = ['labels']
print(load_list_of_words['labels'].values)