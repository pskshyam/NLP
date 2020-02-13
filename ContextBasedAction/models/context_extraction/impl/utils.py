import spacy
import neuralcoref
from app.common.logger import set_up_logging

logger = set_up_logging(__name__)


def get_doc(text, original=False):
    """Obtain the Spacy doc object for a input string

        Parameters
        ----------
        text : string

        original : bool
            True when we don't want to add neuralcoref to spacy pipeline
            False when we need neuralcoref inside spacy pipeline

        Returns
        -------
        Spacy tokens doc object
            An instance of spacy doc with an instance of spacy token for each word in the text

    """
    nlp = spacy.load("en_core_web_sm")
    if not original:
        neuralcoref.add_to_pipe(nlp)

    doc = nlp(text)
    return doc


def get_actions_information_structure(doc):
    """Create a dictionary structure for each action, the dictionary will be populated during the execution
    of the pipeline and will contain all the information about the corresponding action and its context

        Parameters
        ----------
        doc :   Spacy tokens doc object
            An instance of spacy doc with an instance of spacy token for each word in the text

        Returns
        -------
        list
            list of dictionaries with information about each action

    """

    logger.info("************ Getting actions sctructure")

    actions_information = []
    sentence_split_signs_list = ['.', '?', '!']
    for token in doc:
        if token.pos_ == 'PUNCT' and token.text in sentence_split_signs_list:
            if not actions_information:
                action_range = (0, token.i+1)
                action_text = "".join([token.text_with_ws for token in doc[action_range[0]: action_range[1]]])
                action_doc = get_doc(action_text, True)
            else:
                last_action_end_index = actions_information[-1]["action_range"][1]
                action_range = (last_action_end_index, token.i+1)
                action_text = "".join([token.text_with_ws for token in doc[action_range[0]: action_range[1]]])
                action_doc = get_doc(action_text, True)
            action_info = {
                    "doc": action_doc,
                    "action_range": action_range,
                    "action_text": action_text,
                    "context": get_context_structure(),
                    "context_actions": [],
                    "question": check_question(action_doc)
                }
            actions_information.append(action_info)

    logger.info("************ Getting actions sctructure done")

    return actions_information


def check_question(doc):
    """Check if an action is a question

        Parameters
        ----------
        doc :   Spacy tokens doc object
            An instance of spacy doc with an instance of spacy token for each word in the text

        Returns
        -------
        bool
            True if question, False if not

    """
    for token in doc:
        if token.text == u'?':
            return True
    return False


def get_context_structure():
    """Create a dictionary and add it to the action information structure, the dictionary will be populated during the
    execution of the pipeline and will contain all the information about the context related to the corresponding action

    Returns
    -------
    dict
        dict whose keys are the different context parts
    """
    structure = {
        "action_subject":[],
        "indirect_object":[],
        "direct_object":[],
        "auxiliar_object":[],
        "verbs": [],
        "adverb_mod":[],
        "agents":[],
        "attributes":[]
    }
    return structure
