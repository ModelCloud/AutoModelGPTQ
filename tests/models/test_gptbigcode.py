import importlib.util
import os

# TODO: find how ipex registered it jit interpreter
# if intel_extension_for_pytorch was installed, @torch.jit.script in transformers/models/gpt_bigcode/modeling_gpt_bigcode.py will try to use ipex as torchScript interpreter.
# However, in quantization, tensor were on gpu, which will throw RuntimeError: itensor_view_from_dense expects CPU tensor input
if importlib.util.find_spec("intel_extension_for_pytorch"):
    os.environ["PYTORCH_JIT"] = "False"

import torch  # noqa: E402
from model_test import ModelTest  # noqa: E402


class TestGptBigCode(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/gpt_bigcode-santacoder"  # "bigcode/gpt_bigcode-santacoder"
    NATIVE_ARC_CHALLENGE_ACC = 0.1689
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.2056
    TORCH_DTYPE = torch.float16
    TRUST_REMOTE_CODE = True

    def test_gptbigcode(self):
        self.quant_lm_eval()
