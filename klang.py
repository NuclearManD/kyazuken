
op_to_opname = {
    '+' : 'ps',
    '-' : 'ng',
    '&' : 'ad',
    '*' : 'de',
    '~' : 'co',
    '/' : 'dv',
    '%' : 'rm',
    '|' : 'or',
    '^' : 'eo',
    '=' : 'aS',
    '+=' : 'pL',
    '-=' : 'mI',
    '*=' : 'mL',
    '/=' : 'dV',
    '%=' : 'rM',
    '&=' : 'aN',
    '|=' : 'oR',
    '^=' : 'eO',
    '<<' : 'ls',
    '>>' : 'rs',
    '<<=' : 'lS',
    '>>=' : 'rS',
    '==' : 'eq',
    '<' : 'lt',
    '>' : 'gt',
    '<=' : 'le',
    '>=' : 'ge',
    '!=' : 'ne',
    '!' : 'nt',
    '&&' : 'aa',
    '||' : 'oo',
    '++' : 'pp',
    '--' : 'mm',
    ',' : 'cm',
    '()' : 'cl',
    '[]' : 'ix',
    '?' : 'qu',
    ':' : 'it',
    'cast' : 'cv'
    }

def operator_and_argtype_to_signature(classname, op, argtype = None):
    s = '_ZN' + str(len(classname)) + classname + op_to_opname[op]
    s += 'P'

    if argtype != None:
        if type(argtype) == ArrayType:
            s += 'p' + str(len(argtype.basetype)) + argtype.basetype
        else:
            s += str(len(argtype)) + argtype

    return s
    

def name_and_argtypes_to_signature(name, argtypes):
    s = '_Z' + str(len(name)) + name + 'E'
    s += 'P'
    for i in argtypes:

        if type(i) == ArrayType:
            s += 'p' + str(len(i.basetype)) + i.basetype
        else:
            s += str(len(i)) + i

    return s

def class_and_argtypes_to_signature(name, argtypes):
    s = '_ZN' + str(len(name)) + name + 'C1E'
    s += 'P'
    for i in argtypes:

        if type(i) == ArrayType:
            s += 'p' + str(len(i.basetype)) + i.basetype
        else:
            s += str(len(i)) + i

    return s

def name_class_and_argtypes_to_signature(classname, name, argtypes):
    s = '_ZN' + str(len(classname)) + classname + str(len(name)) + name + 'E'
    s += 'P'
    for i in argtypes:

        if type(i) == ArrayType:
            s += 'p' + str(len(i.basetype)) + i.basetype
        else:
            s += str(len(i)) + i

    return s

class KyazukenError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

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
            raise KyazukenError(str(self) + " has no member " + name + " with arguments " + arg_types)

        return self.functions[sig]

    def add_function(self, f):
        self.functions[f.signature()] = f

        # Tell the function it belongs to a class
        f.this = self

class ImportStatement:
    def __init__(self, path, commonname):
        self.commonname = commonname
        self.path = path

class Store:
    def __init__(self, obj, expr):
        self.obj = obj
        self.expr = expr

    def execute(self, context):
        t, v = self.expr.eval(context)

        return self.obj.assign(context, t, v)
    

class Constructor:
    def __init__(self, name, args, statements):
        self.name = name
        self.args = args
        self.statements = statements
    def signature(self):
        return class_and_argtypes_to_signature(self.name, [i.type for i in self.args])

    def call(self, environment, arguments):

        argdict = {}
        argtypes = {}
        for i in self.args:
            argdict[i.name] = arguments.pop(0)
            argtypes[i.name] = i.type

        context = Context(environment, argtypes, argdict)
        for i in self.statements:
            i.execute(context)

    def head_str(self):
        return self.name + '(' + ', '.join([str(i) for i in self.args]) + ')'

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

class NewObject:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def eval(self, context):
        _class = context.get_class(self.name)

        args = [i.eval(context) for i in self.args]

        f = _class.get_constructor([i[0] for i in args])
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
            raise KyazukenError('Invalid expression for if block: must evaluate to a bool')
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
            raise KyazukenError('Invalid expression for if/else block: must evaluate to a bool')
        if ev:
            return self.statement.execute(context)
        else:
            return self.else_statement.execute(context)

