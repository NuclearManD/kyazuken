from klang import *
from kenvironment import KyazukenDocument

from rply import LexerGenerator
from rply import ParserGenerator
from rply.errors import LexingError

import os
import sys

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # Various types
        self.lexer.add('INTTYPE', r'\b[u]{0,1}int(8|16|32|64|)\b')
        self.lexer.add('FLOATTYPE', r'\bfloat(32|64|)\b')
        self.lexer.add('VOID', r'\bvoid\b')
        self.lexer.add('STRINGTYPE', r'\bString\b')
        self.lexer.add('BOOL', r'\bbool\b')

        # Other reserved words
        self.lexer.add('IF', r'\bif\b')
        self.lexer.add('ELSE', r'\belse\b')
        self.lexer.add('WHILE', r'\bwhile\b')
        self.lexer.add('FOR', r'\bfor\b')
        self.lexer.add('CLASS', r'\bclass\b')
        self.lexer.add('OPERATOR', r'\boperator\b')
        self.lexer.add('MUTABLE', r'\bmutable\b')
        self.lexer.add('PUBLIC', r'\bpublic\b')
        self.lexer.add('PRIVATE', r'\bprivate\b')
        self.lexer.add('IMPORT', r'\bimport\b')

        self.lexer.add('RETURN', r'\breturn\b')
        self.lexer.add('EXTENDS', r'\bextends\b')

        self.lexer.add('NEW', r'\bnew\b')
        
        # Name of function or variable
        self.lexer.add('NAME', r'[a-zA-Z_$][a-zA-Z_$0-9]*')
        # Number
        self.lexer.add('DOUBLE', r'\d+[.]\d+')
        self.lexer.add('INTEGER', r'\d+')
        # Parenthesis, Curly Braces, and Brackets
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')
        self.lexer.add('OPEN_CURLY', r'\{')
        self.lexer.add('CLOSE_CURLY', r'\}')
        self.lexer.add('OPEN_BRACKET', r'\[')
        self.lexer.add('CLOSE_BRACKET', r'\]')
        # Syntax Helper Bytes
        self.lexer.add('SEMICOLON', r'\;')
        self.lexer.add('COMMA', r'\,')
        self.lexer.add('CHAR', r"\'([^\\\n\r]|\\[rnft\'])\'")
        self.lexer.add('STRING', r'\"[^"]*\"')
        # Operators
        self.lexer.add('!=', '!=')
        self.lexer.add('==', '==')
        self.lexer.add('>=', '>=')
        self.lexer.add('<=', '<=')
        self.lexer.add('+=', '[+]=')
        self.lexer.add('-=', '[-]=')
        self.lexer.add('*=', '[*]=')
        self.lexer.add('/=', '[/]=')
        self.lexer.add('>', '[>]')
        self.lexer.add('<', '[<]')
        self.lexer.add('>>', '[>][>]')
        self.lexer.add('<<', '[<][<]')
        self.lexer.add('>>=', '>>=')
        self.lexer.add('<<=', '<<=')
        self.lexer.add('^^', r'\^\^')
        self.lexer.add('&&', r'\&\&')
        self.lexer.add('||', r'\|\|')
        self.lexer.add('INC', r'\+\+')
        self.lexer.add('DEC', r'\-\-')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'\-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'\/')
        self.lexer.add('XOR', r'\^')
        self.lexer.add('AND', r'\&')
        self.lexer.add('OR', r'\|')
        self.lexer.add('EQ', r'\=')
        self.lexer.add('MOD', r'\%')
        self.lexer.add('MEMBER', r'\.')
        self.lexer.add('NOT', r'\!')
        # the rest
        self.lexer.add('COLON', r'\:')
        # Ignore comments
        self.lexer.ignore(r'\/\*.*\*\/')
        self.lexer.ignore(r'\/\/.*(\n|\r)')
        # Ignore spaces
        self.lexer.ignore('\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()

OP_NAMES = ['SUM', 'SUB', 'MUL', 'DIV', 'OR', 'AND', 'XOR', 'MOD',
            '==', '!=', '<=', '>=', '<', '>', 'INC', 'DEC', '||', '&&', '^^',
            '+=', '-=', '*=', '/=', '<<', '>>', '<<=', '>>=']

class KSyntaxError(Exception):
    def __init__(self, token):
        super().__init__(token)
        self.token = token
    def __str__(self):
        return "Unexpected '" + self.token.getstr() + "' on line " + str(self.token.getsourcepos().lineno)

class KyazukenParser:
    def __init__(self, file):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['INTEGER', 'NAME', 'OPEN_PAREN', 'CLOSE_PAREN', 'INTTYPE', 'MEMBER', 'FLOATTYPE',
             'OPEN_CURLY', 'CLOSE_CURLY', 'VOID', "STRING", 'STRINGTYPE', 'OPEN_BRACKET', 'CLOSE_BRACKET',
             'IF', 'WHILE', 'RETURN', 'COLON', 'CLASS', 'EXTENDS', 'MUTABLE', 'NOT', 'NEW',
             'DOUBLE', 'BOOL', 'CHAR', 'IMPORT', 'PUBLIC', 'PRIVATE', 'FOR', 'ELSE', 'OPERATOR',
             'SEMICOLON', 'COMMA', 'EQ'] + OP_NAMES,
            precedence = [
                ('right', ['ELSE']),
                ('left', ['IF', 'COLON', 'END', 'WHILE', 'NEW']),
                ('left', ['EQ']),
                ('left', ['&&', '||', '^^']),
                ('left', ['==', '!=', '>=','>', '<', '<=',]),
                ('left', ['SUM', 'SUB',]),
                ('left', ['MUL', 'DIV', 'MOD']),
                ('left', ['AND', 'OR', 'XOR']),
                ('left', ['INC', 'DEC']),
                ('left', ['POUND']),
                ('left', ['OPEN_BRACKET','CLOSE_BRACKET', 'COMMA']),
                ('left', ['MEMBER']),
                ('left', ['NAME', 'INTEGER', 'DOUBLE', 'STRINGTYPE', 'BOOL']),
            ]
        )

        self.path = file

    def parse(self):
        @self.pg.production('program : toplevel')
        def pgm_1(p):
            return [p[0]]
        
        @self.pg.production('program : program toplevel')
        def pgm_2(p):
            return p[0] + [p[1]]

        @self.pg.production('toplevel : func')
        @self.pg.production('toplevel : class')
        @self.pg.production('toplevel : import')
        def toplevel(p):
            return p[0]

        @self.pg.production('class : CLASS NAME OPEN_CURLY class_li CLOSE_CURLY')
        def class_def(p):
            return ClassDefinition(p[1].getstr(), p[3])

        @self.pg.production('class : CLASS NAME EXTENDS NAME OPEN_CURLY class_li CLOSE_CURLY')
        def class_inherit(p):
            return ClassInheriting(p[1].getstr(), p[5], p[3].getstr())

        @self.pg.production('class : MUTABLE CLASS NAME OPEN_CURLY class_li CLOSE_CURLY')
        def class_def_mutable(p):
            return ClassDefinition(p[1].getstr(), p[3])

        @self.pg.production('class : MUTABLE CLASS NAME EXTENDS NAME OPEN_CURLY class_li CLOSE_CURLY')
        def class_inherit_mutable(p):
            return ClassInheriting(p[1].getstr(), p[5], p[3].getstr())

        @self.pg.production('import : IMPORT import_path SEMICOLON')
        def import_statement(p):
            return ImportStatement(*p[1])

        @self.pg.production('import_path : import_path MEMBER NAME')
        def import_path_ext(p):
            path, common = p[0]
            return path + '/' + p[2].getstr(), common + '.' + p[2].getstr()

        @self.pg.production('import_path : NAME')
        def import_path_name_only(p):
            return p[0].getstr(), p[0].getstr()

        @self.pg.production('import_path : MEMBER NAME')
        def import_path_name_local(p):
            return './' + p[1].getstr(), '.' + p[1].getstr()

        @self.pg.production('statement : COLON OPEN_PAREN expr_li CLOSE_PAREN SEMICOLON')
        def superconstructor(p):
            x = SuperConstructor(p[2]);
            x.lineinfo = p[0].getsourcepos()
            return x

        @self.pg.production('class_li : ')
        def class_list_1(p):
            return []

        @self.pg.production('class_li : class_li var_dec SEMICOLON')
        @self.pg.production('class_li : class_li var_dec_eq SEMICOLON')
        def class_list_2(p):
            return p[0] + [p[1]]
        
        @self.pg.production('class_li : class_li scope func')
        @self.pg.production('class_li : class_li scope constructor')
        @self.pg.production('class_li : class_li scope overload')
        def class_list_3(p):
            return p[0] + [p[2]]

        @self.pg.production('scope : PUBLIC')
        @self.pg.production('scope : PRIVATE')
        def scope(p):
            return p[0].getstr()

        @self.pg.production('name_li : NAME')
        def statement_list_1(p):
            return [p[0].getstr()]
            
        @self.pg.production('name_li : name_li NAME')
        def statement_list_2(p):
            return p[0] + [p[1].getstr()]

        @self.pg.production('func : type NAME OPEN_PAREN dec_list CLOSE_PAREN OPEN_CURLY statement_li CLOSE_CURLY')
        def func(p):
            return Function(p[1].getstr(), p[0], p[3], p[6])

        @self.pg.production('constructor : NAME OPEN_PAREN dec_list CLOSE_PAREN OPEN_CURLY statement_li CLOSE_CURLY')
        def constructor(p):
            return Constructor(p[0].getstr(), p[2], p[5])

        @self.pg.production('overload : type OPERATOR uniop OPEN_PAREN CLOSE_PAREN OPEN_CURLY statement_li CLOSE_CURLY')
        @self.pg.production('overload : type OPERATOR COLON OPEN_PAREN CLOSE_PAREN OPEN_CURLY statement_li CLOSE_CURLY')
        def uniop_overload(p):
            return OperatorOverload(p[2].getstr(), p[0], p[6])

        @self.pg.production('overload : type OPERATOR dualop OPEN_PAREN var_dec CLOSE_PAREN OPEN_CURLY statement_li CLOSE_CURLY')
        def dualop_overload(p):
            return OperatorOverload(p[2].getstr(), p[0], p[4], p[6])

        @self.pg.production('expression : NEW NAME OPEN_PAREN expr_li CLOSE_PAREN')
        def new_object(p):
            return NewObject(p[1].getstr(), p[3])

        @self.pg.production('statement_li : statement')
        def statement_list_1(p):
            return [p[0]]
            
        @self.pg.production('statement_li : statement_li statement')
        def statement_list_2(p):
            return p[0] + [p[1]]
        
        @self.pg.production('statement_li :')
        def statement_list_3(p):
            return []

        @self.pg.production('statement : expression SEMICOLON')
        @self.pg.production('statement : var_dec SEMICOLON')
        @self.pg.production('statement : var_dec_eq SEMICOLON')
        def statement_of_expression(p):
            x = p[0]
            x.lineinfo = p[1].getsourcepos()
            return x

        @self.pg.production('statement : IF OPEN_PAREN expression CLOSE_PAREN statement ELSE statement')
        def if_else_block(p):
            x = IfElseBlock(p[2], p[4], p[6])
            x.lineinfo = p[0].getsourcepos()
            return x

        @self.pg.production('statement : IF OPEN_PAREN expression CLOSE_PAREN statement')
        def if_block(p):
            x = IfBlock(p[2], p[4])
            x.lineinfo = p[0].getsourcepos()
            return x

        @self.pg.production('statement : FOR OPEN_PAREN var_dec COLON expression CLOSE_PAREN statement')
        def iterator_for_block(p):
            x = IterForBlock(p[2], p[4], p[6])
            x.lineinfo = p[0].getsourcepos()
            return x

        @self.pg.production('statement : WHILE OPEN_PAREN expression CLOSE_PAREN statement')
        def while_loop(p):
            x = WhileBlock(p[2], p[4])
            x.lineinfo = p[0].getsourcepos()
            return x

        @self.pg.production('statement : OPEN_CURLY statement_li CLOSE_CURLY')
        def statement_group(p):
            return StatementList(p[1])

        @self.pg.production('statement : RETURN expression SEMICOLON')
        def return_expr(p):
            x = Return(p[1])
            x.lineinfo = p[0].getsourcepos()
            return x

        @self.pg.production('statement : RETURN SEMICOLON')
        def return_void(p):
            x = Return()
            x.lineinfo = p[0].getsourcepos()
            return x

        @self.pg.production('dec_list : var_dec')
        def dec_list_1(p):
            return [p[0]]
            
        @self.pg.production('dec_list : dec_list COMMA var_dec')
        def dec_list_2(p):
            return p[0] + [p[2]]

        @self.pg.production('dec_list :')
        def dec_list_3(p):
            return []

        @self.pg.production('var_dec_eq : type NAME EQ expression')
        def var_dec_eq(p):
            return VariableDefinition(p[1].getstr(), p[0], p[3])

        @self.pg.production('var_dec : type NAME')
        def var_dec(p):
            return VariableDeclaration(p[1].getstr(), p[0])

        @self.pg.production('expression : assignable')
        def assignable_to_expr(p):
            return p[0]

        @self.pg.production('assignable : expression OPEN_BRACKET expression CLOSE_BRACKET')
        def subscript(p):
            return Subscript(p[0], p[2])

        @self.pg.production('expression : expression dualop expression')
        def expression(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            return BinOp(left, operator.getstr(), right)

        @self.pg.production('expression : uniop expression')
        def onearg_expr(p):
            return UniOp(p[1], p[0].getstr())

        @self.pg.production('dualop : SUM')
        @self.pg.production('dualop : SUB')
        @self.pg.production('dualop : MUL')
        @self.pg.production('dualop : DIV')
        @self.pg.production('dualop : MOD')
        @self.pg.production('dualop : AND')
        @self.pg.production('dualop : OR')
        @self.pg.production('dualop : XOR')
        @self.pg.production('dualop : >=')
        @self.pg.production('dualop : ==')
        @self.pg.production('dualop : !=')
        @self.pg.production('dualop : <=')
        @self.pg.production('dualop : >')
        @self.pg.production('dualop : <')
        @self.pg.production('dualop : ||')
        @self.pg.production('dualop : &&')
        @self.pg.production('dualop : ^^')
        @self.pg.production('dualop : <<')
        @self.pg.production('dualop : >>')
        @self.pg.production('dualop : <<=')
        @self.pg.production('dualop : >>=')
        @self.pg.production('dualop : +=')
        @self.pg.production('dualop : -=')
        @self.pg.production('dualop : *=')
        @self.pg.production('dualop : /=')
        def dualop(p):
            return p[0]

        @self.pg.production('uniop : INC')
        @self.pg.production('uniop : DEC')
        @self.pg.production('uniop : SUB')
        @self.pg.production('uniop : NOT')
        def uniop(p):
            return p[0]

        @self.pg.production('assignable : expression MEMBER NAME')
        def member(p):
            return Member(p[0], p[2].getstr())

        @self.pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
        def expression_parens(p):
            return p[1]

        @self.pg.production('expression : STRING')
        def expression_string(p):
            return Literal("String", eval(p[0].getstr()))

        @self.pg.production('expression : assignable OPEN_PAREN expr_li CLOSE_PAREN')
        def call(p):
            return FunctionCall(p[0], p[2])

        @self.pg.production('expression : OPEN_BRACKET expr_li CLOSE_BRACKET')
        def newarray(p):
            return ArrayInitializer(p[1])

        @self.pg.production('assignable : NAME')
        def expression_variable(p):
            return Variable(p[0].getstr())

        @self.pg.production('expression : assignable EQ expression')
        def expression_assign_var(p):
            return Store(p[0], p[2])
        
        @self.pg.production('expr_li : expression')
        def expr_list_1(p):
            return [p[0]]
            
        @self.pg.production('expr_li : expr_li COMMA expression')
        def expr_list_2(p):
            return p[0] + [p[2]]

        @self.pg.production('expr_li :')
        def expr_list_3(p):
            return []

        @self.pg.production('expression : INTEGER')
        def number(p):
            return Literal('int', int(p[0].getstr()))

        @self.pg.production('expression : DOUBLE')
        def number(p):
            return Literal('float', float([0].getstr()))

        @self.pg.production('expression : CHAR')
        def number(p):
            return Literal('int', ord(eval(p[0].getstr())))

        @self.pg.production('type : type OPEN_BRACKET CLOSE_BRACKET')
        def array_type(p):
            return ArrayType(p[0])

        @self.pg.production('type : VOID')
        @self.pg.production('type : INTTYPE')
        @self.pg.production('type : FLOATTYPE')
        @self.pg.production('type : STRINGTYPE')
        @self.pg.production('type : NAME')
        @self.pg.production('type : BOOL')
        def base_type(p):
            s = p[0].getstr()

            if s == 'int':
                s = 'int32'
            elif s == 'float':
                s = 'float32'

            return s

        @self.pg.error
        def error_handle(token):
            src = token.getsourcepos()
            print("Syntax error at " + self.path + ':' + str(src.lineno))
            raise KSyntaxError(token)

    def get_parser(self):
        return self.pg.build()

def parse_ast(filename):
    print("Parsing " + filename)

    f = open(filename)
    text = f.read().replace('\r', '\n')
    f.close()

    lines = [''] + text.split('\n')

    try:
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text)
    except LexingError as e:
        srcpos = e.source_pos
        print(e)
        if srcpos.lineno > 0:
            print(lines[srcpos.lineno].replace('\t', ' '))
            print(' '*(srcpos.colno - 1) + '^ here')
        else:
            i = text[:srcpos.idx].rfind('\n') + 1
            print(text[i:].split('\n')[0].replace('\t', ' '))
            print(' '*(srcpos.idx - i) + '^ here')
        print()
        return None

    pg = KyazukenParser(filename)
    pg.parse()
    parser = pg.get_parser()

    try:
        return parser.parse(tokens)
    except KSyntaxError as e:
        srcpos = e.token.getsourcepos()
        print(e)
        print(lines[srcpos.lineno].replace('\t', ' '))
        print(' '*(srcpos.colno - 1) + '^ here')
        print()
        return None

