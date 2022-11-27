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

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        die('invalid arguments')

    file = open(args[1])
    for line in file.readlines():
        lexer = Lexer(line)
        lexer.lex()

        for token in lexer.tokens:
            print(token.kind, token.literal)