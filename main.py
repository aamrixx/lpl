import sys

def die(reason):
    print('\x1b[1;31merror\x1b[0m :', reason)
    sys.exit(1)

class Token:
    Comma = 'Comma'
    Num = 'Num'
    Iden = 'Iden'
    String = 'String'
    Add = 'Add'
    Sub = 'Sub'
    Mul = 'Mul'
    Div = 'Div'
    Echo = 'Echo'

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

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.line_num = 1

    def parse(self):
        if len(self.tokens) == 0:
            return
        
        match self.tokens[0].kind:
            case Token.Add | Token.Sub | Token.Mul | Token.Div:
                if len(self.tokens) != 4:
                    die('\'{}\' requires 2 parameters : line {}'.format(self.tokens[0].literal, self.line_num))

                if self.tokens[1].kind != Token.Num:
                    die('\'{}\' excpected number : line {}'.format(self.tokens[1].literal, self.line_num))
                
                if self.tokens[3].kind != Token.Num:
                    die('\'{}\' excpected number : line {}'.format(self.tokens[3].literal, self.line_num))

                if self.tokens[2].kind != Token.Comma:
                    die('\'{}\' excpected comma : line {}'.format(self.tokens[2].literal, self.line_num))
            case Token.Echo:
                i = 1
                while i < len(self.tokens):
                    if self.tokens[i].kind == Token.Num or self.tokens[i].kind == Token.String:
                        if i < len(self.tokens) - 1 and self.tokens[i + 1].kind != Token.Comma:
                            die('\'{}\' excpected comma : line {}'.format(self.tokens[i + 1].literal, self.line_num))

                    i += 1

        self.line_num += 1

class Stores:
    def __init__(self):
        self.lpl_result = 0.0

class Interpreter:
    def __init__(self, tokens, stores):
        self.tokens = tokens
        self.stores = stores
        
    def interpret(self):
        if len(self.tokens) == 0:
            return
        
        match self.tokens[0].kind:
            case Token.Add:
                self.stores.lpl_result = float(self.tokens[1].literal) + float(self.tokens[3].literal)        
            case Token.Sub:
                self.stores.lpl_result = float(self.tokens[1].literal) - float(self.tokens[3].literal)
            case Token.Mul:
                self.stores.lpl_result = float(self.tokens[1].literal) * float(self.tokens[3].literal)
            case Token.Div:
                self.stores.lpl_result = float(self.tokens[1].literal) / float(self.tokens[3].literal)
            case Token.Echo:
                for element in self.tokens:
                    if element.kind == Token.Num or element.kind == Token.String:
                        print(element.literal, end='')

                print('')

        print(self.stores.lpl_result)

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        die('invalid arguments')

    stores = Stores()

    file = open(args[1])
    for line in file.readlines():
        lexer = Lexer(line)
        lexer.lex()

        for token in lexer.tokens:
            print(token.kind, token.literal)

        parser = Parser(lexer.tokens)
        parser.parse()

        interpreter = Interpreter(parser.tokens, stores)
        interpreter.interpret()

        