from models.context_extraction.impl.utils import get_doc, get_actions_information_structure
from models.context_extraction.impl.context_parts.replacements_extractor import get_all_replacements


class TextInformation():
    """
    A class used to contain all the information, related to the text, that is used during the context extraction

    Attributes
    ----------
    text : str
        a string with the preprocessed text
    doc : Spacy tokens doc
          An instance of spacy doc with an instance of spacy token for each word in the text
    replacements : list
        list of dictionaries, each dictionary contains the information of a replacement obtained from neuralcoref
    actions_context_structure : list
        list of dictionaries, each dictionary inside the list will contain information about an action and its context
    """

    def __init__(self, text):
        self.text = text

        self.doc = get_doc(text)

        self.replacements = get_all_replacements(self.doc)

        self.actions_context_structure = get_actions_information_structure(self.doc)


