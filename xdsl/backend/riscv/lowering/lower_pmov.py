from typing import cast

from xdsl.context import Context
from xdsl.dialects import riscv
from xdsl.dialects.builtin import ModuleOp
from xdsl.passes import ModulePass
from xdsl.pattern_rewriter import (
    PatternRewriter,
    PatternRewriteWalker,
    RewritePattern,
    op_type_rewrite_pattern,
)


class LowerPMovOp(RewritePattern):
    @op_type_rewrite_pattern
    def match_and_rewrite(self, op: riscv.PMovOp, rewriter: PatternRewriter) -> None:
        if any(
            val.type == riscv.Registers.UNALLOCATED_INT
            for vals in (op.operands, op.results)
            for val in vals
        ):
            return

        pairs = tuple(zip(op.operands, op.results))

        same_type_pairs = tuple(
            ip for ip in enumerate(pairs) if ip[1][0].type == ip[1][1].type
        )
        different_type_pairs = tuple(
            ip for ip in enumerate(pairs) if ip[1][0].type != ip[1][1].type
        )

        input_types = set(src.type for _, (src, _) in different_type_pairs)
        output_types = set(dst.type for _, (_, dst) in different_type_pairs)

        if input_types.intersection(output_types):
            raise NotImplementedError

        same_type_moves = tuple(
            (i, riscv.MVOp(src, rd=cast(riscv.IntRegisterType, dst.type)))
            for i, (src, dst) in same_type_pairs
        )

        different_type_moves = tuple(
            (i, riscv.MVOp(src, rd=cast(riscv.IntRegisterType, dst.type)))
            for i, (src, dst) in different_type_pairs
        )

        oredered_moves = (*same_type_moves, *different_type_moves)
        sorted_moves = sorted(oredered_moves, key=lambda pair: pair[0])
        sorted_results = tuple(o.results[0] for _, o in sorted_moves)

        rewriter.replace_matched_op(
            tuple(mv for _, mv in oredered_moves), sorted_results
        )


class LowerPMovPass(ModulePass):
    name = "lower-pmov"

    def apply(self, ctx: Context, op: ModuleOp) -> None:
        PatternRewriteWalker(
            LowerPMovOp(),
            apply_recursively=False,
        ).rewrite_module(op)
