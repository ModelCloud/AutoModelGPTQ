import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from ..model_test import ModelTest  # noqa: E402


class TestGemma(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/gemma-2-9b" # "google/gemma-2-9b"
    NATIVE_ARC_CHALLENGE_ACC = 0.6143
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.6553

    def test_gemma(self):
        self.quant_lm_eval()


