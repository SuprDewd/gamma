import os
import glob
import importlib

for f in glob.glob(os.path.dirname(__file__) + '/*.py'):
    name = os.path.basename(f)[:-3]
    if name == '__init__':
        continue

    module = importlib.import_module('handlers.' + name)
    for k, v in module.__dict__.items():
        if k.endswith('Handler'):
            exec('from %s import %s' % (name, k))  # ugh
