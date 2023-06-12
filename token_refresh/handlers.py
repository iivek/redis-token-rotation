"""
Refresh tokens with rotation and reuse detection, using Redis.
MAX_TOKENS tokens are tracked in the database (FIFO): 1 valid token and MAX_TOKENS - 1 invalidated tokens

Important: no type checking has been implemented. If the client code works with tokens in string format, redis client
also needs to decode tokens in string format. If the formats don't match (e.g. bytes and strings), token validation
will fail. See example
"""

import secrets
import string
from typing import Iterable, Dict


class RedisTokenFIFO:
    def __init__(self, redis_client, fifo_size=2):
        self.redis_client = redis_client
        self.fifo_size = fifo_size

    async def add(self, key, element):
        await self.redis_client.rpush(key, element)
        if await self.redis_client.llen(key) > self.fifo_size:
            await self.redis_client.lpop(key)

    async def get_invalidated(self, key) -> Iterable:
        """Get the entire FIFO excluding the freshest element"""
        return await self.redis_client.lrange(key, 0, -2)

    async def get_valid(self, key) -> Iterable:
        """Get freshest element"""
        return (await self.redis_client.lrange(key, -1, -1))



class TokenManager:
    """Routines for token rotation and reuse detection"""

    status_messages = {
        -1: "Token reused",
        0: "Invalid token",
        1: "Valid token"
    }
    alphabet = string.ascii_letters + string.digits

    def __init__(self, fifo, token_length=32, callbacks: Dict[int, Callable] = None):
        """

        :param fifo:
        :param token_length:
        :param callbacks: binds callbacks to each of the statuses
        """
        self.token_length = token_length
        self.rotation = fifo
        self.callbacks = callbacks or {}
        invalid_keys = set(self.callbacks.keys) - set(self.status_messages.keys)
        if invalid_keys:
            raise ValueError(f"Invalid callback keys: {invalid_keys}")

    @classmethod
    def encode_token(cls, token):
        # Handle encoding for bytes-based Redis clients
        if isinstance(token, bytes):
            return token.decode()
        return token

    @classmethod
    def decode_token(cls, encoded_token) -> str:
        # Handle decoding for bytes-based Redis clients
        if isinstance(encoded_token, bytes):
            return encoded_token.decode()
        return encoded_token

    @classmethod
    def generate_token(cls, token_length=32):
        return ''.join(secrets.choice(cls.alphabet) for _ in range(token_length))

    @classmethod
    def status_message(cls, status_code):
        return cls.status_messages[status_code]

    @classmethod
    def is_valid_format(cls, token):
        return token is not None and token != ""

    async def issue_token(self, user_id):
        token = self.generate_token(self.token_length)
        await self.rotation.add(user_id, token)
        return token

    async def validate_token(self, user_id, token):
        if self.is_valid_format(token) and (await self.rotation.get_valid(user_id) == [token]):
            return 1
        elif token in (await self.rotation.get_invalidated(user_id)):
            return -1
        else:
            return 0

    async def revoke_token(self, user_id):
        await self.rotation.add(user_id, "")

    async def provide_token(self, user_id, token):
        """
        Actions triggered by token submission by the user.

        Args:
            self:
            user_id:
            token: token provided by the user

        Returns:

        """
        new_token = None
        status = await self.validate_token(user_id, token)
        if status == 1:
            new_token = await self.issue_token(user_id)
        elif status == -1:
            await self.revoke_token(user_id)

        await self._execute_callbacks[status]

        return new_token, status

    async def _execute_callback(self, status):
        callback = self.callback_manager.callbacks.get(status)
        if callback:
            await callback()

