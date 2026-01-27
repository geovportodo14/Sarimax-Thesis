import sys
import importlib

packages = ['numpy', 'pandas', 'sklearn', 'tensorflow']
missing = []

for pkg in packages:
    try:
        importlib.import_module(pkg)
        print(f"{pkg} is installed")
    except ImportError:
        missing.append(pkg)
        print(f"{pkg} is MISSING")

if missing:
    sys.exit(1)
else:
    sys.exit(0)
