import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from model_test import ModelTest


class TestLongLlama(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/long_llama_3b_instruct" # "syzymon/long_llama_3b_instruct"
    NATIVE_ARC_CHALLENGE_ACC = 0.3
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.3
    TRUST_REMOTE_CODE = True
    QUANT_ARC_MAX_NEGATIVE_DELTA = 0.4
    USE_VLLM = False

    def test_longllama(self):
        self.quant_lm_eval()
