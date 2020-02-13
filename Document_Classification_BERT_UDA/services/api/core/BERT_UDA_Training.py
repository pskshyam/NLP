# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:02:03 2019

@author: 141032
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import numpy as np
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import tensorflow as tf
from services.api.core.main import *
from services.api.core import uda
from services.api.utils import proc_data_utils
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

tf.logging.set_verbosity(tf.logging.INFO)

class BERT_UDA_Training(object):
    def __init__(self, do_train, do_eval, do_predict, train_batch_size, eval_batch_size, predict_batch_size,
                 max_seq_length, unsup_data_dir, eval_data_dir, predict_data_dir, vocab_file, bert_config_file,
                 init_checkpoint, model_dir, learning_rate, tsa, num_train_steps=20000, unsup_ratio=3,
                 aug_ops="bt-0.9", aug_copy=1):
        # Enable TF Eager execution
        tfe = tf.contrib.eager
        tfe.enable_eager_execution()

        FLAGS.do_train=do_train
        FLAGS.do_eval=do_eval
        FLAGS.do_predict=do_predict
        FLAGS.train_batch_size = train_batch_size
        FLAGS.eval_batch_size = eval_batch_size
        FLAGS.predict_batch_size = predict_batch_size
        FLAGS.max_seq_length = max_seq_length
        FLAGS.unsup_data_dir=unsup_data_dir
        FLAGS.eval_data_dir=eval_data_dir
        FLAGS.predict_data_dir=predict_data_dir
        FLAGS.bert_config_file=bert_config_file
        FLAGS.vocab_file=vocab_file
        FLAGS.init_checkpoint=init_checkpoint
        FLAGS.model_dir=model_dir
        FLAGS.num_train_steps=num_train_steps
        FLAGS.learning_rate=learning_rate
        FLAGS.unsup_ratio=unsup_ratio
        FLAGS.tsa=tsa
        FLAGS.aug_ops=aug_ops
        FLAGS.aug_copy=aug_copy

    def process(self):
        #ToDO: Bring this label list from processor
        label_list = [0, 1, 2, 3, 4]      
        bert_config = modeling.BertConfig.from_json_file(FLAGS.bert_config_file, FLAGS.model_dropout)
        #tf.gfile.MakeDirs(model_dir)
        '''flags_dict = tf.app.flag_values_dict()
        with tf.gfile.Open(os.path.join(FLAGS.model_dir, "json"), "w") as ouf:
            json.dump(flags_dict, ouf)'''
        save_checkpoints_steps = FLAGS.num_train_steps
        iterations_per_loop = min(save_checkpoints_steps, FLAGS.iterations_per_loop)
        #tpu_cluster_resolver = tf.contrib.cluster_resolver.TPUClusterResolver(
        #        tpu_name, zone=tpu_zone, project=gcp_project)
        tpu_cluster_resolver = None

        is_per_host = tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2
        run_config = tf.contrib.tpu.RunConfig(
          cluster=tpu_cluster_resolver,
          master=FLAGS.master,
          model_dir=FLAGS.model_dir,
          save_checkpoints_steps=save_checkpoints_steps,
          keep_checkpoint_max=1,
          # train_distribute=train_distribute,
          tpu_config=tf.contrib.tpu.TPUConfig(
              iterations_per_loop=iterations_per_loop,
              per_host_input_for_training=is_per_host))
        model_fn = uda.model_fn_builder(
          bert_config=bert_config,
          init_checkpoint=FLAGS.init_checkpoint,
          learning_rate=FLAGS.learning_rate,
          clip_norm=FLAGS.clip_norm,
          num_train_steps=FLAGS.num_train_steps,
          num_warmup_steps=FLAGS.num_warmup_steps,
          use_tpu=FLAGS.use_tpu,
          use_one_hot_embeddings=FLAGS.use_one_hot_embeddings,
          num_labels=len(label_list),
          unsup_ratio=FLAGS.unsup_ratio,
          uda_coeff=FLAGS.uda_coeff,
          tsa=FLAGS.tsa,
          print_feature=False,
          print_structure=False,
        )
        # If TPU is not available, this will fall back to normal Estimator on CPU
        # or GPU.
        estimator = tf.contrib.tpu.TPUEstimator(
          use_tpu=FLAGS.use_tpu,
          model_fn=model_fn,
          config=run_config,
          params={"model_dir": FLAGS.model_dir},
          train_batch_size=FLAGS.train_batch_size,
          eval_batch_size=FLAGS.eval_batch_size,
          predict_batch_size = FLAGS.predict_batch_size
        )

        if FLAGS.do_train:
            tf.logging.info("  >>> sup data dir : {}".format(FLAGS.sup_data_dir))
            if FLAGS.unsup_ratio > 0:
                tf.logging.info("  >>> unsup data dir : {}".format(FLAGS.unsup_data_dir))

            train_input_fn = proc_data_utils.training_input_fn_builder(
                FLAGS.sup_data_dir,
                FLAGS.unsup_data_dir,
                FLAGS.aug_ops,
                FLAGS.aug_copy,
                FLAGS.unsup_ratio)

        if FLAGS.do_eval:
            tf.logging.info("  >>> dev data dir : {}".format(FLAGS.eval_data_dir))
            eval_input_fn = proc_data_utils.evaluation_input_fn_builder(
                FLAGS.eval_data_dir,
                "clas")

            # ToDO: Bring this label list from processor
            #eval_size = processor.get_dev_size()
            eval_size = 1000
            eval_steps = int(eval_size / FLAGS.eval_batch_size)

        if FLAGS.do_predict:
            tf.logging.info("  >>> predict data dir : {}".format(FLAGS.predict_data_dir))
            predict_input_fn = proc_data_utils.evaluation_input_fn_builder(
                FLAGS.predict_data_dir,
                "clas")

        if FLAGS.do_train and FLAGS.do_eval:
            tf.logging.info("***** Running training & evaluation *****")
            tf.logging.info("  Supervised batch size = %d", FLAGS.train_batch_size)
            tf.logging.info("  Unsupervised batch size = %d",
                            FLAGS.train_batch_size * FLAGS.unsup_ratio)
            tf.logging.info("  Num steps = %d", FLAGS.num_train_steps)
            tf.logging.info("  Base evaluation batch size = %d", FLAGS.eval_batch_size)
            tf.logging.info("  Num steps = %d", eval_steps)
            best_acc = 0
            for _ in range(0, FLAGS.num_train_steps, save_checkpoints_steps):
              tf.logging.info("*** Running training ***")
              estimator.train(
                  input_fn=train_input_fn,
                  steps=save_checkpoints_steps)
              tf.logging.info("*** Running evaluation ***")
              dev_result = estimator.evaluate(input_fn=eval_input_fn, steps=eval_steps)
              tf.logging.info(">> Results:")
              for key in dev_result.keys():
                tf.logging.info("  %s = %s", key, str(dev_result[key]))
                dev_result[key] = dev_result[key].item()
              best_acc = max(best_acc, dev_result["eval_classify_accuracy"])
            tf.logging.info("***** Final evaluation result *****")
            tf.logging.info("Best acc: {:.3f}\n\n".format(best_acc))
        elif FLAGS.do_train:
            tf.logging.info("***** Running training *****")
            tf.logging.info("  Supervised batch size = %d", FLAGS.train_batch_size)
            tf.logging.info("  Unsupervised batch size = %d",
                            FLAGS.train_batch_size * FLAGS.unsup_ratio)
            tf.logging.info("  Num steps = %d", FLAGS.num_train_steps)
            estimator.train(input_fn=train_input_fn, max_steps=FLAGS.num_train_steps)
        elif FLAGS.do_eval:
            tf.logging.info("***** Running evaluation *****")
            tf.logging.info("  Base evaluation batch size = %d", FLAGS.eval_batch_size)
            tf.logging.info("  Num steps = %d", eval_steps)
            checkpoint_state = tf.train.get_checkpoint_state(FLAGS.model_dir)

            best_acc = 0
            for ckpt_path in checkpoint_state.all_model_checkpoint_paths:
              if not tf.gfile.Exists(ckpt_path + ".data-00000-of-00001"):
                tf.logging.info(
                    "Warning: checkpoint {:s} does not exist".format(ckpt_path))
                continue
              tf.logging.info("Evaluating {:s}".format(ckpt_path))
              dev_result = estimator.evaluate(
                  input_fn=eval_input_fn,
                  steps=eval_steps,
                  checkpoint_path=ckpt_path,
              )
              tf.logging.info(">> Results:")
              for key in dev_result.keys():
                tf.logging.info("  %s = %s", key, str(dev_result[key]))
                dev_result[key] = dev_result[key].item()
              best_acc = max(best_acc, dev_result["eval_classify_accuracy"])
            tf.logging.info("***** Final evaluation result *****")
            tf.logging.info("Best acc: {:.3f}\n\n".format(best_acc))
        elif FLAGS.do_predict:
            tf.logging.info("***** Running prediction *****")
            print(FLAGS.model_dir)
            checkpoint_state = tf.train.get_checkpoint_state(FLAGS.model_dir)

            best_acc = 0
            for ckpt_path in checkpoint_state.all_model_checkpoint_paths:
                if not tf.gfile.Exists(ckpt_path + ".data-00000-of-00001"):
                    tf.logging.info(
                        "Warning: checkpoint {:s} does not exist".format(ckpt_path))
                    continue
                tf.logging.info("Predicting {:s}".format(ckpt_path))
                result = estimator.predict(
                    input_fn=predict_input_fn,
                    checkpoint_path=ckpt_path,
                )
                tf.logging.info(">> Results:")
                preds = [p for p in result]
                return str(np.argmax(preds, axis=1)[0])

if __name__ == '__main__':
    cls = BERT_UDA_Training(False, False, True, 4, 4, 1, 128, '../../../output/', '../../../output/eval/', '../../../output/predict',
            '../../../uncased_L-12_H-768_A-12/vocab.txt', '../../../uncased_L-12_H-768_A-12/bert_config.json',
            '../../../uncased_L-12_H-768_A-12/bert_model.ckpt', '../../../model/', 2e-05, 'linear_schedule')
    cls.process()
