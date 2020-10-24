from klang import *

# Note the $ is not here - it can be used in symbol names.
# the " and ' is handled separately because they behave oddly
TOKEN_CHARS = "~!@#%^&*()[]{}-+=;:<>/?.,|"

# Operators that are multiple characters
DUALOPS = ['==','>=','<=','++','--','*=','/=','+=','-=','&=','|=','^=','%=','!=']

class KyazukenLexer:
    def __init__(self, file):
        self.file = file
        self.buffer = ''
    def get_next_token(self):
        while len(self.buffer) == 0 or self.buffer.isspace():
            self.buffer = self.file.readline()
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

        self.buffer = self.buffer[i + 1:].strip()
        return tmp
                

class KyazukenParser:
    def __init__(self, lex):
        self.lex = lex
    def error(self, msg):
        print(msg)

    def parse_file(self):
        while True:
            token = self.lex.get_next_token()

            if token == '_start':
                token = self.lex.get_next_token()

                if token != '{':
                    self.error("_start not followed by '{', required syntax is _start { <...code...> }")
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

            tree.append(statement)

        return tree

    def parse_statement(self):
        tokens = []

        while True:
            token = self.lex.get_next_token()

            if token == '}':
                if len(tokens) != 0:
                    self.error("'}' after unterminated statement - perhaps you were missing a semicolon?")
                return None

            if token == None or token == ';':
                break

            elif token == '{':
                tokens.append(self.parse_code())
            else:
                tokens.append(token)

        return tokens


f = open('test.kya')
lex = KyazukenLexer(f)
parser = KyazukenParser(lex)
parser.parse_file()

print(parser.entry.lines)

