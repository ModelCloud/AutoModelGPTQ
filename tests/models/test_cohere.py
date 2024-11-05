from model_test import ModelTest

class TestCohere(ModelTest):
    NATIVE_MODEL_ID = "CohereForAI/aya-expanse-8b"
    NATIVE_ARC_CHALLENGE_ACC = 0.5401
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.5640
    QUANT_ARC_MAX_NEGATIVE_DELTA = 0.12

    def test_cohere(self):
        model, tokenizer = self.quantModel(self.NATIVE_MODEL_ID)
        task_results = self.lm_eval(model)
        for filter, value in task_results.items():
            per = self.calculatorPer(filter=filter, value=value)
            self.assertTrue(90 <= per <= 110,
                            f"{filter}: {value} diff {per:.2f}% is out of the expected range (90%-110%)")