import pkgutil, importlib as _ilb

def _auto_import():
    for mod in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
        try:
            _ilb.import_module(mod.name)
        except Exception as e:
            print("[tool:skip] {}: {}".format(mod.name, e))

_auto_import()