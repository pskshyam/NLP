import spacy
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class Generate_Msa_Entities(object):

    def __init__(self, filename):
        self.filename = filename
        # Load spacy
        self.nlp = spacy.load('en_core_web_sm')

    def generate_entities(self,text):
        entities = None
        try:
            logger.info("[{}] Started getting NER tags".format(self.filename))
            doc = self.nlp(text)
            entities = []
            for ent in doc.ents:
                entities.append((ent.text, ent.start_char, ent.end_char, ent.label_))
            logger.info("[{}] Completed getting NER tags".format(self.filename))
        except Exception as ex:
            logger.error('[{}] Exception raised - {}'.format(self.filename, ex))
        return (entities)
