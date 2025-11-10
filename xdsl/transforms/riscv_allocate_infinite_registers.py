from collections import defaultdict
from collections.abc import Iterable

from xdsl.backend.riscv.register_stack import RiscvRegisterStack
from xdsl.context import Context
from xdsl.dialects import riscv_func
from xdsl.dialects.builtin import IntAttr, ModuleOp
from xdsl.dialects.riscv import IntRegisterType, MVOp, RISCVRegisterType
from xdsl.passes import ModulePass
from xdsl.rewriter import Rewriter


def reg_types_by_name(regs: Iterable[RISCVRegisterType]) -> dict[str, set[str]]:
    """
    Groups register types by name.
    """
    res = defaultdict[str, set[str]](set)
    for reg in regs:
        res[reg.name].add(reg.register_name.data)
    return res


class RISCVAllocateInfiniteRegistersPass(ModulePass):
    """
    Allocates unallocated registers in the module.
    """

    name = "riscv-allocate-infinite-registers"

    def apply(self, ctx: Context, op: ModuleOp) -> None:
        func_ops = tuple(
            inner_op
            for inner_op in op.walk()
            if isinstance(inner_op, riscv_func.FuncOp)
        )

        for func_op in func_ops:
            available_registers = [
                t
                for t in RiscvRegisterStack.default_allocatable_registers()
                if isinstance(t, IntRegisterType)
            ]
            physical_reg_by_infinite_reg: dict[
                RISCVRegisterType, RISCVRegisterType
            ] = {}
            for inner_op in func_op.walk():
                for result in inner_op.results:
                    if (
                        isinstance(result.type, RISCVRegisterType)
                        and isinstance(result.type.index, IntAttr)
                        and result.type.index.data < 0
                    ):
                        if result.type not in physical_reg_by_infinite_reg:
                            if not available_registers:
                                raise RuntimeError(
                                    "Ran out of physical registers when allocating "
                                    "infinite registers."
                                )
                            if (
                                isinstance(inner_op, MVOp)
                                and (
                                    t_index := available_registers.index(
                                        inner_op.rs.type
                                    )
                                )
                                != -1
                            ):
                                physical_reg = available_registers.pop(t_index)

                            else:
                                physical_reg = available_registers.pop()
                            physical_reg_by_infinite_reg[result.type] = physical_reg

                        Rewriter.replace_value_with_new_type(
                            result,
                            physical_reg_by_infinite_reg[result.type],
                        )
