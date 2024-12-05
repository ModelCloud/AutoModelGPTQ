from model_test import ModelTest


class TestOpt(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/opt-125m"  # "facebook/opt-125m"
    NATIVE_ARC_CHALLENGE_ACC = 0.1894
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.2278

    KERNEL_QUANT = {"OPTDecoder", "ReLU", "MarlinQuantLinear", "Linear", "OPTAttention", "ModuleList", "OPTForCausalLM", "OPTDecoderLayer", "OPTModel", "OPTLearnedPositionalEmbedding", "Embedding", "OPTGPTQ", "LayerNorm"}
    KERNEL_INFERENCE = {'Embedding', 'LayerNorm', 'Linear', 'MarlinQuantLinear', 'ModuleList', 'OPTAttention', 'OPTDecoder', 'OPTDecoderLayer', 'OPTForCausalLM', 'OPTGPTQ', 'OPTLearnedPositionalEmbedding', 'OPTModel', 'ReLU'}

    def test_opt(self):
        self.quant_lm_eval()
