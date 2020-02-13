import falcon
import json
from services.api.utils.prepare_data import create_test_file
from services.api.utils.BERT_UDA_Preprocess import BERT_UDA_Preprocess
from services.api.core.BERT_UDA_Training import BERT_UDA_Training
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class DocumentClassification(object):
    def on_post(self, req, resp):
        text = req.stream.read()
        logger.info("Request received is - {}".format(text))

        doc = json.loads(text.decode('latin1'))
        try:
             #data = ''.join(l[:-1] for l in open('services/api/core/text.txt'))
            text = doc['content']
            callback = doc['callBack']
            logger.info("[{}] File received for classification".format(doc["callBack"]["fileName"]))
            create_test_file(text)
            BERT_UDA_Preprocess().generate_labeled_features('data/predict/predict.csv', 'output/predict/', '../../../uncased_L-12_H-768_A-12/vocab.txt')
            logger.info("[{}] TF Records dumped".format(doc["callBack"]["fileName"]))
            logger.info("[{}] Classification process started".format(doc["callBack"]["fileName"]))
            label_index = BERT_UDA_Training(False, False, True, 4, 4, 1, 128, 'output/', 'output/eval/',
                                                  'output/predict', '../../../uncased_L-12_H-768_A-12/vocab.txt',
                                                  '../../../uncased_L-12_H-768_A-12/bert_config.json', '../../../uncased_L-12_H-768_A-12/bert_model.ckpt', '../../../model/', 2e-05, 'linear_schedule').process()
            logger.info("[{}] Classification process completed".format(doc["callBack"]["fileName"]))

            labels = {"0": "ADDENDUM", "1": "MSA", "2": "NDA", "3": "OTHERS", "4": "SOW"}
            logger.info("[{}] Classification output is {}".format(doc["callBack"]["fileName"], labels[label_index]))
            resp.data = bytes(json.dumps({"category": labels[label_index],"callBack":callback,"error":"false","errorMessage":""}), 'utf-8')

        except Exception as ex:
            logger.error("[{}] Exception occurred in classification process. Exception - {} ".format(doc["callBack"]["fileName"],ex))
            resp.data = bytes(json.dumps({"category": "","callBack":callback,"error":"true","errorMessage":"Classification failed"}), 'utf-8')
