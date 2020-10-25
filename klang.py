
class KyazukenClass:
    def __init__(self, name):
        self.name = name

class KyazukenEntryPoint:
    def __init__(self, lines):
        self.lines = lines

class KyazukenObject:
    def __init__(self, val):
        self._val = val
    def resolve(self):
        return self._val

class Literal:
    def __init__(self, _type: str, value):
        self.type = _type
        self.value = value

    def eval(self, env):
        return self.type, self.value

    def get_type(self):
        return self.type

class FunctionCall:
    def __init__(self, name : str, args : tuple):
        self.name = name
        self.args = args
    def execute(self, context):
        args = [i.eval(context) for i in self.args]
        context.call(self.name.name, 'void', [i[0] for i in args], [i[1] for i in args])


class IfBlock:
    def __init__(self, condition, lines):
        self.condition = condition
        self.lines = lines
    def execute(self, context):
        et, ev = self.condition.eval(context)
        if et != 'bool':
            raise Exception('Invalid expression for if block')
        if ev:
            for i in self.lines:
                i.execute(context)

class WhileBlock:
    def __init__(self, condition, lines):
        self.condition = condition
        self.lines = lines

class ExitBlock:
    def __init__(self, code):
        self.code = code

class ArrayType:
    def __init__(self, basetype):
        self.basetype = basetype

class ArrayObject:
    def __init__(self, basetype, data):
        self.type = basetype
        self.data = data

class VariableDeclaration:
    def __init__(self, name, _type):
        self.name = name
        self.type = _type

class Variable:
    def __init__(self, name):
        self.name = name

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def eval(self, context):
        ta, a = self.left.eval(context)
        tb, b = self.right.eval(context)
        if tb.startswith('int') and tb.startswith('int'):
            if self.op == '/':
                return ta, a // b
            elif self.op == '&':
                return ta, a & b
            elif self.op == '|':
                return ta, a | b
            elif self.op == '^':
                return ta, a ^ b
        if self.op == '+':
            return ta, a + b
        elif self.op == '-':
            return ta, a - b
        elif self.op == '*':
            return ta, a * b
        elif self.op == '/':
            return ta, a / b
        elif self.op == '%':
            return ta, a % b
        elif self.op == '==':
            return 'bool', a == b
        else:
            raise Exception("Invalid operation")

class Function:
    def __init__(self, name, rettype, args, statements):
        self.name = name
        self.rettype = rettype
        self.args = args
        self.statements = statements
    def signature(self):
        s = '_Z' + str(len(self.name)) + self.name + 'E'
        s += 'P'
        for i in self.args:
            i = i.type

            if type(i) == ArrayType:
                s += 'p' + str(len(i.basetype)) + i.basetype
            else:
                s += str(len(i)) + i

        s += 'R' + str(len(self.rettype)) + self.rettype

        return s

    def call(self, environment, arguments):

        argdict = {}
        for i in self.args:
            argdict[i.name] = arguments.pop(0)

        context = Context(environment, argdict)
        for i in self.statements:
            i.execute(context)


class PyFunctionWrapper(Function):
    def __init__(self, name, rettype, args, f):
        self.name = name
        self.rettype = rettype
        self.args = args
        self.f = f
    def call(self, env, args):
        self.f(*args)

class Context:
    def __init__(self, env, var):
        self.vars = var
        self.env = env
    def getvar(self, name):
        return self.vars[name]
    def setvar(self, name, val):
        if not name in self.vars.keys():
            raise Exception('Variable ' + name + ' does not exist.')
        self.vars[name] = val
    def mkvar(self, varname, value):
        self.vars[varname] = value
    def call(self, name, expect_rettype, argtypes, argvals):
        return self.env.call(self, name, expect_rettype, argtypes, argvals)

class KyazukenEnvironment:
    def __init__(self, functions):
        self.functions = functions
    def call(self, environment, name, expect_rettype, argtypes, argvals):

        # first figure out the function signature
        s = '_Z' + str(len(name)) + name + 'E'
        s += 'P'
        for i in argtypes:
            if type(i) == ArrayType:
                s += 'p' + str(len(i.basetype)) + i.basetype
            else:
                s += str(len(i)) + i

        s_r = s + 'R' + str(len(expect_rettype)) + expect_rettype

        if not s_r in self.functions.keys():
            candidates = []
            for i in self.functions.keys():
                if i.startswith(s):
                    candidates.append(i)

            if expect_rettype == 'void':
                if len(candidates) > 1:
                    raise Exception("Too many candidates for " + name)
                elif len(candidates) == 0:
                    raise Exception("No function matches requested " + name)
                else:
                    f = self.functions[candidates[0]]
            elif expect_rettype.startswith('int'):

                int_candidates = []
                for i in candidates:
                    i = self.functions[i]
                    if i.rettype in ['int', 'int8', 'int16', 'int32', 'int64']:
                        int_candidates.append(i)

                if len(int_candidates) > 1:
                    raise Exception("Too many candidates for " + name)
                elif len(int_candidates) == 0:
                    raise Exception("No function matches requested " + name)
                else:
                    f = int_candidates[0]
            elif expect_rettype.startswith('uint'):

                uint_candidates = []
                for i in candidates:
                    i = self.functions[i]
                    if i.rettype in ['uint', 'uint8', 'uint16', 'uint32', 'uint64']:
                        uint_candidates.append(i)

                if len(uint_candidates) > 1:
                    raise Exception("Too many candidates for " + name)
                elif len(uint_candidates) == 0:
                    raise Exception("No function matches requested " + name)
                else:
                    f = uint_candidates[0]
            elif expect_rettype.startswith('float'):

                float_candidates = []
                for i in candidates:
                    i = self.functions[i]
                    if i.rettype.startswith('float'):
                        float_candidates.append(i)

                if len(float_candidates) > 1:
                    raise Exception("Too many candidates for " + name)
                elif len(float_candidates) == 0:
                    raise Exception("No function matches requested " + name)
                else:
                    f = float_candidates[0]
            raise Exception("Function not found " + s)
        else:
            f = self.functions[s_r]

        return f.call(environment, argvals)

class KyazukenDocument:
    def __init__(self, entry = None):
        self.functions = {}
        self.classes = {}
        self.entry = None
    def execute(self, environment):
        if len(self.entry.args) == 1:
            self.entry.call(environment, [ArrayObject('String', [])])
        else:
            self.entry.call(environment, [])

def elaborate_ast(ast):
    doc = KyazukenDocument()

    for i in ast:
        if type(i) == Function:
            if i.signature() in ['_Z4mainEPp6StringR4void', '_Z4mainEPp6StringR5int32', '_Z4mainEPR4void']:
                # main function
                doc.entry = i
            else:
                doc.functions[i.signature()] = i

    return doc
