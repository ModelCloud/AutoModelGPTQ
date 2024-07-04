# -- do not touch
import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# -- end do not touch

import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402

import torch.cuda  # noqa: E402
from datasets import load_dataset  # noqa: E402
from parameterized import parameterized  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

from gptqmodel import Backend, GPTQModel, __version__  # noqa: E402
from gptqmodel.quantization import FORMAT, QUANT_CONFIG_FILENAME, QuantizeConfig  # noqa: E402
from gptqmodel.quantization.config import META_FIELD_QUANTIZER, META_QUANTIZER_GPTQMODEL  # noqa: E402


class TestQuantization(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.pretrained_model_dir = "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T"

        self.tokenizer = AutoTokenizer.from_pretrained(self.pretrained_model_dir, use_fast=True)
        traindata = load_dataset("wikitext", "wikitext-2-raw-v1", split="train").filter(lambda x: len(x['text']) >= 512)
        self.calibration_dataset = [self.tokenizer(example["text"]) for example in traindata.select(range(1024))]

    @parameterized.expand(
        [
            (Backend.EXLLAMA_V2, True, FORMAT.GPTQ_V2),
            (Backend.EXLLAMA_V2, False, FORMAT.GPTQ),
            (Backend.MARLIN, True, FORMAT.MARLIN),
        ]
    )
    def test_quantize(self, backend: Backend, sym: bool, format: FORMAT):
        quantize_config = QuantizeConfig(
            bits=4,
            group_size=128,
            desc_act=False if format == FORMAT.MARLIN else True,
            sym=sym,
            format=format,
        )

        model = GPTQModel.from_pretrained(
            self.pretrained_model_dir,
            quantize_config=quantize_config,
        )

        model.quantize(self.calibration_dataset, batch_size=128)

        with tempfile.TemporaryDirectory() as tmpdirname:
            model.save_quantized(tmpdirname)

            logging.info(f"Saved config mem: {model.quantize_config}")

            with open(tmpdirname + "/" + QUANT_CONFIG_FILENAME, "r") as f:
                file_dict = json.loads(f.read())
                # skip comparison of these two model path specific fields that do not exist in memory
                file_dict["model_name_or_path"] = None
                file_dict["model_file_base_name"] = None

                # make sure the json dict saved to file matches config in memory
                assert model.quantize_config.to_dict() == file_dict
                logging.info(f"Saved config file: {file_dict}")

            model = GPTQModel.from_quantized(
                tmpdirname,
                device="cuda:0",
                backend=backend,
            )

            logging.info(f"Loaded config: {model.quantize_config}")
            assert model.quantize_config.meta_get_versionable(META_FIELD_QUANTIZER) == (
                META_QUANTIZER_GPTQMODEL,
                __version__,
            )
            del model
            torch.cuda.empty_cache()

            # skip compat test with sym=False and v1 since we do meta version safety check
            if not sym and format == FORMAT.GPTQ:
                return

            # test compat: 1) with simple dict type 2) is_marlin_format
            compat_quantize_config = {
                "bits": 4,
                "group_size": 128,
                "sym": sym,
                "desc_act": False if format == FORMAT.MARLIN else True,
                "is_marlin_format": backend == Backend.MARLIN,
            }

            model = GPTQModel.from_quantized(
                tmpdirname,
                device="cuda:0",
                quantize_config=compat_quantize_config,
            )
            assert isinstance(model.quantize_config, QuantizeConfig)

            del model
            torch.cuda.empty_cache()

            # test checkpoint_format hint to from_quantized()
            os.remove(f"{tmpdirname}/{QUANT_CONFIG_FILENAME}")

            compat_quantize_config = {
                "bits": 4,
                "group_size": 128,
                "sym": sym,
                "desc_act": False if format == FORMAT.MARLIN else True,
            }
            model = GPTQModel.from_quantized(
                tmpdirname,
                device="cuda:0",
                quantize_config=compat_quantize_config,
                format=format,
            )
            assert isinstance(model.quantize_config, QuantizeConfig)

    def test_gptq_8bit(self):
        quantize_config = QuantizeConfig(
            bits=8,
            group_size=128,
            format=FORMAT.GPTQ,
            desc_act=True
        )

        model = GPTQModel.from_pretrained(
            self.pretrained_model_dir,
            quantize_config=quantize_config,
        )

        model.quantize(self.calibration_dataset, batch_size=128)

        with tempfile.TemporaryDirectory() as tmpdirname:
            err = None
            try:
                model.save_quantized(tmpdirname)
            except Exception as e:
                print(e)
                err = e
            self.assertTrue(err is None)
