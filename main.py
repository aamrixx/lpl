import sys

def usage():
    print('usage : [python] [--print_tokens] [file')

def die(reason):
    print('\x1b[1;31merror\x1b[0m :', reason, file=sys.stderr)
    sys.exit(1)

class Token:
    Comma = 'Comma'
    Num = 'Num'
    Iden = 'Iden'
    String = 'String'
    Assign = 'Assign'
    Add = 'Add'
    Sub = 'Sub'
    Mul = 'Mul'
    Div = 'Div'
    Echo = 'Echo'
    ResultStore = 'ResultStore'
    StoreA = 'StoreA'
    StoreB = 'StoreB'
    StoreC = 'StoreC'
    StoreD = 'StoreD'
    StoreE = 'StoreE'
    StoreF = 'StoreF'

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
                case ',':
                    self.tokens.append(Token(Token.Comma, ','))
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
                        case 'assign':
                            self.tokens.append(Token(Token.Assign, 'assign'))
                        case 'add':
                            self.tokens.append(Token(Token.Add, 'add'))
                        case 'sub':
                            self.tokens.append(Token(Token.Sub, 'sub'))
                        case 'mul':
                            self.tokens.append(Token(Token.Mul, 'mul'))
                        case 'div':
                            self.tokens.append(Token(Token.Div, 'div'))
                        case 'echo':
                            self.tokens.append(Token(Token.Echo, 'echo'))
                        case '[result]':
                            self.tokens.append(Token(Token.ResultStore, '[result]'))
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

class Stores:
    def __init__(self):
        self.lpl_result = None
        self.lpl_store_a = None
        self.lpl_store_b = None
        self.lpl_store_c = None
        self.lpl_store_d = None
        self.lpl_store_e = None
        self.lpl_store_f = None

class Parser:
    def __init__(self, tokens, stores):
        self.tokens = tokens
        self.line_num = 1
        self.stores = stores

    def parse(self):
        if len(self.tokens) == 0:
            return
        
        match self.tokens[0].kind:
            case Token.Add | Token.Sub | Token.Mul | Token.Div:
                if len(self.tokens) != 4:
                    die('\'{}\' requires 2 parameters : line {}'.format(self.tokens[0].literal, self.line_num))

                if self.tokens[1].kind != Token.Num and not self.is_store(self.tokens[1].kind):
                    die('\'{}\' excpected number/store : line {}'.format(self.tokens[1].literal, self.line_num))
                
                if self.tokens[3].kind != Token.Num and not self.is_store(self.tokens[3].kind):
                    die('\'{}\' excpected number/store : line {}'.format(self.tokens[3].literal, self.line_num))

                if self.tokens[2].kind != Token.Comma:
                    die('\'{}\' excpected comma : line {}'.format(self.tokens[2].literal, self.line_num))

                if self.is_store(self.tokens[1].kind):
                    self.tokens[1] = self.get_store_data(self.tokens[1].kind)
                
                if self.is_store(self.tokens[3].kind):
                    self.tokens[3] = self.get_store_data(self.tokens[3].kind)
            case Token.Echo:
                if self.tokens[len(self.tokens) - 1].kind == Token.Comma:
                    die('\'{}\' excpected number/string/store : line {}'.format(self.tokens[2].literal, self.line_num))

                i = 1
                while i < len(self.tokens):
                    if self.is_store(self.tokens[i].kind):
                        self.tokens[i] = self.get_store_data(self.tokens[i].kind)

                    if self.tokens[i].kind == Token.Num or self.tokens[i].kind == Token.String:
                        if i < len(self.tokens) - 1 and self.tokens[i + 1].kind != Token.Comma:
                            die('\'{}\' excpected comma : line {}'.format(self.tokens[i + 1].literal, self.line_num))

                    i += 1

        self.line_num += 1

    def is_store(self, kind):
        match kind:
            case Token.ResultStore | Token.StoreA | Token.StoreB | Token.StoreC | Token.StoreD | Token.StoreE| Token.StoreF:
                return True
            case _:
                return False

    def get_store_data(self, kind):
        match kind:
            case Token.ResultStore:
                return self.stores.lpl_result
            case Token.StoreA:
                return self.stores.lpl_store_a
            case Token.StoreB:
                return self.stores.lpl_store_b
            case Token.StoreC:
                return self.stores.lpl_store_c
            case Token.StoreD:
                return self.stores.lpl_store_d
            case Token.StoreE:
                return self.stores.lpl_store_e
            case Token.StoreF:
                return self.stores.lpl_store_f
            case _:
                return None

class Interpreter:
    def __init__(self, tokens, stores):
        self.tokens = tokens
        self.stores = stores
        
    def interpret(self):
        if len(self.tokens) == 0:
            return
        
        match self.tokens[0].kind:
            case Token.Add:
                self.stores.lpl_result = Token(Token.Num, str(float(self.tokens[1].literal) + float(self.tokens[3].literal)))
            case Token.Sub:
                self.stores.lpl_result = Token(Token.Num, str(float(self.tokens[1].literal) - float(self.tokens[3].literal)))
            case Token.Mul:
                self.stores.lpl_result = Token(Token.Num, str(float(self.tokens[1].literal) * float(self.tokens[3].literal)))
            case Token.Div:
                self.stores.lpl_result = Token(Token.Num, str(float(self.tokens[1].literal) / float(self.tokens[3].literal)))
            case Token.Echo:
                for element in self.tokens:
                    if element.kind == Token.Num or element.kind == Token.String:
                        print(element.literal, end='')

                print('')

        print(self.stores.lpl_result.literal)

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

    stores = Stores()

    for line in file.readlines():
        lexer = Lexer(line)
        lexer.lex()

        parser = Parser(lexer.tokens, stores)
        parser.parse()

        if print_tokens:
            for token in parser.tokens:
                print(token.kind, token.literal)

        interpreter = Interpreter(parser.tokens, stores)
        interpreter.interpret()

        