# DeepNews.ai

The objective of this project is to develop a messenger bot, which provides a technological watch on a specific theme (artificial intelligence in our case).

The project operates in several stages:

1. Load and clean the previously crawled data 
2. We get the last users and create a session for them if they are new
3. We load the data of each user and we reentrain the DNN
4. We predict which articles are the most suitable for each user
5. We update the data on S3

![Alt](UserData/Deepnews.ai.png).

There are 4 Python files in this repository :

- Main.py is the main file, which calls every other classes and functions from python other files. We load the list of user from AWS S3 and we perform some computation to predict which articles are the most likely to match with user preferences. 
- DailyData.py collects all csv files locally stored clean them and generate a new csv file : AI_articles_dataset.csv
- S3Manager.py : Set of functions allowing to upload or download files on a bucket S3
- TrainModel.py : retrain everyday the each user's model with previous data collected from S3 and predict with are the 3 best articles for the user. For the prediction, we use a DeepNeural Network and we ue transfer learning for the embedding layer (universal-sentence-encoder 2)


We user a bat file to automate the articles distribution : we activate the virtual environnement, crawl each websites, and then run Main.py to clean data and make the predictions. 
