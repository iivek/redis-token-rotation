import secrets
import string
from typing import Iterable, Dict, Callable


class TokenManager:
    """A concurrent mechanism for (refresh) token generation, rotation and reuse detection.
    Pass tokens and client_ids in string format.
    """

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
        invalid_keys = set(self.callbacks.keys()) - set(self.status_messages.keys())
        if invalid_keys:
            raise ValueError(f"Invalid callback keys: {invalid_keys}")

    @classmethod
    def generate_token(cls, token_length=32):
        return ''.join(secrets.choice(cls.alphabet) for _ in range(token_length))

    @classmethod
    def status_message(cls, status_code):
        return cls.status_messages[status_code]

    @classmethod
    def is_valid_format(cls, token: str):
        return token is not None and token != ""

    async def issue_token(self, user_id: str):
        """
        Issue a new token for the user_id.

        Args:
            user_id:

        Returns:

        """
        token = self.generate_token(self.token_length)
        await self.rotation.add(user_id, token)
        return token

    async def validate_token(self, user_id: str, token: str):
        if self.is_valid_format(token) and (await self.rotation.get_valid(user_id) == [token]):
            return 1
        elif token in (await self.rotation.get_invalidated(user_id)):
            return -1
        else:
            return 0

    async def revoke_token(self, user_id: str):
        await self.rotation.add(user_id, "")

    async def receive_token(self, user_id, token: str):
        """
        Token submission, from the user's side.

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

        await self._execute_callbacks(status)

        return new_token, status

    async def _execute_callbacks(self, status):
        callback = self.callbacks.get(status)
        if callback:
            await callback()

