from cryptography.fernet import Fernet
from .config import settings
import json

class SecureDict:
    def __init__(self, key: str):
        self._data = {}
        self._cipher = Fernet(key.encode())
    
    def __setitem__(self, key, value):
        json_str = json.dumps(value)
        encrypted_data = self._cipher.encrypt(json_str.encode())
        self._data[key] = encrypted_data
    
    def __getitem__(self, key):
        if key not in self._data:
            raise KeyError(key)
        encrypted_data = self._data[key]
        json_str = self._cipher.decrypt(encrypted_data).decode()
        return json.loads(json_str)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def pop(self, key, default=None):
        try:
            value = self[key]
            del self._data[key]
            return value
        except KeyError:
            if default is not None:
                return default
            raise