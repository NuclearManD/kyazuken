from klang import *
import klib

class KyazukenEnvironment:
    def __init__(self, functions, classes):
        self.functions = functions
        self.classes = classes

    def get_function(self, name, argtypes):

        s = name_and_argtypes_to_signature(name, argtypes)

        if not s in self.functions.keys():
            raise KyazukenError("Did not find function '" + name + '\' accepting arguments ' + str(argtypes))
        else:
            f = self.functions[s]

        return f

    def get_class(self, name):
        return self.classes[name]

VarDec = VariableDeclaration

class KyazukenDocument:
    def __init__(self, entry = None):
        self.functions = {}
        self.classes = {}
        self.entry = None
    def execute(self, environment, argv = []):
        if len(self.entry.args) == 1:
            self.entry.call(environment, [ArrayObject('String', argv)])
        else:
            self.entry.call(environment, [])

    def make_default_env(self):

        # Set up base environment
        functions = {}
        klib.add_functions(functions)

        # Add user functions
        functions.update(self.functions)

        # Create the environment
        return KyazukenEnvironment(functions, self.classes)

def elaborate_ast(ast):
    doc = KyazukenDocument()

    for i in ast:
        if type(i) == Function:
            if i.signature() in ['_Z4mainEPp6String', '_Z4mainEPp6String', '_Z4mainEP']:
                # main function
                doc.entry = i
            else:
                doc.functions[i.signature()] = i
        elif type(i) in [ClassDefinition, ClassInheriting]:
            doc.classes[i.name] = i

    return doc