class WhileBlock:
    def __init__(self, condition, statement):
        self.condition = condition
        self.statement = statement
    def execute(self, context):
        while True:
            et, ev = self.iterable.eval(context)

            if et != 'bool':
                raise KyazukenError('Invalid expression for while block: must evaluate to a bool')
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

            mini_context = Context(context, {self.vardec.name: self.vardec.type}, {self.vardec.name: val})

            v = self.statement.execute(mini_context)
            if v != None:
                return v

class CForBlock:
    def __init__(self, loop_init, loop_condition, loop_end, loop_code):
        self.loop_init = loop_init
        self.loop_condition = loop_condition
        self.loop_end = loop_end
        self.loop_code = loop_code
    def execute(self, context):

        loop_context = Context(context, {}, {})

        v = self.loop_init(loop_context)
        if v != None:
            return v
        
        while True:
            et, ev = self.loop_condition.eval(loop_context)

            if et != 'bool':
                raise KyazukenError('Invalid expression for a for block: must evaluate to a bool')
            if not ev:
                break

            v = self.loop_code.execute(loop_context)
            if v != None:
                return v

            self.loop_end.eval(loop_context)

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

    def getitem(self, i):
        return self.type, self.data[i]

    def setitem(self, i, _type, value):
        if _type == self.type:
            self.data[i] = value
        else:
            raise KyazukenError("Cannot assign " + str(_type) + " to " + str(ArrayType(self.type)))
    

class VariableDeclaration:
    def __init__(self, name, _type):
        self.name = name
        self.type = _type

    def __str__(self):
        return str(self.type) + ' ' + self.name

class VariableDefinition:
    def __init__(self, name, _type, value_expr):
        self.name = name
        self.type = _type
        self.expr = value_expr

    def execute(self, context):
        t, v = self.expr.eval(context)

        if t != self.type:
            raise KyazukenError('Attempted to assign a ' + str(t) + ' to new variable of type ' + str(self.type))
        context.mkvar(self.name, t, v)

class Subscript:
    def __init__(self, src, idx):
        self.src = src
        self.idx = idx

    def eval(self, context):
        st, sv = self.src.eval(context)
        it, iv = self.idx.eval(context)

        if not it.startswith('int'):
            raise KyazukenError("Failed: attempted subscript of " + str(self.src) + ' using type ' + str(it))

        return sv.getitem(iv)

    def assign(self, context, _type, val):
        st, sv = self.src.eval(context)
        it, iv = self.idx.eval(context)

        if not it.startswith('int'):
            raise KyazukenError("Failed: attempted subscript of " + str(self.src) + ' using type ' + str(it))

        return sv.setitem(context, iv, _type, val)

class Variable:
    def __init__(self, name):
        self.name = name

    def eval(self, context):
        return context.getvar(self.name)

    def get_function(self, context, argtypes):
        return context.get_function(self.name, argtypes)

    def assign(self, context, _type, val):
        return context.setvar(self.name, _type, val)

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
            raise KyazukenError("Invalid operation: " + str(ta) + ' ' + self.op + ' ' + str(tb))

class UniOp:
    def __init__(self, left, op):
        self.left = left
        self.op = op
        assert op in ['!', '-']

    def eval(self, context):
        et, ev = self.left.eval(context)

        if self.op == '!':
            ev = not ev
        elif self.op == '-':
            ev = -ev

        return et, ev

class PreIncDec:
    def __init__(self, obj, op):
        self.obj = obj
        self.op = op
        assert op in ['++', '--']

    def eval(self, context):
        et, ev = self.obj.eval(context)

        if self.op == '--':
            ev = ev - 1
        elif self.op == '++':
            ev = ev + 1

        self.obj.assign(context, et, ev)

        return et, ev

class PostIncDec:
    def __init__(self, obj, op):
        self.obj = obj
        self.op = op
        assert op in ['++', '--']

    def eval(self, context):
        et, ev = self.obj.eval(context)

        if self.op == '--':
            evn = ev - 1
        elif self.op == '++':
            evn = ev + 1

        self.obj.assign(context, et, evn)

        return et, ev

class Return:
    def __init__(self, val = None):
        self.val = val
    def execute(self, context):
        if self.val != None:
            return self.val.eval(context)
        else:
            return None, None

