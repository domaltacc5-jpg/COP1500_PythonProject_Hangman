import datamuse
import inspect
from datamuse import Datamuse

api = Datamuse()

print("Imported from:", datamuse.__file__)
print("Datamuse version:", getattr(datamuse, "__version__", "Unknown"))
print("Method signature:", inspect.signature(api.words))

print(api.words(rel_rhy="orange", max=5))