#!/usr/bin/env python
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

#
# Modified by Olivia Guest.
#

"""Simple image classification with Inception.

Run image classification with Inception trained on ImageNet 2012 Challenge data
set.

This program creates a graph from a saved GraphDef protocol buffer,
and runs inference on an input JPEG image. It outputs human readable
strings of the top 5 predictions along with their probabilities.

Change the --image_file argument to any jpg image to compute a
classification of that image.

Please see the tutorial and website for a detailed description of how
to use this script to perform image recognition.

https://tensorflow.org/tutorials/image_recognition/
"""

from __future__ import absolute_import, division, print_function

import os
import os.path
import fnmatch

import numpy as np
import tensorflow as tf
import pandas as pd

from cog_dev_experiment.accuracy import EXP_DIR

from utils.misc import LAYER_NAMES, make_2d
from utils.iv3 import (maybe_download_and_extract,
                       run_inference_on_image,
                       create_graph)


def run_on_images_and_save_as_dfs(images):
    """Create graph from saved GraphDef."""
    create_graph()

    sess = tf.Session()
    labels = [image.split('/')[-1].split('.')[0] for image in images]
    # Get every state (per requested layer, see: layer_names) for every image:
    states = [[] for image in images]
    for i, image in enumerate(images):
        states[i] = run_inference_on_image(image, sess)
    # Take the states and make them 100% flat for each layer for each input:
    layers = len(states[0])
    for l in range(layers):
        layer = np.empty((len(images), states[0][l].flatten().shape[0]))
        # Flatten this layer:
        for i, image in enumerate(images):
            layer[i] = states[i][l].flatten()
        # This code verifies that the first layer is pixel space:
        # if l == 0:
            # print(layer[i], layer[i].shape)
            # image = layer[i].reshape((462,462,3))
            # image = image -255
            # plt.imshow(image)
            # plt.show()

        # Flatten it more:
        layer = make_2d(layer)
        # print(layer.shape)
        rep_dict = {}
        # For all the individual representations in this layer (i.e., one per
        # input image):
        for i, image_rep in enumerate(layer):
            rep_dict[labels[i]] = image_rep
            # print(rep_dict)
        # This dataframe holds all the representations (one per input image) a
        # layer takes on:
        layer_df = pd.DataFrame(rep_dict)
        # print(layer_df.head())
        try:
            os.makedirs(EXP_DIR + 'layer_representations')
        except OSError:
            pass
        layer_df.to_csv(EXP_DIR + 'layer_representations/' +
                        LAYER_NAMES[l].replace("/", "_") + '.csv', index=False)


def main(_):
    """Main function that calls all others."""
    maybe_download_and_extract()

    images = []
    for root, _, filenames in os.walk(EXP_DIR + 'stimuli/'):
        for filename in fnmatch.filter(filenames, '*.jpg'):
            images.append(os.path.join(root, filename))
    if images == []:
        print('You need to download the stimuli!')
        exit()
    run_on_images_and_save_as_dfs(images)


if __name__ == '__main__':
    tf.app.run()
