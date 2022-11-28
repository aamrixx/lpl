import sys
import os

def usage():
    print('usage : [python] [--print_tokens] [file')

def die(reason):
    print('\x1b[1;31merror\x1b[0m :', reason, file=sys.stderr)
    sys.exit(1)

class Token:
    # Syntax Sugar
    Comma = 'Comma'
    # Types
    Num = 'Num'
    Iden = 'Iden'
    String = 'String'
    # Keywords
    Run = 'Run'
    Import = 'Import'
    Constant = 'Constant'
    Variable = 'Variable'
    Procedure = 'Procedure'
    End = 'End'
    Add = 'Add'
    Sub = 'Sub'
    Mul = 'Mul'
    Div = 'Div'
    Echo = 'Echo'
    Read = 'Read'
    # Store
    StoreR = 'StoreR'

    def __init__(self, kind, literal):
        self.kind = kind
        self.literal = literal

class Lexer:
    def __init__(self, line):
        if line[len(line) - 1] == '\n':
            self.line = line[:len(line) - 1]
        else:
            self.line = line
        
        self.pos = 0
        self.tokens = []

    def lex(self):
        while self.pos < len(self.line):
            match self.get_char():
                case '#':
                    return
                case '+':
                    self.tokens.append(Token(Token.Add, '+'))
                case '-':
                    self.tokens.append(Token(Token.Sub, '-'))
                case '*':
                    self.tokens.append(Token(Token.Mul, '*'))
                case '/':
                    self.tokens.append(Token(Token.Div, '/'))
                case ',':
                    self.tokens.append(Token(Token.Comma, ','))
                case '^':
                    self.tokens.append(Token(Token.StoreR, '^'))
                case '"':
                    buffer = ''
                    
                    self.advance()
                    while self.get_char() != '"':
                        buffer += self.get_char()
                        self.advance()

                    self.tokens.append(Token(Token.String, buffer))
                case _:
                    buffer = ''
                    while self.pos < len(self.line) and self.get_char() != ',' and self.get_char() != ' ':
                        buffer += self.get_char()

                        if self.pos < len(self.line) - 1 and self.get_next_char() == ',':
                            break

                        self.advance()

                    match buffer:
                        case 'run':
                            self.tokens.append(Token(Token.Run, 'run'))
                        case 'import':
                            self.tokens.append(Token(Token.Import, 'import'))
                        case 'const':
                            self.tokens.append(Token(Token.Constant, 'const'))
                        case 'var':
                            self.tokens.append(Token(Token.Variable, 'var'))
                        case 'proc':
                            self.tokens.append(Token(Token.Procedure, 'proc'))
                        case 'end':
                            self.tokens.append(Token(Token.End, 'end'))
                        case 'echo':
                            self.tokens.append(Token(Token.Echo, 'echo'))
                        case 'read':
                            self.tokens.append(Token(Token.Read, 'read'))
                        case _:
                            is_num = True
                            for char in buffer:
                                if not char.isdigit() and char != '.' and char != '-':
                                    is_num = False
                                    break
                            
                            if is_num and buffer != '':
                                self.tokens.append(Token(Token.Num, buffer))
                            elif buffer != '':
                                self.tokens.append(Token(Token.Iden, buffer))

            self.advance()

    def get_char(self):
        return self.line[self.pos]

    def get_next_char(self):
        return self.line[self.pos + 1]

    def advance(self):
        self.pos += 1

class DataType:
    def __init__(self, token, is_const):
        self.is_const = is_const
        self.token = token

class Stores:
    def __init__(self):
        self.lpl_store_r = Token('', '')
        # Global Constants
        self.lpl_global_consts_vars_dict = {}
        # Procedures
        self.lpl_global_procedures_dict = {}
        self.lpl_global_procedures = [[[]]]
        self.in_procedure = False
        self.procedure_index = 0

    def search_procedures_dict(self, term):
        if term in self.lpl_global_procedures_dict:
            return self.lpl_global_procedures[self.lpl_global_procedures_dict[term]]
        else:
            return None        

    def search_consts_vars_dict(self, term):
        if term in self.lpl_global_consts_vars_dict:
            return self.lpl_global_consts_vars_dict[term].token
        else:
            return None        

