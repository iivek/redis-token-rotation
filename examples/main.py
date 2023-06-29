import asyncio
import aioredis

from token_refresh.redis_token_fifo import RedisTokenFIFO
from token_refresh.token_manager import TokenManager
from configuration import env


async def main():
    print(f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}/{env.REDIS_DB}")
    async_client = await aioredis.from_url(
        f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}/{env.REDIS_DB}"
    )
    token_handler = TokenManager(RedisTokenFIFO(async_client))

    # Issue a token for a user
    user_id = 123
    issued_token = await token_handler.issue_token(user_id)
    print("Issued token:", issued_token)

    # Validate a token
    status = await token_handler.validate_token(user_id, issued_token)
    print(f"Checking validity for {issued_token}:", token_handler.status_messages[status])

    # User provides a token that's valid
    new_token, status = await token_handler.receive_token(user_id, issued_token)
    print(f"User provided the token {issued_token}: {token_handler.status_messages[status]}. Auth service issued a new token: {new_token}")

    # User attempts to provide a token that is no longer valid due to token rotation
    new_token, status = await token_handler.receive_token(user_id, issued_token)
    print(f"User provided the token {issued_token}: {token_handler.status_messages[status]}. Auth service issued a new token: {new_token}")

    await async_client.close()


if __name__ == '__main__':
    asyncio.run(main())
