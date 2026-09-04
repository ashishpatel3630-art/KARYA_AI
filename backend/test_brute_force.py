import asyncio

from app.security.brute_force import (
    is_login_blocked,
    record_failed_login,
    reset_failed_logins,
)


async def main():

    identifier = "test@example.com"

    await reset_failed_logins(identifier)

    print("Initial blocked:", await is_login_blocked(identifier))

    for i in range(5):
        attempts = await record_failed_login(identifier)

        print(
            f"Failed attempt {i + 1}: {attempts}"
        )

    print(
        "After 5 attempts:",
        await is_login_blocked(identifier),
    )

    await reset_failed_logins(identifier)

    print(
        "After reset:",
        await is_login_blocked(identifier),
    )


if __name__ == "__main__":
    asyncio.run(main())