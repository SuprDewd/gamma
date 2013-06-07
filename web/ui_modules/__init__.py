import os
import glob
import importlib

modules = {}

for f in glob.glob(os.path.dirname(__file__) + '/*.py'):
    name = os.path.basename(f)[:-3]
    if name == '__init__':
        continue

    module = importlib.import_module('ui_modules.' + name)
    for k, v in module.__dict__.items():
        if k.endswith('Module'):
            exec('from %s import %s' % (name, k))  # ugh
            modules[k[:-len('Module')]] = v

