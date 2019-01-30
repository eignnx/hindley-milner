from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")
MISSING = object()


@dataclass
class Env(Generic[K, V]):
    locals: Dict[K, V] = field(default_factory=dict)
    parent: Optional[Env[K, V]] = None

    def __setitem__(self, key: K, value: V):
        self.locals[key] = value

    def __getitem__(self, key: K) -> V:
        res = self.locals.get(key, MISSING)
        if res is not MISSING:
            return res
        elif self.parent is not None:
            return self.parent[key]
        else:
            raise KeyError
