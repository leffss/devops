from django.conf import settings
from cryptography.fernet import Fernet


key = settings.CRYPTOGRAPHY_TOKEN.encode()


def encrypt(s):
    if s:
        f = Fernet(key)
        return f.encrypt(s.encode()).decode()
    return ''


def decrypt(s):
    if s:
        f = Fernet(key)
        return f.decrypt(s.encode()).decode()
    return ''
