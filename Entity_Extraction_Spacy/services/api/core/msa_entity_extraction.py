from datetime import datetime
import datefinder
import re
from services.api.util.config.cms_config import CMSConfig
from services.api.util.preprocess import Msa_Preprocess
from services.api.util.generate_entities import Generate_Msa_Entities
from services.api.util.extract_entity_boundary import Extract_Entity_Boundary
from services.api.common.logger import set_up_logging
from services.api.util.extract_other_entities import get_other_entities_model
import os
import pandas as pd
logger = set_up_logging(__name__)

class entity_extraction(object):

    def __init__(self,filename):
        self.filename = filename

    def process(self, text):
        entities = None
        try:
            unprocessed_text = text
            text = Msa_Preprocess(self.filename).preprocess(text)
            data = Generate_Msa_Entities(self.filename).generate_entities(text)
            containRebateTable = self.get_rebate_table_flag(text)
            otherentities = self.get_other_entities(self.filename, unprocessed_text)
            entities = self.get_entities(self.filename, data, text, containRebateTable)
            entities.update(otherentities)
        except Exception as ex:
            logger.error('[{}] Exception raised - {}'.format(self.filename, ex))
        return entities

    def get_other_entities(self, filename,text):
            payment = None
            indemnification = None
            warranties = None
            termination =None

            try:
                text = re.sub('[^a-zA-Z0-9 .$/,&()]', ' ',text.replace('\n','ABCDXYZ'))
                text = text.replace('ABCDXYZ','\n')
                logger.info("[{}] Started Extracting Other Entities".format(self.filename))
                payment_term = self.get_payment_term(text)
                termmination_term = self.get_termination_term(text)
                warranties_term = self.get_warranties_term(text)
                indemnification_term = self.get_indemnification_term(text)
                if payment_term != None:
                    payment= payment_term
                if warranties_term != None:
                    warranties = warranties_term
                if indemnification_term != None:
                    indemnification = indemnification_term
                if termmination_term != None:
                    termination = termmination_term
                if any([entity is None for entity in [payment, warranties, indemnification, termination]]):
                    other_entities = get_other_entities_model(filename, text)
                    if payment is None:
                        payment = other_entities['payment']
                    if indemnification is None:
                        indemnification = other_entities['indemnification']
                    if warranties is None:
                        warranties = other_entities['warranties']
                    if termination is None:
                        termination = other_entities['termination']

                logger.info("[{}] Completed Extracting Other Entities".format(self.filename))
                #print(filename,payment,warranties,termination,indemnification)

            except Exception as ex:
                logger.error('[{}] Exception raised - {}'.format(self.filename, ex))

            return {"payment": payment, "warranties":warranties,"termination": termination,"indemnification":indemnification}

    def get_payment_term(self,text):
        for pattern in CMSConfig.payment_term_start_patterns:
            if re.search(pattern, text):
                start = re.search(pattern, text).start()
                end_string = [pattern for pattern in CMSConfig.payment_term_end_patterns if
                              re.search(pattern, text) != None]
                for end_str in end_string:
                    end = re.search(''.join(end_str), text).start()
                    if end > start:
                        payment_Term = str(text[start:end]).replace('\n', ' ')
                        return payment_Term

    def get_termination_term(self,text):
        for pattern in CMSConfig.termination_term_start_patterns:
            if re.search(pattern, text):
                start = re.search(pattern, text).start()
                end_string = [pattern for pattern in CMSConfig.termination_term_end_patterns if
                              re.search(pattern, text) != None]
                for end_str in end_string:
                    end = re.search(''.join(end_str), text).start()
                    if end > start:
                        Termination_Term = str(text[start:end]).replace('\n', ' ')
                        return Termination_Term

    def get_warranties_term(self,text):
        for pattern in CMSConfig.warranties_term_start_patterns:
            if re.search(pattern, text):
                start = re.search(pattern, text).start()
                end_string = [pattern for pattern in CMSConfig.warranties_term_end_patterns if
                              re.search(pattern, text) != None]
                for end_str in end_string:
                    end = re.search(''.join(end_str), text).start()
                    if end > start:
                        Warranties_Term = str(text[start:end]).replace('\n', ' ')
                        return Warranties_Term

    def get_indemnification_term(self,text):
        for pattern in CMSConfig.indemnification_term_start_patterns:
            if re.search(pattern, text):
                start = re.search(pattern, text).start()
                end_string = [pattern for pattern in CMSConfig.indemnification_term_end_patterns if
                              re.search(pattern, text) != None]
                for end_str in end_string:
                    end = re.search(''.join(end_str), text).start()
                    if end > start:
                        Indemnification_Term = str(text[start:end]).replace('\n', ' ')
                        return Indemnification_Term


    def get_entities(self, filename, tags, text, rebate_table_flag):
        first_party = None
        second_party = None
        effective_date = None

        months = ['JANUARY', 'JAN', 'FEBRUARY', 'FEB', 'MARCH', 'MAR', 'APRIL', 'APR', 'MAY', 'JUNE', 'JUN', 'JULY',
                  'JUL', 'AUGUST', 'AUG', 'SEPTEMBER', 'SEP', 'OCTOBER', 'OCT', 'NOVEMBER', 'NOV', 'DECEMBER', 'DEC']
        date_format = "%m/%d/%Y"
        orgs = []
        dates = []

        try:
            logger.info("[{}] Started Extracting Entities".format(self.filename))
            for tag in tags:
                (ent_name, ent_start, ent_end, ent_label) = tag
                # print(tag)

                # Organization or Person names extraction
                if ent_label == 'ORG' or ent_label == 'PERSON':
                    start = 0
                    org = Extract_Entity_Boundary(self.filename).extract_entity_boundary(text, tag, start)
                    (ent_label, preceding_text, succeeding_text) = org
                    # print(ent_name, org)

                    if len(preceding_text.split()) > 0:
                        if preceding_text.split()[-1] in CMSConfig.fp_start_keywords and first_party is None \
                                and not (any(key == ent_name.strip().lower() for key in CMSConfig.party_exclude_keywords)):
                            if 'Inc.' in ent_name:
                                first_party = ent_name.split('Inc.')[0] + 'Inc.'
                            elif 'Ltd.' in ent_name:
                                first_party = ent_name.split('Ltd.')[0] + 'Ltd.'
                            else:
                                first_party = ent_name
                        elif preceding_text.split()[-1] in CMSConfig.sp_start_keywords and second_party is None and first_party is not None \
                                and not (any(key == ent_name.strip().lower() for key in CMSConfig.party_exclude_keywords)) and ent_name != first_party:
                            if 'Inc.' in ent_name:
                                second_party = ent_name.split('Inc.')[0] + 'Inc.'
                            elif 'Ltd.' in ent_name:
                                second_party = ent_name.split('Ltd.')[0] + 'Ltd.'
                            else:
                                second_party = ent_name 
                    orgs.append((ent_name, org))

                # Effective Date extraction
                elif ent_label == 'DATE':
                    start = 0
                    date = Extract_Entity_Boundary(self.filename).extract_entity_boundary(text, tag, start)
                    (ent_label, preceding_text, succeeding_text) = date
                    #print(ent_name, date)

                    if effective_date is None:
                        # print(ent_name, date)
                        date_keyword_in_preceding_words = (any(item in preceding_text for item in CMSConfig.date_start_keywords)
                                                           or any(item in succeeding_text for item in CMSConfig.date_end_keywords)) \
                                                          and (any(item in months for item in ent_name.upper().split()) or len(ent_name.split('/'))>1)
                        if date_keyword_in_preceding_words and list(datefinder.find_dates(ent_name)):
                            effective_date = datetime.strftime(list(datefinder.find_dates(ent_name))[0], date_format)
                    dates.append((ent_name, date))
                start = ent_end + 1

            logger.info("[{}] Completed Extracting Entities".format(self.filename))

        except Exception as ex:
            logger.error('[{}] Exception raised - {}'.format(self.filename, ex))

        return {"filename": filename, "first_party": first_party, "second_party": second_party, "effective_date": effective_date, "rebate_table_flag": rebate_table_flag}

    def get_rebate_table_flag(self, text):
        try:
            logger.info("[{}] Getting Rebate Table Flag".format(self.filename))
            text = " ".join(text.split("\n")).lower()
            if text.count("volume rebate table") == 2:
                return "True"
            else:
                return "False"
        except Exception as ex:
            logger.error('[{}] Exception raised - {}'.format(self.filename, ex))


if __name__ == '__main__':
    path = "../../data/MSA/"
    for file in os.listdir(path):
        file = 'D16244.pdf.out.html.txt'
        with open(path+file) as f:
            data = f.read()
            #text = re.sub('[^a-zA-Z0-9 ]', '', data.replace('\n', ' '))
            entities = entity_extraction(file).process(data)
            #df = pd.DataFrame([entities])
            #df.to_csv('../../data/processed/MSA/MAS_Entities_Duckling_Oct23.csv', mode='a', index=None, header=False)
            print('Entities extracted for msa file {} are : {}'.format(file, entities))
        break
    #cls = entity_extraction("filename")
    #cls.process("text")

