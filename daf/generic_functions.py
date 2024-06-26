"""
Types that arguably should belong in a more general-purpose package. See the Julia
`documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/generic.html>`__ for details.
"""

from typing import Literal

from .julia_import import jl

__all__ = ["AbnormalHandler", "inefficient_action_handler"]


#: The action to take when encountering an "abnormal" (but recoverable) operation. See the Julia
#: `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/generic.html#Daf.Generic.AbnormalHandler>`__ for details.
AbnormalHandler = Literal["IgnoreHandler"] | Literal["WarnHandler"] | Literal["ErrorHandler"]

JL_ABNORMAL_HANDLER = {
    "IgnoreHandler": jl.Daf.GenericFunctions.IgnoreHandler,
    "WarnHandler": jl.Daf.GenericFunctions.WarnHandler,
    "ErrorHandler": jl.Daf.GenericFunctions.ErrorHandler,
}

PY_ABNORMAL_HANDLER = {
    jl.Daf.GenericFunctions.IgnoreHandler: "IgnoreHandler",
    jl.Daf.GenericFunctions.WarnHandler: "WarnHandler",
    jl.Daf.GenericFunctions.ErrorHandler: "ErrorHandler",
}


# flake8: noqa
# pylint: disable=line-too-long


def inefficient_action_handler(handler: AbnormalHandler) -> AbnormalHandler:
    """
    Specify the ``AbnormalHandler`` to use when accessing a matrix in an inefficient way ("against the grain"). Returns
    the previous handler. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/generic_functions.html#Daf.MatrixLayouts.inefficient_action_handler>`__
    for details.
    """
    return PY_ABNORMAL_HANDLER[jl.Daf.MatrixLayouts.inefficient_action_handler(JL_ABNORMAL_HANDLER[handler])]  # type: ignore
