"""
Interface of ``DafReader`` and ``DafWriter``. See the Julia
`documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html>`__ for details.
"""

from contextlib import contextmanager
from typing import AbstractSet
from typing import Any
from typing import Iterator
from typing import Literal
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import overload
from weakref import WeakValueDictionary

import numpy as np
import pandas as pd  # type: ignore
import scipy.sparse as sp  # type: ignore

from .julia_import import JlObject
from .julia_import import Undef
from .julia_import import UndefInitializer
from .julia_import import _as_vector
from .julia_import import _from_julia_array
from .julia_import import _from_julia_frame
from .julia_import import _jl_pairs
from .julia_import import _to_julia
from .julia_import import jl
from .queries import Query
from .storage_types import StorageScalar

__all__ = ["DafReader", "DafWriter", "CacheType"]


#: Types of cached data inside ``Daf``. See the Julia
#: `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Formats.CacheType>`__ for details.
CacheType = Literal["MappedData"] | Literal["MemoryData"] | Literal["QueryData"]

JL_CACHE_TYPE = {
    "MappedData": jl.Daf.MappedData,
    "MemoryData": jl.Daf.MemoryData,
    "QueryData": jl.Daf.QueryData,
}


def _to_jl_cache_type(cache_type: Optional[CacheType]) -> jl.Daf.CacheType:
    if cache_type is not None:
        return JL_CACHE_TYPE[cache_type]
    return None


