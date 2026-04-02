from jose import jwt
import os

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default_key')

def encrpypt_message(message: str) -> str:
	return jwt.encode({"message": message}, ENCRYPTION_KEY, algorithm="HS256")

def decrypt_message(token: str) -> str:
	try:
		payload = jwt.decode(token, ENCRYPTION_KEY, algorithms=["HS256"])
		return payload.get("message", "")
	except jwt.JWTError:
		return ""