class NoOperation:
    def execute(self, context):
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
        self._class = None
    def signature(self):
        argtypes = [i.type for i in self.args]

        if self._class == None:
            return name_and_argtypes_to_signature(self.name, argtypes)
        else:
            return name_class_and_argtypes_to_signature(self._class.name, self.name, argtypes)

    def call(self, environment, arguments):

        argdict = {}
        argtypes = {}
        for i in self.args:
            argdict[i.name] = arguments.pop(0)
            argtypes[i.name] = i.type

        context = Context(environment, argtypes, argdict)
        for i in self.statements:
            i.execute(context)

class OperatorOverload(Function):
    def __init__(self, op, rettype, statements, arg = None):
        super().__init__(None, rettype, [] if arg is None else [arg], statements)

        self.op = op
        self.arg = arg
    def signature(self):
        return operator_and_argtype_to_signature(self._class.name, self.op, self.arg)

class ClassDefinition:
    def __init__(self, name, items):
        self.name = name
        self._handle_items(items)

    def _handle_items(self, items):
        name = self.name
        con = {}
        func = {}
        var = {}
        for i in items:
            if isinstance(i, VariableDeclaration) or isinstance(i, VariableDefinition):
                var[i.name] = i
            elif isinstance(i, Constructor):
                if i.name != name:
                    raise ValueError("Constructor name is {} but class name is {}".format(i.name, name))
                con[i.signature()] = i

                # set class for constructor so it can find it later
                i._class = self

            elif isinstance(i, Function):
                i._class = self
                func[i.signature()] = i
            else:
                raise Exception("INTERNAL ERROR: " + str(i))
        self.con = con
        self.func = func
        self.vars = var

    def get_constructor(self, argtypes):
        s = class_and_argtypes_to_signature(self.name, argtypes)

        if not s in self.con.keys():
            msg = 'No constructor for class ' + self.name + ' matches argument types ' + str(argtypes) + '\n'
            if len(self.con.keys()) == 0:
                msg += "This class does not have any constructors."
            else:
                msg += 'Note: available constructors:\n'
                for i in self.con.values():
                    msg += '  ' + i.head_str() + '\n'

            raise KyazukenError(msg)

        return self.con[s]

    def __str__(self):
        s = 'class ' + self.name + ' {\n'
        for i in self.vars.values():
            s += '\t' + str(i) + ';\n'
        s += '\n'
        for i in self.con.values():
            s += '\t' + str(i) + '\n'
        s += '\n'
        for i in self.func.values():
            s += '\t' + str(i) + '\n'
        return s + '}\n'

class ClassInheriting(ClassDefinition):
    def __init__(self, name, items, inherited):
        self.name = name
        self._handle_items(items)

    def __str__(self):
        s = 'class ' + self.name + ' extends ' + self.inherited + ' {\n'
        for i in self.vars.values():
            s += '\t' + str(i) + ';\n'
        s += '\n'
        for i in self.con.values():
            s += '\t' + str(i) + '\n'
        s += '\n'
        for i in self.func.values():
            s += '\t' + str(i) + '\n'
        return s + '}\n'


class PyFunctionWrapper(Function):
    def __init__(self, name, rettype, args, f):
        super().__init__(name, rettype, args, None)
        self.f = f
    def call(self, env, args):
        return self.rettype, self.f(*args)

class Context:
    def __init__(self, env, var_types, var):
        self.vars = var
        self.var_types = var_types
        self.env = env

    def getvar(self, name):
        if not name in self.vars.keys():
            raise KyazukenError('Variable \'' + name + '\' does not exist.')

        return self.var_types[name], self.vars[name]

    def setvar(self, name, _type, val):
        if not name in self.vars.keys():
            raise KyazukenError('Variable \'' + name + '\' does not exist.')

        if self.var_types[name] != _type:
            msg = f'Attempted to assign value of type {_type} to variable of type {self.var_types[name]}'
            raise KyazukenError(msg)

        self.vars[name] = val

    def mkvar(self, vartype, varname, value):
        self.vars[varname] = value
        self.var_types[name] = vartype

    def get_function(self, name, argtypes):
        return self.env.get_function(name, argtypes)

    def get_class(self, name):
        return self.env.get_class(name)
