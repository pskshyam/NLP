import re
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class junk_file_filter(object):

    def __init__(self, filename):
        self.name = 'Document Filtering'
        self.filename = filename

    def filter(self, text):

        class_keywords = ['agreement', 'statement of work', 'sow', 'addendum', 'amendment', 'work order', 'nda']
        search_keywords = ['between', 'among', 'undersigned', 'effective', 'dated']

        text = text.lower()
        start_pos = []

        try:
            for key in class_keywords:
                if key in text:
                    index1 = [m.start() for m in re.finditer(key, text)]
                    start_pos.append(index1)
            index1_list = [item for sublist in start_pos for item in sublist]

            if not index1_list:  # if index1 is not found
                return True

            else:
                start_indices = sorted(index1_list)  # sort the start indices
                match_found = False
                for index1 in start_indices:
                    if not (match_found):
                        for key in search_keywords:
                            if not (match_found) and key in text:
                                index2 = text.find(key)
                                if index2 is not None and index1 < index2 and len(text[index1:index2].split()) < 30:
                                    return False
                                match_found = True

            if not (match_found):
                return True

        except Exception as ex:
            logger.error('[{}] Exception occurred in junk file filtering - {}'.format(self.filename, ex))
            return None