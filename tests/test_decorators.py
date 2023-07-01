import pytest

from token_rotation.decorators import (
    decode_output_to_string,
    decode_args_to_string,
)


@pytest.mark.asyncio
async def test_decode_output_to_string():
    @decode_output_to_string
    async def example_function():
        return b"Hello, World!"

    # Test singleton output
    result = await example_function()
    assert isinstance(result, str)
    assert result == "Hello, World!"

    # Test iterable output
    @decode_output_to_string
    async def example_function_iterable():
        return [b"Hello", b"World!"]

    result_iterable = await example_function_iterable()
    assert isinstance(result_iterable, list)
    assert all(isinstance(item, str) for item in result_iterable)
    assert result_iterable == ["Hello", "World!"]

    # Test non-bytes output
    @decode_output_to_string
    async def example_function_no_bytes():
        return "Hello, World!"

    result_no_bytes = await example_function_no_bytes()
    assert isinstance(result_no_bytes, str)
    assert result_no_bytes == "Hello, World!"


@pytest.mark.asyncio
async def test_decode_from_bytes_decorator():
    @decode_args_to_string
    async def dummy_function(arg1, arg2, **kwargs):
        return [arg1, arg2, kwargs]

    # Test case with bytes arguments
    result_bytes_args = await dummy_function(
        b"Hello", b"World", key1=b"Value1", key2=b"Value2"
    )
    expected_bytes_args = [
        "Hello",
        "World",
        {"key1": "Value1", "key2": "Value2"},
    ]
    assert result_bytes_args == expected_bytes_args

    # Test case with mixed arguments (bytes and non-bytes)
    result_mixed_args = await dummy_function(
        b"Hello", "World", key1=b"Value1", key2="Value2"
    )
    expected_mixed_args = [
        "Hello",
        "World",
        {"key1": "Value1", "key2": "Value2"},
    ]
    assert result_mixed_args == expected_mixed_args

    # Test case with non-bytes arguments
    result_no_bytes = await dummy_function(
        "Hello", "World", key1="Value1", key2="Value2"
    )
    expected_no_bytes = [
        "Hello",
        "World",
        {"key1": "Value1", "key2": "Value2"},
    ]
    assert result_no_bytes == expected_no_bytes
