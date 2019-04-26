import boto3
import pandas as pd


''' -------------------- S3 Manager ------------------

Ensemble de fonctions permettant d'upload ou downloader des fichiers sur
un bucket S3s

'''

def load_answer_from_S3(user_id):
    client = boto3.client('s3')
    obj = client.get_object(Bucket='dnai-aie', Key='UserData/' + user_id + '/yesterday_answer.csv')
    grid_sizes = pd.read_csv(obj['Body'], header=None)
    return grid_sizes

def load_previous_articles_from_S3(user_id):
    client = boto3.client('s3')
    obj = client.get_object(Bucket='dnai-aie', Key='UserData/' + user_id + '/today_selected_articles.json')
    grid_sizes = pd.read_json(obj['Body'])
    return grid_sizes

def upload_selected_articles_to_S3(user_id):
    s3 = boto3.client('s3')
    filename = 'UserData/'+user_id+'/today_selected_articles.json'
    bucket_name = 'dnai-aie'
    s3.upload_file(filename, bucket_name, filename)

def reset_answer(user_id):
    s3 = boto3.client('s3')
    filename = 'UserData/Default_Data/yesterday_answer.csv'
    loc = 'UserData/' + user_id + '/yesterday_answer.csv'
    bucket_name = 'dnai-aie'
    s3.upload_file(filename, bucket_name, loc)

def load_all_ids():
    client = boto3.client('s3')
    obj = client.get_object(Bucket='dnai-aie', Key='all_ids.csv')
    grid_sizes = pd.read_csv(obj['Body'], header=None)
    grid_sizes.to_csv('UserData/all_ids.csv', index=False)
    return grid_sizes

# print(load_previous_articles_from_S3('2077391485703101'))