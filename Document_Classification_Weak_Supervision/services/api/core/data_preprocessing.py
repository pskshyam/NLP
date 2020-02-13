import re
from nltk.corpus import stopwords
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

stop_words = set(stopwords.words("english"))

class data_preprocessing(object):

    def __init__(self, filename):
            self.name = 'Text Pre-processing'
            self.filename = filename

    def get_text_start_pos(self, text):
        pos = 0
        match1 = re.search(r"(addendum|amendment|change request|change order|agreement|sow|statement of work|work order|task order)\s+(\S+\s+){1,30}(by and between|by and among|between|among) (.+?) and (.+?)", text)
        match2 = re.search(r"(addendum|amendment|change request|change order|agreement|sow|statement of work|work order|task order)\s+(\S+\s+){1,30}(effective|dated|entered|executed|made) (.+?) and (.+?)", text)
        match3 = re.search(r"(addendum|amendment|change request|change order|agreement|sow|statement of work|work order|task order)(.+?)(the undersigned)(.+?) and (.+?)", text)

        if match1 and match1.start() < 1000:
            pos = match1.start()
        elif match2 and match2.start() < 1000:
            pos = match2.start()
        elif match3 and match3.start() < 1000:
            pos = match3.start()
        logger.info('[{}] Identified start position of the agreement'.format(self.filename))
        return pos


    def preprocess(self,text):
        # Preprocess
        try:
            text = text.replace('\n', ' ').lower()
            # Remove non-alpha characters
            text = re.sub('[^a-zA-Z]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            pos = self.get_text_start_pos(text)
            text = text[pos:]
            logger.info('[{}] Data Pre-processing completed'.format(self.filename))
            return text
        except Exception as ex:
            logger.error('[{}] Exception occurred in Data Pre-processing - {}'.format(self.filename, ex))
            return None