
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

class ImportStatement:
    def __init__(self, path):
        self.path = path

class Store:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def execute(self, context):
        t, v = self.expr.eval(context)
        context.setvar(self.name, v)

class Constructor:
    def __init__(self, name, args, statements):
        self.name = name
        self.args = args
        self.statements = statements
    def signature(self):
        s = '_Z' + str(len(self.name)) + self.name + 'C1E'
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

class IterForBlock:
    def __init__(self, vardec, iterable, lines):
        self.vardec = vardec
        self.iterable = iterable
        self.lines = lines
    def execute(self, context):
        et, ev = self.iterable.eval(context)
        while True:
            val = ev.iter()
            if val == None:
                return

            mini_context = Context(context, {self.vardec.name: val})

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

class VariableDefinition:
    def __init__(self, name, _type, value_expr):
        self.name = name
        self.type = _type
        self.expr = value_expr

class Subscript:
    def __init__(self, src, idx):
        self.src = src
        self.idx = idx

    def eval(self, context):
        st, sv = self.src.eval(context)
        it, iv = self.idx.eval(context)

        if not it.startswith('int'):
            raise Exception("Failed: attempted subscript of " + str(self.src) + ' using type ' + str(it))

        return sv[iv]

    def assign(self, context, _type, val):
        st, sv = self.src.eval(context)
        it, iv = self.idx.eval(context)

        if not it.startswith('int'):
            raise Exception("Failed: attempted subscript of " + str(self.src) + ' using type ' + str(it))

        return sv.assign_idx(context, iv, _type, val)

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

class UniOp:
    def __init__(self, left, op):
        self.left = left
        self.op = op
    def eval(self, context):
        et, ev = self.left.eval(context)

        if self.op == '!':
            ev = not ev
        elif self.op == '-':
            ev = -ev
        elif self.op == '--':
            ev = ev - 1
        elif self.op == '++':
            ev = ev + 1

        if self.op == '++' or self.op == '--':
            self.left.assign(context, et, ev)

        return et, ev

class Return:
    def __init__(self, val = None):
        self.val = val
    def execute(self, context):
        if self.val != None:
            return self.val.eval(context)
        else:
            return None, None

class Member:
    def __init__(self, src, sub):
        self.src = src
        self.sub = sub
    def eval(self, context):
        et, ev = self.src.eval(context)

        return ev.sub(self.sub)
    def assign(self, context, _type, val):
        et, ev = self.src.eval(context)

        ev.assign_sub(context, self.sub, _type, val)

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

class ClassDefinition:
    def __init__(self, name, items):
        self.name = name
        con = []
        func = []
        var = []
        for i in items:
            if isinstance(i, VariableDeclaration):
                var.append(i)
            elif isinstance(i, Constructor):
                if i.name != name:
                    raise ValueError("Constructor name is {} but class name is {}".format(i.name, name))
                con.append(i)
            elif isinstance(i, Function):
                i.args.insert(0, VariableDeclaration('this', ObjectType(name)))
                func.append(i)
        self.con = con
        self.func = func
        self.vars = var
        self.compiled = False

    def __str__(self):
        s = 'class ' + self.name + ' {\n'
        for i in self.vars:
            s += '\t' + str(i) + ';\n'
        s += '\n'
        for i in self.con:
            s += '\t' + str(i) + '\n'
        s += '\n'
        for i in self.func:
            s += '\t' + str(i) + '\n'
        return s + '}\n'

class ClassInheriting:
    def __init__(self, name, items, inherited):
        self.name = name
        con = []
        func = []
        var = []
        for i in items:
            if isinstance(i, VariableDeclaration):
                var.append(i)
            elif isinstance(i, Constructor):
                if i.name != name:
                    raise ValueError("Constructor name is {} but class name is {}".format(i.name, name))
                con.append(i)
            elif isinstance(i, Function):
                i.args.insert(0, VariableDeclaration('this', ObjectType(name)))
                func.append(i)
        self.con = con
        self.func = func
        self.vars = var
        self.inherited = inherited
        self.compiled = False

    def __str__(self):
        s = 'class ' + self.name + ' extends ' + self.inherited + ' {\n'
        for i in self.vars:
            s += '\t' + str(i) + ';\n'
        s += '\n'
        for i in self.con:
            s += '\t' + str(i) + '\n'
        s += '\n'
        for i in self.func:
            s += '\t' + str(i) + '\n'
        return s + '}\n'


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