FILE_EXTENTIONS = ['.kya', '.k']

def elaborate_ast(ast, filename, docs = None):
    doc = KyazukenDocument()

    root_path = os.path.dirname(filename)

    if docs == None:
        docs = {filename: doc}

    all_statements = ast.copy()

    errors = 0

    for i in ast:
        if type(i) == ImportStatement:
            path = i.path.replace('.', root_path)

            for j in FILE_EXTENTIONS:
                if os.path.exists(path + j):
                    path += j
                    break

            if not '.' in path.split('/')[-1]:
                print("Error: Could not import " + i.commonname + ' from file ' + filename)
                errors += 1
            else:
                new_ast = parse_ast(path)
                if new_ast is None:
                    print("Skipping " + path + " due to syntax error(s), will continue elaboration without it")
                    print()
                    errors += 1
                else:
                    imported_doc, docs, new_errors = elaborate_ast(new_ast, path, docs)
                    doc.add_imported_document(imported_doc)
                    errors += new_errors

    for i in ast:
        if type(i) == Function:
            if i.signature() in ['_Z4mainEPp6String', '_Z4mainEPp6String', '_Z4mainEP']:
                # main function
                doc.entry = i
            else:
                doc.functions[i.signature()] = i
        elif type(i) in [ClassDefinition, ClassInheriting]:
            doc.classes[i.name] = i

    return doc, docs, errors

filename = 'kyac/main.k'

ast = parse_ast(filename)

print('Elaborate...')
document, documents, errors = elaborate_ast(ast, filename)

if errors == 0:
    print('Execute:')

    try:
        document.execute(document.make_default_env(), ['kyac', 'kyac/main.k'])
    except KyazukenError as e:
        sys.stderr.write("Error: " + str(e) + '\n')
else:
    print("There were errors.  Will not execute.")

