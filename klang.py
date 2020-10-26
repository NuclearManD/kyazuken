
def name_and_argtypes_to_signature(name, argtypes):
    s = '_Z' + str(len(name)) + name + 'E'
    s += 'P'
    for i in argtypes:

        if type(i) == ArrayType:
            s += 'p' + str(len(i.basetype)) + i.basetype
        else:
            s += str(len(i)) + i

    return s

class KyazukenClass:
    def __init__(self, name):
        self.name = name

class KyazukenEntryPoint:
    def __init__(self, lines):
        self.lines = lines

class KyazukenObject:
    def __init__(self):
        self.functions = {}

    def get_function(self, context, name, arg_types):
        sig = name_and_argtypes_to_signature(name, arg_types)

        if not sig in self.functions:
            raise Exception(str(self) + " has no member " + name + " with arguments " + arg_types)

        return self.functions[sig]

    def add_function(self, f):
        self.functions[f.signature()] = f

        # Tell the function it belongs to a class
        f.this = self

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
    def __init__(self, func, args : tuple):
        self.func = func
        self.args = args

    def eval(self, context):
        args = [i.eval(context) for i in self.args]

        f = self.func.get_function(context, [i[0] for i in args])
        return f.call(context, [i[1] for i in args])

    def execute(self, context):
        self.eval(context)

class StatementList:
    def __init__(self, statements):
        self.statements = statements

    def execute(self, context):
        for i in self.statements:
            v = i.execute(context)

            if v != None:
                return v

class IfBlock:
    def __init__(self, condition, statement):
        self.condition = condition
        self.statement = statement
    def execute(self, context):
        et, ev = self.condition.eval(context)
        if et != 'bool':
            raise Exception('Invalid expression for if block')
        if ev:
            return self.statement.execute(context)

class IfElseBlock:
    def __init__(self, condition, statement, else_statement):
        self.condition = condition
        self.statement = statement
        self.else_statement = else_statement

    def execute(self, context):
        et, ev = self.condition.eval(context)
        if et != 'bool':
            raise Exception('Invalid expression for if block')
        if ev:
            return self.statement.execute(context)
        else:
            return self.else_statement.execute(context)

class WhileBlock:
    def __init__(self, condition, lines):
        self.condition = condition
        self.lines = lines
    def execute(self, context):
        while True:
            et, ev = self.iterable.eval(context)

            if et != 'bool':
                raise Exception('Invalid expression for if block')
            if not ev:
                break

            v = self.statement.execute(context)
            if v != None:
                return v

class IterForBlock:
    def __init__(self, vardec, iterable, statement):
        self.vardec = vardec
        self.iterable = iterable
        self.statement = statement
    def execute(self, context):
        et, ev = self.iterable.eval(context)
        while True:
            val = ev.iter()
            if val == None:
                return

            mini_context = Context(context, {self.vardec.name: val})

            v = self.statement.execute(context)
            if v != None:
                return v

class ExitBlock:
    def __init__(self, code):
        self.code = code

class ArrayType:
    def __init__(self, basetype):
        self.basetype = basetype

    def __str__(self):
        return str(self.basetype) + '[]'

class ArrayObject(KyazukenObject):
    def __init__(self, basetype, data):
        super().__init__()

        self.type = basetype
        self.data = data

        # Add functions
        self.add_function(PyFunctionWrapper('length', 'int', [], self.length))

    def length(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]
    def setitem(self, i, _type, value):
        if _type == self.type:
            self.data[i] = value
        else:
            raise Exception("Cannot assign " + str(_type) + " to " + str(ArrayType(self.type)))
    

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

    def eval(self, context):
        return '', context.getvar(self.name)

    def get_function(self, context, argtypes):
        return context.get_function(self.name, argtypes)

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
        elif self.op == '!=':
            return 'bool', a != b
        else:
            raise Exception("Invalid operation: " + str(ta) + ' ' + self.op + ' ' + str(tb))

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
        else:
            raise Exception("Invalid operation: " + self.op + ' ' + str(et))

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

    def get_function(self, context, arg_types):
        et, ev = self.src.eval(context)
        return ev.get_function(context, self.sub, arg_types)

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
        return self.rettype, self.f(*args)

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

    def get_function(self, name, argtypes):
        return self.env.get_function(name, argtypes)

class KyazukenEnvironment:
    def __init__(self, functions):
        self.functions = functions

    def get_function(self, name, argtypes):

        s = name_and_argtypes_to_signature(name, argtypes)

        if not s in self.functions.keys():
            raise Exception("Did not find function '" + name + '\' accepting arguments ' + str(argtypes))
        else:
            f = self.functions[s]

        return f

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
            if i.signature() in ['_Z4mainEPp6String', '_Z4mainEPp6String', '_Z4mainEP']:
                # main function
                doc.entry = i
            else:
                doc.functions[i.signature()] = i

    return doc
