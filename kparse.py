from klang import *
import re

# Note the $ is not here - it can be used in symbol names.
# the " and ' is handled separately because they behave oddly
TOKEN_CHARS = "~!@#%^&*()[]{}-+=;:<>/?.,|"

# Operators that are multiple characters
DUALOPS = ['==','>=','<=','++','--','*=','/=','+=','-=','&=','|=','^=','%=','!=']

name_pattern = re.compile('[a-zA-Z$_][a-zA-Z$_0-9]*')

class KyazukenLexer:
    def __init__(self, file):
        self.file = file
        self.buffer = ''
        self.line_no = 0

    def _peek_token_raw(self):
        while len(self.buffer) == 0 or self.buffer.isspace():
            self.buffer = self.file.readline()
            self.line_no += 1
            if len(self.buffer) == 0:
                return None
            self.buffer = self.buffer.strip()

        tmp = ''
        instr = False
        inch = False
        for i in range(len(self.buffer)):
            c = self.buffer[i]
            if instr:
                # process string stuff
                tmp += c
                if c == '"':
                    instr = False
                    break
            elif inch:
                # process char stuff
                tmp += c
                if c == "'":
                    inch = False
                    break
            else:
                if c.isspace():
                    if tmp == '':
                        continue
                    else:
                        break
                elif c in TOKEN_CHARS:
                    if tmp != '':
                        i -= 1
                        break
                    if i + 1 < len(self.buffer):
                        op_test = c + self.buffer[i + 1]
                        if op_test in DUALOPS:
                            tmp = op_test
                            i += 1
                            break
                    tmp = c
                    break
                elif c == '"':
                    instr = True
                    tmp += c
                elif c == "'":
                    inch = True
                    tmp += c
                else:
                    tmp += c
        return tmp, i

    def get_next_token(self):
        tmp, i = self._peek_token_raw()
        self.buffer = self.buffer[i + 1:].strip()
        return tmp

    def peek_next_token(self):
        tmp, i = self._peek_token_raw()
        return tmp

    def get_line_number(self):
        return self.line_no
                

class KyazukenParser:
    def __init__(self, lex):
        self.lex = lex
    def syntax_error(self, msg):
        print("line", self.lex.get_line_number(), ":", msg)

    def parse_file(self):
        while True:
            token = self.lex.get_next_token()

            if token == '_start':
                token = self.lex.get_next_token()

                if token != '{':
                    self.syntax_error("_start not followed by '{', required syntax is _start { <...code...> }")
                    break
                self.entry = self.parse_main()

            else:
                break

    def parse_main(self):
        return KyazukenEntryPoint(self.parse_code())

    def parse_code(self):
        tree = []

        while True:
            statement = self.parse_statement()

            if statement == None:
                break

            if statement != ';':
                tree.append(statement)

        return tree

    def parse_statement(self):
        token = self.lex.get_next_token()

        if token == '}':
            return None

        if token == None:
            self.syntax_error("EOF inside unterminated block of code.  You probably forgot a '}'")
            return None

        if token == ';':
            return ';'

        if token in ['if', 'while']:
            block = token
            token = self.lex.get_next_token()
            if token != '(':
                self.syntax_error("'(' not found after " + block + " block.  Must use parenthesis around condition.")

            expr = self.parse_expr_to_paren()

            token = self.lex.peek_next_token()
            if token != '{':
                self.lex.get_next_token()
                li = [self.parse_statement()]
            else:
                li = self.parse_code()

            if block == 'if':
                return IfBlock(expr, li)
            elif block == 'while':
                return WhileBlock(expr, li)

        if token == 'exit':
            exit_code = self.parse_expr_to_semicolon()
            return ExitBlock(exit_code)

        if name_pattern.fullmatch(token) != None:
            a = token
            b = self.lex.get_next_token()

            if name_pattern.fullmatch(b) != None:
                # Variable declaration, can't handle this *yet*
                if self.lex.get_next_token() != ';':
                    self.syntax_error("Missing semicolon after variable decleration")
                return a + ' ' + b

            elif b == '(':
                # Function call
                args = self.parse_expr_tuple()
                if self.lex.get_next_token() != ';':
                    self.syntax_error("Missing semicolon after function call.")
                return FunctionCall(a, args)

    def parse_expr_to_paren(self):
        return Literal('String', self.lex.get_next_token())
    def parse_expr_to_semicolon(self):
        return Literal('String', self.lex.get_next_token())
    def parse_expr_tuple(self):
        li = []
        while True:
            token = self.lex.peek_next_token()
            if token == ')':
                break
            li.append(self.parse_expr_to_semicolon())

        self.lex.get_next_token()
        return tuple(li)
    

f = open('test.kya')
lex = KyazukenLexer(f)
parser = KyazukenParser(lex)
parser.parse_file()

print(parser.entry.lines)