class Parser:
    def __init__(self, tokens, stores):
        self.tokens = tokens
        self.line_num = 1
        self.stores = stores

    def parse(self):
        if len(self.tokens) == 0:
            self.line_num += 1
            return
        
        match self.tokens[0].kind:
            case Token.Run:
                if len(self.tokens) != 2:
                    die(f'\'{self.tokens[0].literal}\' requires 1 parameter : line {self.line_num}')
                
                if self.tokens[1].kind != Token.Iden:
                    die(f'\'{self.tokens[1].literal}\' expected literal : line {self.line_num}')

                if self.stores.search_consts_vars_dict(self.tokens[1].literal) != None:
                    die(f'\'{self.tokens[1].literal}\' can only be used on procedures: line {self.line_num}')

                if self.stores.search_procedures_dict(self.tokens[1].literal) == None:
                    die(f'\'{self.tokens[1].literal}\' undefined procedure : line {self.line_num}')
            case Token.Import:
                if len(self.tokens) != 2:
                    die(f'\'{self.tokens[0].literal}\' requires 1 parameter : line {self.line_num}')

                if self.tokens[1].kind != Token.String:
                    die(f'\'{self.tokens[1].literal}\' expected string : line {self.line_num}')

                for _, _, files in os.walk('.'):
                    if self.tokens[1].literal in files:
                        return
                
                die(f'\'{self.tokens[1].literal}\' could not be found : line {self.line_num}')
            case Token.Constant:
                if len(self.tokens) != 3:
                    die(f'\'{self.tokens[0].literal}\' requires 2 parameters : line {self.line_num}')
                
                if self.stores.in_procedure:
                    die(f'\'{self.tokens[0].literal}\' can not be in procedures : line {self.line_num}')

                if self.tokens[1].kind != Token.Iden:
                    die(f'\'{self.tokens[1].literal}\' expected literal : line {self.line_num}')

                if self.stores.search_consts_vars_dict(self.tokens[1].literal) != None:
                    die(f'\'{self.tokens[1].literal}\' redefined constant : line {self.line_num}')

                if self.tokens[2].kind == Token.Iden:
                    if self.stores.search_constants_dict(self.tokens[2].literal) == None:
                        die(f'\'{self.tokens[1].literal}\' undefined constant : line {self.line_num}')
                    else:
                        self.tokens[2] = self.stores.search_constants_dict(self.tokens[2].literal)
                
                self.stores.lpl_global_consts_vars_dict[self.tokens[1].literal] = DataType(self.tokens[2], False)
            case Token.Variable:
                if len(self.tokens) != 3:
                    die(f'\'{self.tokens[0].literal}\' requires 2 parameters : line {self.line_num}')
                
                if self.stores.in_procedure:
                    die(f'\'{self.tokens[0].literal}\' can not be in procedures : line {self.line_num}')

                if self.tokens[1].kind != Token.Iden:
                    die(f'\'{self.tokens[1].literal}\' expected literal : line {self.line_num}')

                if self.stores.search_consts_vars_dict(self.tokens[1].literal) != None:
                    die(f'\'{self.tokens[1].literal}\' redefined constant/variable : line {self.line_num}')

                if self.tokens[2].kind == Token.Iden:
                    if self.stores.search_consts_vars_dict(self.tokens[2].literal) == None:
                        die(f'\'{self.tokens[1].literal}\' undefined constant/variable : line {self.line_num}')
                    else:
                        self.tokens[2] = self.stores.search_consts_vars_dict(self.tokens[2].literal)
                
                self.stores.lpl_global_consts_vars_dict[self.tokens[1].literal] = DataType(self.tokens[2], False)
            case Token.Procedure:
                if self.stores.in_procedure:
                    die(f'\'{self.tokens[0].literal}\' can not be nested : line {self.line_num}')
                
                if len(self.tokens) != 2:
                    die(f'\'{self.tokens[0].literal}\' requires 1 parameter : line {self.line_num}')

                if self.tokens[1].kind != Token.Iden:
                    die(f'\'{self.tokens[1].literal}\' expected literal : line {self.line_num}')
                
                if self.stores.search_consts_vars_dict(self.tokens[1].literal) != None:
                    die(f'\'{self.tokens[1].literal}\' redefined as procedure : line {self.line_num}')

                if self.stores.search_procedures_dict(self.tokens[1].literal) != None:
                    die(f'\'{self.tokens[1].literal}\' redefined procedure : line {self.line_num}')
            case Token.End:
                if len(self.tokens) != 1:
                    die(f'\'{self.tokens[0].literal}\' requires no parameters : line {self.line_num}')

                self.stores.in_procedure = False
            case Token.Add | Token.Sub | Token.Mul | Token.Div:
                if len(self.tokens) != 4:
                    die(f'\'{self.tokens[0].literal}\' requires 2 parameters : line {self.line_num}')
                
                if self.tokens[1].kind != Token.Num and \
                   self.tokens[1].kind != Token.Iden and not \
                   self.is_store(self.tokens[1].kind):
                    die(f'\'{self.tokens[1].literal}\' expected number/store/constant : line {self.line_num}')

                if self.tokens[3].kind != Token.Num and \
                   self.tokens[3].kind != Token.Iden and not \
                   self.is_store(self.tokens[3].kind):
                    die(f'\'{self.tokens[3].literal}\' expected number/store/constant : line {self.line_num}')

                if self.tokens[2].kind != Token.Comma:
                    die(f'\'{self.tokens[2].literal}\' expected comma : line {self.line_num}')

                if self.tokens[1].kind == Token.StoreR:
                    self.tokens[1] = self.get_store_data(self.tokens[1].kind)
                    if self.tokens[1] == DataType(Token('', ''), None):
                        die(f'\'{self.tokens[1].literal}\' not a store or result store is immutable : line {self.line_num}')
                elif self.tokens[3].kind == Token.StoreR:
                    self.tokens[3] = self.get_store_data(self.tokens[3].kind)
                    if self.tokens[3] == Token('', ''):
                        die(f'\'{self.tokens[3].literal}\' not a store or result store is immutable : line {self.line_num}')
                elif self.tokens[1].kind == Token.Iden:
                    if self.stores.search_consts_vars_dict(self.tokens[1].literal) == None:
                        die(f'\'{self.tokens[1].literal}\' undefined constant : line {self.line_num}')
                    else:
                        self.tokens[1] = self.stores.search_constants_dict(self.tokens[1].literal)
                elif self.tokens[3].kind == Token.Iden:
                    if self.stores.search_consts_vars_dict(self.tokens[3].literal) == None:
                        die(f'\'{self.tokens[3].literal}\' undefined constant : line {self.line_num}')
                    else:
                        self.tokens[3] = self.stores.search_constants_dict(self.tokens[3].literal)
            case Token.Echo:
                if self.tokens[len(self.tokens) - 1].kind == Token.Comma:
                    die(f'\'{self.tokens[2].literal}\' expected number/string/store/constant : line {self.line_num}')

                i = 1
                while i < len(self.tokens):
                    if self.tokens[i].kind == Token.Num or self.tokens[i].kind == Token.String:
                        if i < len(self.tokens) - 1 and self.tokens[i + 1].kind != Token.Comma:
                            die(f'\'{self.tokens[i + 1].literal}\' expected comma : line {self.line_num}')
                    else:
                        if self.tokens[i].kind == Token.StoreR or self.tokens[i].kind == Token.Comma:
                            self.tokens[i] = self.get_store_data(self.tokens[i].kind)
                           
                            if self.tokens[i] == Token('', ''):
                                die(f'\'{self.tokens[i].literal}\' not a store or result store is immutable : line {self.line_num}')
                        else:
                            if self.stores.search_consts_vars_dict(self.tokens[i].literal) != None:
                                self.tokens[i] = self.stores.search_consts_vars_dict(self.tokens[i].literal)
                            else:
                                die(f'\'{self.tokens[i].literal}\' undefined constant : line {self.line_num}')

                    i += 1
            case Token.Read:
                if len(self.tokens) != 2:
                    die(f'\'{self.tokens[0].literal}\' requires 1 parameters : line {self.line_num}')

                if self.tokens[1].kind != Token.String:
                    die(f'\'{self.tokens[1].literal}\' expected string : line {self.line_num}')
            case _:
                die(f'\'{self.tokens[0].literal}\' unknown literal : line {self.line_num}')

        self.line_num += 1

    def is_store(self, kind):
        match kind:
            case Token.StoreR:
                return True
            case _:
                return False

    def get_store_data(self, kind):
        match kind:
            case Token.StoreR:
                return self.stores.lpl_store_r
            case _:
                return Token('', '')

