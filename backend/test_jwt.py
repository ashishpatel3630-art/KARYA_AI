from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


user_id = "123"


access_token = create_access_token(user_id)
refresh_token, _, _, _ = create_refresh_token(user_id)


print("ACCESS TOKEN:")
print(access_token)

print("\nREFRESH TOKEN:")
print(refresh_token)


print("\nACCESS PAYLOAD:")
print(decode_token(access_token))

print("\nREFRESH PAYLOAD:")
print(decode_token(refresh_token))