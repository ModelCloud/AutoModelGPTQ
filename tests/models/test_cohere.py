import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from ..model_test import ModelTest  # noqa: E402


class TestCohere(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/aya-expanse-8b" # "CohereForAI/aya-expanse-8b"
    NATIVE_ARC_CHALLENGE_ACC = 0.46
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.46
    QUANT_ARC_MAX_NEGATIVE_DELTA = 0.12
    BATCH_SIZE = 4

    def test_cohere(self):
        self.quant_lm_eval()
