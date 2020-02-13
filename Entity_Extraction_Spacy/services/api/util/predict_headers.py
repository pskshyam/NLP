import pandas as pd
import re
import pickle
import os
import numpy as np


def get_features_and_content_df(predict_data):

    extract_features(predict_data)
    clean_text(predict_data)
    content_dataframe = pd.DataFrame(predict_data["content"].values, columns=[predict_data["content"].name])
    predict_data.drop(columns=["content"], inplace=True)
    return predict_data, content_dataframe


def extract_features(data):
    data['number_of_capital_letter'] = data.apply(lambda row: get_number_of_capitale_letters(row["content"]), axis=1)
    data['start_by_number'] = data.apply(lambda row: get_start_by_number(row["content"]), axis=1)
    data['period_at_beggining'] = data.apply(lambda row: get_period_at_beggining(row["content"]), axis=1)
    data['contains_quotes'] = data.apply(lambda row: get_contains_special_characters(row["content"], '"'), axis=1)
    data['contains_dash'] = data.apply(lambda row: get_contains_special_characters(row["content"], '-'), axis=1)
    data['contains_question_mark'] = data.apply(lambda row: get_contains_special_characters(row["content"], '?'), axis=1)
    data['contains_colon'] = data.apply(lambda row: get_contains_special_characters(row["content"], ':'), axis=1)
    data['number_of_characters'] = data.apply(lambda row: get_text_len(row["content"]), axis=1)
    data['end_in_period'] = data.apply(lambda row: get_end_in_period(row["content"]), axis=1)


def get_number_of_capitale_letters(text):
    return sum(1 for c in str(text) if c.isupper()) * 100 /len(text)

def get_start_by_number(text):
    return True if re.match(r'(?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})',str(text), flags=re.IGNORECASE) or any(c.isnumeric() for c in text[0:3]) else False

def get_period_at_beggining(text):
    return True if '.' in str(text[0:4]) else False

def get_contains_special_characters(text, character):
    return True if character in str(text) else False

def get_text_len(text):
    return len(str(text))

def get_end_in_period(text):
    return True if str(text[-1]) == '.' else False

def clean_text(data):
    data['clean_content'] = data.apply(lambda row: clean_row_text(row["content"]), axis=1)

def clean_row_text(row):
    return row

def load_binary_classifier():
    with open("services/api/util/models/Binary_classifier/pipeline_model_DownSamp.pkl", "rb") as classifier_file:
        binary_classifier = pickle.load(classifier_file)
        return binary_classifier

def get_predictions(predict_data, classifier_model, content_dataframes):

    predictions = classifier_model.predict(predict_data)
    df_prediction = pd.DataFrame(np.concatenate([content_dataframes.values, predictions[:, np.newaxis]], axis=1),
                                 columns=["content", "prediction"])
    headers = df_prediction.content[df_prediction.prediction == 1]
    headers = pd.DataFrame(headers, columns=["content"])
    return headers

def predict_headers(splitted_text):
    predict_data, content_dataframes = get_features_and_content_df(splitted_text)
    classifier = load_binary_classifier()
    headers = get_predictions(predict_data, classifier, content_dataframes)
    return headers


