import asyncio
import aioredis

from token_refresh.handlers import TokenHandler, RedisTokenFIFO
from configuration import env


async def main():
    async_client = await aioredis.from_url(
        f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}/{env.REDIS_DB}",
        decode_responses=True   # This is important
    )
    token_handler = TokenHandler(RedisTokenFIFO(async_client))

    # Issue a token for a user
    user_id = 123
    issued_token = await token_handler.issue_token(user_id)
    print("Issued token:", issued_token)

    # Validate a token
    status = await token_handler.validate_token(user_id, issued_token)
    print(f"Checking validity for {issued_token}:", token_handler.status_messages[status])

    new_token, status = await token_handler.provide_token(user_id, issued_token)
    print(f"Provided the token {issued_token}: {token_handler.status_messages[status]}. Newly issued token: {new_token}")

    new_token, status = await token_handler.provide_token(user_id, issued_token)
    print(f"Provided the token {issued_token}: {token_handler.status_messages[status]}. Newly issued token: {new_token}")

    await async_client.close()


if __name__ == '__main__':
    asyncio.run(main())
