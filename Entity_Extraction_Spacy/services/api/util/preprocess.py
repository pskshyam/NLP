import re
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class Msa_Preprocess(object):

    def __init__(self, filename):
        self.filename = filename

    def preprocess(self, data):
        try:
            logger.info("[{}] Started data preprocessing".format(self.filename))
            data = re.sub('[^a-zA-Z0-9 .$/,&()]', ' ', data.replace('\n', ' '))
            data = re.sub(r"\s+", " ", data)
            #if ('Inc' in data.split()):
            #    data = re.sub('Inc', 'Inc.', data)
            if ('incorporated' in data.lower().split()):
                data = re.sub('INCORPORATED', 'Inc.', data)
                data = re.sub('Incorporated', 'Inc.', data)
            # if ('LLC' in data.split()):
            #    data = re.sub('LLC', '', data)
            if ('limited' in data.lower().split()):
                data = re.sub('Limited', 'Ltd.', data)
                data = re.sub('limited', 'Ltd.', data)
            data = re.sub('BETWEEN' ,'between', data)
            data = re.sub('Between', 'between', data)
            data = re.sub(r'\bAND\b', 'and', data)
            data = re.sub(r'\bAnd\b', 'and', data)
            data = re.sub('WHEREAS', 'whereas', data)
            data = re.sub(r'\blst\b', '1st', data)
            data = re.sub('&', 'and', data)
            data = data.replace(' US $', ' $')
            months = ['JANUARY' ,'JAN' ,'FEBRUARY' ,'FEB' ,'MARCH' ,'MAR' ,'APRIL' ,'APR' ,'MAY' ,'JUNE' ,'JUN' ,'JULY' ,'JUL'
                      ,'AUGUST' ,'AUG' ,'SEPTEMBER' ,'SEP' ,'OCTOBER' ,'OCT' ,'NOVEMBER' ,'NOV' ,'DECEMBER' ,'DEC']
            if [data.replace(month, month.capitalize()) for month in months if month in data]:
                data = [data.replace(month, month.capitalize()) for month in months if month in data][0]
            logger.info("[{}] Completed data preprocessing".format(self.filename))
        except Exception as ex:
            logger.error('[{}] Exception raised - {}'.format(self.filename, ex))
        return data
