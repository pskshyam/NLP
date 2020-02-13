from models.context_extraction.impl.context_parts.utils import retokenize_object_final, replace_object, remove_extra_index, cut_objects
from app.common.logger import set_up_logging


class IndirectObjectExtractor:
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
        self.logger.info("************ Extracting indirect objects")
        retokenize_object_final(text_information.actions_context_structure, 'indirect_object', ['dative', 'iobj'])

        cut_objects(text_information.actions_context_structure, 'indirect_object')

        replace_object(text_information.actions_context_structure, text_information.replacements, 'indirect_object')

        remove_extra_index(text_information.actions_context_structure, 'indirect_object')

        self.logger.info("************ Extracting indirect objects done")

