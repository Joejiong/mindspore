# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
Testing the CutMixBatch op in DE
"""
import numpy as np
import pytest
import mindspore.dataset as ds
import mindspore.dataset.transforms.vision.c_transforms as vision
import mindspore.dataset.transforms.c_transforms as data_trans
import mindspore.dataset.transforms.vision.utils as mode
from mindspore import log as logger
from util import save_and_check_md5, diff_mse, visualize_list, config_get_set_seed, \
    config_get_set_num_parallel_workers

DATA_DIR = "../data/dataset/testCifar10Data"

GENERATE_GOLDEN = False


def test_cutmix_batch_success1(plot=False):
    """
    Test CutMixBatch op with specified alpha and prob parameters on a batch of CHW images
    """
    logger.info("test_cutmix_batch_success1")

    # Original Images
    ds_original = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)
    ds_original = ds_original.batch(5, drop_remainder=True)

    images_original = None
    for idx, (image, _) in enumerate(ds_original):
        if idx == 0:
            images_original = image
        else:
            images_original = np.append(images_original, image, axis=0)

    # CutMix Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)
    hwc2chw_op = vision.HWC2CHW()
    data1 = data1.map(input_columns=["image"], operations=hwc2chw_op)
    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NCHW, 2.0, 0.5)
    data1 = data1.batch(5, drop_remainder=True)
    data1 = data1.map(input_columns=["image", "label"], operations=cutmix_batch_op)

    images_cutmix = None
    for idx, (image, _) in enumerate(data1):
        if idx == 0:
            images_cutmix = image.transpose(0, 2, 3, 1)
        else:
            images_cutmix = np.append(images_cutmix, image.transpose(0, 2, 3, 1), axis=0)
    if plot:
        visualize_list(images_original, images_cutmix)

    num_samples = images_original.shape[0]
    mse = np.zeros(num_samples)
    for i in range(num_samples):
        mse[i] = diff_mse(images_cutmix[i], images_original[i])
    logger.info("MSE= {}".format(str(np.mean(mse))))


def test_cutmix_batch_success2(plot=False):
    """
    Test CutMixBatch op with default values for alpha and prob on a batch of HWC images
    """
    logger.info("test_cutmix_batch_success2")

    # Original Images
    ds_original = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)
    ds_original = ds_original.batch(5, drop_remainder=True)

    images_original = None
    for idx, (image, _) in enumerate(ds_original):
        if idx == 0:
            images_original = image
        else:
            images_original = np.append(images_original, image, axis=0)

    # CutMix Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)
    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NHWC)
    data1 = data1.batch(5, drop_remainder=True)
    data1 = data1.map(input_columns=["image", "label"], operations=cutmix_batch_op)

    images_cutmix = None
    for idx, (image, _) in enumerate(data1):
        if idx == 0:
            images_cutmix = image
        else:
            images_cutmix = np.append(images_cutmix, image, axis=0)
    if plot:
        visualize_list(images_original, images_cutmix)

    num_samples = images_original.shape[0]
    mse = np.zeros(num_samples)
    for i in range(num_samples):
        mse[i] = diff_mse(images_cutmix[i], images_original[i])
    logger.info("MSE= {}".format(str(np.mean(mse))))


def test_cutmix_batch_nhwc_md5():
    """
    Test CutMixBatch on a batch of HWC images with MD5:
    """
    logger.info("test_cutmix_batch_nhwc_md5")
    original_seed = config_get_set_seed(0)
    original_num_parallel_workers = config_get_set_num_parallel_workers(1)

    # CutMixBatch Images
    data = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    one_hot_op = data_trans.OneHot(num_classes=10)
    data = data.map(input_columns=["label"], operations=one_hot_op)
    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NHWC)
    data = data.batch(5, drop_remainder=True)
    data = data.map(input_columns=["image", "label"], operations=cutmix_batch_op)

    filename = "cutmix_batch_c_nhwc_result.npz"
    save_and_check_md5(data, filename, generate_golden=GENERATE_GOLDEN)

    # Restore config setting
    ds.config.set_seed(original_seed)
    ds.config.set_num_parallel_workers(original_num_parallel_workers)


def test_cutmix_batch_nchw_md5():
    """
    Test CutMixBatch on a batch of CHW images with MD5:
    """
    logger.info("test_cutmix_batch_nchw_md5")
    original_seed = config_get_set_seed(0)
    original_num_parallel_workers = config_get_set_num_parallel_workers(1)

    # CutMixBatch Images
    data = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)
    hwc2chw_op = vision.HWC2CHW()
    data = data.map(input_columns=["image"], operations=hwc2chw_op)
    one_hot_op = data_trans.OneHot(num_classes=10)
    data = data.map(input_columns=["label"], operations=one_hot_op)
    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NCHW)
    data = data.batch(5, drop_remainder=True)
    data = data.map(input_columns=["image", "label"], operations=cutmix_batch_op)

    filename = "cutmix_batch_c_nchw_result.npz"
    save_and_check_md5(data, filename, generate_golden=GENERATE_GOLDEN)

    # Restore config setting
    ds.config.set_seed(original_seed)
    ds.config.set_num_parallel_workers(original_num_parallel_workers)


def test_cutmix_batch_fail1():
    """
    Test CutMixBatch Fail 1
    We expect this to fail because the images and labels are not batched
    """
    logger.info("test_cutmix_batch_fail1")

    # CutMixBatch Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NHWC)
    with pytest.raises(RuntimeError) as error:
        data1 = data1.map(input_columns=["image", "label"], operations=cutmix_batch_op)
        for idx, (image, _) in enumerate(data1):
            if idx == 0:
                images_cutmix = image
            else:
                images_cutmix = np.append(images_cutmix, image, axis=0)
        error_message = "You must batch before calling CutMixBatch"
        assert error_message in str(error.value)


def test_cutmix_batch_fail2():
    """
    Test CutMixBatch Fail 2
    We expect this to fail because alpha is negative
    """
    logger.info("test_cutmix_batch_fail2")

    # CutMixBatch Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    with pytest.raises(ValueError) as error:
        vision.CutMixBatch(mode.ImageBatchFormat.NHWC, -1)
        error_message = "Input is not within the required interval"
        assert error_message in str(error.value)


def test_cutmix_batch_fail3():
    """
    Test CutMixBatch Fail 2
    We expect this to fail because prob is larger than 1
    """
    logger.info("test_cutmix_batch_fail3")

    # CutMixBatch Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    with pytest.raises(ValueError) as error:
        vision.CutMixBatch(mode.ImageBatchFormat.NHWC, 1, 2)
        error_message = "Input is not within the required interval"
        assert error_message in str(error.value)


def test_cutmix_batch_fail4():
    """
    Test CutMixBatch Fail 2
    We expect this to fail because prob is negative
    """
    logger.info("test_cutmix_batch_fail4")

    # CutMixBatch Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    with pytest.raises(ValueError) as error:
        vision.CutMixBatch(mode.ImageBatchFormat.NHWC, 1, -1)
        error_message = "Input is not within the required interval"
        assert error_message in str(error.value)


def test_cutmix_batch_fail5():
    """
    Test CutMixBatch op
    We expect this to fail because label column is not passed to cutmix_batch
    """
    logger.info("test_cutmix_batch_fail5")

    # CutMixBatch Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NHWC)
    data1 = data1.batch(5, drop_remainder=True)
    data1 = data1.map(input_columns=["image"], operations=cutmix_batch_op)

    with pytest.raises(RuntimeError) as error:
        images_cutmix = np.array([])
        for idx, (image, _) in enumerate(data1):
            if idx == 0:
                images_cutmix = image
            else:
                images_cutmix = np.append(images_cutmix, image, axis=0)
    error_message = "Both images and labels columns are required"
    assert error_message in str(error.value)


def test_cutmix_batch_fail6():
    """
    Test CutMixBatch op
    We expect this to fail because image_batch_format passed to CutMixBatch doesn't match the format of the images
    """
    logger.info("test_cutmix_batch_fail6")

    # CutMixBatch Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    one_hot_op = data_trans.OneHot(num_classes=10)
    data1 = data1.map(input_columns=["label"], operations=one_hot_op)
    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NCHW)
    data1 = data1.batch(5, drop_remainder=True)
    data1 = data1.map(input_columns=["image", "label"], operations=cutmix_batch_op)

    with pytest.raises(RuntimeError) as error:
        images_cutmix = np.array([])
        for idx, (image, _) in enumerate(data1):
            if idx == 0:
                images_cutmix = image
            else:
                images_cutmix = np.append(images_cutmix, image, axis=0)
    error_message = "CutMixBatch: Image doesn't match the given image format."
    assert error_message in str(error.value)


def test_cutmix_batch_fail7():
    """
    Test CutMixBatch op
    We expect this to fail because labels are not in one-hot format
    """
    logger.info("test_cutmix_batch_fail7")

    # CutMixBatch Images
    data1 = ds.Cifar10Dataset(DATA_DIR, num_samples=10, shuffle=False)

    cutmix_batch_op = vision.CutMixBatch(mode.ImageBatchFormat.NHWC)
    data1 = data1.batch(5, drop_remainder=True)
    data1 = data1.map(input_columns=["image", "label"], operations=cutmix_batch_op)

    with pytest.raises(RuntimeError) as error:
        images_cutmix = np.array([])
        for idx, (image, _) in enumerate(data1):
            if idx == 0:
                images_cutmix = image
            else:
                images_cutmix = np.append(images_cutmix, image, axis=0)
    error_message = "CutMixBatch: Label's must be in one-hot format and in a batch"
    assert error_message in str(error.value)


if __name__ == "__main__":
    test_cutmix_batch_success1(plot=True)
    test_cutmix_batch_success2(plot=True)
    test_cutmix_batch_nchw_md5()
    test_cutmix_batch_nhwc_md5()
    test_cutmix_batch_fail1()
    test_cutmix_batch_fail2()
    test_cutmix_batch_fail3()
    test_cutmix_batch_fail4()
    test_cutmix_batch_fail5()
    test_cutmix_batch_fail6()
    test_cutmix_batch_fail7()
