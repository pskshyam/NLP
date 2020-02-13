import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import global_variables
from databaseUtils import DBUtil
from modelSessionManager import SessionManager
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from logger.logger import set_up_logging
logger = set_up_logging(__name__)
from config.constants  import ENV

class SentenceSemanticService:


    """
    Description : Service Class For Sentence Semantic Model Service
    Author : Sachin Ichake

    """

    @classmethod
    def embed_customer_data(cls, customer_all_statement): #get embedding for the kb question data
        try:
            sts_encode1 = tf.nn.l2_normalize(global_variables.sentence_embed(customer_all_statement))
            sts_encode1 = global_variables.kbid_session.run(sts_encode1)
            logger.info("Embedding for all customer has loaded successfully")
            return sts_encode1
        except Exception as e:
            logger.exception("embed_customer_data: Embedding for all customer has failed to load")
            logger.exception(str(e))

    @classmethod
    def define_placeholders(cls): #placehoder from tensorflow which required for model restore and prediction
        try:
            global_variables.kbid_session = tf.Session()
            global_variables.sentence_embed = hub.Module(ENV.get("TFHUB_SENTENCE_MODEL_DIR"))
            global_variables.sts_encode11 = tf.placeholder(tf.float32, shape=(None, 512))
            global_variables.sts_encode3 = tf.placeholder(tf.float32, shape=(None, 512))
            global_variables.sts_input2 = tf.placeholder(tf.string, shape=(None))
            global_variables.sts_encode2 = global_variables.sentence_embed(global_variables.sts_input2)
            global_variables.sim_scores = tf.reduce_sum(
                tf.multiply(global_variables.sts_encode11, tf.nn.l2_normalize(global_variables.sts_encode3)), axis=1)
            with global_variables.kbid_session.as_default() as sess:
                sess.run(tf.global_variables_initializer())
                sess.run(tf.tables_initializer())
        except Exception as e :
            print(e)
            logger.exception(str(e))


    @classmethod
    def create_only_statements_list(cls, unique_statement_list): #create uniq list of statements
        only_statements = []
        for item in unique_statement_list:
            only_statements.append(cls.remove_non_english_words(cls.remove_stop_words(cls.remove_special_char(item[0]))).lower())
        return only_statements

    @classmethod
    def remove_non_english_words(cls,sentence): # method to remove non english words
        words = set(nltk.corpus.words.words())
        return " ".join(w for w in nltk.wordpunct_tokenize(sentence) if w.lower() in words or not w.isalpha())

    @classmethod
    def remove_special_char(cls,sentence): # method to remove special characters
        tempstr1 = re.sub(r'[?|$|.|!]', r'', sentence)
        return re.sub(r'[^a-zA-Z0-9 ]', r'', tempstr1)

    @classmethod
    def remove_stop_words(cls,sentence): # method to remove stop words
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(sentence)
        return " ".join(w for w in word_tokens if not w in stop_words)
    
    @classmethod
    def process(cls, userQuery, kbid, topN):
        try: #based on userquery retun matching statement
            customer_session = cls.getModelSession(kbid)
            unique_data_with_model = customer_session["unique_data_with_model"]
            customer_embed = customer_session["customer_embed"]
            matched_statement = cls.getScore(userQuery, unique_data_with_model, customer_embed, topN)
            logger.info('Matching statements are pulled')
            return matched_statement
        except Exception as e:
            logger.exception('process: Failed at last stage : ' + str(e))

    @classmethod
    def getModelSession(cls, kbid): #get model sessio n from SessionManager
        customerModelSession = SessionManager.getModelSessionByKbid(kbid)
        return customerModelSession

    @classmethod
    def restoreModels(cls, customerList): #restore Models
        try:
            cls.initilize_placeholders()
            cls.loadTrainedDataStoreSession(customerList)
        except Exception as e:
            logger.exception('Confidence Checker Model Not Restored for All Customer : ' + str(e))

    @classmethod
    def loadTrainedDataStoreSession(cls, kbid): #loading data from database
        is_model_loaded = SessionManager.getModelSessionByKbid(kbid)

        if not is_model_loaded:
            try:
                unique_data_list = DBUtil.getData('kb_qna', {'kb_id': kbid})
                unique_statement_list = cls.create_only_statements_list(unique_data_list)
                customer_embed = cls.embed_customer_data(unique_statement_list)
                embeding_dict = {"unique_data_with_model": unique_data_list,
                                 "unique_statement_list": unique_statement_list,
                                 "customer_embed": customer_embed}
                SessionManager.setModelSessionByKbid(kbid=kbid, model_session=embeding_dict)
                logger.info('Confidence Checker Model Restored for Customer : ' + str(kbid))

            except Exception as e:
                logger.exception('Confidence Checker Model Not Restored for Customer : ' + str(e))

    @classmethod
    def column(self, matrix, i):
        return [row[i] for row in matrix]

    @classmethod
    def run_sts_benchmark(cls, statement_list, text_a, userQuery, topN):
        try:#comparison of extracted embedding and input question embedding
            sess = global_variables.kbid_session
            emebb = sess.run([global_variables.sts_encode2], feed_dict={global_variables.sts_input2: userQuery})
            embedding_uq_list = []
            for i in range(len(statement_list)):
                embedding_uq_list.append(emebb[0])
            embedding_uq_list = np.squeeze(embedding_uq_list, axis=1)
            scores = sess.run(
                [global_variables.sim_scores],
                feed_dict={
                    global_variables.sts_encode11: text_a,
                    global_variables.sts_encode3: embedding_uq_list
                })

            Confidence_Score = (scores[0] * len(statement_list)) * 100.

            uniqueData = np.array(statement_list)

            matchingAnswer = sorted(
                list(zip(SentenceSemanticService.column(uniqueData, 0), Confidence_Score,
                         SentenceSemanticService.column(uniqueData, 2),
                         SentenceSemanticService.column(uniqueData, 1))),
                key=lambda x: x[1], reverse=True)[0:topN]
            return matchingAnswer
        except Exception as e:
            logger.exception("run_sts_benchmark: Error while executing run_sts_benchmark: " + str(e))


    @classmethod
    def getScore(cls, userQuery, statement_list, customer_embed, topN): # return matching statement
        matchingsentence= None
        try:
            line_c = [userQuery.lower()]
            matchingsentence = cls.run_sts_benchmark(statement_list, customer_embed,
                                                     line_c,
                                                     topN)
        except Exception as e:
            logger.exception("getScore: Error while returning score: "+str(e))

        return matchingsentence
