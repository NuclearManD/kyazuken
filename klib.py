
from klang import KyazukenObject, PyFunctionWrapper
from klang import VariableDeclaration as Arg

class KyazukenFile(KyazukenObject):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.add_function(PyFunctionWrapper('readline', 'String', [], base.readline))
        self.add_function(PyFunctionWrapper('write', 'String', [], base.write))

def _fopen_base(name, mode):
    return KyazukenFile(open(name, mode))

default_functions = [
    PyFunctionWrapper('fopen', 'File', [Arg('path', 'String'), Arg('mode', 'String')], _fopen_base),
    PyFunctionWrapper('println', 'void', [Arg('s', 'String')], print)
    ]
    

def add_functions(func_dict : dict):
    for i in default_functions:
        func_dict[i.signature()] = i
