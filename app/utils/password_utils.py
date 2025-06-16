import re
from passlib.context import CryptContext
from zxcvbn import zxcvbn

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def validate_password(password: str) -> bool:
    if len(password) < 12:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[+#!?@$%^&*-]", password):
        return False

    # zxcvbn strength check (score 3 or 4 is strong)
    result = zxcvbn(password)
    if result["score"] < 3:
        return False
    return True

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password) 