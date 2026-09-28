# Theme preview
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class User:
    id: int
    name: str
    active: bool = True
    tags: set[str] = field(default_factory=set)

    def rename(self, name: str) -> None:
        if not name.strip():
            raise ValueError("empty name")
        self.name = name


class Repository:
    def __init__(self) -> None:
        self.users: dict[int, User] = {}

    def add(self, user: User) -> None:
        if user.id in self.users:
            raise KeyError(user.id)
        self.users[user.id] = user

    def active(self) -> list[User]:
        return [u for u in self.users.values() if u.active]

    def serialize(self) -> str:
        return json.dumps([u.__dict__ for u in self.active()])


async def main() -> None:
    repository = Repository()
    repository.add(User(1, "Alice", tags={"admin", "linux"}))
    repository.add(User(2, "Bob", False, {"guest"}))
    repository.add(User(3, "Carol", True, {"python", "async"}))

    await asyncio.sleep(0)
    data = repository.serialize()
    Path("users.json").write_text(data, encoding="utf-8")

    print(f"users={len(repository.active())}")
    print(data)


if __name__ == "__main__":
    asyncio.run(main())
