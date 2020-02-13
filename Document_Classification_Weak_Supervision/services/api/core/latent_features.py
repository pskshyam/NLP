import pandas as pd
from services.api.util.regex_functions import regex_functions
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class latent_features(object):

    def __init__(self, filename):
        self.name = 'Forming Latent Features Dataframe'
        self.filename = filename

    def feature_extraction(self, text):
        msa_keywords = ['indemnified party', 'indemnifying party', 'force majeure', 'industrial property right',
                        'privacy restricted data',
                        'prior written notice', 'subject matter hereof']

        addendum_keywords = ['addendum number', 'addendum date', 'addendum effective date',
                             'term of addendum', 'term of amendment', 'addendum made',
                             'addendum entered', 'duration of the addendum', 'purpose of the addendum',
                             'subsequent addendum', 'amendment number', 'amendment date', 'amendment entered',
                             'amendment made', 'amendment executed', 'amendment effective date',
                             'agreement hereby amended', 'service agreement amendment']

        sow_keywords = ['sow effective date', 'work sow', 'sow shall', 'sow term', 'client sow',
                        'sow agreement', 'statement of work effective', 'sow end date', 'sow duration']

        nda_keywords = ['mutual confidentiality', 'affiliated entity', 'agreement negotiation', 'disclosure hereunder',
                        'mutual confidentiality agreement', 'non confidential basis', 'confidential information agent',
                        'confidentiality non disclosure', 'party certain confidential information',
                        'party furnish']

        other_keywords = ['sir madam', 'letter to inform', 'engagement letter', 'service order form',
                          'change request form', 'signature form', 'agreement service order', 'service component order',
                          'component order', 'editorial service order']

        msa_keywords_count = 0
        sow_keywords_count = 0
        nda_keywords_count = 0
        addendum_keywords_count = 0
        others_keywords_count = 0
        dict_latent = {}
        # ============MSA=============

        # Check for matching MSA keywords
        try:
            for key in msa_keywords:
                if key in text:
                    dict_latent[key] = 1
                    msa_keywords_count += 1
                else:
                    dict_latent[key] = 0
            dict_latent['msa_keywords_count'] = msa_keywords_count
            # Call MSA regex lookup function
            dict_latent['msa_regex_lookup'] = regex_functions(self.filename).msa_regex_lookup(text)
        # ============SOW=============

        # Check for matching SOW keywords
            for key in sow_keywords:
                if key in text:
                    dict_latent[key] = 1
                    sow_keywords_count += 1
                else:
                    dict_latent[key] = 0
            dict_latent['sow_keywords_count'] = sow_keywords_count
            # Call SOW regex lookup function
            dict_latent['sow_regex_lookup'] = regex_functions(self.filename).sow_regex_lookup(text)
            # ==========ADDENDUM=============

            # Check for matching Addendum keywords
            for key in addendum_keywords:
                if key in text:
                    dict_latent[key] = 1
                    addendum_keywords_count += 1
                else:
                    dict_latent[key] = 0
            dict_latent['addendum_keywords_count'] = addendum_keywords_count
            # Call Addendum regex lookup function
            dict_latent['addendum_regex_lookup'] = regex_functions(self.filename).addendum_regex_lookup(text)
            # ============NDA=============

            # Check for matching NDA keywords
            for key in nda_keywords:
                if key in text:
                    dict_latent[key] = 1
                    nda_keywords_count += 1
                else:
                    dict_latent[key] = 0
            dict_latent['nda_keywords_count'] = nda_keywords_count
            # Call NDA regex lookup function
            dict_latent['nda_regex_lookup'] = regex_functions(self.filename).nda_regex_lookup(text)
            # ============Others===========

            # Check for matching Others keywords
            for key in other_keywords:
                if key in text:
                    dict_latent[key] = 1
                    others_keywords_count += 1
                else:
                    dict_latent[key] = 0

            dict_latent['others_keywords_count'] = others_keywords_count
            # Call Others regex lookup function
            dict_latent['others_lookup'] = regex_functions(self.filename).others_lookup(text)

            # Append dictionary to the DataFrame
            df_latent_pred = pd.DataFrame()
            df_latent_pred = df_latent_pred.append(dict_latent, ignore_index=True)

            # fill NaNs with 0
            df_latent_pred.fillna(0, inplace=True)
            logger.info('[{}] Keywords search completed'.format(self.filename))
            return df_latent_pred

        except Exception as ex:
            logger.error('[{}] Exception occurred in forming data frame with latent features  - {}'.format(self.filename, ex))
            return None



