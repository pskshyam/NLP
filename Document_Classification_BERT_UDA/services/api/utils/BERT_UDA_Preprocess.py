# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:45:33 2019

@author: 141032
"""

import copy
import os
import sys

import numpy as np
import pandas as pd
import tensorflow as tf
from services.api.utils.augmentation import sent_level_augment
from services.api.utils.preprocess import *
from services.api.utils import tokenization

tf.logging.set_verbosity(tf.logging.INFO)


class PaddingInputExample(object):
    """Fake example so the num input examples is a multiple of the batch size.
  When running eval/predict on the TPU, we need to pad the number of examples
  to be a multiple of the batch size, because the TPU requires a fixed batch
  size. The alternative is to drop the last batch, which is bad because it means
  the entire output data won't be generated.
  We use this class instead of `None` because treating `None` as padding
  battches could cause silent errors.
  """

class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, label=None):
        """Constructs a InputExample.
    Args:
      guid: Unique id for the example.
      text_a: string. The untokenized text of the first sequence. For single
        sequence tasks, only this sequence must be specified.
      text_b: (Optional) string. The untokenized text of the second sequence.
        Only must be specified for sequence pair tasks.
      label: (Optional) string. The label of the example. This should be
        specified for train and dev examples, but not for test examples.
    """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label

class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, input_type_ids, label_id):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.input_type_ids = input_type_ids
        self.label_id = label_id
        
    def _create_int_feature(self, values):
        feature = tf.train.Feature(int64_list=tf.train.Int64List(value=list(values)))
        return feature

    def get_dict_features(self):
        return {
            "input_ids": self._create_int_feature(self.input_ids),
            "input_mask": self._create_int_feature(self.input_mask),
            "input_type_ids": self._create_int_feature(self.input_type_ids),
            "label_ids": self._create_int_feature([self.label_id])
        }


class PairedUnsupInputFeatures(object):
    """Features for paired unsup data."""

    def __init__(self, ori_input_ids, ori_input_mask, ori_input_type_ids,
               aug_input_ids, aug_input_mask, aug_input_type_ids):
        self.ori_input_ids = ori_input_ids
        self.ori_input_mask = ori_input_mask
        self.ori_input_type_ids = ori_input_type_ids
        self.aug_input_ids = aug_input_ids
        self.aug_input_mask = aug_input_mask
        self.aug_input_type_ids = aug_input_type_ids
    
    def _create_int_feature(self, values):
        feature = tf.train.Feature(int64_list=tf.train.Int64List(value=list(values)))
        return feature

    def get_dict_features(self):
        return {
            "ori_input_ids": self._create_int_feature(self.ori_input_ids),
            "ori_input_mask": self._create_int_feature(self.ori_input_mask),
            "ori_input_type_ids": self._create_int_feature(self.ori_input_type_ids),
            "aug_input_ids": self._create_int_feature(self.aug_input_ids),
            "aug_input_mask": self._create_int_feature(self.aug_input_mask),
            "aug_input_type_ids": self._create_int_feature(self.aug_input_type_ids),
        }

class BERT_Feature_Generation(object):
    def __init__(self):
        #Add the checkpoint path here
        self.bert_model_path = "uncased_L-12_H-768_A-12/"
        
    
    def create_tokenizer(self, vocab_file):
        return tokenization.FullTokenizer(vocab_file=vocab_file, do_lower_case=True)
    
    def convert_single_example(self, tokenizer, example, max_seq_length=128):
        """Converts a single `InputExample` into a single `InputFeatures`."""
    
        if isinstance(example, PaddingInputExample):
            input_ids = [0] * max_seq_length
            input_mask = [0] * max_seq_length
            segment_ids = [0] * max_seq_length
            label = 0
            return input_ids, input_mask, segment_ids, label
    
        tokens_a = tokenizer.tokenize(example.text_a)
        if len(tokens_a) > max_seq_length - 2:
            tokens_a = tokens_a[0 : (max_seq_length - 2)]
    
        tokens = []
        segment_ids = []
        tokens.append("[CLS]")
        segment_ids.append(0)
        for token in tokens_a:
            tokens.append(token)
            segment_ids.append(0)
        tokens.append("[SEP]")
        segment_ids.append(0)
    
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
    
        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1] * len(input_ids)
    
        # Zero-pad up to the sequence length.
        while len(input_ids) < max_seq_length:
            input_ids.append(0)
            input_mask.append(0)
            segment_ids.append(0)
    
        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length
    
        return input_ids, input_mask, segment_ids, example.label
    
    def convert_local_examples_to_features(self, tokenizer, examples, max_seq_length=128):
        """Convert a set of `InputExample`s to a list of `InputFeatures`."""
        features = []
        for example in examples:
            input_id, input_mask, segment_id, label = self.convert_single_example(
                tokenizer, example, max_seq_length
            )
            features.append(
            InputFeatures(
                input_ids=input_id,
                input_mask=input_mask,
                input_type_ids=segment_id,
                label_id=label))
        return features
    
    def convert_text_to_examples(self, texts, labels):
        """Create InputExamples"""
        InputExamples = []
        for text, label in zip(texts, labels):
            InputExamples.append(
                InputExample(guid=None, text_a=" ".join(text), text_b=None, label=label)
            )
        return InputExamples
    
    def get_bert_tokenizer(self, vocab_file):
        # Instantiate tokenizer
        tokenizer = self.create_tokenizer(vocab_file)
        return tokenizer
    
class BERT_UDA_Preprocess(object):
    def get_sup_features(self, texts, labels, vocab_file, seq_length=128):
        feature_gen = BERT_Feature_Generation()
        tokenizer = feature_gen.get_bert_tokenizer(vocab_file)
        
        # Convert data to InputExample format
        train_examples = feature_gen.convert_text_to_examples(texts, labels)
    
        # Convert to features
        features = feature_gen.convert_local_examples_to_features(tokenizer, train_examples, seq_length)
        return features
    
    def get_unsup_features(self, unsup_texts, unsup_labels, aug_ops, sub_set, aug_copy_num, vocab_file, bt_filepath, seq_length=128):
        feature_gen = BERT_Feature_Generation()
        tokenizer = feature_gen.get_bert_tokenizer(vocab_file)

        ori_examples = unsup_texts
        data_total_size= len(ori_examples)
        start = 0
        end = len(ori_examples)
        unsup_labels = []
        labels = unsup_labels + ['unsup']
    
        
        ori_examples = feature_gen.convert_text_to_examples(ori_examples, labels)

        aug_examples = copy.deepcopy(ori_examples)
        aug_examples = sent_level_augment.run_augment(
          aug_examples, aug_ops, sub_set,
          aug_copy_num,
          start, end, data_total_size, bt_filepath)
        
        for ex in aug_examples[:10]:
            print(ex.text_a)
    
        # Instantiate tokenizer
        #tokenizer = create_tokenizer_from_hub_module()
    
        # Convert original examples to InputExample format
        ori_features = feature_gen.convert_local_examples_to_features(tokenizer, ori_examples, max_seq_length=seq_length)
        
        #Convert augmented examples to Paired Unsupervised Input Features
        #aug_examples = convert_text_to_examples(aug_examples, labels)
        aug_features = feature_gen.convert_local_examples_to_features(tokenizer, aug_examples, max_seq_length=seq_length)
        
        unsup_features = []
        for ori_feat, aug_feat in zip(ori_features, aug_features):
            unsup_features.append(PairedUnsupInputFeatures(
                ori_feat.input_ids,
                ori_feat.input_mask,
                ori_feat.input_type_ids,
                aug_feat.input_ids,
                aug_feat.input_mask,
                aug_feat.input_type_ids,
                ))
        print("Unsup Features: ", unsup_features)
        return unsup_features
    
    def dump_tfrecord(self, features, data_path, worker_id=0, max_shard_size=4096):
        """Dump tf record."""
        if not tf.gfile.Exists(data_path):
            tf.gfile.MakeDirs(data_path)
        tf.logging.info("dumping TFRecords")
        np.random.shuffle(features)
        shard_cnt = 0
        shard_size = 0
        tfrecord_writer = obtain_tfrecord_writer(data_path, worker_id, shard_cnt)
        for feature in features:
            tf_example = tf.train.Example(
                features=tf.train.Features(feature=feature.get_dict_features()))
            if shard_size >= max_shard_size:
                tfrecord_writer.close()
                shard_cnt += 1
                tfrecord_writer = obtain_tfrecord_writer(data_path, worker_id, shard_cnt)
                shard_size = 0
            shard_size += 1
            tfrecord_writer.write(tf_example.SerializeToString())
        tfrecord_writer.close()

    def process_data(self, input_filepath):
        df = pd.read_csv(input_filepath)
        texts = df['text']
        labels = df['label']
        return texts, labels
    
    def generate_labeled_features(self, input_filepath, output_filepath, vocab_file):
        texts, labels = self.process_data(input_filepath)
        features = self.get_sup_features(texts, labels, vocab_file)
        self.dump_tfrecord(features, output_filepath)

    def generate_unlabeled_features(self, input_filepath, output_filepath, vocab_file, bt_filepath):
        aug_ops = 'bt-0.9'
        sub_set = 'unsup_in'
        aug_copy_num = 0
        texts, labels = self.process_data(input_filepath)
        features = self.get_unsup_features(texts, labels, aug_ops, sub_set, aug_copy_num, vocab_file, bt_filepath)
        unsup_out_dir = os.path.join(output_filepath, aug_ops, str(aug_copy_num))
        self.dump_tfrecord(features, unsup_out_dir)


"""if __name__ == '__main__':
    output_filepath = sys.argv[1]
#    eval_output_filepath = sys.argv[1]
    sup_filepath = sys.argv[2]
#    eval_filepath = sys.argv[2]
#    unsup_filepath = sys.argv[2]
    vocab_file = sys.argv[3]
#    bt_filepath = sys.argv[4]
    preprocess = BERT_UDA_Preprocess()
    preprocess.generate_labeled_features(sup_filepath, output_filepath, vocab_file)
#    preprocess.generate_labeled_features(eval_filepath, eval_output_filepath, vocab_file)
 #   preprocess.generate_unlabeled_features(unsup_filepath, output_filepath, vocab_file, bt_filepath)
"""
