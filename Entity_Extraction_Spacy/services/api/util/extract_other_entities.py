import pandas as pd
from services.api.util.predict_headers import predict_headers
from services.api.util.predict_headers_category import predict_headers_category
from services.api.util.extract_entities_information import get_paragraph_ranges, get_paragraphs

from services.api.common.logger import set_up_logging

logger = set_up_logging(__name__)


def get_other_entities_model(filename, text):
    try:
        logger.info("[{}] Started other entities extraction using model".format(filename))
        predict_data = get_text_sentences(text)

        headers_predictions = predict_headers(predict_data)
        headers_category_predictions_df = predict_headers_category(headers_predictions)

        headers_predictions["indexes"] = list(headers_predictions.index)

        header_index_category = pd.merge(headers_category_predictions_df, headers_predictions, on='content')
        paragraph_ranges = get_paragraph_ranges(len(predict_data["clean_content"]), header_index_category)
        payment_information = get_paragraphs(predict_data["clean_content"], paragraph_ranges["p"])
        warranties_information = get_paragraphs(predict_data["clean_content"], paragraph_ranges["w"])
        indemnification_information = get_paragraphs(predict_data["clean_content"], paragraph_ranges["i"])
        termination_information = get_paragraphs(predict_data["clean_content"], paragraph_ranges["t"])
        return {'payment':payment_information, 'warranties':warranties_information, 'indemnification':indemnification_information, 'termination':termination_information}
    except Exception as ex:
        logger.error('[{}] Exception raised - {}'.format(filename, ex))

def get_text_sentences(text):
    text = text.splitlines()
    text_sentences = [line for line in text if line != '']
    predict_data = pd.DataFrame(text_sentences, columns=["content"])
    return predict_data