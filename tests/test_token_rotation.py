import pytest

from token_refresh.handlers import TokenHandler, RedisTokenFIFO
from tests.mock_redis import redis_mock


@pytest.mark.asyncio
async def test_provide_token(redis_mock, mocker):
    # Create an instance of TokenHandler with the mocked Redis FIFO
    token_handler = TokenHandler(RedisTokenFIFO(redis_mock, fifo_size=2))

    # Define the expected side effect
    side_effects = [1, 0, -1]
    async def side_effect(user_id, token):
        return side_effects.pop(0)

    # Patch the validate_token method with the side effect
    mocker.patch.object(token_handler, 'validate_token', side_effect=side_effect)

    # Call the provide_token method with different token statuses
    status_valid = await token_handler.provide_token("user_id", "valid_token")
    status_invalid = await token_handler.provide_token("user_id", "invalid_token")
    status_reused = await token_handler.provide_token("user_id", "invalidated_token")

    # Assert the expected status codes
    assert status_valid == 1
    assert status_invalid == 0
    assert status_reused == -1