class DafReader(JlObject):
    """
    Read-only access to ``Daf`` data. See the Julia
    `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html>`__ for details.
    """

    def __init__(self, jl_obj) -> None:
        super().__init__(jl_obj)
        self.weakrefs: WeakValueDictionary[Any, Any] = WeakValueDictionary()

    @property
    def name(self) -> str:
        """
        Return the (hopefully unique) name of the ``Daf`` data set.
        """
        return self.jl_obj.name

    def description(self, *, cache: bool = False, deep: bool = False) -> str:
        """
        Return a (multi-line) description of the contents of ``Daf`` data. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.description>`__ for details.
        """
        return jl.Daf.description(self.jl_obj, cache=cache, deep=deep)

    def has_scalar(self, name: str) -> bool:
        """
        Check whether a scalar property with some ``name`` exists in the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.has_scalar>`__ for details.
        """
        return jl.Daf.has_scalar(self.jl_obj, name)

    def get_scalar(self, name: str) -> StorageScalar:
        """
        Get the value of a scalar property with some ``name`` in the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.get_scalar>`__ for details.

        Numeric scalars are always returned as ``int`` or ``float``, regardless of the specific data type they are
        stored in the ``Daf`` data set (e.g., a ``UInt8`` will be returned as an ``int`` instead of a ``np.uint8``).
        """
        return jl.Daf.get_scalar(self.jl_obj, name)

    def scalar_names(self) -> AbstractSet[str]:
        """
        The names of the scalar properties in the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.scalar_names>`__ for details.
        """
        return jl.Daf.scalar_names(self.jl_obj)

    def has_axis(self, axis: str) -> bool:
        """
        Check whether some ``axis`` exists in the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.has_axis>`__ for details.
        """
        return jl.Daf.has_axis(self.jl_obj, axis)

    def axis_names(self) -> AbstractSet[str]:
        """
        The names of the axes of the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.axis_names>`__ for details.
        """
        return jl.Daf.axis_names(self.jl_obj)

    def axis_length(self, axis: str) -> int:
        """
        The number of entries along the ``axis`` i the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.axis_length>`__ for details.
        """
        return jl.Daf.axis_length(self.jl_obj, axis)

    def get_axis(self, axis: str) -> np.ndarray:
        """
        The unique names of the entries of some ``axis`` of the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.get_axis>`__ for details.

        This creates an in-memory copy of the data, which is cached for repeated calls.
        """
        axis_version_counter = jl.Daf.axis_version_counter(self.jl_obj, axis)
        axis_key = (axis_version_counter, axis)
        axis_entries = self.weakrefs.get(axis_key)
        if axis_entries is None:
            axis_entries = _from_julia_array(jl.Daf.get_axis(self.jl_obj, axis))
            self.weakrefs[axis_key] = axis_entries
        return axis_entries

    def has_vector(self, axis: str, name: str) -> bool:
        """
        Check whether a vector property with some ``name`` exists for the ``axis`` in the ``Daf`` data set. See the
        Julia `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.has_vector>`__ for details.
        """
        return jl.Daf.has_vector(self.jl_obj, axis, name)

    def vector_names(self, axis: str) -> AbstractSet[str]:
        """
        The names of the vector properties for the ``axis`` in ``Daf`` data set, **not** including the special ``name``
        property. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.vector_names>`__ for details.
        """
        return jl.Daf.vector_names(self.jl_obj, axis)

    @overload
    def get_np_vector(
        self,
        axis: str,
        name: str,
        *,
        default: None,
    ) -> Optional[np.ndarray]: ...

    @overload
    def get_np_vector(
        self,
        axis: str,
        name: str,
        *,
        default: StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
    ) -> np.ndarray: ...

    def get_np_vector(
        self,
        axis,
        name,
        *,
        default: None | StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
    ) -> Optional[np.ndarray]:
        """
        Get the vector property with some ``name`` for some ``axis`` in the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.get_vector>`__ for details.

        This always returns a ``numpy`` vector (unless ``default`` is ``None`` and the vector does not exist). If the
        stored data is numeric and dense, this is a zero-copy view of the data stored in the ``Daf`` data set.
        Otherwise, a Python copy of the data as a dense ``numpy`` array is returned (and cached for repeated calls).
        Since Python has no concept of sparse vectors (because "reasons"), you can't zero-copy view a sparse ``Daf``
        vector using the Python API.
        """
        if not jl.Daf.has_vector(self.jl_obj, axis, name):
            if default is None:
                return None
            return _from_julia_array(jl.Daf.get_vector(self.jl_obj, axis, name, default=_to_julia(default)).array)

        vector_version_counter = jl.Daf.vector_version_counter(self.jl_obj, axis, name)
        vector_key = (vector_version_counter, axis, name)
        vector_value = self.weakrefs.get(vector_key)
        if vector_value is None:
            vector_value = _from_julia_array(jl.Daf.get_vector(self.jl_obj, axis, name).array)
            self.weakrefs[vector_key] = vector_value
        return vector_value

    @overload
    def get_pd_vector(
        self,
        axis: str,
        name: str,
        *,
        default: None,
    ) -> Optional[pd.Series]: ...

    @overload
    def get_pd_vector(
        self,
        axis: str,
        name: str,
        *,
        default: StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
    ) -> pd.Series: ...

    def get_pd_vector(
        self,
        axis: str,
        name: str,
        *,
        default: None | StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
    ) -> Optional[pd.Series]:
        """
        Get the vector property with some ``name`` for some ``axis`` in the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.get_vector>`__ for details.

        This is a wrapper around ``get_np_vector`` which returns a ``pandas`` series using the entry names of the axis
        as the index.
        """
        vector_value = self.get_np_vector(axis, name, default=_to_julia(default))
        if vector_value is None:
            return None
        return pd.Series(vector_value, index=self.get_axis(axis))

    def has_matrix(self, rows_axis: str, columns_axis: str, name: str, *, relayout: bool = True) -> bool:
        """
        Check whether a matrix property with some ``name`` exists for the ``rows_axis`` and the ``columns_axis`` in the
        ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.has_matrix>`__ for details.
        """
        return jl.Daf.has_matrix(self.jl_obj, rows_axis, columns_axis, name, relayout=relayout)

    def matrix_names(self, rows_axis: str, columns_axis: str, *, relayout: bool = True) -> AbstractSet[str]:
        """
        The names of the matrix properties for the ``rows_axis`` and ``columns_axis`` in the ``Daf`` data set. See the
        Julia `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.matrix_names>`__ for details.
        """
        return jl.Daf.matrix_names(self.jl_obj, rows_axis, columns_axis, relayout=relayout)

    @overload
    def get_np_matrix(
        self, rows_axis: str, columns_axis: str, name: str, *, default: None, relayout: bool = True
    ) -> Optional[np.ndarray | sp.csc_matrix]: ...

    @overload
    def get_np_matrix(
        self,
        rows_axis: str,
        columns_axis: str,
        name: str,
        *,
        default: StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
        relayout: bool = True,
    ) -> np.ndarray | sp.csc_matrix: ...

    def get_np_matrix(
        self,
        rows_axis: str,
        columns_axis: str,
        name: str,
        *,
        default: None | StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
        relayout: bool = True,
    ) -> Optional[np.ndarray | sp.csc_matrix]:
        """
        Get the column-major matrix property with some ``name`` for some ``rows_axis`` and ``columns_axis`` in the
        ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.get_matrix>`__ for details.

        This always returns a column-major ``numpy`` matrix or a ``scipy`` sparse ``csc_matrix``, (unless ``default`` is
        ``None`` and the matrix does not exist). If the stored data is numeric and dense, this is a zero-copy view of
        the data stored in the ``Daf`` data set.

        Note that by default ``numpy`` matrices are in row-major (C) layout and not in column-major (Fortran) layout. To
        get a row-major matrix, simply flip the order of the axes, and call transpose on the result (which is an
        efficient zero-copy operation). This will also (zero-copy) convert the ``csc_matrix`` into a ``csr_matrix``.

        Also note that although we call this ``get_np_matrix``, the result is **not** the deprecated ``np.matrix``
        (which is to be avoided at all costs).
        """
        if not jl.Daf.has_matrix(self.jl_obj, rows_axis, columns_axis, name, relayout=relayout):
            if default is None:
                return None
            return _from_julia_array(
                jl.Daf.get_matrix(
                    self.jl_obj, rows_axis, columns_axis, name, default=_to_julia(default), relayout=relayout
                ).array
            )

        matrix_version_counter = jl.Daf.matrix_version_counter(self.jl_obj, rows_axis, columns_axis, name)
        matrix_key = (matrix_version_counter, rows_axis, columns_axis, name)
        matrix_value = self.weakrefs.get(matrix_key)
        if matrix_value is None:
            matrix_value = _from_julia_array(
                jl.Daf.get_matrix(self.jl_obj, rows_axis, columns_axis, name, relayout=relayout).array
            )
            self.weakrefs[matrix_key] = matrix_value
        return matrix_value

    @overload
    def get_pd_matrix(
        self,
        rows_axis: str,
        columns_axis: str,
        name: str,
        *,
        default: None,
        relayout: bool = True,
    ) -> Optional[pd.DataFrame]: ...

    @overload
    def get_pd_matrix(
        self,
        rows_axis: str,
        columns_axis: str,
        name: str,
        *,
        default: StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
        relayout: bool = True,
    ) -> pd.DataFrame: ...

    def get_pd_matrix(
        self,
        rows_axis: str,
        columns_axis: str,
        name: str,
        *,
        default: None | StorageScalar | Sequence[StorageScalar] | np.ndarray | UndefInitializer = Undef,
        relayout: bool = True,
    ) -> Optional[pd.DataFrame]:
        """
        Get the column-major matrix property with some ``name`` for some ``rows_axis`` and ``columns_axis`` in the
        ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.get_matrix>`__ for details.

        This is a wrapper around ``get_np_matrix`` which returns a ``pandas`` data frame using the entry names of the
        axes as the indices.

        Note that since ``pandas`` data frames can't contain a sparse matrix, the data will always be in a dense
        ``numpy`` matrix, so take care not to invoke this for a too-large sparse data matrix.

        This is not to be confused with ``get_frame`` which returns a "real" ``pandas`` data frame, with arbitrary
        (query) columns, possibly using a different data type for each.
        """
        matrix_value = self.get_np_matrix(rows_axis, columns_axis, name, default=_to_julia(default), relayout=relayout)
        if matrix_value is None:
            return None
        if sp.issparse(matrix_value):
            matrix_value = matrix_value.toarray()
        return pd.DataFrame(matrix_value, index=self.get_axis(rows_axis), columns=self.get_axis(columns_axis))

    def empty_cache(self, *, clear: Optional[CacheType] = None, keep: Optional[CacheType] = None) -> None:
        """
        Clear some cached data. By default, completely empties the caches. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Data.empty_cache!>`__ for details.
        """
        jl.Daf.empty_cache_b(self.jl_obj, clear=_to_jl_cache_type(clear), keep=_to_jl_cache_type(keep))

    def get_np_query(self, query: str | Query, *, cache: bool = True) -> StorageScalar | np.ndarray | AbstractSet[str]:
        """
        Apply the full ``query`` to the ``Daf`` data set and return the result. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Operations.get_query>`__ for details.

        If the result isn't a scalar, and isn't an array of names, then we return a ``numpy`` array or a ``scipy``
        ``csc_matrix``.
        """
        result = jl.Daf.Queries.get_query(self.jl_obj, _to_julia(query), cache=cache)
        if not isinstance(result, (str, int, float, AbstractSet)):
            result = result.array
            result = _from_julia_array(result)
        return result

    def get_pd_query(
        self, query: str | Query, *, cache: bool = True
    ) -> StorageScalar | pd.Series | pd.DataFrame | AbstractSet[str]:
        """
        Similar to ``get_np_query``, but return a ``pandas`` series or data frame for vector and matrix data.

        Note that since ``pandas`` data frames can't contain a sparse matrix, the data will always be in a dense
        ``numpy`` matrix, so take care not to invoke this for a too-large sparse data matrix.
        """
        result = jl.Daf.Queries.get_query(self.jl_obj, _to_julia(query), cache=cache)
        if not isinstance(result, (str, int, float, AbstractSet)):
            values = _from_julia_array(result.array)
            if sp.issparse(values):
                values = values.toarray()  # type: ignore
            assert 1 <= values.ndim <= 2
            if values.ndim == 1:
                result = pd.Series(values, index=_from_julia_array(jl.NamedArrays.names(result, 1)))
            else:
                result = pd.DataFrame(
                    values,
                    index=_from_julia_array(jl.names(result, 1)),
                    columns=_from_julia_array(jl.names(result, 2)),
                )
        return result

    def __getitem__(self, query: str | Query) -> StorageScalar | np.ndarray | AbstractSet[str]:
        """
        The shorthand ``data[query]`` is equivalent to ``data.get_np_query(query)``.
        """
        return self.get_np_query(query)

    def get_pd_frame(
        self,
        axis: str | Query,
        columns: Optional[Sequence[str] | Mapping[str, str | Query]] = None,
        *,
        cache: bool = False,
    ) -> pd.DataFrame:
        """
        Return a ``DataFrame`` containing multiple vectors of the same ``axis``. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/queries.html#Daf.Queries.get_frame>`__ for details.

        Note this is different from ``get_pd_matrix`` which returns some 2D data as a ``pandas`` data frame. Here, each
        column can be the result of an arbitrary query and may have a different data type.

        The order of the columns matters. Luckily, the default dictionary type is ordered in modern Python, so if you
        write ``columns = {"color": ": type => color", "age": ": batch => age"}`` you can trust that the ``color``
        column will be first and the ``age`` column will be second.
        """
        if isinstance(columns, Mapping):
            columns = jl._pairify_columns(_jl_pairs(columns))
        else:
            columns = _to_julia(columns)
        jl_frame = jl.Daf.Queries.get_frame(self.jl_obj, axis, columns, cache=cache)
        return _from_julia_frame(jl_frame)


