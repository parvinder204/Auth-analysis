import hashlib
import os
from typing import Optional


class UserStore:
    def __init__(self):
        self._users: dict[str, dict] = {}
        self._id_counter = 1

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def create_user(self, username: str, password: str) -> dict:
        salt = os.urandom(16).hex()
        hashed = self._hash_password(password, salt)

        user = {
            "id": self._id_counter,
            "username": username,
            "password_hash": hashed,
            "salt": salt,
            "email": f"{username}@example.com",
        }

        self._users[username] = user
        self._id_counter += 1
        return {"id": user["id"], "username": user["username"], "email": user["email"]}

    def get_user(self, username: str) -> Optional[dict]:
        return self._users.get(username)

    def verify_password(self, username: str, password: str) -> bool:
        user = self.get_user(username)
        if not user:
            return False
        expected = self._hash_password(password, user["salt"])
        return expected == user["password_hash"]

    def exists(self, username: str) -> bool:
        return username in self._users


user_store = UserStore()