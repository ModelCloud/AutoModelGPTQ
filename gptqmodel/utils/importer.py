from logging import getLogger

try:
    import bitblas  # noqa: F401

    BITBLAS_AVAILABLE = True
    BITBLAS_EXCEPTION = None
except Exception as e:
    BITBLAS_AVAILABLE = False
    BITBLAS_EXCEPTION = e

logger = getLogger(__name__)


# auto select the correct/optimal QuantLinear class
def select_quant_linear(
    use_triton: bool,
    desc_act: bool,
    group_size: int,
    bits: int,
    disable_exllama: bool = False,
    disable_exllamav2: bool = False,
    use_marlin: bool = False,
    use_bitblas: bool = True,
):
    if use_triton:
        logger.info("Using tritonv2 for GPTQ")
        from ..nn_modules.qlinear.qlinear_tritonv2 import QuantLinear
    else:
        if use_bitblas:
            from ..nn_modules.qlinear.qlinear_bitblas import QuantLinear
        if bits == 4 and use_marlin:
            from ..nn_modules.qlinear.qlinear_marlin import QuantLinear
        elif bits == 4 and not disable_exllamav2:
            from ..nn_modules.qlinear.qlinear_exllamav2 import QuantLinear
        elif bits == 4 and not disable_exllama:
            from ..nn_modules.qlinear.qlinear_exllama import QuantLinear
        elif not desc_act or group_size == -1:
            from ..nn_modules.qlinear.qlinear_cuda_old import QuantLinear
        else:
            from ..nn_modules.qlinear.qlinear_cuda import QuantLinear

    return QuantLinear
