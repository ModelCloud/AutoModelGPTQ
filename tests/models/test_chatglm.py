from model_test import ModelTest  # noqa: E402


class TestChatGlm(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/chatglm3-6b" # "THUDM/chatglm3-6b"
    NATIVE_ARC_CHALLENGE_ACC = 0.3319
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.3729
    TRUST_REMOTE_CODE = True

    def test_chatglm(self):
        self.quant_lm_eval()
