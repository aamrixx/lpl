import sys

def die(reason):
    print('\x1b[1;31merror\x1b[0m :', reason)
    sys.exit(1)

class Token:
    Comma = 'Comma'
    Num = 'Num'
    Iden = 'Iden'
    Add = 'Add'
    Sub = 'Sub'
    Mul = 'Mul'
    Div = 'Div'
    Push = 'Push'
    Pop = 'Pop'

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
                case _:
                    buffer = ''
                    while self.pos < len(self.line) and self.get_char() != ',' and self.get_char() != ' ':
                        buffer += self.get_char()
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
                        case 'push':
                            self.tokens.append(Token(Token.Push, 'push'))
                        case 'pop':
                            self.tokens.append(Token(Token.Pop, 'pop'))
                        case _:
                            is_num = True
                            for char in buffer:
                                if not char.isdigit() and char != '.' and char != '-':
                                    is_num = False
                                    break
                            
                            if is_num:
                                self.tokens.append(Token(Token.Num, buffer))
                            else:
                                self.tokens.append(Token(Token.Iden, buffer))

            self.advance()

    def get_char(self):
        return self.line[self.pos]

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
            case Token.Push:
                if len(self.tokens) != 2:
                    die('\'{}\' requires 1 parameter : line {}'.format(self.tokens[0].literal, self.line_num))
                
                if self.tokens[1].kind != Token.Num:
                    die('\'{}\' excpected number : line {}'.format(self.tokens[1].literal, self.line_num))

            case Token.Add | Token.Sub | Token.Mul | Token.Div | Token.Pop:
                if len(self.tokens) != 1:
                    die('\'{}\' does not require any parameters : line {}'.format(self.tokens[0].literal, self.line_num))
                    
        self.line_num += 1

class Stores:
    def __init__(self):
        self.lpl_list = []
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
                for element in self.stores.lpl_list:
                    self.stores.lpl_result += float(element)
            case Token.Sub:
                for element in self.stores.lpl_list:
                    self.stores.lpl_result -= float(element)
            case Token.Mul:
                for element in self.stores.lpl_list:
                    self.stores.lpl_result *= float(element)
            case Token.Div:
                for element in self.stores.lpl_list:
                    self.stores.lpl_result /= float(element)
            case Token.Push:
                self.stores.lpl_list.append(float(self.tokens[1].literal))

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

        parser = Parser(lexer.tokens)
        parser.parse()

        interpreter = Interpreter(parser.tokens, stores)
        interpreter.interpret()

        #for token in parser.tokens:
        #    print(token.kind, token.literal)