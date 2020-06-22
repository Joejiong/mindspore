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
# ============================================================================

"""MaxPoolGradWithArgmax op"""
from mindspore.ops.op_info_register import op_info_register


@op_info_register("""{
    "op_name": "MaxPoolGradWithArgmax",
    "imply_type": "AutoDiff",
    "fusion_type": "CONVLUTION",
    "attr": [
        {
            "name": "pad_mode",
            "param_type": "optional",
            "type": "str"
         },
        {
            "name": "window",
            "param_type": "optional",
            "type": "int"
        },
        {
            "name": "pad",
            "param_type": "optional",
            "type": "int"
        },
        {
            "name": "stride",
            "param_type": "optional",
            "type": "int"
        }
    ],
    "inputs": [
        {
            "index": 0,
            "dtype": [
                "float16", "float16"
            ],
            "format": [
                "NC1HWC0", "NC1HWC0"
            ],
            "name": "x"
        },
        {
            "index": 1,
            "dtype": [
                "float16", "float32"
            ],
            "format": [
                "DefaultFormat", "DefaultFormat"
            ],
            "name": "argmax"
        },
        {
            "index": 2,
            "dtype": [
                "float16", "float32"
            ],
            "format": [
                "NC1HWC0", "NC1HWC0"
            ],
            "name": "grad"
        }
    ],
    "outputs": [
        {
            "index": 0,
            "dtype": [
                "float16", "float32"
            ],
            "format": [
                "NC1HWC0", "NC1HWC0"
            ],
            "name": "output"
        }
    ]
}""")
def _max_pool_grad_with_argmax_akg():
    """MaxPoolGradWithArgmax AutoDiff register"""
    return