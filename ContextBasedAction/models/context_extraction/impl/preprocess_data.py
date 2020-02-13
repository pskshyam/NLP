import re
from models.context_extraction.impl.utils import get_doc
from models.context_extraction.impl.context_parts.utils import print_doc_tokens


def preprocess_text(text, conversational):
    """Calls different methods to preprocess the text depending on "conversational" flag value

    Parameters
    ----------
    text : str(non conversational data) or list(conversational data)
        The text inside the file that was sent to /extract API
    conversational : bool
        A flag used to identify conversational(True) or non-conversational(False) data

    Returns
    -------
    str
        A string with the preprocessed text
    """
    if conversational:
        text = [phrase for phrase in text.split("\n") if len(phrase) > 0]
        text = transform_conversation(text)
    text = replace_marks(text)
    doc = get_doc(text)
    text = clean_data(doc)
    return text


def transform_conversation(text):
    """This method will be used in case of conversational data
    Preprocess a list of sentences separately then join them in a single text

    Parameters
    ----------
    text : list
        List of strings with the text inside the input file

    Returns
    -------
    str
        A string with the preprocessed text
    """
    transformed_sentences_list = []
    for sentence in text:
        transformed_sentences_list.append(transform_sentence(sentence))
    entire_text = ' '.join(transformed_sentences_list)
    return entire_text


def get_colons_index(doc):
    """This method will be used in case of conversational data
    Get the index position of the first colons value of each sentence
    Parameters
    ----------
    doc : Spacy tokens doc
        An instance of spacy doc with an instance of spacy token for each word in the sentence

    Returns
    -------
    int
        Position of the first colons found in the sentence
    """
    colons_index = None
    for token in doc:
        if token.text == ':':
            colons_index = token.i
            break
    if colons_index is None:
        raise Exception("Text has not a valid conversational format")
    return colons_index


def transform_sentence(sentence):
    """This method will be used in case of conversational data
    Apply different preprocessors to each sentence of the conversation
    Parameters
    ----------
    sentence : str
        A string with a sentence of the conversational data text

    Returns
    -------
    str
        A string with the preprocessed sentence
    """

    doc = get_doc(sentence)
    colons_index = get_colons_index(doc)
    name = " ".join([doc[x].text for x in range(colons_index)])
    name_reference_list = ["I", "ME", "MY"]
    verb_reference_list = ["'M", "AM"]

    transformed_tokens = []
    for token in doc[colons_index+1:]:
        if token.pos_ != 'PUNCT' and token.pos_ != 'SPACE':
            if token.text.upper() in name_reference_list:
                transformed_tokens.append(' ' + name)
            elif token.text.upper() in verb_reference_list:
                transformed_tokens.append(' ' + 'is')
            elif token.text[0] == "'" and token.text.upper() not in verb_reference_list:
                transformed_tokens.append(token.text)
            else:
                transformed_tokens.append(' ' + token.text)
        else:
            transformed_tokens.append(token.text)

    if doc[-1].pos_ != 'PUNCT':
        transformed_tokens.append('.')
    text = ''.join(transformed_tokens)[1:]
    return text


def replace_marks(text):
    """This method will be used for both conversational and non-conversational data
    Apply different regex patterns to clean the text

    Parameters
    ----------
    text : str

    Returns
    -------
    str
        The method input text after the apply different regex patterns
    """
    text = replace_text(text)
    text = re.sub(r'(\s*\!*\s*\,*\s*\?+\s*\.*\s*)+', '? ',  text)
    text = re.sub(r'(\s*\!+\s*\,*\s*\.*\s*)+', '. ',  text)
    text = re.sub(r'(\s*\,+\s*)+', ', ', text)
    text = re.sub(r'(\s*\.+\s*)+', '. ', text)
    text = re.sub(r'(\d)\s*\.+\s*(\d)', r'\1.\2', text)
    return text


