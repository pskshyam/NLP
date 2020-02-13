from app.common.logger import set_up_logging
logger = set_up_logging(__name__)


def get_all_replacements(doc):
    """Obtain the references from neuralcoref reference clusters
     and recursively check if a reference is contained in other reference cluster and replace it

        Parameters
        ----------
        doc : Spacy tokens doc
            An instance of spacy doc with an instance of spacy token for each word in the text

        Returns
        -------
        list
            list of dictionaries, each dictionary contains the information of a replacement
    """

    logger.info("************ Getting replacements")
    replacement_list = sorted(get_initial_replacement(doc), key=lambda x:x['initial_index'][0])
    replacement_list_aux = ""
    count = 0
    while replacement_list_aux != str(replacement_list):
        count += 1
        replacement_list_aux = str(replacement_list)
        check_replacements(replacement_list)
        if count > 10:
            replacement_list = sorted(get_initial_replacement(doc), key=lambda x: x['initial_index'][0])
            break
    logger.info("************ Getting replacements done")
    return replacement_list


def get_initial_replacement(doc):
    """Obtain the replacements from neuralcoref reference clusters

        Parameters
        ----------
        doc : Spacy tokens doc
            An instance of spacy doc with an instance of spacy token for each word in the text

        Returns
        -------
        list
            list of dictionaries, each dictionary contains the information of a reference obtained from neuralcoref
    """

    replacement_list = [{
        "initial_value": mention.text,
        "initial_index": (mention.start, mention.end),
        "replacement_value": cluster.main.text,
        "replacement_main_token": cluster.main,
        "initial_main_token": mention
    } for cluster in doc._.coref_clusters for mention in cluster.mentions if
        mention.text.lower() != cluster.main.text.lower()]
    remove_pronouns_replacements(replacement_list)
    return replacement_list


def check_replacements(replacement_list):
    """Recursively check if a reference inside the input list is contained in other reference cluster and replace it

        Parameters
        ----------
        replacement_list : list
        list of dictionaries, each dictionary contains the information of a reference obtained from neuralcoref

        Returns
        -------
        list
            list of dictionaries, each dictionary contains the information of a replacement
    """

    for i, replacement in enumerate(replacement_list):
        replacement_list[i]['replacement_value_list'] = replacement_list[i]['replacement_value'].split(u' ')

    for i, replacement in enumerate(replacement_list):
        list_replacements = replacement_list[i]['replacement_value_list']
        for num_word, word in enumerate(list_replacements):
            indexes_rep = []
            for j, replacementj in enumerate(replacement_list):
                if list_replacements[num_word] == replacementj['initial_value'] and i > j:
                    indexes_rep.append(j)
            if len(indexes_rep) > 0:
                j_nearest = indexes_rep[-1]
                replacement_list[i]['replacement_value_list'][num_word] = replacement_list[j_nearest]['replacement_value']

    for i, replacement in enumerate(replacement_list):
        new_replaced_value = u" ".join(replacement_list[i]['replacement_value_list'])
        if new_replaced_value != replacement_list[i]['replacement_value']:
            replacement_list[i]['replacement_value'] = new_replaced_value
        replacement_list[i].pop('replacement_value_list')


def remove_pronouns_replacements(replacement_list):
    """Remove those replacements whose main token is only a pronoun or a determinant

        Parameters
        ----------
        replacement_list : list
            list of dictionaries, each dictionary contains the information of a replacement

        Returns
        -------
        list
            list of dictionaries, each dictionary contains the information of a replacement
    """

    replacement_to_remove = []
    for i, replacement in enumerate(replacement_list):
        if replacement['initial_value'] != replacement['replacement_value']:
            initial_token_text = [token for token in replacement['initial_main_token']]
            replacement_token_text = [token for token in replacement['replacement_main_token']]

            different_tokens = [token for token in replacement_token_text if token not in initial_token_text]
            pos_tag_list = ['DET', 'PRON']
            if all(token.pos_ in pos_tag_list for token in different_tokens):
                replacement_to_remove.append(i)
    for rep_index in reversed(replacement_to_remove):
        replacement_list.pop(rep_index)

