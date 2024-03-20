"""
A ``Daf`` query can use operations to process the data: ``EltwiseOperation`` that preserve the shape of the data, and
``ReductionOperation`` that reduce a matrix to a vector, or a vector to a scalar. See the Julia
`documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/operations.html>`__ for details.
"""

from math import e
from math import inf
from typing import Optional
from typing import Type

from .julia_import import JlObject
from .julia_import import _to_julia
from .julia_import import jl

__all__ = [
    "QueryOperation",
    "QuerySequence",
    "EltwiseOperation",
    "ReductionOperation",
    "Abs",
    "Clamp",
    "Convert",
    "Fraction",
    "Log",
    "Max",
    "Median",
    "Mean",
    "Min",
    "Quantile",
    "Round",
    "Significant",
    "Std",
    "StdN",
    "Sum",
    "Var",
    "VarN",
]


class QueryOperation(JlObject):
    """
    Base class for all query operations.
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Registry.QueryOperation>`__ for details.

    Query operations can be chained into a ``QuerySequence`` using the ``|`` operator in Python (instead of the ``|>``
    operator in Julia).
    """

    def __or__(self, other: "QueryOperation") -> "QuerySequence":
        return QuerySequence(jl.Daf.QuerySequence(self.jl_obj, other.jl_obj))

    def __str__(self) -> str:
        return jl.string(self.jl_obj)


class QuerySequence(QueryOperation):
    """
    A sequence of ``QueryOperation``. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Queries.QuerySequence>`__ for details.

    Query operations can be chained into a ``QuerySequence`` using the ``|`` operator in Python (instead of the ``|>``
    operator in Julia).
    """


class EltwiseOperation(QueryOperation):
    """
    Base class for all element-wise operations. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/registry.html#Daf.Registry.EltwiseOperation>`__ for
    details.
    """


class ReductionOperation(QueryOperation):
    """
    Abstract type for all reduction operations. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/registry.html#Daf.Registry.ReductionOperation>`__ for
    details.
    """


class Abs(EltwiseOperation):
    """
    Element-wise operation that converts every element to its absolute value. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Abs>`__ for details.
    """

    def __init__(self, *, dtype: Optional[Type] = None) -> None:
        super().__init__(jl.Daf.Abs(dtype=_to_julia(dtype)))


class Round(EltwiseOperation):
    """
    Element-wise operation that converts every element to the nearest integer value. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Round>`__ for details.
    """

    def __init__(self, *, dtype: Optional[Type] = None) -> None:
        super().__init__(jl.Daf.Round(dtype=_to_julia(dtype)))


class Clamp(EltwiseOperation):
    """
    Element-wise operation that converts every element to a value inside a range. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Clamp>`__ for details.
    """

    def __init__(self, *, min: float = -inf, max: float = inf) -> None:  # pylint: disable=redefined-builtin
        super().__init__(jl.Daf.Clamp(min=min, max=max))


class Convert(EltwiseOperation):
    """
    Element-wise operation that converts every element to a given data type. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Convert>`__ for details.
    """

    def __init__(self, *, dtype: Type) -> None:
        super().__init__(jl.Daf.Convert(dtype=_to_julia(dtype)))


class Fraction(EltwiseOperation):
    """
    Element-wise operation that converts every element to its fraction out of the total. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Fraction>`__ for details.
    """

    def __init__(self, *, dtype: Optional[Type] = None) -> None:
        super().__init__(jl.Daf.Fraction(dtype=_to_julia(dtype)))


class Log(EltwiseOperation):
    """
    Element-wise operation that converts every element to its logarithm. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Log>`__ for details.
    """

    def __init__(self, *, dtype: Optional[Type] = None, base: float = e, eps: float = 0) -> None:
        super().__init__(jl.Daf.Log(dtype=_to_julia(dtype), base=base, eps=eps))


class Significant(EltwiseOperation):
    """
    Element-wise operation that zeros all "insignificant" values. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Significant>`__ for details.
    """

    def __init__(self, *, dtype: Optional[Type] = None, high: float, low: Optional[float] = None) -> None:
        super().__init__(jl.Daf.Significant(dtype=_to_julia(dtype), high=high, low=low))


class Sum(ReductionOperation):
    """
    Reduction operation that sums elements. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Sum>`__ for details.
    """

    def __init__(self, *, dtype: Optional[Type] = None) -> None:
        super().__init__(jl.Daf.Sum(dtype=_to_julia(dtype)))


class Min(ReductionOperation):
    """
    Reduction operation that returns the minimal element. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Min>`__ for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.Min())


class Median(ReductionOperation):
    """
    Reduction operation that returns the median value. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Median>`__ for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.Median())


class Quantile(ReductionOperation):
    """
    Reduction operation that returns the quantile value, that is, a value such that a certain fraction of the values is
    lower. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Quantile>`__ for details.
    """

    def __init__(self, *, dtype: Optional[Type] = None, p: float) -> None:
        super().__init__(jl.Daf.Quantile(dtype=_to_julia(dtype), p=p))


class Mean(ReductionOperation):
    """
    Reduction operation that returns the mean value. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Mean>`__ for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.Mean())


class Max(ReductionOperation):
    """
    Reduction operation that returns the maximal element. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Max>`__ for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.Max())


class Var(ReductionOperation):
    """
    Reduction operation that returns the variance of the values. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Var>`__ for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.Var())


class VarN(ReductionOperation):
    """
    Reduction operation that returns the variance of the values, normalized (divided) by the mean of the values. See the
    Julia `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Var>`__ for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.VarN())


class Std(ReductionOperation):
    """
    Reduction operation that returns the standard deviation of the values. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Std>`__ for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.Std())


class StdN(ReductionOperation):
    """
    Reduction operation that returns the standard deviation of the values, normalized (divided) by the mean of the
    values. See the Julia `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.Std>`_
    for details.
    """

    def __init__(self) -> None:
        super().__init__(jl.Daf.StdN())