class DafWriter(DafReader):
    """
    Read-write access to ``Daf`` data.
    """

    def set_scalar(self, name: str, value: StorageScalar, *, overwrite: bool = False) -> None:
        """
        Set the ``value`` of a scalar property with some ``name`` in a ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.set_scalar!>`__ for details.

        You can force the data type numeric scalars are stored in by using the appropriate ``numpy`` type (e.g., a
        ``np.uint8`` will be stored as a ``UInt8``).
        """
        jl.Daf.set_scalar_b(self.jl_obj, name, value, overwrite=overwrite)

    def delete_scalar(self, name: str, *, must_exist: bool = True) -> None:
        """
        Delete a scalar property with some ``name`` from the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.delete_scalar!>`__ for details.
        """
        jl.Daf.delete_scalar_b(self.jl_obj, name, must_exist=must_exist)

    def add_axis(self, axis: str, entries: Sequence[str] | np.ndarray) -> None:
        """
        Add a new ``axis`` to the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.add_axis!>`__ for details.
        """
        jl.Daf.add_axis_b(self.jl_obj, axis, _to_julia(entries))

    def delete_axis(self, axis: str, *, must_exist: bool = True) -> None:
        """
        Delete an ``axis`` from the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.delete_axis!>`__ for details.
        """
        jl.Daf.delete_axis_b(self.jl_obj, axis, must_exist=must_exist)

    def set_vector(
        self,
        axis: str,
        name: str,
        value: Sequence[StorageScalar] | np.ndarray | sp.csc_matrix | sp.csr_matrix,
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Set a vector property with some ``name`` for some ``axis`` in the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.set_vector!>`__ for details.

        If the provided ``value`` is numeric and dense, this passes a zero-copy view of the data to the ``Daf`` data
        set. Otherwise, a Python copy of the data is made (as a dense ``numpy`` array), and passed to ``Daf``.

        As a convenience, you can pass a 1xN or Nx1 matrix here and it will be mercifully interpreted as a vector. This
        allows creating sparse vectors in ``Daf`` by passing a 1xN slice of a sparse (column-major) Python matrix.
        """
        if (isinstance(value, sp.csc_matrix) and value.shape[1] == 1) or (
            isinstance(value, sp.csr_matrix) and value.shape[0] == 1
        ):
            with self.empty_sparse_vector(
                axis,
                name,
                value.data.dtype,
                value.nnz,
                value.indptr.dtype,
                overwrite=overwrite,
            ) as (nzind, nzval):
                nzind[:] = value.indices[:]
                nzind += 1
                nzval[:] = value.data[:]
            return

        if (isinstance(value, sp.csc_matrix) and value.shape[0] == 1) or (
            isinstance(value, sp.csr_matrix) and value.shape[1] == 1
        ):
            with self.empty_sparse_vector(
                axis,
                name,
                value.data.dtype,
                value.nnz,
                value.indptr.dtype,
                overwrite=overwrite,
            ) as (nzind, nzval):
                nzind[:] = np.where(np.ediff1d(value.indptr) == 1)[0]
                nzind += 1
                nzval[:] = value.data[:]
            return

        jl.Daf.set_vector_b(self.jl_obj, axis, name, _as_vector(_to_julia(value)), overwrite=overwrite)

    @contextmanager
    def empty_dense_vector(
        self, axis: str, name: str, eltype: Type, *, overwrite: bool = False
    ) -> Iterator[np.ndarray]:
        """
        Create an empty dense vector property with some ``name`` for some ``axis`` in the ``Daf`` data set, and pass it
        to the block to be filled. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.empty_dense_vector!>`__ for details.
        """
        vector = jl.Daf.get_empty_dense_vector_b(self.jl_obj, axis, name, _to_julia(eltype), overwrite=overwrite)
        try:
            yield _from_julia_array(vector)
            jl.Daf.filled_empty_dense_vector_b(self.jl_obj, axis, name, vector, overwrite=overwrite)
        finally:
            jl.Daf.end_write_lock(self.jl_obj)

    @contextmanager
    def empty_sparse_vector(
        self, axis: str, name: str, eltype: Type, nnz: int, indtype: Type, *, overwrite: bool = False
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Create an empty sparse vector property with some ``name`` for some ``axis`` in the ``Daf`` data set, pass its
        parts (``nzind`` and ``nzval``) to the block to be filled. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.empty_sparse_vector!>`__ for
        details.

        Note that the code block will get a tuple of ``(nzind, nzval)`` arrays for *Julia's* ``SparseVector``, **not** a
        tuple of ``(data, indices, indptr)`` for Python's ``csc_matrix``. First, ``numpy`` (that is, ``scipy``) has no
        concept of sparse vectors. In addition ``nzind`` is 1-based (Julia) and not 0-based (Python).
        """
        nzind, nzval, extra = jl.Daf.get_empty_sparse_vector_b(
            self.jl_obj, axis, name, _to_julia(eltype), nnz, _to_julia(indtype), overwrite=overwrite
        )
        try:
            yield (_from_julia_array(nzind), _from_julia_array(nzval))
            jl.Daf.filled_empty_sparse_vector_b(self.jl_obj, axis, name, nzind, nzval, extra, overwrite=overwrite)
        finally:
            jl.Daf.end_write_lock(self.jl_obj)

    def delete_vector(self, axis: str, name: str, *, must_exist: bool = True) -> None:
        """
        Delete a vector property with some ``name`` for some ``axis`` from the ``Daf`` data set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.delete_vector!>`__ for details.
        """
        jl.Daf.delete_vector_b(self.jl_obj, axis, name, must_exist=must_exist)

    def set_matrix(
        self,
        rows_axis: str,
        columns_axis: str,
        name: str,
        value: np.ndarray | sp.csc_matrix,
        *,
        overwrite: bool = False,
        relayout: bool = True,
    ) -> None:
        """
        Set the matrix property with some ``name`` for some ``rows_axis`` and ``columns_axis`` in the ``Daf`` data set.
        See the Julia `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.set_matrix!>`__ for
        details.

        Since ``Daf`` is implemented Julia, this should be a column-major ``matrix``, so if you have a standard
        ``numpy`` or ``scipy`` row-major matrix, flip the order of the axes and pass the ``transpose`` (which is an
        efficient zero-copy operation).
        """
        jl.Daf.set_matrix_b(
            self.jl_obj, rows_axis, columns_axis, name, _to_julia(value), overwrite=overwrite, relayout=relayout
        )

    @contextmanager
    def empty_dense_matrix(
        self, rows_axis: str, columns_axis: str, name: str, eltype: Type, *, overwrite: bool = False
    ) -> Iterator[np.ndarray]:
        """
        Create an empty (column-major) dense matrix property with some ``name`` for some ``rows_axis`` and
        ``columns_axis`` in the ``Daf`` data set, and pass it to the block to be filled. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.empty_dense_matrix!>`__ for details.
        """
        matrix = jl.Daf.get_empty_dense_matrix_b(
            self.jl_obj, rows_axis, columns_axis, name, _to_julia(eltype), overwrite=overwrite
        )
        try:
            yield _from_julia_array(matrix)
            jl.Daf.filled_empty_dense_matrix_b(self.jl_obj, rows_axis, columns_axis, name, matrix, overwrite=overwrite)
        finally:
            jl.Daf.end_write_lock(self.jl_obj)

    @contextmanager
    def empty_sparse_matrix(
        self,
        rows_axis: str,
        columns_axis: str,
        name: str,
        eltype: Type,
        nnz: int,
        indtype: Type,
        *,
        overwrite: bool = False,
    ) -> Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Create an empty (column-major) sparse matrix property with some ``name`` for some ``rows_axis`` and
        ``columns_axis`` in the ``Daf`` data set, and pass its parts (``colptr``, ``rowval`` and ``nzval``) to the block
        to be filles. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.empty_sparse_matrix!>`__ for
        details.

        Note that the code block will get a tuple of ``(colptr, rowval, nzval)`` arrays for Julia's ``SparseMatrixCSC``,
        **not** a tuple of ``(data, indices, indptr)`` for Python's ``csc_matrix``. Yes, ``data`` is the same as
        ``nzval``, but ``colptr = indptr + 1`` and ``rowval = indices + 1``, because Julia uses 1-based indexing, and
        Python uses 0-based indexing. For this reason, sparse data can't ever be zero-copy between Julia and Python.
        Sigh.
        """
        colptr, rowval, nzval, extra = jl.Daf.get_empty_sparse_matrix_b(
            self.jl_obj, rows_axis, columns_axis, name, _to_julia(eltype), nnz, _to_julia(indtype), overwrite=overwrite
        )
        try:
            yield (_from_julia_array(colptr), _from_julia_array(rowval), _from_julia_array(nzval))
            jl.Daf.filled_empty_sparse_matrix_b(
                self.jl_obj, rows_axis, columns_axis, name, colptr, rowval, nzval, extra, overwrite=overwrite
            )
        finally:
            jl.Daf.end_write_lock(self.jl_obj)

    def relayout_matrix(self, rows_axis: str, columns_axis: str, name: str, *, overwrite: bool = False) -> None:
        """
        Given a matrix property with some ``name`` exists (in column-major layout) in the ``Daf`` data set for the
        ``rows_axis`` and the ``columns_axis``, then relayout it and store the row-major result as well (that is, with
        flipped axes). See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.relayout_matrix!>`__ for details.
        """
        jl.Daf.relayout_matrix_b(self.jl_obj, rows_axis, columns_axis, name, overwrite=overwrite)

    def delete_matrix(self, rows_axis: str, columns_axis: str, name: str, *, must_exist: bool = True) -> None:
        """
        Delete a matrix property with some ``name`` for some ``rows_axis`` and ``columns_axis`` from the ``Daf`` data
        set. See the Julia
        `documentation <https://tanaylab.github.io/Daf.jl/v0.1.0/data.html#Daf.Data.delete_matrix!>`__ for details.
        """
        jl.Daf.delete_matrix_b(self.jl_obj, rows_axis, columns_axis, name, must_exist=must_exist)
