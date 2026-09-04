import base64
import hashlib
import hmac
import secrets
import struct
import time


def generate_secret() -> str:
	return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _counter_bytes(counter: int) -> bytes:
	return struct.pack(">Q", counter)


def verify_code(secret: str, code: str, window: int = 1) -> bool:
	if not code.isdigit() or len(code) != 6:
		return False
	padded_secret = secret + "=" * (-len(secret) % 8)
	try:
		key = base64.b32decode(padded_secret, casefold=True)
	except ValueError:
		return False
	current_counter = int(time.time()) // 30
	for offset in range(-window, window + 1):
		digest = hmac.new(
			key,
			_counter_bytes(current_counter + offset),
			hashlib.sha1,
		).digest()
		index = digest[-1] & 0x0F
		value = struct.unpack(">I", digest[index:index + 4])[0] & 0x7FFFFFFF
		expected = f"{value % 1_000_000:06d}"
		if hmac.compare_digest(expected, code):
			return True
	return False


def provisioning_uri(secret: str, email: str) -> str:
	return (
		"otpauth://totp/KARYA%20AI:"
		f"{email}?secret={secret}&issuer=KARYA%20AI"
	)
