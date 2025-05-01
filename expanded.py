from sly import Lexer
from sly import Parser
from formatting import terminal_colors
import os
import webbrowser


class BasicLexer(Lexer): 
    # Set of token names.   This is always required
    tokens = { NAME, STRING, NUMBER,
               IF, ELSE,  
               WHILE, FOR, IN,
               PLUS, MINUS, TIMES, DIVIDE, SQR, 
               ASSIGN,
               PRINT, OPEN,
               APPEND, REMOVE,
               EQ, LT, LE, GT, GE, NE }


    literals = { '(', ')', '{', '}', ';', ":", ",", ".", "[", "]" , "\\"}

    # String containing ignored characters
    ignore = ' \t'

    # Regular expression rules for tokens
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    SQR     = r'\^'
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

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'"[^"]*"'

    NAME['if'] = IF
    NAME['else'] = ELSE
    NAME['while'] = WHILE
    NAME['for'] = FOR
    NAME['in'] = IN
    NAME['print'] = PRINT
    NAME['def'] = DEF
    NAME['app'] = APPEND
    NAME['rem'] = REMOVE
    NAME['open'] = OPEN
    

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
    tokens = BasicLexer.tokens 
  
    precedence = ( 
        ('left', PLUS, MINUS), 
        ('left', TIMES, DIVIDE), 
        ('right', 'UMINUS')
    )
  
    def __init__(self): 
        self.env = { } 
    
    @_('while_loop')
    def statement(self, p):
        return p.while_loop
    
    @_('WHILE expr "," statement')
    def while_loop(self, p):
        return ('while', p.expr, p.statement) 
    
    @_('FOR expr IN expr "," statement')
    def for_loop(self, p):
        return ('for', p.expr0, p.expr1, p.statement)
    
    @_('for_loop')
    def statement(self, p):
        return p.for_loop

    @_('IF expr "," statement ";" ELSE statement')
    def statement(self, p):
        return ('if', p.expr, p.statement0, p.statement1)
  
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
    
    @_('STRING PLUS concat_list')
    def expr(self, p):
        return ('concat', [p.STRING[1:-1]] + p.concat_list)

    @_('STRING PLUS STRING')
    def concat_list(self, p):
        return [p.STRING0[1:-1], p.STRING1[1:-1]]

    @_('STRING PLUS concat_list')
    def concat_list(self, p):
        return [p.STRING[1:-1]] + p.concat_list
    
    @_('OPEN STRING')
    def open_statement(self, p):
        return ('open', p.STRING[1:-1])
    
    @_('open_statement')
    def statement(self, p):
        return p.open_statement

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
    
    @_('NAME ASSIGN "[" expr "]"')
    def statement(self, p):
        return('list_assign', p.NAME, p.expr)
  
    @_('NAME ASSIGN expr') 
    def var_assign(self, p): 
        return ('var_assign', p.NAME, p.expr) 
    
    @_('expr comparison_op expr')
    def expr(self, p):
        return ('cmp', p.comparison_op, p.expr0, p.expr1)
    
    @_('LT', 'GT', 'EQ', 'NE', 'LE', 'GE')
    def comparison_op(self, p):
        return p[0]

    @_('"[" list_items "]"')
    def expr(self, p):
        return p.list_items  # Return the list
    
    @_('list_items "," expr')
    def list_items(self, p):
        return p.list_items + [p.expr]
    
    @_('NAME "." APPEND "(" expr ")"')
    def statement(self, p):
        return ('list_append', p.NAME, p.expr)

    @_('NAME "." REMOVE "(" expr ")"')
    def statement(self, p):
        return ('list_remove', p.NAME, p.expr)

    @_('expr')  # Base case: A single-element list
    def list_items(self, p):
        return [p.expr]

    @_('NAME') 
    def expr(self, p): 
        return ('var', p.NAME) 
  
    @_('NUMBER') 
    def expr(self, p): 
        return ('num', p.NUMBER)

    
class BasicExecute: 
    def __init__(self, tree, env): 
        self.env = env 
        self.functions = {}
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
                print(f"{terminal_colors.FAIL}Undefined variable '"+node[1]+"' found!") 
            

        if node[0] == 'list_assign':
            list_name = node[1]
            list_values = [self.walkTree(value) for value in node[2]]  # Evaluates each value
            self.env[list_name] = list_values  # Stores the list in the environment


        if node[0] == 'list_append':
            list_name = node[1]
            value = self.walkTree(node[2])

            if list_name in self.env and isinstance(self.env[list_name], list):
                self.env[list_name].append(value)
            else:
                raise Exception(f"{terminal_colors.FAIL}Error: '{list_name}' is not a valid list.")


        if node[0] == 'list_remove':
            list_name = node[1]
            value = self.walkTree(node[2])  # Get raw value to remove

            # Ensure the list exists and is stored correctly
            if list_name in self.env and isinstance(self.env[list_name], list):

                # Extract only the values from the stored tuples
                extracted_values = [item[1] if isinstance(item, tuple) and len(item) == 2 else item for item in self.env[list_name]]

                if value in extracted_values:
                    # values are stored as tupe so need to find the actual value
                    self.env[list_name] = [item for item in self.env[list_name] if item[1] != value]
                else:
                    raise Exception(f"{terminal_colors.FAIL}Error: Value {value} not found in list '{list_name}'.")
            else:
                raise Exception(f"{terminal_colors.FAIL}Error: '{list_name}' is not a valid list.")


        if node[0] == 'concat':
            print(''.join(node[1]))
            return ''.join(node[1])


        if node[0] == 'print':
            value = self.walkTree(node[1])
            
            # Handle undefined values
            if value is None:
                print(f"{terminal_colors.FAIL}Error: Undefined variable or value.")
                return None
            
            if isinstance(value, list):
                for item in value:
                    print(item[1], end=' ')
                print()

            else:
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


        if node[0] == 'if':
            cond = node[1]
            stmt = node[2]
            else_stmt = node[3]

            if bool(self.walkTree(cond)):
                self.walkTree(stmt)
            else:
                self.walkTree(else_stmt)


        if node[0] == 'open':
            link = node[1]
            if link.startswith('http://') or link.startswith('https://'):
                try:
                    webbrowser.open(link)  # Open link in the default browser
                    print(f"Successfully opened {link}!")
                except Exception as e:
                    print(f"{terminal_colors.FAIL}Uh oh! Failed opening link! {link} ({e})")
            
            elif os.path.exists(link):  # Check if it's a valid file path
                try:
                    os.startfile(link)  # Open the file using the system's default application
                    print(f"Successfully opened file! {link}")
                except Exception as e:
                    print(f"{terminal_colors.FAIL}Error opening file! {link} ({e})")


        if node[0] == 'for':
            loop_var = node[1][1]  # Extract variable name correctly
            iterable = self.walkTree(node[2])  # Evaluate iterable
            stmt = node[3]  # Statement inside the loop

            if not isinstance(iterable, list):
                raise Exception(f"{terminal_colors.FAIL}Error: {iterable} is not iterable.")

            index = 0
            length = len(iterable)
            while index < length:
                value = iterable[index]  # Get current item

                if isinstance(value, tuple):  # Extract actual value if stored as ('num', 1)
                    value = value[1]

                self.env[loop_var] = value  # Store extracted value dynamically
                self.walkTree(stmt)  # Execute statement inside loop
                index += 1