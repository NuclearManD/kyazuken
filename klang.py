
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
    def __init__(self, _type: str, value : KyazukenObject):
        self.type = _type
        self.value = value

    def eval(self):
        return self.value

    def get_type(self):
        return self.type

class FunctionCall:
    def __init__(self, name : str, args : tuple):
        self.name = name
        self.args = args

class IfBlock:
    def __init__(self, condition, lines):
        self.condition = condition
        self.lines = lines

class WhileBlock:
    def __init__(self, condition, lines):
        self.condition = condition
        self.lines = lines

class ExitBlock:
    def __init__(self, code):
        self.code = code