def replace_text(text):
    """Replace let's expression
        Parameters
        ----------
        text : str

        Returns
        -------
        str
            Text after replacement
        """
    text = replace_str(text, "let's get", "we")
    text = replace_str(text, "let's", "we")
    return text


def replace_str(text, str_to_rep, str_rep):
    """Replace a string by a value if the string is found into a text
        Parameters
        ----------
        text : str
        str_to_rep : str
        str_rep : str

        Returns
        -------
        str
            Text after replacement
        """
    replacement_str = re.compile(re.escape(str_to_rep), re.IGNORECASE)
    text = replacement_str.sub(str_rep, text)
    return text


def get_nearest_token_index(doc, i):
    """This method is used to take the nearest token of a contracted auxiliar
      doc : Spacy tokens doc
        An instance of spacy doc with an instance of spacy token for each word in the sentence

      i: int
        index number of the token in the sentence
      Returns
      -------
      str
        A string with the corresponding auxiliar text
    """
    if doc[i+1]:
        for token in doc[i + 1:]:
            if token.pos_ is not "PUNCT":
                if doc[i+2] and token.pos_ is 'ADV':
                    nearest_token_index = token.i+1
                else:
                    nearest_token_index = token.i
                return nearest_token_index
    return -1


def expand_contracted_auxiliar(doc, i, token):
        """This method is used for both conversational and non-conversational data
         It is used to replace contracted auxiliar verb by its non-contracted form

        Parameters
        ----------
        doc : Spacy tokens doc
        An instance of spacy doc with an instance of spacy token for each word in the sentence

        i: int
          index number of the token in the sentence

        token : Spacy tokens object
          A spacy token object of a word

        Returns
        -------
        str
            A string with the corresponding auxiliar text

        """
        index = token.text.index("'", 0, len(token.text))
        aux_token = token.text[index:]
        main_token = " " + token.text[0:index] if len(token.text[0:index]) != 0 else "" + token.text[0:index]
        if aux_token.upper() == "'RE":
            aux_token = " are"
        elif aux_token.upper() == "'VE":
            aux_token = " have"
        elif aux_token.upper() == "'LL":
            aux_token = " will"
        elif aux_token.upper() == "'D":
            nearest_index = get_nearest_token_index(doc, i)
            if nearest_index != -1:
                #TODO create invariant verbs list
                invariant_verbs_list = []
                bad_recognized_verbs_list = ["like"]
                if (doc[nearest_index].tag_ in ["VB", "VBP"]
                    or(doc[nearest_index].text in bad_recognized_verbs_list and doc[nearest_index].pos_ is 'ADP'))\
                        and not doc[nearest_index].text in invariant_verbs_list:
                    aux_token = " would"
                elif doc[nearest_index].text in invariant_verbs_list:
                    aux_token = " " + aux_token
                else:
                    aux_token = " had"
            else:
                aux_token = " " + aux_token
        return main_token, aux_token


def clean_data(doc):
    """This method will be used in case of both conversational and non-conversational data.
    Join spacy tokens into a string that has the proper format to be used as input for the context extractor

        Parameters
        ----------
        doc : Spacy tokens doc
            An instance of spacy doc with an instance of spacy token for each word in the text

        Returns
        -------
        str
            A string that will be sent to the context extractor
        """
    auxiliar_contracted = ["'RE", "'VE", "'D", "'LL"]
    text_tokens = []
    for i, token in enumerate(doc):
        if token.pos_ != 'PUNCT' and token.pos_ != 'SPACE':
            if token.pos_ != 'PROPN' and token.text.isupper():
                text_tokens.append(' ' + token.text.lower())
            elif any(aux_ctr in token.text.upper() for aux_ctr in auxiliar_contracted):
                text_tokens.extend(expand_contracted_auxiliar(doc, i, token))
            else:
                text_tokens.append(' ' + token.text)
        elif token.pos_ == 'PUNCT':
            text_tokens.append(token.text)
    text = ''.join(text_tokens)
    if doc[-1].pos_ != 'PUNCT':
        text = text + '.'
    return text[1:]

