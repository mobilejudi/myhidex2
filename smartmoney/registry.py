# smartmoney/registry.py
import csv
from typing import Iterable

SMART_TAGS = {"KOL","SMART","MM"}

class SmartRegistry:
    def __init__(self):
        self._set = set()         # addresses lower
        self.alias = {}           # addr -> alias

    def add(self, addr: str, alias: str | None = None):
        a = addr.lower()
        self._set.add(a)
        if alias:
            self.alias[a] = alias

    def load_csv(self, path: str):
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                self.add(row["address"], row.get("alias"))

    def contains(self, addr: str) -> bool:
        return addr.lower() in self._set

registry = SmartRegistry()
