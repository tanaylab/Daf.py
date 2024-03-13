"""
Test ``Daf`` storage formats.
"""

# pylint: disable=wildcard-import,unused-wildcard-import,missing-function-docstring
# flake8: noqa: F403,F405

from textwrap import dedent
from typing import Callable
from typing import Tuple

import numpy as np
import pytest

from daf import *

FORMATS = [("MemoryDaf", lambda: MemoryDaf(name="test!"))]


@pytest.mark.parametrize("format_data", FORMATS)
@pytest.mark.parametrize(
    "scalar_data", [("version", "1.0.1", "String"), ("int8", np.int8(1), "Int8"), ("float", 0.5, "Float64")]
)
def test_scalars(format_data: Tuple[str, Callable[[], DafWriter]], scalar_data: Tuple[str, StorageScalar, str]) -> None:
    format_name, create_empty = format_data
    scalar_name, scalar_value, julia_type = scalar_data

    data = create_empty()

    assert len(data.scalar_names()) == 0
    assert isinstance(data.scalar_names(), AbstractSet)
    assert data.name == "test!"
    assert not data.has_scalar(scalar_name)
    data.set_scalar(scalar_name, scalar_value)
    assert data.has_scalar(scalar_name)
    assert data.get_scalar(scalar_name) == scalar_value
    assert set(data.scalar_names()) == set([scalar_name])

    if julia_type == "String":
        scalar_value = '"' + str(scalar_value) + '"'
    else:
        scalar_value = f"{scalar_value} ({julia_type})"

    assert (
        data.description()
        == dedent(
            f"""
                name: test!
                type: {format_name}
                scalars:
                  {scalar_name}: {scalar_value}
            """
        )[1:]
    )

    data.delete_scalar(scalar_name)
    assert (
        data.description()
        == dedent(
            f"""
                name: test!
                type: {format_name}
            """
        )[1:]
    )


@pytest.mark.parametrize("format_data", FORMATS)
@pytest.mark.parametrize("axis_data", [("cell", ["A", "B"]), ("gene", np.array(["X", "Y", "Z"]))])
def test_axes(format_data: Tuple[str, Callable[[], DafWriter]], axis_data: Tuple[str, Sequence[str]]) -> None:
    format_name, create_empty = format_data
    axis_name, axis_entries = axis_data

    data = create_empty()

    assert len(data.axis_names()) == 0
    assert not data.has_axis(axis_name)
    data.add_axis(axis_name, axis_entries)
    assert data.axis_length(axis_name) == len(axis_entries)
    assert list(data.get_axis(axis_name)) == list(axis_entries)
    assert set(data.axis_names()) == set([axis_name])
    assert (
        data.description()
        == dedent(
            f"""
                name: test!
                type: {format_name}
                axes:
                  {axis_name}: {len(axis_entries)} entries
            """
        )[1:]
    )

    data.delete_axis(axis_name)
    assert (
        data.description()
        == dedent(
            f"""
                name: test!
                type: {format_name}
            """
        )[1:]
    )
