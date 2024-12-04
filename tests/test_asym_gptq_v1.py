# -- do not touch
import os
import tempfile

from gptqmodel import QuantizeConfig, GPTQModel

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# -- end do not touch
from gptqmodel.quantization import FORMAT  # noqa: E402

from models.model_test import ModelTest  # noqa: E402
from parameterized import parameterized  # noqa: E402


class Test(ModelTest):
    NATIVE_MODEL_ID = "/monster/data/model/Llama-3.2-1B-Instruct"  # "meta-llama/Llama-3.2-1B-Instruct"
    QUANT_FORMAT = FORMAT.GPTQ
    NATIVE_ARC_CHALLENGE_ACC = 0.2747
    NATIVE_ARC_CHALLENGE_ACC_NORM = 0.2935

    @classmethod
    def setUpClass(self):
        self.tokenizer = self.load_tokenizer(self.NATIVE_MODEL_ID)
        self.datas = self.load_dataset(self.tokenizer)

    @parameterized.expand([True, False])
    def test(self, sym: bool):
        quantize_config = QuantizeConfig(
            format=self.QUANT_FORMAT,
            desc_act=self.DESC_ACT,
            sym=sym,
        )
        model = GPTQModel.load(
            self.NATIVE_MODEL_ID,
            quantize_config=quantize_config,
            device_map="auto",
        )

        model.quantize(self.datas)

        with (tempfile.TemporaryDirectory()) as tmpdirname:
            model.save(tmpdirname)
            self.tokenizer.save_pretrained(tmpdirname)
            model, tokenizer = self.loadQuantModel(tmpdirname)

            task_results = self.lm_eval(model=model)
            self.check_results(task_results)
