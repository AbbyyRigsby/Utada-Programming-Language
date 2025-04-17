from sly import Lexer
from sly import Parser
from ctypes import c_int, addressof
import encode_class

## EDIT ON THIS PAGE

class CalcLexer(Lexer):
    # Set of token names.   This is always required
    tokens = { NAME, NUMBER, PLUS, TIMES, MINUS, DIVIDE, LPAREN, RPAREN, COMMA,
               LT, LE, GT, GE, EQ, NE, IF, THEN, ELSE, ASSIGN, SEMI, PRINT, FOR}

    # String containing ignored characters
    ignore = ' \t'

    # Regular expression rules for tokens
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    LPAREN = r'\('
    RPAREN = r'\)'
    COMMA = r','
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    ASSIGN = r'='
    SEMI = ';'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Identifiers and keywords
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['if'] = IF
    ID['else'] = ELSE
    ID['while'] = WHILE
    ID['print'] = PRINT
    ID['for'] = FOR

    # Ignored pattern
    ignore_newline = r'\n+'
    ignore_comment = r'#.*\n'

    # Line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1

class CalcParser(Parser):
    # Get the token list from the lexer (required)
    tokens = CalcLexer.tokens

    precedence = (
        ('left', IF, ELSE),
        ('left', EQ, NE, LT, LE, GT, GE),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', UMINUS)
        )

    def __init__(self):
        self.functions = { }
        self.module = encode_class.Module()

    @_('functions function')
    def functions(self, p):
        pass

    @_('function')
    def functions(self, p):
        pass

    @_('function_decl ASSIGN expr SEMI')
    def function(self, p):
        self.function.block_end()
        self.function = None

    @_('NAME LPAREN parms RPAREN')
    def function_decl(self, p):
        self.locals = { name:n for n, name in enumerate(p.parms) }
        self.function = self.module.add_function(p.NAME, [encode_class.i32]*len(p.parms), [encode_class.i32])
        self.functions[p.NAME] = self.function

    @_('NAME LPAREN RPAREN')
    def function_decl(self, p):
        self.locals = { }
        self.function = self.module.add_function(p.NAME, [], [encode_class.i32])
        self.functions[p.NAME] = self.function

    @_('parms COMMA parm')
    def parms(self, p):
        return p.parms + [p.parm]

    @_('parm')
    def parms(self, p):
        return [ p.parm ]

    @_('NAME')
    def parm(self, p):
        return p.NAME

    @_('expr PLUS expr')
    def expr(self, p):
        self.function.i32.add()

    @_('expr MINUS expr')
    def expr(self, p):
        self.function.i32.sub()

    @_('expr TIMES expr')
    def expr(self, p):
        self.function.i32.mul()

    @_('expr DIVIDE expr')
    def expr(self, p):
        self.function.i32.div_s()

    @_('expr LT expr')
    def expr(self, p):
        self.function.i32.lt_s()

    @_('expr LE expr')
    def expr(self, p):
        self.function.i32.le_s()

    @_('expr GT expr')
    def expr(self, p):
        self.function.i32.gt_s()

    @_('expr GE expr')
    def expr(self, p):
        self.function.i32.ge_s()

    @_('expr EQ expr')
    def expr(self, p):
        self.function.i32.eq()

    @_('expr NE expr')
    def expr(self, p):
        self.function.i32.ne()

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        pass

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        pass

    @_('NUMBER')
    def expr(self, p):
        self.function.i32.const(int(p.NUMBER))

    @_('NAME')
    def expr(self, p):
        self.function.local.get(self.locals[p.NAME])

    @_('NAME LPAREN exprlist RPAREN')
    def expr(self, p):
        self.function.call(self.functions[p.NAME])

    @_('NAME LPAREN RPAREN')
    def expr(self, p):
        self.function.call(self.functions[p.NAME])

    @_('IF expr thenexpr ELSE expr')
    def expr(self, p):
        self.function.block_end()

    @_('exprlist COMMA expr')
    def exprlist(self, p):
        pass

    @_('expr')
    def exprlist(self, p):
        pass

    @_('startthen expr')
    def thenexpr(self, p):
        self.function.else_start()
    
    @_('THEN')
    def startthen(self, p):
        self.function.if_start(encode_class.i32)

    @_('FOR ex')
    def for_loop(self, p):
        pass



if __name__ == '__main__':
    lexer = CalcLexer()
    parser = CalcParser()

    while True:
        try:
            text = input('calc > ')
            result = parser.parse(lexer.tokenize(text))
            print(result)
        except EOFError:
            break
