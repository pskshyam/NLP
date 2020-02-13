from models.context_extraction.impl.context_parts.adv_mod_extractor import AdverbModExtractor
from models.context_extraction.impl.context_parts import adv_mod_extractor
from models.context_extraction import context_extractor
import textacy


def test_extract(mocker):
    adv_mod_extractor_instance = AdverbModExtractor()
    mocker.patch.object(AdverbModExtractor, "retokenize_adverb")
    mocker.patch.object(adv_mod_extractor, "retokenize_object_final")
    mocker.patch.object(adv_mod_extractor, "cut_objects")
    mocker.patch.object(adv_mod_extractor, "replace_object")
    text_information = mocker.patch.object(context_extractor, 'TextInformation')

    adv_mod_extractor_instance.extract(text_information)

    assert AdverbModExtractor.retokenize_adverb.call_count == 1
    assert adv_mod_extractor.retokenize_object_final.call_count == 1
    assert adv_mod_extractor.cut_objects.call_count == 1
    assert adv_mod_extractor.replace_object.call_count == 1


def test_retokenize_adverb(mocker):

    adv_mod_extractor_instance = AdverbModExtractor()

    mocker.patch.object(textacy.extract, "pos_regex_matches", return_value=[])
    mocker.patch.object(AdverbModExtractor, "filter_adverbs")

    adv_mod_extractor_instance.retokenize_adverb([{"doc": "doc_example",
                                                   "context": {"obj_type": ""}}],
                                                 "obj_type", [])

    assert AdverbModExtractor.filter_adverbs.call_count == 1


def test_filter_adverbs_check_tuples_true(mocker):

    obj_list = [{'indexes': (2, 7)}, {'indexes': (4, 6)}]
    adv_mod_extractor_instance = AdverbModExtractor()

    mocker.patch.object(adv_mod_extractor, "check_tuples", return_value=True)

    obj_list_return = adv_mod_extractor_instance.filter_adverbs(obj_list)

    assert adv_mod_extractor.check_tuples.call_count == 4
    assert len(obj_list_return) == 0


def test_filter_adverbs_check_tuples_false(mocker):

    obj_list = [{'indexes': (2, 7)}, {'indexes': (4, 6)}]
    adv_mod_extractor_instance = AdverbModExtractor()

    mocker.patch.object(adv_mod_extractor, "check_tuples", return_value=False)

    obj_list_return = adv_mod_extractor_instance.filter_adverbs(obj_list)

    assert adv_mod_extractor.check_tuples.call_count == 4
    assert len(obj_list_return) == 2



