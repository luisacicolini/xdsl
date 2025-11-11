from xdsl.context import Context
from xdsl.dialects import builtin
from xdsl.passes import ModulePass
from xdsl.pattern_rewriter import (
    GreedyRewritePatternApplier,
    PatternRewriteWalker,
)
from xdsl.transforms.canonicalization_patterns.riscv import RemoveRedundantMv
from xdsl.transforms.dead_code_elimination import RemoveUnusedOperations, region_dce


class CanonicalizePostRegisterAllocationPass(ModulePass):
    """
    Applies only moves-related canonicalization patterns.
    """

    name = "canonicalize-register-allocation"

    def apply(self, ctx: Context, op: builtin.ModuleOp) -> None:
        pattern = GreedyRewritePatternApplier(
            [
                RemoveUnusedOperations(),
                RemoveRedundantMv(),
            ]
        )
        PatternRewriteWalker(pattern, post_walk_func=region_dce).rewrite_module(op)
