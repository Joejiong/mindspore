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

#include "tools/anf_importer/anf_populater/anf_depthwiseconv2d_populater.h"
#include <vector>
#include <string>
#include <memory>
#include "tools/anf_importer/anf_populater/anf_node_populater_registry.h"
#include "ir/func_graph.h"
#include "src/ir/tensor.h"
#include "tools/converter/quantizer/quantize_util.h"

namespace mindspore::lite {
void AnfDepwiseconv2DPopulater::CalQuantParam(const double &mean, const double &stdDev, float *mMin, float *mMax) {
  constexpr float qmin = 0;
  constexpr float qmax = 255;
  *mMin = static_cast<float>((qmin - mean) / stdDev);
  *mMax = static_cast<float>((qmax - mean) / stdDev);
}

void AnfDepwiseconv2DPopulater::PopulaterQuantParam(
        const PrimitivePtr &prim,
        std::vector<std::vector<schema::QuantParamT>> *vecInputQuantParam,
        std::vector<std::vector<schema::QuantParamT>> *vecOutputQuantParam) {
  auto narrow_range = prim->GetAttr("narrow_range");
  bool narrowRangeQuantParam = GetValue<bool>(narrow_range);
  auto num_bits = prim->GetAttr("num_bits");
  int32_t numbitsRangeQuantParam = GetValue<int32_t>(num_bits);

  std::vector<schema::QuantParamT> quants;
  schema::QuantParamT quantParam;
  auto mean = prim->GetAttr("mean");
  auto std_dev = prim->GetAttr("std_dev");
  if (mean != nullptr && std_dev != nullptr) {
    auto meanQuantOaram = GetValue<double>(mean);
    double stddevQuantOaram = GetValue<double>(std_dev);
    float mMin = 0.0;
    float mMax = 0.0;
    CalQuantParam(meanQuantOaram, stddevQuantOaram, &mMin, &mMax);
    quantParam.min = mMin;
    quantParam.max = mMax;
  } else {
    auto inputMin = prim->GetAttr("input_minq");
    auto inputMax = prim->GetAttr("input_maxq");
    auto inputMinPtr = inputMin->cast<lite::tensor::TensorPtr>();
    auto inputMaxPtr = inputMax->cast<lite::tensor::TensorPtr>();
    float *minBuf = static_cast<float *>(inputMinPtr->Data());
    float *maxBuf = static_cast<float *>(inputMaxPtr->Data());
    quantParam.min = *minBuf;
    quantParam.max = *maxBuf;
  }
  quant::CalQuantizationParams(&quantParam, quantParam.min, quantParam.max, narrowRangeQuantParam,
                               numbitsRangeQuantParam);
  quants.emplace_back(quantParam);
  vecInputQuantParam->emplace_back(quants);

  quants.clear();
  int biasQuantSize = 0;
  auto filterMin = prim->GetAttr("filter_minq");
  auto filterMax = prim->GetAttr("filter_maxq");
  if (filterMin != nullptr && filterMax != nullptr) {
    auto filterMinPtr = filterMin->cast<lite::tensor::TensorPtr>();
    auto filterMaxPtr = filterMax->cast<lite::tensor::TensorPtr>();
    float *minBuf = static_cast<float *>(filterMinPtr->Data());
    float *maxBuf = static_cast<float *>(filterMaxPtr->Data());
    biasQuantSize = filterMinPtr->DataSize();
    for (int i = 0; i < biasQuantSize; ++i) {
      quantParam.min = *(minBuf++);
      quantParam.max = *(maxBuf++);
      quant::CalQuantizationParams(&quantParam, quantParam.min, quantParam.max, narrowRangeQuantParam,
                                   numbitsRangeQuantParam);
      quants.emplace_back(quantParam);
    }
    vecInputQuantParam->emplace_back(quants);
  }

  quants.clear();
  for (int i = 0; i < biasQuantSize; ++i) {
    quantParam.min = 0.0;
    quantParam.max = 0.0;
    quantParam.zeroPoint = 0;

    quantParam.scale =
            vecInputQuantParam->at(0).at(0).scale * vecInputQuantParam->at(1).at(i).scale;
    quants.emplace_back(quantParam);
  }
  vecInputQuantParam->emplace_back(quants);

  quants.clear();
  auto outputMin = prim->GetAttr("output_minq");
  auto outputMax = prim->GetAttr("output_maxq");
  if (outputMin != nullptr && outputMax != nullptr) {
    auto outputMinPtr = outputMin->cast<lite::tensor::TensorPtr>();
    auto outputMaxPtr = outputMax->cast<lite::tensor::TensorPtr>();
    float *minBuf = static_cast<float *>(outputMinPtr->Data());
    float *maxBuf = static_cast<float *>(outputMaxPtr->Data());
    quantParam.min = *minBuf;
    quantParam.max = *maxBuf;
    quant::CalQuantizationParams(&quantParam, quantParam.min, quantParam.max, narrowRangeQuantParam,
                                 numbitsRangeQuantParam);
    quants.emplace_back(quantParam);
    vecOutputQuantParam->emplace_back(quants);
  }
}

int AnfDepwiseconv2DPopulater::Populate(const PrimitivePtr &prim, PrimitiveTValue *primitiveTValuePtr,
                                        const std::vector<AnfNodePtr> &inputs) {
  auto primitive = std::make_unique<schema::PrimitiveT>();
  auto attr = std::make_unique<schema::DepthwiseConv2DT>();

  auto format = GetValue<std::string>(prim->GetAttr("data_format"));
  if (format == "NCHW") {
    attr->format = schema::Format_NCHW;
  } else if (format == "NHWC") {
    attr->format = schema::Format_NHWC;
  } else {
    attr->format = schema::Format_NUM_OF_FORMAT;
  }
  auto pad_list = GetValue<std::vector<int>>(prim->GetAttr("pads"));
  attr->padUp = pad_list[0];
  attr->padDown = pad_list[1];
  attr->padLeft = pad_list[2];
  attr->padRight = pad_list[3];

  auto dilation = GetValue<std::vector<int>>(prim->GetAttr("dilation"));
  attr->dilateH = dilation[0];
  attr->dilateW = dilation[1];

  auto kernel_size = GetValue<std::vector<int>>(prim->GetAttr("kernel_size"));
  attr->kernelH = kernel_size[0];
  attr->kernelW = kernel_size[1];

  auto stride = GetValue<std::vector<int>>(prim->GetAttr("stride"));
  attr->strideH = stride[2];
  attr->strideW = stride[3];

  auto pad_mode = GetValue<std::string>(prim->GetAttr("pad_mode"));
  if (pad_mode == "valid") {
    attr->padMode = schema::PadMode_VALID;
  } else if (pad_mode == "same") {
    attr->padMode = schema::PadMode_SAME;
  } else {
    attr->padMode = schema::PadMode_NOTSET;
  }

  auto channel_multiplier = GetValue<int>(prim->GetAttr("channel_multiplier"));
  attr->channelMultiplier = channel_multiplier;

  MS_ASSERT(inputs.size() == kAnfPopulaterTwo);
  auto inputNode = inputs[kAnfPopulaterOne];
  MS_ASSERT(inputNode != nullptr);
  if (inputNode->isa<Parameter>()) {
    auto paramNode = inputNode->cast<ParameterPtr>();
    auto abstractBase = paramNode->abstract();
    MS_ASSERT(abstractBase != nullptr);
    if (utils::isa<abstract::AbstractTensorPtr>(abstractBase)) {
      auto abstractTensor = utils::cast<abstract::AbstractTensorPtr>(abstractBase);
      MS_ASSERT(abstractTensor != nullptr);
      if (utils::isa<abstract::ShapePtr>(abstractTensor->BuildShape())) {
        auto dims = utils::cast<abstract::ShapePtr>(abstractTensor->BuildShape())->shape();
        attr->channelIn = dims[kAnfPopulaterOne];
      }
    }
  }

  primitive->value.type = schema::PrimitiveType_DepthwiseConv2D;
  primitive->value.value = attr.release();
  MS_ASSERT(primitiveTValuePtr != nullptr);
  primitiveTValuePtr->SetPrimitiveT(primitive.release());

  if (primitiveTValuePtr->GetQuantType() == schema::QuantType_AwareTraining) {
    std::vector<std::vector<schema::QuantParamT>> vecInputQuantParam;
    std::vector<std::vector<schema::QuantParamT>> vecOutputQuantParam;
    PopulaterQuantParam(prim, &vecInputQuantParam, &vecOutputQuantParam);
    primitiveTValuePtr->SetInputQuantParam(vecInputQuantParam);
    primitiveTValuePtr->SetOutputQuantParam(vecOutputQuantParam);
  }
  return 0;
}
AnfNodePopulaterRegistrar anfdepthwise2dPopulater("DepthwiseConv2D", new AnfDepwiseconv2DPopulater());
AnfNodePopulaterRegistrar anfdepthwise2dnativePopulater("DepthwiseConv2dNative", new AnfDepwiseconv2DPopulater());
}  // namespace mindspore::lite
