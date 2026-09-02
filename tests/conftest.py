import pathlib
import sys
import types


class _Decorator:
    def __call__(self, fn):
        return fn


class _Public:
    write = _Decorator()
    view = _Decorator()
    write.payable = _Decorator()


class _TreeMap:
    def __class_getitem__(cls, _item):
        return cls


fake = types.ModuleType("genlayer")
fake.gl = types.SimpleNamespace(public=_Public(), Contract=object)
fake.u256 = int
fake.Address = str
fake.TreeMap = _TreeMap
fake.__all__ = ["gl", "u256", "Address", "TreeMap"]
sys.modules.setdefault("genlayer", fake)
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "contracts"))
