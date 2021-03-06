/**
 * Copyright 2019-2020 Huawei Technologies Co., Ltd
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

#include <vector>
#include <set>
#include <cmath>
#include "ir/dtype/type_id.h"
#include "mindspore/lite/c_ops/primitive_c.h"
#ifdef PRIMITIVE_WRITEABLE
#include "schema/inner/model_generated.h"
#else
#include "schema/model_generated.h"
#endif

#ifndef LITE_MINDSPORE_LITE_C_OPS_POOLING_H_
#define LITE_MINDSPORE_LITE_C_OPS_POOLING_H_

namespace mindspore {
class Pooling : public PrimitiveC {
 public:
#ifdef PRIMITIVE_WRITEABLE
  explicit Pooling(schema::PrimitiveT *primitive) : PrimitiveC(primitive) {}
#else
  explicit Pooling(schema::Primitive *primitive) : PrimitiveC(primitive) {}
#endif
  int InferShape(std::vector<lite::tensor::Tensor *> inputs_, std::vector<lite::tensor::Tensor *> outputs_) override;
  int GetFormat() const;
  int GetPoolingMode() const;
  bool GetGlobal() const;
  int GetWindowW() const;
  int GetWindowH() const;
  int GetStrideW() const;
  int GetStrideH() const;
  int GetPadMode() const;
  int GetPadUp() const;
  int GetPadDown() const;
  int GetPadLeft() const;
  int GetPadRight() const;
  int GetRoundMode() const;
  void SetFormat(int format);
  void SetPoolingMode(int pooling_mode);
  void SetGlobal(bool global);
  void SetWindowW(int window_w);
  void SetWindowH(int window_h);
  void SetStrideW(int stride_w);
  void SetStrideH(int stride_h);
  void SetPadMode(int pad_mode);
  void SetPadUp(int pad_up);
  void SetPadDown(int pad_down);
  void SetPadLeft(int pad_left);
  void SetPadRight(int pad_right);
  void SetRoundMode(int round_mode);

  int PadUp() const { return this->pad_u_; }
  int PadDown() const { return this->pad_d_; }
  int PadLeft() const { return this->pad_l_; }
  int PadRight() const { return this->pad_r_; }

 protected:
  int pad_u_ = 0;
  int pad_d_ = 0;
  int pad_l_ = 0;
  int pad_r_ = 0;
};
}  // namespace mindspore

#endif  // LITE_MINDSPORE_LITE_C_OPS_POOLING_H_
