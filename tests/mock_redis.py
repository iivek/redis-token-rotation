import pytest


def create_redis_mock(redis_mock, redis_dict):
    """Mocking the redis client, with the goal to use python lists in place of of redis lists."""
    redis_client_mock = redis_mock.return_value

    # Mock the rpush function
    async def mock_rpush(key, value):
        if key not in redis_dict:
            redis_dict[key] = []
        redis_dict[key].append(value)

    # Mock the llen function
    async def mock_llen(key):
        if key in redis_dict:
            return len(redis_dict[key])
        return 0

    # Mock the lpop function
    async def mock_lpop(key):
        if key in redis_dict and redis_dict[key]:
            return redis_dict[key].pop(0)
        return None

    # Mock the lrange function
    async def mock_lrange(key, start, end):
        if key in redis_dict:
            lst = redis_dict[key]
            length = len(lst)

            # Convert negative indices to positive indices
            start = start + length if start < 0 else start
            end = end + length if end < 0 else end

            # Adjust the end index to make it inclusive
            end = end + 1

            # Return the sublist based on the start and end indices
            return lst[start:end]

        return []

    # Assign the mock rpush function to the mock client
    redis_client_mock.rpush.side_effect = mock_rpush
    redis_client_mock.llen.side_effect = mock_llen
    redis_client_mock.lpop.side_effect = mock_lpop
    redis_client_mock.lrange.side_effect = mock_lrange

    return redis_client_mock


@pytest.fixture
def redis_mock(mocker):
    redis_mock = mocker.patch('redis.Redis')
    redis_dict = {}
    return create_redis_mock(redis_mock, redis_dict)