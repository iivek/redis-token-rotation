from typing import Iterable

from token_refresh.decorators import decode_args_to_string, decode_output_to_string


class RedisTokenFIFO:
    """FIFO Queue implementation in Redis using an async Redis client.

    This class provides a First-In-First-Out (FIFO) queue functionality in Redis.
    The functions in this class use decorators to enforce the expected datatypes for keys and values,
    ensuring that both arguments and function outputs are strings or iterables of strings,
    regardless of the encoding that the client uses,
    """

    def __init__(self, redis_client, fifo_length=2):
        """
        Initialize the RedisTokenFIFO instance.

        Args:
            redis_client: Asynchronous Redis client.
            fifo_length: The length of the FIFO queue (default: 2).

        """
        self.redis_client = redis_client
        self.fifo_size = fifo_length

    @decode_args_to_string
    async def add(self, key, element: str):
        """Add an element to the FIFO queue."""
        await self.redis_client.rpush(key, element)
        if await self.redis_client.llen(key) > self.fifo_size:
            await self.redis_client.lpop(key)

    @decode_output_to_string
    async def get_invalidated(self, key) -> Iterable:
        """Get the entire FIFO except the freshest element"""
        return await self.redis_client.lrange(key, 0, -2)

    @decode_output_to_string
    async def get_valid(self, key) -> Iterable:
        """Get the freshest element in the queue"""
        return await self.redis_client.lrange(key, -1, -1)
