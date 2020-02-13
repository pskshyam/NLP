from keras.engine import Layer, InputSpec
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Dropout, Embedding, Conv1D, Activation, ZeroPadding1D, Permute, Reshape, Flatten
from keras.layers.normalization import BatchNormalization
from keras.layers.merge import concatenate
import tensorflow as tf
import pickle
import numpy as np
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class KMaxPooling(Layer):
    """ K-max pooling layer that extracts the k-highest activations from a sequence (2nd dimension).
    TensorFlow backend. """

    def __init__(self, k=1, **kwargs):
        super().__init__(**kwargs)
        self.input_spec = InputSpec(ndim=3)
        self.k = k

    def compute_output_shape(self, input_shape):
        return (input_shape[0], (input_shape[1] * self.k))

    def call(self, inputs):
        # swap last two dimensions since top_k will be applied along the last dimension
        # shifted_input = tf.transpose(inputs, [0, 2, 1])
        # extract top_k, returns two tensors [values, indices]
        top_k = tf.nn.top_k(inputs, k=self.k, sorted=True, name=None)[0]
        # return flattened output
        return top_k

class dcnn(object):

    def __init__(self, df_latent, filename):
        self.df_latent = df_latent
        self.name = 'DCNN'
        self.filename = filename

    def two_conv_dynamic_cnn(self, k1=12, k2=8, ksize1=5, ksize2=5):
        max_features = 512
        latent_features_size = self.df_latent.shape[1]
        word_index = 386003
        EMBEDDING_DIM = 128
        inputs = Input(shape=(max_features,))
        inputs_latent = Input(shape=(latent_features_size,))
        embed = Embedding(word_index, 128, input_length=512)(inputs)
        conv_results = []
        # two feature maps using for loop
        for i in range(2):
            padded = ZeroPadding1D(ksize1 - 1)(embed)
            conv1 = Conv1D(EMBEDDING_DIM, ksize1, activation='relu')(padded)
            permuted = Permute((2, 1))(conv1)
            #kmaxpool1 = self.Kmax(k1)(permuted)
            kmaxpool1 = KMaxPooling(k1)(permuted)
            kmaxpool1 = Reshape((k1, -1))(kmaxpool1)
            padded = ZeroPadding1D(ksize2 - 1)(kmaxpool1)
            conv2 = Conv1D(EMBEDDING_DIM, ksize2, activation='relu')(padded)
            permuted = Permute((2, 1))(conv2)
            #kmaxpool2 = self.Kmax(k2)(permuted)
            kmaxpool2 = KMaxPooling(k2)(permuted)
            kmaxpool2 = Reshape((k2, -1))(kmaxpool2)
            flattened = Flatten()(kmaxpool2)
            conv_results.append(flattened)
        x = concatenate(conv_results)
        x = concatenate([x, inputs_latent], axis=1)
        x = BatchNormalization()(x)
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.2)(x)
        outputs = Dense(5, activation='softmax')(x)

        model = Model(inputs=[inputs, inputs_latent], outputs=outputs)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        logger.info('[{}] DCNN model created'.format(self.filename))
        return model

class classifier_model(object):

    def __init__(self,df_latent, text, filename):
        self.df_latent = df_latent
        self.text = text
        self.labels_dict = {0: 'Addendum', 1: 'MSA', 4: 'SOW', 2: 'NDA', 3: 'Others'}
        self.name = 'Prediction'
        self.filename = filename

    def predict(self):
        try:
            countvect_model_pkl = '/services/api/util/models/count_vectorizer.pkl'
            with open(countvect_model_pkl, 'rb') as f:
                countvect_model = pickle.load(f)

            X_text = countvect_model.transform(np.array([self.text]))
            logger.info('[{}] Count vector model loaded'.format(self.filename))

            dcnn_model_ckpt = '/services/api/util/models/dcnn-10epochs-90.0-98.97-99.52.hdf5'
            dcnn_model = dcnn(self.df_latent, self.filename).two_conv_dynamic_cnn()
            dcnn_model.load_weights(dcnn_model_ckpt)
            logger.info('[{}] DCNN model loaded'.format(self.filename))

            probs_test = dcnn_model.predict([X_text, self.df_latent])

            result = list(map(self.labels_dict.get, probs_test.argmax(axis=1)))[0]
            logger.info('[{}] Classification output - {}'.format(self.filename, result))
            return result

        except Exception as ex:
            logger.error('[{}] Exception occurred in Prediction- {}'.format(self.filename, ex))
            return None
