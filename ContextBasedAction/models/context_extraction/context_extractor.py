from models.context_extraction.impl.preprocess_data import preprocess_text
from models.context_extraction.impl.text_information import TextInformation
from models.context_extraction.impl.context_parts.subject_extractor import SubjectExtractor
from models.context_extraction.impl.context_parts.indirect_object_extractor import IndirectObjectExtractor
from models.context_extraction.impl.context_parts.direct_object_extractor import DirectObjectExtractor
from models.context_extraction.impl.context_parts.adv_mod_extractor import AdverbModExtractor
from models.context_extraction.impl.context_parts.verbs_extractor import VerbsExtractor
from models.context_extraction.impl.context_parts.action_extractor import ActionExtractor
from models.context_extraction.impl.context_parts.agents_extractor import AgentsExtractor
from app.common.logger import set_up_logging

logger = set_up_logging(__name__)

class ContextExtractor(object):

    def __init__(self, **kwargs):
        pass

    def raise_wrong_value(self, parameter):
        """Raise bad request exception when parameter value is not valid, add it to the logger and create response"""

        description = '"{}" value is not valid. ' \
                      'Please check your request params and retry'.format(parameter)
        logger.exception(description)
        raise Exception("Bad Request", description)

    def get_conversational(self, **kwargs):
        """check if conversational parameter from the request is valid and transform its value into a boolean

            Parameters

            kwargs : dict
                dict that can contain multiple parameters, in this case it will contain flag for conversational data

            Returns
            -------
            bool
                Boolean value for conversational data
        """

        if kwargs is not None and 'conversational' in kwargs.keys():
            assert kwargs['conversational'].lower() in ["true", "false"], self.raise_wrong_value('conversational')
            if kwargs['conversational'].lower() == 'true':
                return True
            else:
                return False
        else:
            return False

    def predict(self, text, **kwargs):
        """Call different methods to preprocess the text, then extract text information and finally creates and executes
         a pipeline to extract the context using different classes

        Parameters
        ----------
        text : str(non conversational data) or list(conversational data)
            The text inside the file that was sent to /extract API
        kwargs : dict
            dict that can contain multiple parameters, in this case it will contain a boolean flag for conversational data

        Returns
        -------
        list
            a list of dictionaries stored inside "actions_context_structure" attribute of a TextInformation class instance.
            that was created previously. The list contains the context of each action.
        """
        conversational = self.get_conversational(**kwargs)
        logger.info("====== Cleaning input data ======")
        text = preprocess_text(text, conversational)
        logger.info("====== Cleaning input data done ======")

        logger.info("====== Extracting the information of input text ======")
        text_information = TextInformation(text)
        logger.info("====== Extracting the information of input text done ======")

        logger.info("====== Creating extraction pipeline ======")
        pipeline = self.create_pipeline()
        logger.info("====== Creating extraction pipeline done ======")

        logger.info("====== Running the extraction pipeline ======")
        self.execute_pipeline(pipeline, text_information)
        logger.info("====== Running the extraction pipeline done ======")

        return text_information.actions_context_structure


    def create_pipeline(self):
        """Create a pipeline with multiple steps, each step will be a class used to extract a part of the context

        Returns
        -------
        list
            a list of classes, each of them has a method called "extract" to extract the corresponding part of the context,
            that method will be used to execute the list as a pipeline
        """

        pipeline = [VerbsExtractor(), AgentsExtractor(), IndirectObjectExtractor(), AdverbModExtractor(),
                    DirectObjectExtractor(), SubjectExtractor(), ActionExtractor()]
        return pipeline


    def execute_pipeline(self,pipeline, text_information):
        """Iterate over pipeline list and calls "extract" method for each step.

        Parameters
        ----------
        pipeline : a list of classes

        text_information : TextInformation class instance,
            An instance of TextInformation class which contains different information of the entire text
             of the input text(neuracoref replacements, spacy doc...)
        """

        for step in pipeline:
            step.extract(text_information)




