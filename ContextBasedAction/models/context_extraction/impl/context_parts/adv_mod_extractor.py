from models.context_extraction.impl.context_parts.utils import retokenize_object_final, check_tuples, cut_objects, replace_object
from app.common.logger import set_up_logging
import copy
import textacy


class AdverbModExtractor:
    """This class is one of the steps of the pipeline that we will use to extract the context"""
    def __init__(self):

        self.logger = set_up_logging(__name__)

    def extract(self, text_information):
        """This method is present in all the steps of the pipeline that we will use to extract the context
        and is the first that is called to extract the corresponding part of the context

        Parameters
        ----------
        text_information : instance of text_information class
            contains all the information related to the text and its context
        """
        self.logger.info("************ Extracting Adverbs")
        self.retokenize_adverb(text_information.actions_context_structure, 'adverb_mod', ['advmod', 'acomp'])

        retokenize_object_final(text_information.actions_context_structure, 'attributes', ['attr'])
        cut_objects(text_information.actions_context_structure, 'attributes')
        replace_object(text_information.actions_context_structure, text_information.replacements, 'attributes')

        self.logger.info("************ Extracting Adverbs done")

    def retokenize_adverb(self, actions_structure, obj_type, list_to_check):
        """Join different tokens (retokenize from spacy). Used for adverbs only

        Parameters
        ----------
        actions_structure : list
            list of dictionaries, each dictionary contains the information of an action

        obj_type :  str
            string with the context part type

        list_to_check :  list
            list of string with the part of speech names of the words that need to be retokenized

        """

        pattern = r'(<CCONJ>*<ADJ>*<ADV>*)*'
        for i, action_dict in enumerate(actions_structure):
            obj_list = []
            doc = copy.copy(action_dict['doc'])
            list_adverbs = textacy.extract.pos_regex_matches(doc, pattern)
            for element in list_adverbs:
                if element[-1].pos_ == u'CCONJ':
                    element = element[:-1]
                for token in element:
                    if token.dep_ in list_to_check:
                        obj_list.append({'initial_value': element.text, 'indexes': (element[0].i, element[-1].i + 1),
                                         'replacement_value': element.text})
                        break
            obj_list = self.filter_adverbs(obj_list)
            actions_structure[i]['context'][obj_type] = obj_list

    def filter_adverbs(self, obj_list):
        """Use token indexes to remove repeated adverbs or adverbs that are contained into other

        Parameters
        ----------
        obj_list :  list of dictionaries with information about the adverbs

        Returns
        -------
        list
            list of dictionaries with information about the adverbs

        """
        index_remove = []
        for i, obj_dict_i in enumerate(obj_list):
            for j, obj_dict_j in enumerate(obj_list):
                if check_tuples(obj_dict_i['indexes'], obj_dict_j['indexes']) \
                        and obj_dict_i['indexes'] != obj_dict_j['indexes']:
                    index_remove.append(j)
        for index in reversed(list(set(index_remove))):
            obj_list.pop(index)
        return obj_list
