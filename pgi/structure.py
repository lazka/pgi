# Copyright 2012 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

from ctypes import cast

from pgi.gir import GIStructInfoPtr, GIFunctionInfoFlags
from pgi.obj import _ClassMethodAttribute
from pgi.gtype import PGType


class _Structure(object):
    """Class template for structures."""

    _obj = None  # the address of the struct
    __gtype__ = None  # the gtype

    def __init__(self, *args, **kwargs):
        raise TypeError


def StructureAttribute(info, namespace, name, lib):
    """Creates a new struct class."""

    struct_info = cast(info, GIStructInfoPtr)

    # copy the template and add the gtype
    cls_dict = dict(_Structure.__dict__)
    cls_dict["__gtype__"] = PGType(struct_info.get_g_type())

    # create a new class
    cls = type(name, _Structure.__bases__, cls_dict)
    cls.__module__ = namespace

    # add methods
    for i in xrange(struct_info.get_n_methods()):
        func_info = struct_info.get_method(i)
        func_flags = func_info.get_flags()

        if func_flags.value == GIFunctionInfoFlags.IS_METHOD:
            method_name = func_info.get_name()
            attr = _ClassMethodAttribute(func_info, method_name, lib)
            setattr(cls, method_name, attr)
        else:
            func_info.unref()

    return cls
