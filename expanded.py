from sly import Lexer
from sly import Parser
import requests

class BasicLexer(Lexer): 
    # Set of token names.   This is always required
    tokens = { NAME, STRING, NUMBER, WHILE, IF, ELSE, PRINT, FOR,
               PLUS, MINUS, TIMES, DIVIDE, SQR, 
               ASSIGN, SQGL,
               EQ, LT, LE, GT, GE, NE }


    literals = { '(', ')', '{', '}', ';', ","}

    # String containing ignored characters
    ignore = ' \t'

    # Regular expression rules for tokens
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    SQR     = r'\^'
    SQGL    = r'~'
    EQ      = r'=='
    LE      = r'<='
    GE      = r'>='
    NE      = r'!='
    GT      = r'>'
    LT      = r'<'
    ASSIGN  = r'='

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Identifiers and keywords
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NAME['if'] = IF
    NAME['else'] = ELSE
    NAME['while'] = WHILE
    NAME['for'] = FOR
    NAME['print'] = PRINT
    STRING = r'"[^"]*"' 

    ignore_comment = r'\#.*'

    # Line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1
  
    # Comment token 
    @_(r'//.*') 
    def COMMENT(self, t): 
        pass
  

class BasicParser(Parser): 
    #tokens are passed from lexer to parser 
    tokens = BasicLexer.tokens 
  
    precedence = ( 
        ('left', PLUS, MINUS), 
        ('left', TIMES, DIVIDE), 
        ('right', 'UMINUS'), 
    ) 
  
    def __init__(self): 
        self.env = { } 
    
    @_('while_loop')
    def statement(self, p):
        return p.while_loop
    
    @_('WHILE expr "," statement')
    def while_loop(self, p):
        return ('while', p.expr, p.statement) 
    
    # TODO: for loop working
    # TODO: functions working
    # TODO: if else working
    # TODO: print working
    # TODO: list working
  
    @_('expr') 
    def statement(self, p): 
        return (p.expr)
    
    @_('') 
    def statement(self, p): 
        return None
    
    @_('PRINT expr')
    def print_statement(self, p):
        return ('print', p.expr)
    
    @_('print_statement')  
    def statement(self, p):  
        return p[0]
    
    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING[1:-1])
    
    @_('expr PLUS expr') 
    def expr(self, p): 
        return ('add', p.expr0, p.expr1) 
  
    @_('expr MINUS expr') 
    def expr(self, p): 
        return ('sub', p.expr0, p.expr1) 
  
    @_('expr TIMES expr') 
    def expr(self, p): 
        return ('mul', p.expr0, p.expr1) 
  
    @_('expr DIVIDE expr') 
    def expr(self, p): 
        return ('div', p.expr0, p.expr1) 
    
    @_('expr SQR expr')
    def expr(self, p):
        return ('sqr', p.expr0, p.expr1)
  
    @_('"-" expr %prec UMINUS') 
    def expr(self, p): 
        return -p.expr 

    @_('var_assign') 
    def statement(self, p): 
        return p.var_assign 
  
    @_('NAME ASSIGN expr') 
    def var_assign(self, p): 
        return ('var_assign', p.NAME, p.expr) 
  
    @_('NAME ASSIGN STRING') 
    def var_assign(self, p): 
        return ('var_assign', p.NAME, p.STRING) 
    
    @_('expr comparison_op expr')
    def expr(self, p):
        return ('cmp', p.comparison_op, p.expr0, p.expr1)
    
    # Define comparison operators as tokens
    @_('LT', 'GT', 'EQ', 'NE', 'LE', 'GE')
    def comparison_op(self, p):
        return p[0]

    @_('NAME') 
    def expr(self, p): 
        return ('var', p.NAME) 
  
    @_('NUMBER') 
    def expr(self, p): 
        return ('num', p.NUMBER)


# create dataclass for paths
    
class BasicExecute: 
    def __init__(self, tree, env): 
        self.env = env 
        result = self.walkTree(tree) 
        if result is not None and isinstance(result, int): 
            print(result) 
        if result is not None and isinstance(result, float): 
            print(result) 
        if isinstance(result, str) and result[0] == '"': 
            print(result) 
  

    def walkTree(self, node): 
        if isinstance(node, int): 
            return node 
        if isinstance(node, str): 
            return node 
        if isinstance(node, float): 
            return node
        if isinstance(node, bool):
            return node
  
        if node is None: 
            return None
  
        if node[0] == 'program': 
            if node[1] == None: 
                self.walkTree(node[2]) 
            else: 
                self.walkTree(node[1]) 
                self.walkTree(node[2]) 
  

        if node[0] == 'num': 
            return node[1] 
  
        if node[0] == 'str': 
            return node[1] 
        
        if node[0] == 'float':
            return node[1]
  
        if node[0] == 'add': 
            return self.walkTree(node[1]) + self.walkTree(node[2]) 
        elif node[0] == 'sub': 
            return self.walkTree(node[1]) - self.walkTree(node[2]) 
        elif node[0] == 'mul': 
            return self.walkTree(node[1]) * self.walkTree(node[2]) 
        elif node[0] == 'div': 
            if self.walkTree(node[1]) / self.walkTree(node[2]):
                return self.walkTree(node[1]) / self.walkTree(node[2])
        elif node[0] == 'sqr':
            return self.walkTree(node[1]) ** self.walkTree(node[2])
  
        if node[0] == 'var_assign': 
            self.env[node[1]] = self.walkTree(node[2]) 
            return node[1] 
  
        if node[0] == 'var': 
            try: 
                return self.env[node[1]] 
            except KeyError: 
                print("Undefined variable '"+node[1]+"' found!") 
                return 0
            
        if node[0] == 'print':
            value = self.walkTree(node[1])
            
            # Handle undefined values
            if value is None:
                print("Error: Undefined variable or value.")
                return None

            # Print the value correctly
            print(value)
        
        if node[0] == 'cmp':
            op = node[1]
            left = self.walkTree(node[2])
            right = self.walkTree(node[3])
            if op == '<': 
                return left < right
            if op == '>': 
                return left > right
            if op == '==': 
                return left == right
            if op == '!=': 
                return left != right
            if op == '<=': 
                return left <= right
            if op == '>=': 
                return left >= right
        
        if node[0] == 'while':
            cond = node[1]
            stmt = node[2]
            while bool(self.walkTree(cond)):
                self.walkTree(stmt)
                cond = node[1]


if __name__ == '__main__': 
    lexer = BasicLexer() 
    parser = BasicParser() 
    print('Abby Rigsby Programming Language') 
    env = {} 
      
    while True:        
        try: 
            text = input(' > ') 
        except EOFError: 
            break
          
        if text: 
            tree = parser.parse(lexer.tokenize(text)) 
            BasicExecute(tree, env)