from services.api.core.junk_file_filter import junk_file_filter
from services.api.core.data_preprocessing import data_preprocessing
from services.api.core.latent_features import latent_features
from services.api.core.classifier_model import classifier_model
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class document_classifier(object):

    def __init__(self, text, filename):
        self.text = text
        self.name = 'Document Classifier'
        self.filename = filename

    def check_for_junk_file(self):
        filter = junk_file_filter(self.filename)
        is_junk = filter.filter(self.text)
        logger.info('[{}] Junk file check completed'.format(self.filename))
        return is_junk


    def classify(self):
        #Check if the file is junk. If it is label as others and stop
        try:
            is_junk = self.check_for_junk_file()
            if is_junk:
                logger.info('[{}] is a junk file'.format(self.filename))
                return "Others"
            else:
                #Preprocess Text
                preprocessor = data_preprocessing(self.filename)
                preprocessed_text = preprocessor.preprocess(self.text)

                #Generate Latent Features
                feature_extractor = latent_features(self.filename)
                df_latent = feature_extractor.feature_extraction(preprocessed_text)
                logger.info('[{}] Latent feature extraction completed'.format(self.filename))


                #Perform prediction
                classifier = classifier_model(df_latent, preprocessed_text, self.filename)
                result = classifier.predict()
                return result

        except Exception as ex:
            logger.error('[{}] Exception occurred in classification process - {}'.format(self.filename, ex))
            return None

if __name__ == '__main__':

    text = 'tang'
    cls = document_classifier(text, 'filename')
    result = cls.classify()
    print(result)

