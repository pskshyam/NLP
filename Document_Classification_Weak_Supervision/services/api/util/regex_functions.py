import re
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class regex_functions(object):

    def __init__(self, filename):
            self.name = 'Keyword Search'
            self.filename = filename

    def msa_regex_lookup(self, x):
        nonmsa_keywords = ['sow', 'statement of work', 'addendum', 'amendment', 'confidentiality agreement',
                           'disclosure agreement']
        match1 = re.search(
            r"(agreement agreement|master agreement|master services agreement|this agreement)\s+(\S+\s+){1,30}(by and between|by and among|between|among)(.+?) and (.+?)",
            x)
        match2 = re.search(
            r"(agreement agreement|master agreement|master services agreement|this agreement)\s+(\S+\s+){1,30}(effective)(.+?) and (.+?)",
            x)
        match3 = re.search(
            r"(agreement agreement|master agreement|master services agreement|this agreement)\s+(\S+\s+){1,30}(the undersigned)(.+?) and (.+?)",
            x)

        if (match1 and not (any(key in x[:match1.end()] for key in nonmsa_keywords))) \
            or (match2 and not (any(key in x[:match2.end()] for key in nonmsa_keywords))) \
            or (match3 and not (any(key in x[:match3.end()] for key in nonmsa_keywords))):
            return 1
        return 0

    def addendum_regex_lookup(self,x):
        match1 = re.search(
            r"(addendum|amendment|change request|change order)\s+(\S+\s+){1,30}(by and between|by and among|between) (.+?) and (.+?)",
            x)
        match2 = re.search(r"(addendum|amendment)\s+(\S+\s+){1,30}(schedule a|effective) (.+?) and (.+?)", x)
        match3 = re.search(r"(addendum|amendment) (.+?) (the undersigned) (.+?) and (.+?)", x)

        if (match1 and match1.start() < 1000) or (match2 and match2.start() < 1000) or (
            match3 and match3.start() < 1000):
            return 1
        return 0

    def sow_regex_lookup(self,x):
        nonsow_keywords = ['addendum', 'amendment']
        match1 = re.search(
            r"(sow|statement of work|work order|task order)\s+(\S+\s+){1,30}(by and between|by and among|executed by|between|entered into)(.+?) and (.+?)",
            x)
        match2 = re.search(r"(sow|statement of work|work order|task order)\s+(\S+\s+){1,30}(effective) (.+?) and (.+?)",
                           x)
        match3 = re.search(
            r"(sow|statement of work|work order|task order)\s+(\S+\s+){1,30}(the undersigned) (.+?) and (.+?)", x)

        if (match1 and match1.start() < 1000 and not (any(key in x[:match1.end()] for key in nonsow_keywords))
                or (match2 and match2.start() < 1000 and not (any(key not in x[:match2.end()] for key in nonsow_keywords)))
                or match3 and match3.start() < 1000 and not (any(key not in x[:match3.end()] for key in nonsow_keywords))):
            return 1
        return 0

    def nda_regex_lookup(self,x):
        nda_keywords = ['mutual confidentiality', 'confidentiality agreement', 'disclosure agreement']
        match1 = re.search(
            r"(disclosure agreement|confidentiality agreement)\s+(\S+\s+){1,30}(by and between|by and among|between|among)(.+?) and (.+?)",
            x)

        if match1 and match1.start() < 1000 and any(key in x for key in nda_keywords):
            return 1
        return 0

    def others_lookup(self,x):
        msa = self.msa_regex_lookup(x)
        sow = self.sow_regex_lookup(x)
        addendum = self.addendum_regex_lookup(x)
        nda = self.nda_regex_lookup(x)

        if msa == 0 and sow == 0 and addendum == 0 and nda == 0:
            return 1
        logger.info('[{}] Keywords lookup completed'.format(self.filename))
        return 0