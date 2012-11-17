# Copyright 2012 Christoph Reiter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import types

_overrides = []
_active_module = []


def load(namespace, module):
    global _active_module, _overrides

    # look away now
    p = sys.path
    sys.path = [os.path.dirname(__file__)]
    _active_module.append(module)
    _overrides.append({})
    try:
        override_module = __import__(namespace, globals())
    except ImportError:
        pass
    else:
        # inject a module copy into the override module that
        # has the original classes for all overriden ones
        # so the classes can access the bases at runtime
        module_copy = types.ModuleType("")
        module_copy.__dict__.update(module.__dict__)
        for name, klass in _overrides[-1].iteritems():
            setattr(module_copy, name, klass)
        vars(override_module)[namespace] = module_copy

    _active_module.pop(-1)
    _overrides.pop(-1)
    sys.path = p


def duplicate(klass, name):
    global _active_module
    module = _active_module[-1]

    assert not hasattr(module, name)
    setattr(module, name, klass)


def override(klass):
    global _active_module, _overrides
    module = _active_module[-1]

    # FIXME: hack
    if hasattr(klass, "_is_function"):
        def wrap(wrapped):
            setattr(module, klass.__class__.__name__, wrapped)
            return wrapped
        return wrap

    old_klass = klass.__mro__[1]
    name = old_klass.__name__
    klass.__name__ = name
    klass.__module__ = old_klass.__module__

    assert getattr(module, name) is old_klass

    setattr(module, name, klass)
    _overrides[-1][name] = old_klass

    return klass
