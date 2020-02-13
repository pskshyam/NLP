from __future__ import unicode_literals
import textacy
from app.common.logger import set_up_logging


class VerbsExtractor:
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
        self.logger.info("************ Extracting verbs.")
        self.verb_extraction(text_information.actions_context_structure)
        self.logger.info("************ extracting verbs done.")

    def verb_extraction(self, actions_structure):
        """obtain all the verbs in the sentence using spacy part of speech and textacy regex match,
         then split and filter the verbs to obtain the final verb component of the action

        Parameters
        ----------
        actions_structure : list
            list of dictionaries, each dictionary contains the information of an action
        """
        pattern = r'(<VERB>*<AUX>*<ADJ>*<ADV>*<CCONJ>*<PART>*<VERB>+<PART>*)+'
        for i, action_dict in enumerate(actions_structure):
            doc = action_dict['doc']
            lists = textacy.extract.pos_regex_matches(doc, pattern)
            sent_verbs = []
            for j, span in enumerate(lists):
                span, verb_dict = self.clean_init_verb(['CCONJ', 'PART'], doc, span)
                if u'auxpass' in verb_dict['dep_']:
                    verb_dict = self.clean_aux_passive(span, verb_dict)
                if 'xcomp' in verb_dict['dep_'] and 'ROOT' not in verb_dict['dep_']\
                        and verb_dict['pos_'].count("VERB") == 1:
                    verb_dict['aux'] = True
                verb_dict = self.filtering_verbs(verb_dict, span, doc)
                if verb_dict is not None:
                    verb_dict.pop('dep_')
                    verb_dict.pop('pos_')
                    sent_verbs.append(verb_dict)
            actions_structure[i]["context"]["verbs"] = sent_verbs

    def filtering_verbs(self, verb_dict, span, doc):
        """Check if it is necessary to split the verbs or not

        Parameters
        ----------
        verb_dict : dict
            dictionary with the information of a verb
        span : tuple
            range of the verb
        doc : Spacy tokens doc
          An instance of spacy doc with an instance of spacy token for each word in the text
        """
        if ('compound' in verb_dict['dep_'] or 'amod' in verb_dict['dep_']) and len(span) == 1:
            return None
        elif ('compound' in verb_dict['dep_'] or 'amod' in verb_dict['dep_']) and len(span) > 1:
            verb_dict = self.cut_verbs(verb_dict, span, doc)
        return verb_dict

    def cut_verbs(self, verb_dict, span, doc):
        """Split the verbs parts depending on syntactic dependency relation tokens from spacy
            Parameters
            ----------
            verb_dict : dict
                dict with verb context information
            span : spacy doc instance
                doc object of a part of the sentence with a spacy token instance for each word
            doc : spacy doc instance
                doc object of the sentence with a spacy token instance for each word
            Returns
            -------
            verb_dct : dict
                if span len is higher or equal than 1, returns dict with verb context information
                none if span len is zero
        """
        index_final = span.end
        for index in range(span.start, span.end):
            if doc[index].dep_ in ['compound', 'amod']:
                index_final = index
                break
        span = doc[span.start:index_final]
        if len(span) >= 1:
            verb_dict["initial_value"] = span.text
            verb_dict["replacement_value"] = span.text
            verb_dict["indexes"] = (span.start, span.end)
            return verb_dict
        else:
            return None

    def clean_aux_passive(self, span, verb_dict):
        """Remove passive auxiliar verb from the span obtained from textacy regex extract
            Parameters
            ----------
            span : spacy doc instance
                doc object of a part of the sentence with a spacy token instance for each word
            verb_dict : dict
                dict with verb context information

            Returns
            -------
            verb_dct : dict
                dict with verb context information
        """
        verb_clean_text = " ".join([token.text for token in span if token.dep_ != u'auxpass'])
        verb_dict['initial_value'] = verb_clean_text
        verb_dict['replacement_value'] = verb_clean_text
        verb_dict['active'] = False
        return verb_dict

    def clean_init_verb(self, pos_to_remove_list, doc, span):
        """Remove some parts of speech from the verb tokens list
            Parameters
            ----------
            pos_to_remove_list : list
                list of string with the part of speech tag to be removed
            doc : spacy doc instance
                doc object of the sentence with a spacy token instance for each word
            span : spacy doc instance
                doc object of a part of the sentence with a spacy token instance for each word
            Returns
            -------
            span : spacy doc instance
                doc object of a part of the sentence with a spacy token instance for each word

            verb_dct : dict
                dict with verb context information
        """

        init_index_verb = span.start
        for token in span:
            if token.pos_ not in pos_to_remove_list:
                init_index_verb = token.i
                break
        if init_index_verb != span.start:
            span = doc[init_index_verb:span.end]
        verb_dict = {"initial_value": span.text, "indexes": (span.start, span.end),
                     "replacement_value": span.text, "aux": False, "active": True,
                     "dep_": [doc[index].dep_ for index in range(span.start, span.end)],
                     "pos_": [doc[index].pos_ for index in range(span.start, span.end)]}
        return span, verb_dict

