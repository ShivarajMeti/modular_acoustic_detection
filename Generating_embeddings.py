

#This code is copied from https://github.com/tensorflow/models/blob/master/research/audioset/vggish_inference_demo.py

r"""A simple demonstration of running VGGish in inference mode.
This is intended as a toy example that demonstrates how the various building
blocks (feature extraction, model definition and loading, postprocessing) work
together in an inference context.
A WAV file (assumed to contain signed 16-bit PCM samples) is read in, converted
into log mel spectrogram examples, fed into VGGish, the raw embedding output is
whitened and quantized, and the postprocessed embeddings are optionally written
in a SequenceExample to a TFRecord file (using the same format as the embedding
features released in AudioSet).

Usage:
  # Run a WAV file through the model and print the embeddings. The model
  # checkpoint is loaded from vggish_model.ckpt and the PCA parameters are
  # loaded from vggish_pca_params.npz in the current directory.
  $ python vggish_inference_demo.py --wav_file /path/to/a/wav/file

  # Run a WAV file through the model and also write the embeddings to
  # a TFRecord file. The model checkpoint and PCA parameters are explicitly
  # passed in as well.
  $ python vggish_inference_demo.py --wav_file /path/to/a/wav/file \
                                    --tfrecord_file /path/to/tfrecord/file \
                                    --checkpoint /path/to/model/checkpoint \
                                    --pca_params /path/to/pca/params

  # Run a built-in input (a sine wav) through the model and print the
  # embeddings. Associated model files are read from the current directory.
  $ python vggish_inference_demo.py
"""

from __future__ import print_function

import numpy as np
from scipy.io import wavfile
import six
import tensorflow as tf
import vggish_input
import vggish_params
import vggish_postprocess
import vggish_slim
import pickle
import glob
import os



flags = tf.app.flags

flags.DEFINE_string(
    'wav_file',None,
    'Path to a wav file. Should contain signed 16-bit PCM samples. '
    'If none is provided, a synthetic sound is used.')

flags.DEFINE_string(
    'checkpoint', 'vggish_model.ckpt',
    'Path to the VGGish checkpoint file.')

flags.DEFINE_string(
    'pca_params', 'vggish_pca_params.npz',
    'Path to the VGGish PCA parameters file.')

flags.DEFINE_string(
    'tfrecord_file', None,
    'Path to a TFRecord file where embeddings will be written.')

FLAGS = flags.FLAGS



def main(_):

#Specify the path for the downloaded or recorded audio files and also path for writing the embeddings or pickle files

  wav_files=glob.glob('<path to wave file >*.wav')
  pickle_files=glob.glob('<path to write the embeddings or pickle files >/*.pkl')
  wav_lst=[]
  for pkl in wav_files:
      c_lst.append(pkl.split('/')[-1])


  for i in wav_files:
      pkl=str(i).split('.')[0]+'.pkl'
      indexs= a.index(i)
      print(indexs)

      #No need to generate the embeddings that are already generated.
      if pkl in pickle_files:
          print('done')
          print(pkl)


          # In this simple example, we run the examples from a single audio file through
          # the model. If none is provided, we generate a synthetic input.
      else:
          if FLAGS.wav_file:
            wav_file = i
          else:
            # Write a WAV of a sine wav into an in-memory file object.
            num_secs = 5
            freq = 1000
            sr = 44100
            t = np.linspace(0, num_secs, int(num_secs * sr))
            x = np.sin(2 * np.pi * freq * t)
            # Convert to signed 16-bit samples.
            samples = np.clip(x * 32768, -32768, 32767).astype(np.int16)
            wav_file = six.BytesIO()
            wavfile.write(wav_file, sr, samples)
            wav_file.seek(0)
          examples_batch = vggish_input.wavfile_to_examples(wav_file)
          print(examples_batch)

          # Prepare a postprocessor to munge the model embeddings.
          pproc = vggish_postprocess.Postprocessor(FLAGS.pca_params)

          # If needed, prepare a record writer to store the postprocessed embeddings.
          writer = tf.python_io.TFRecordWriter(
              FLAGS.tfrecord_file) if FLAGS.tfrecord_file else None

          with tf.Graph().as_default(), tf.Session() as sess:
            # Define the model in inference mode, load the checkpoint, and
            # locate input and output tensors.
            vggish_slim.define_vggish_slim(training=False)
            vggish_slim.load_vggish_slim_checkpoint(sess, FLAGS.checkpoint)
            features_tensor = sess.graph.get_tensor_by_name(
                vggish_params.INPUT_TENSOR_NAME)
            embedding_tensor = sess.graph.get_tensor_by_name(
                vggish_params.OUTPUT_TENSOR_NAME)

            # Run inference and postprocessing.
            [embedding_batch] = sess.run([embedding_tensor],
                                         feed_dict={features_tensor: examples_batch})
            print(embedding_batch)
            postprocessed_batch = pproc.postprocess(embedding_batch)
            print(postprocessed_batch)


            #Specify the same path that is mentioned above for writing the embeddings or pickle files
            with open('< path to write the embeddings or pickle files >'+b,'w') as f:
                pickle.dump(postprocessed_batch, f)


if __name__ == '__main__':
  tf.app.run()
