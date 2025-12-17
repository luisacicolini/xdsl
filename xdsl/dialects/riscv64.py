from __future__ import annotations

from xdsl.dialects.riscv import (
    RdRsImmShiftOperation, 
    RISCVVariant, 
    SlliOp,
    SrliOp
)

from typing import ClassVar


from xdsl.ir import (
    Dialect,
)

from xdsl.irdl import (
    irdl_op_definition,
)


@irdl_op_definition
class RV64SlliOp(SlliOp):
    """
    Performs logical left shift on the value in register rs1 by the shift amount
    held in the lower 6 bits of the immediate.

    x[rd] = x[rs1] << shamt

    See external [documentation](https://msyksphinz-self.github.io/riscv-isadoc/html/rvi.html#slli).
    """

    name = "riscv64.slli"
    
    RVVARIANT: ClassVar[RISCVVariant] = RISCVVariant.RV64


@irdl_op_definition
class RV64SrliOp(SrliOp):
    """
    Performs logical right shift on the value in register rs1 by the shift amount held
    in the lower 6 bits of the immediate.

    x[rd] = x[rs1] >>u shamt

    See external [documentation](https://msyksphinz-self.github.io/riscv-isadoc/html/rvi.html#srli).
    """

    name = "riscv64.srli"
    
    RVVARIANT: ClassVar[RISCVVariant] = RISCVVariant.RV64

@irdl_op_definition
class RV64SraiOp(RdRsImmShiftOperation):
    """
    Performs arithmetic right shift on the value in register rs1 by the shift amount
    held in the lower 6 bits of the immediate.

    x[rd] = x[rs1] >>s shamt

    See external [documentation](https://msyksphinz-self.github.io/riscv-isadoc/html/rvi.html#srai).
    """

    name = "riscv32.srai"

    RVVARIANT: ClassVar[RISCVVariant] = RISCVVariant.RV64
    
    
RISCV64 = Dialect(
    "riscv64",
    [
        RV64SlliOp,
        RV64SrliOp,
        RV64SraiOp,
    ],
    [],
)
