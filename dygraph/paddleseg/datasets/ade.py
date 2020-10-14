# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
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

import os

import numpy as np
from PIL import Image

from paddleseg.datasets import Dataset
from paddleseg.utils.download import download_file_and_uncompress
from paddleseg.utils import seg_env
from paddleseg.cvlibs import manager
from paddleseg.transforms import Compose

URL = "http://data.csail.mit.edu/places/ADEchallenge/ADEChallengeData2016.zip"


@manager.DATASETS.add_component
class ADE20K(Dataset):
    """
    ADE20K dataset `http://sceneparsing.csail.mit.edu/`.

    Args:
        transforms (list): Transforms for image.
        dataset_root (str): The dataset directory.
        mode (str): Which part of dataset to use.. it is one of ('train', 'val'). Default: 'train'.
        download (bool): Whether to download dataset if `dataset_root` is None.
    """

    def __init__(self,
                 transforms,
                 dataset_root=None,
                 mode='train',
                 download=True):
        self.dataset_root = dataset_root
        self.transforms = Compose(transforms)
        mode = mode.lower()
        self.mode = mode
        self.file_list = list()
        self.num_classes = 150
        self.ignore_index = 255

        if mode not in ['train', 'val']:
            raise ValueError(
                "`mode` should be one of ('train', 'val') in ADE20K dataset, but got {}."
                .format(mode))

        if self.transforms is None:
            raise ValueError("`transforms` is necessary, but it is None.")

        if self.dataset_root is None:
            if not download:
                raise ValueError(
                    "`dataset_root` not set and auto download disabled.")
            self.dataset_root = download_file_and_uncompress(
                url=URL,
                savepath=seg_env.DATA_HOME,
                extrapath=seg_env.DATA_HOME,
                extraname='ADEChallengeData2016')
        elif not os.path.exists(self.dataset_root):
            raise FileNotFoundError('there is not `dataset_root`: {}.'.format(
                self.dataset_root))

        if mode == 'train':
            img_dir = os.path.join(self.dataset_root, 'images/training')
            label_dir = os.path.join(self.dataset_root, 'annotations/training')
        elif mode == 'val':
            img_dir = os.path.join(self.dataset_root, 'images/validation')
            label_dir = os.path.join(self.dataset_root,
                                     'annotations/validation')
        img_files = os.listdir(img_dir)
        label_files = [i.replace('.jpg', '.png') for i in img_files]
        for i in range(len(img_files)):
            img_path = os.path.join(img_dir, img_files[i])
            label_path = os.path.join(label_dir, label_files[i])
            self.file_list.append([img_path, label_path])

    def __getitem__(self, idx):
        image_path, label_path = self.file_list[idx]
        if self.mode == 'val':
            im, im_info, _ = self.transforms(im=image_path)
            im = im[np.newaxis, ...]
            label = np.asarray(Image.open(label_path))
            # The class 0 is ignored. And it will equal to 255 after
            # subtracted 1, because the dtype of label is uint8.
            label = label - 1
            label = label[np.newaxis, np.newaxis, :, :]
            return im, im_info, label
        else:
            im, im_info, label = self.transforms(
                im=image_path, label=label_path)
            label = label - 1
            return im, label