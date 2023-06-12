import pytest
import string
from token_refresh.handlers import RedisTokenFIFO, TokenManager
from tests.mock_redis import redis_mock


@pytest.fixture
def token_reuse(redis_mock):
    fifo = RedisTokenFIFO(redis_mock, fifo_size=2)
    return TokenManager(fifo, token_length=32, fifo_length=2)


def test_generate_token():
    token_length = 10
    token = TokenManager.generate_token(token_length)
    assert len(token) == token_length
    assert all(ch in string.ascii_letters + string.digits for ch in token)


@pytest.mark.asyncio
async def test_issue_token(token_reuse, mocker):
    user_id = 'user1'

    first_issued_token = await token_reuse.issue_token(user_id)
    assert await token_reuse.rotation.get_valid(user_id) == [first_issued_token]

    second_issued_token = await token_reuse.issue_token(user_id)
    assert await token_reuse.rotation.get_valid(user_id) == [second_issued_token]
    assert first_issued_token in await token_reuse.rotation.get_invalidated(user_id)


def test_is_valid_format():
    valid_token = 'abc123'
    assert TokenManager.is_valid_format(valid_token)

    invalid_token = ""
    assert not TokenManager.is_valid_format(invalid_token)


@pytest.mark.asyncio
async def test_validate_token(token_reuse, mocker):
    user_id = 'user1'
    token = 'abc123'
    status = await token_reuse.validate_token(user_id, token)
    assert status == 0
    status = await token_reuse.validate_token(user_id, None)
    assert status == 0

    first_issued_token = await token_reuse.issue_token(user_id)
    status = await token_reuse.validate_token(user_id, first_issued_token)
    assert status == 1
    status = await token_reuse.validate_token(user_id, None)
    assert status == 0

    second_issued_token = await token_reuse.issue_token(user_id)
    status = await token_reuse.validate_token(user_id, second_issued_token)
    assert status == 1
    status = await token_reuse.validate_token(user_id, first_issued_token)
    assert status == -1
    status = await token_reuse.validate_token(user_id, None)
    assert status == 0


@pytest.mark.asyncio
async def test_revoke_token(token_reuse):
    user_id = 'user1'
    token = await token_reuse.issue_token(user_id)
    await token_reuse.revoke_token(user_id)

    assert await token_reuse.validate_token(user_id, token) == -1
    assert await token_reuse.validate_token(user_id, None) == 0


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
