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
        self.imports = []
    def execute(self, environment, argv = []):
        if len(self.entry.args) == 1:
            self.entry.call(environment, [ArrayObject('String', argv)])
        else:
            self.entry.call(environment, [])

    def update_dicts(self, funcs, classes):
        funcs.update(self.functions)
        classes.update(self.classes)

    def make_default_env(self):

        # Set up base environment
        functions = {}
        classes = {}
        klib.add_functions(functions)

        # Add functions and classes from imported files
        for i in self.imports:
            i.update_dicts(functions, classes)

        # Add functions and classes from this document
        self.update_dicts(functions, classes)

        # Create the environment
        return KyazukenEnvironment(functions, classes)

    def add_imported_document(self, imported):
        self.imports.append(imported)
