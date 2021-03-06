/**
 * Copyright 2020 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_NNACL_FP32_BROADCAST_TO_H_
#define MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_NNACL_FP32_BROADCAST_TO_H_

#ifdef ENABLE_NEON
#include <arm_neon.h>
#endif
#include "nnacl/op_base.h"

#define BROADCAST_TO_SHAPE_MAX_SIZE 4

typedef struct BroadcastToParameter {
  OpParameter op_parameter_;
  int shape_[BROADCAST_TO_SHAPE_MAX_SIZE];
  size_t shape_size_;
} BroadcastToParameter;

typedef struct BroadcastShapeInfo {
  int input_shape_[BROADCAST_TO_SHAPE_MAX_SIZE];
  int input_shape_size_;
  int output_shape_[BROADCAST_TO_SHAPE_MAX_SIZE];
  int output_shape_size_;
} BroadcastShapeInfo;

#ifdef __cplusplus
extern "C" {
#endif
int BroadcastTo(const float *input, BroadcastShapeInfo *shape_info, float *output);
#ifdef __cplusplus
}
#endif

#endif  // MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_NNACL_FP32_BROADCAST_TO_H_
