from models.context_extraction.impl.context_parts.utils import check_tuples, cut_element, retokenize_object_final, replace_object, remove_extra_index
from app.common.logger import set_up_logging
import copy


class SubjectExtractor:
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
        self.logger.info("************ Extracting subject objects")
        retokenize_object_final(text_information.actions_context_structure, 'action_subject', ['nsubj', 'nsubjpass'])

        self.cut_subject(text_information.actions_context_structure)

        replace_object(text_information.actions_context_structure, text_information.replacements, 'action_subject')

        remove_extra_index(text_information.actions_context_structure, 'action_subject')

        self.logger.info("************ Extracting subject done")

    def cut_subject(self, actions_structure):
        """Check if the verb has been retokenized into the subject, in that case remove if from the subject part

        Parameters
        ----------
        actions_structure : list
            list of dictionaries, each dictionary contains the information of an action
        """
        for action_dict in actions_structure:
            doc = copy.copy(action_dict['doc'])
            for subj_dict in action_dict['context']['action_subject']:
                for verb_dict in action_dict['context']['verbs']:
                    if check_tuples(subj_dict['indexes'], verb_dict['indexes']):
                        cut_element(subj_dict, doc)





