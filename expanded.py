from sly import Lexer
from sly import Parser
import requests
from dataclasses import dataclass


# create dataclass for paths
@dataclass
class Path:
    name: str

    def __repr__(self):
        for char in self.name:
            if char == '/':
                self.name = self.name.replace(char, '\\')
        return self.name
    

class BasicLexer(Lexer): 
    # Set of token names.   This is always required
    tokens = { NAME, STRING, NUMBER, 
               WHILE, IF, ELSE, PRINT, FOR, IN,
               PLUS, MINUS, TIMES, DIVIDE, SQR, 
               ASSIGN, SQGL, DEF,
               APPEND, REMOVE,
               EQ, LT, LE, GT, GE, NE }


    literals = { '(', ')', '{', '}', ';', ":", ",", ".", "[", "]" }

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
    NAME['in'] = IN
    NAME['print'] = PRINT
    NAME['def'] = DEF
    NAME['app'] = APPEND
    NAME['rem'] = REMOVE
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
    
    @_('FOR expr IN expr "," statement')
    def for_loop(self, p):
        return ('for', p.expr0, p.expr1, p.statement)
    
    @_('for_loop')
    def statement(self, p):
        return p.for_loop

    # TODO: functions working

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
    
    # Define comparison operators as tokens
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
        if isinstance(node, list):
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
            

        if node[0] == 'list_assign':
            list_name = node[1]
            list_values = [self.walkTree(value) for value in node[2]]  # Evaluates each value
            self.env[list_name] = list_values  # Stores the list in the environment

        if node[0] == 'list_append':
            list_name = node[1]
            value = self.walkTree(node[2])

            if list_name in self.env and isinstance(self.env[list_name], list):
                self.env[list_name].append(value)
                # print(f"DEBUG: Appended {value} to {list_name} → {self.env[list_name]}")
            else:
                raise Exception(f"Error: '{list_name}' is not a valid list.")


        if node[0] == 'list_remove':
            list_name = node[1]
            value = self.walkTree(node[2])  # Get raw value to remove

            # Ensure the list exists and is stored correctly
            if list_name in self.env and isinstance(self.env[list_name], list):

                # Extract only the values from the stored tuples
                extracted_values = [item[1] if isinstance(item, tuple) and len(item) == 2 else item for item in self.env[list_name]]

                if value in extracted_values:
                    # Find and remove the correct tuple containing the value
                    self.env[list_name] = [item for item in self.env[list_name] if item[1] != value]
                else:
                    raise Exception(f"Error: Value {value} not found in list '{list_name}'.")
            else:
                raise Exception(f"Error: '{list_name}' is not a valid list.")


        if node[0] == 'concat':
            print(''.join(node[1]))
            return ''.join(node[1])


        if node[0] == 'print':
            value = self.walkTree(node[1])
            
            # Handle undefined values
            if value is None:
                print("Error: Undefined variable or value.")
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


        if node[0] == 'for':
            loop_var = node[1][1]  # Extract variable name correctly
            iterable = self.walkTree(node[2])  # Evaluate iterable
            stmt = node[3]  # Statement inside the loop

            if not isinstance(iterable, list):
                raise Exception(f"Error: {iterable} is not iterable.")

            index = 0
            length = len(iterable)
            while index < length:
                value = iterable[index]  # Get current item

                if isinstance(value, tuple):  # Extract actual value if stored as ('num', 1)
                    value = value[1]

                self.env[loop_var] = value  # Store extracted value dynamically
                self.walkTree(stmt)  # Execute statement inside loop
                index += 1

        """ if node[0] == 'function_def':
            self.functions[node[1]] = (node[2], node[3])  # Store (params, statement)
            print(f"Function '{node[1]}' defined with parameters {node[2]}")
            return f"Function '{node[1]}' defined"
        
        if node[0] == 'function_call':
            func_name = node[1]
            args = [self.walkTree(arg) for arg in node[2]]

            if func_name not in self.functions:
                print(f"DEBUG: Function '{func_name}' NOT FOUND")
                raise Exception(f"Error: Undefined function '{func_name}'")
            else:
                print(f"DEBUG: Function '{func_name}' FOUND with arguments {args}")

            params, stmt = self.functions[func_name]

            if len(params) != len(args):
                print(f"DEBUG: Argument mismatch! Expected {len(params)}, got {len(args)}")
                raise Exception(f"Error: Function '{func_name}' expected {len(params)} arguments, got {len(args)}")

            local_env = {}

            # Ensure parameters are properly assigned
            for i in range(len(params)):
                param_name = params[i][1] if isinstance(params[i], tuple) and params[i][0] == 'var' else params[i]
                local_env[param_name] = args[i]
                print(f"DEBUG: Assigned parameter '{param_name}' = {args[i]}")

            saved_env = self.env
            self.env = local_env  # Switch to function scope

            print(f"DEBUG: Executing function '{func_name}' body")
            result = self.walkTree(stmt)

            self.env = saved_env  # Restore global environment

            return result """


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