import pandas as pd
import re


def create_test_file(data):
    text = re.sub('[^a-zA-Z0-9 ]', '', data.replace('\n', ' '))
    data_bert_predict = pd.DataFrame({'id': 1,
                                      'text': text,
                                       'label': 0}, index=[0])
    data_bert_predict.to_csv('data/predict/predict.csv', sep=',', index=False, header=True)
