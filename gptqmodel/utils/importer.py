from collections import OrderedDict
from logging import getLogger

from ..nn_modules.qlinear.qlinear_bitblas import BitBLASQuantLinear
from ..nn_modules.qlinear.qlinear_cuda import CudaQuantLinear
from ..nn_modules.qlinear.qlinear_cuda_old import CudaOldQuantLinear
from ..nn_modules.qlinear.qlinear_exllama import ExllamaQuantLinear
from ..nn_modules.qlinear.qlinear_exllamav2 import ExllamaV2QuantLinear
from ..nn_modules.qlinear.qlinear_marlin import MarlinQuantLinear
from ..nn_modules.qlinear.qlinear_tritonv2 import TritonV2QuantLinear
from ..quantization import FORMAT
from .backend import Backend

backend_dict = OrderedDict({
    Backend.MARLIN: MarlinQuantLinear,
    Backend.EXLLAMA_V2: ExllamaV2QuantLinear,
    Backend.EXLLAMA: ExllamaQuantLinear,
    Backend.TRITON: TritonV2QuantLinear,
    Backend.CUDA_OLD: CudaOldQuantLinear,
    Backend.CUDA: CudaQuantLinear,
    Backend.BITBLAS: BitBLASQuantLinear,
})

format_dict = {
    FORMAT.GPTQ: [Backend.EXLLAMA_V2, Backend.EXLLAMA, Backend.CUDA_OLD, Backend.CUDA],
    FORMAT.GPTQ_V2: [Backend.EXLLAMA_V2, Backend.EXLLAMA, Backend.CUDA_OLD, Backend.CUDA],
    FORMAT.MARLIN: [Backend.MARLIN],
    FORMAT.BITBLAS: [Backend.BITBLAS],
}

logger = getLogger(__name__)


# auto select the correct/optimal QuantLinear class
def select_quant_linear(
        bits: int,
        group_size: int,
        desc_act: bool,
        sym: bool,
        backend: Backend,
        format: FORMAT,
        pack: bool = False,
        disable_exllama: bool = False,
):
    # Handle the case where backend is AUTO.
    if backend == Backend.AUTO:
        allow_backends = format_dict[format]
        for k, v in backend_dict.items():
            in_allow_backends = k in allow_backends
            validate = v.validate(bits, group_size, desc_act, sym, raise_error=False)
            check_pack_func = hasattr(v, "pack") if pack else True
            check_exllama = v != ExllamaQuantLinear and v != ExllamaV2QuantLinear if disable_exllama else True
            if in_allow_backends and validate and check_pack_func and check_exllama:
                logger.info(f"Auto choose the fastest one based on quant model compatibility: {v}")
                return v

    # Handle the case where backend is not AUTO.
    if backend == Backend.TRITON:
        return TritonV2QuantLinear
    elif backend == Backend.BITBLAS:
        return BitBLASQuantLinear
    elif bits == 4 and sym and not desc_act and backend == Backend.MARLIN:
        return MarlinQuantLinear
    elif bits == 4 and backend == Backend.EXLLAMA_V2:
        return ExllamaV2QuantLinear
    elif bits == 4 and backend == Backend.EXLLAMA:
        return ExllamaQuantLinear
    elif not desc_act or group_size == -1:
        return CudaOldQuantLinear
    else:
        return CudaQuantLinear
