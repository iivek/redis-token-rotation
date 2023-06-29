import pytest
import string

from token_refresh.redis_token_fifo import RedisTokenFIFO
from token_refresh.token_manager import TokenManager
from tests.mock_redis import redis_mock


@pytest.fixture
def token_manager(redis_mock):
    fifo = RedisTokenFIFO(redis_mock, fifo_length=2)
    return TokenManager(fifo, token_length=32)


def test_generate_token():
    token_length = 10
    token = TokenManager.generate_token(token_length)
    assert len(token) == token_length
    assert all(ch in string.ascii_letters + string.digits for ch in token)


@pytest.mark.asyncio
async def test_issue_token(token_manager, mocker):
    user_id = 'user1'

    first_issued_token = await token_manager.issue_token(user_id)
    assert await token_manager.rotation.get_valid(user_id) == [first_issued_token]

    second_issued_token = await token_manager.issue_token(user_id)
    assert await token_manager.rotation.get_valid(user_id) == [second_issued_token]
    assert first_issued_token in await token_manager.rotation.get_invalidated(user_id)


def test_is_valid_format():
    valid_token = 'abc123'
    assert TokenManager.is_valid_format(valid_token)

    invalid_token = ""
    assert not TokenManager.is_valid_format(invalid_token)


@pytest.mark.asyncio
async def test_validate_token(token_manager, mocker):
    user_id = 'user1'
    token = 'abc123'
    status = await token_manager.validate_token(user_id, token)
    assert status == 0
    status = await token_manager.validate_token(user_id, None)
    assert status == 0

    first_issued_token = await token_manager.issue_token(user_id)
    status = await token_manager.validate_token(user_id, first_issued_token)
    assert status == 1
    status = await token_manager.validate_token(user_id, None)
    assert status == 0

    second_issued_token = await token_manager.issue_token(user_id)
    status = await token_manager.validate_token(user_id, second_issued_token)
    assert status == 1
    status = await token_manager.validate_token(user_id, first_issued_token)
    assert status == -1
    status = await token_manager.validate_token(user_id, None)
    assert status == 0


@pytest.mark.asyncio
async def test_revoke_token(token_manager):
    user_id = 'user1'
    token = await token_manager.issue_token(user_id)
    await token_manager.revoke_token(user_id)

    assert await token_manager.validate_token(user_id, token) == -1
    assert await token_manager.validate_token(user_id, None) == 0


@pytest.mark.asyncio
def test_status_message():
    status_code = -1
    expected_message = "Token reused"
    assert TokenManager.status_message(status_code) == expected_message

    status_code = 0
    expected_message = "Invalid token"
    assert TokenManager.status_message(status_code) == expected_message

    status_code = 1
    expected_message = "Valid token"
    assert TokenManager.status_message(status_code) == expected_message


@pytest.mark.asyncio
async def test_provide_token(redis_mock, mocker):
    # Create an instance of TokenHandler with the mocked Redis FIFO
    token_handler = TokenManager(RedisTokenFIFO(redis_mock, fifo_length=2))

    # Define the expected side effect
    side_effects = [1, 0, -1]
    async def side_effect(user_id, token):
        return side_effects.pop(0)

    # Patch the validate_token method with the side effect
    mocker.patch.object(token_handler, 'validate_token', side_effect=side_effect)

    # Call the provide_token method with different token statuses
    _, status_valid = await token_handler.receive_token("user_id", "valid_token")
    _, status_invalid = await token_handler.receive_token("user_id", "invalid_token")
    _, status_reused = await token_handler.receive_token("user_id", "invalidated_token")

    # Assert the expected status codes
    assert status_valid == 1
    assert status_invalid == 0
    assert status_reused == -1
