from tests.mock_redis import create_redis_mock
from token_rotation.redis_token_fifo import RedisTokenFIFO


def test_redis_token_fifo(mocker):
    redis_mock = mocker.patch("redis.Redis")
    redis_dict = {}
    redis_client_mock = create_redis_mock(redis_mock, redis_dict)

    # Perform the test
    redis_token_fifo: RedisTokenFIFO = RedisTokenFIFO(
        redis_client_mock, fifo_length=3
    )
    redis_token_fifo.add("key1", "token1")
    redis_token_fifo.add("key1", "token2")
    redis_token_fifo.add("key1", "token3")
    redis_token_fifo.add("key1", "token4")
    redis_token_fifo.get_valid("key1") == ["token4"]
    redis_token_fifo.get_invalidated("key1") == ["token2", "token3"]
