from app.core.security import (
    hash_password,
    verify_password,
)


password = "MyStrongPassword123!"

hashed = hash_password(password)

print("Original password:")
print(password)

print("\nArgon2 hash:")
print(hashed)

print("\nCorrect password:")
print(verify_password(password, hashed))

print("\nWrong password:")
print(verify_password("WrongPassword", hashed))