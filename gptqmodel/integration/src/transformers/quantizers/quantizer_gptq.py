# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
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
import importlib
from typing import TYPE_CHECKING, Optional

from gptqmodel.integration.src.transformers.utils.import_utils import is_gptqmodel_available
from packaging import version
from transformers.quantizers.base import HfQuantizer

if TYPE_CHECKING:
    from transformers.modeling_utils import PreTrainedModel

from transformers.utils import is_auto_gptq_available, is_optimum_available, is_torch_available, logging
from transformers.utils.quantization_config import GPTQConfig, QuantizationConfigMixin

if is_torch_available():
    import torch

logger = logging.get_logger(__name__)


class GptqHfQuantizer(HfQuantizer):
    """
    Quantizer of the GPTQ method - for GPTQ the quantizer support calibration of the model through
    `auto_gptq` or `gptqmodel` package. Quantization is done under the hood for users if they load a non-prequantized model.
    """

    requires_calibration = False
    required_packages = ["optimum", "auto_gptq", "gptqmodel"]
    optimum_quantizer = None

    def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs):
        super().__init__(quantization_config, **kwargs)
        from optimum.gptq import GPTQQuantizer

        self.optimum_quantizer = GPTQQuantizer.from_dict(self.quantization_config.to_dict_optimum())

    def validate_environment(self, *args, **kwargs):
        if not is_optimum_available():
            raise ImportError("Loading a GPTQ quantized model requires optimum (`pip install optimum`)")
        if is_auto_gptq_available() and is_gptqmodel_available():
            logger.warning(
                "Detected gptqmodel and auto-gptq, will use gptqmodel, auto-gptq will be deprecated in the future."
            )

        gptq_supports_cpu = (
                                    is_auto_gptq_available()
                                    and version.parse(importlib.metadata.version("auto-gptq")) > version.parse("0.4.2")
                            ) or is_gptqmodel_available()
        if not gptq_supports_cpu and not torch.cuda.is_available():
            raise RuntimeError("GPU is required to quantize or run quantize model.")
        elif not (is_auto_gptq_available() or is_gptqmodel_available()):
            raise ImportError(
                "Loading a GPTQ quantized model requires gptqmodel (`pip install gptqmodel`) or auto-gptq (`pip install auto-gptq`) library. Please notice that auto-gptq will be deprecated in the future."
            )
        elif is_auto_gptq_available() and version.parse(importlib.metadata.version("auto_gptq")) < version.parse(
                "0.4.2"
        ):
            raise ImportError(
                "You need a version of auto_gptq >= 0.4.2 to use GPTQ: `pip install --upgrade auto-gptq` or use gptqmodel by `pip install gptqmodel`. Please notice that auto-gptq will be deprecated in the future."
            )
        elif is_gptqmodel_available() and (
                version.parse(importlib.metadata.version("gptqmodel")) <= version.parse("1.3.1")
                or version.parse(importlib.metadata.version("optimum")) < version.parse("1.23.3")
        ):
            raise ImportError("The gptqmodel version should be >= 1.3.2, optimum version should >= 1.24.0")

    def update_torch_dtype(self, torch_dtype: "torch.dtype") -> "torch.dtype":
        if torch_dtype is None:
            torch_dtype = torch.float16
        elif torch_dtype != torch.float16:
            logger.info("We suggest you to set `torch_dtype=torch.float16` for better efficiency with GPTQ.")
        return torch_dtype

    def _process_model_before_weight_loading(self, model: "PreTrainedModel", **kwargs):
        if model.__class__.main_input_name != "input_ids":
            raise RuntimeError("We can only quantize pure text model.")

        if self.pre_quantized:
            model = self.optimum_quantizer.convert_model(model, **kwargs)

    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        if self.pre_quantized:
            model = self.optimum_quantizer.post_init_model(model)
        else:
            if self.quantization_config.tokenizer is None:
                self.quantization_config.tokenizer = model.name_or_path

            self.optimum_quantizer.quantize_model(model, self.quantization_config.tokenizer)
            model.config.quantization_config = GPTQConfig.from_dict(self.optimum_quantizer.to_dict())

    @property
    def is_trainable(self, model: Optional["PreTrainedModel"] = None):
        return True

    def is_serializable(self, safe_serialization=None):
        return True