class Interpreter:
    def __init__(self, tokens, stores):
        self.tokens = tokens
        self.stores = stores
        
    def interpret(self):
        if len(self.tokens) == 0:
            return

        if self.stores.in_procedure:
            self.stores.lpl_global_procedures[self.stores.procedure_index].append(self.tokens)
        else:
            match self.tokens[0].kind:
                case Token.Run:
                    lines = self.stores.search_procedures_dict(self.tokens[1].literal)

                    for line in lines:                        
                        interpreter = Interpreter(line, stores)
                        interpreter.interpret()
                case Token.Import:
                    file = open(self.tokens[1].literal)
                    for line in file.readlines():
                        lexer = Lexer(line)
                        lexer.lex()

                        parser.tokens = lexer.tokens
                        parser.parse()

                        interpreter = Interpreter(parser.tokens, stores)
                        interpreter.interpret()
                case Token.Procedure:
                    self.stores.lpl_global_procedures_dict[self.tokens[1].literal] = self.stores.procedure_index
                    self.stores.in_procedure = True
                case Token.End:
                    self.stores.procedure_index += 1
                case Token.Add:
                    self.stores.lpl_store_r = Token(Token.Num, str(float(self.tokens[1].literal) + float(self.tokens[3].literal)))
                case Token.Sub:
                    self.stores.lpl_store_r = Token(Token.Num, str(float(self.tokens[1].literal) - float(self.tokens[3].literal)))
                case Token.Mul:
                    self.stores.lpl_store_r = Token(Token.Num, str(float(self.tokens[1].literal) * float(self.tokens[3].literal)))
                case Token.Div:
                    self.stores.lpl_store_r = Token(Token.Num, str(float(self.tokens[1].literal) / float(self.tokens[3].literal)))
                case Token.Echo:
                    for element in self.tokens:
                        if element.kind == Token.Num or element.kind == Token.String:
                            print(element.literal, end='')
                    print('')
                case Token.Read:
                    stdin = input(self.tokens[1].literal)

                    is_num = True
                    for char in stdin:
                        if not char.isdigit() and char != '.' and char != '-':
                            is_num = False
                            break
                            
                    if is_num and stdin != '':
                        self.stores.lpl_store_r = Token(Token.Num, stdin)
                    elif stdin != '':
                        self.stores.lpl_store_r = Token(Token.String, stdin)

if __name__ == '__main__':
    args = sys.argv
    print_tokens = False

    if len(args) != 2 and len(args) != 3:
        usage()
        die('invalid arguments')

    file = None

    if len(args) == 3:
        if args[1] != '--print_tokens':
            usage()
            die('invalid arguments')
        else:
            print_tokens = True
            file = open(args[2])
    else:
        file = open(args[1])

    # Classes for Parser and Procedures/Constants/Stores
    stores = Stores()
    parser = Parser([], stores)

    for line in file.readlines():
        lexer = Lexer(line)
        lexer.lex()

        parser.tokens = lexer.tokens
        parser.parse()

        if print_tokens:
            for token in parser.tokens:
                print(token.kind, token.literal)

        interpreter = Interpreter(parser.tokens, stores)
        interpreter.interpret()

        