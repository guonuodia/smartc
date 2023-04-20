# Lexical Analyzer
import re

# Token types
INTEGER = 'INTEGER'
HEXSTR = 'HEXSTR'
FUNCID = 'FUNCID'
FUNC = 'FUNC'
VAR = 'VAR'
STRING = 'STRING'
NONE = 'NONE'
BOOL = 'BOOL'

PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
MOD = 'MOD'
PLUSASSIGN = 'PLUSASSIGN'
MINUSASSIGN = 'MINUSASSIGN'
MULASSIGN = 'MULTASSIGN'
DIVASSIGN = 'DIVASSIGN'
MODASSIGN = 'MODASSIGN'
PPP = 'PPP'
MMP = 'MMP'
PPS = 'PPS'
MMS = 'MMS'

LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LBRACE = 'LBRACE'
RBRACE = 'RBRACE'
LBRACKET = 'LBRACKET'
RBRACKET = 'RBRACKET'
COMMA = 'COMMA'
COLON = 'COLON'

ASSIGN = 'ASSIGN'
SEMI = 'SEMI'
IF = 'IF'
ELSE = 'ELSE'
FOR = 'FOR'
DO = 'DO'
WHILE = 'WHILE'
BREAK = 'BREAK'
CONTINUE = 'CONTINUE'
SWITCH = 'SWITCH'
CASE = 'CASE'
RETURN = 'RETURN'
DEFAULT = 'DEFAULT'
EQ = 'EQ'
NE = 'NE'
LT = 'LT'
GT = 'GT'
LE = 'LE'
GE = 'GE'
BOR = 'BOR'
BXOR = 'BXOR'
BNOT = 'BNOT'
BAND = 'BAND'
NOT = 'NOT'
OR = 'OR'
AND = 'AND'
SHIFTLEFT = 'SHIFTLEFT'
SHIFTRIGHT = 'SHIFTRIGHT'

EOF = 'EOF'

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Lexer(object):
    def __init__(self,text):
        self.text = text
        self.pos = 0
        self.lineNum = 1
        self.linesPos = 0
        self.current_char = self.text[self.pos]
        self.token = None
            

    def error(self):
        print("Invalid character at lineNum: {},position:{},char:{}".format(self.lineNum,self.pos - self.linesPos,self.current_char))
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            if self.current_char == b'x09':
                pass

    def peek_next_token(self):
        pos = self.pos
        current_char = self.current_char
        bakToken = self.token
        token = self.get_next_token()
        self.pos = pos
        self.current_char = current_char
        self.token = bakToken
        return token

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.lineNum += 1
                self.linesPos = self.pos
            self.advance()
    def return_token(self,token):
        self.token = token
        return self.token
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char == '/':
                if self.pos < len(self.text) - 1 and self.text[self.pos + 1] == '/':
                    self.pos = self.text.find('\n', self.pos) + 1
                    self.current_char = self.text[self.pos]
                    self.lineNum+=1
                    self.linesPos = self.pos
                    continue
                elif self.pos < len(self.text) - 1 and self.text[self.pos + 1] == '*':
                    findCommentEnd = False
                    while self.pos < len(self.text) - 1:
                        if self.text[self.pos] == '\n':
                            self.lineNum += 1
                            self.linesPos = self.pos
                        if self.text[self.pos] == '*' and self.text[self.pos + 1] == '/':
                            self.pos = self.pos + 2
                            findCommentEnd = True
                            break
                        self.pos += 1
                    if not findCommentEnd:
                        self.error()
                    self.current_char = self.text[self.pos]
                    continue
            
            if self.current_char == '\"':
                self.advance()
                start_pos = self.pos
                while self.current_char != '\"':
                    self.advance()
                value = self.text[start_pos:self.pos]
                self.advance()
                return self.return_token(Token(STRING, value))
            if  self.current_char == ';':
                self.advance()
                self.token = Token(SEMI,';')
                return self.token
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    self.token = Token(LE, '<=')
                    return self.token
                elif self.current_char == '<':
                    self.advance()
                    self.token = Token(SHIFTLEFT, '<<')
                    return self.token
                else:
                    self.token = Token(LT, '<')
                    return self.token
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    self.token = Token(GE, '>=')
                    return self.token
                elif self.current_char == '>':
                    self.advance()
                    self.token = Token(SHIFTRIGHT, '>>')
                    return self.token
                else:
                    self.token = Token(GT, '>')
                    return self.token
            if self.current_char == '+':
                self.advance()
                if self.token.type == VAR:
                    if self.current_char == '+':
                        self.advance()
                        self.token = Token(PPS, '++')
                        return self.token
                    elif self.current_char == '=':
                        self.advance()
                        self.token = Token(PLUSASSIGN, '+=')
                        return self.token
                    else:
                        self.token = Token(PLUS, '+')
                        return self.token
                elif self.token.type == INTEGER:
                    self.token = Token(PLUS, '+')
                    return self.token
                else:
                    if self.current_char == '+':
                        self.advance()
                        self.token = Token(PPP, '++')
                        return self.token
                    else:
                        self.token = Token(PLUS, '+')
                        return self.token
            if self.current_char == '-':
                self.advance()
                if self.current_char == '-':
                    self.advance()
                    if self.token.type == VAR:
                        self.token = Token(MMS, '--')
                        return self.token
                    else:
                        self.token = Token(MMP, '--')
                        return self.token
                elif self.current_char == '=':
                    self.advance()
                    self.token = Token(MINUSASSIGN, '-=')
                    return self.token
                else:
                    self.token = Token(MINUS, '-')
                    return self.token
            if self.current_char == '*':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    self.token = Token(MULASSIGN, '*=')
                    return self.token
                else:
                    self.token = Token(MUL,'*')
                    return self.token
            if self.current_char == '/':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    self.token = Token(DIVASSIGN, '/=')
                    return self.token
                else:
                    self.token = Token(DIV,'/')
                    return self.token
            if self.current_char == '%':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    self.token = Token(MODASSIGN, '%=')
                    return self.token
                else:
                    self.token = Token(MOD,'%')
                    return self.token
            if self.current_char == '(':
                self.advance()
                self.token = Token(LPAREN, '(')
                return self.token
            if self.current_char == ')':
                self.advance()
                self.token = Token(RPAREN, ')')
                return self.token
            if self.current_char == '{':
                self.advance()
                return self.return_token(Token(LBRACE, '{'))
            if self.current_char == '}':
                self.advance()
                return self.return_token(Token(RBRACE, '}'))
            if self.current_char == '[':
                self.advance()
                return self.return_token(Token(LBRACKET, '['))
            if self.current_char == ']':
                self.advance()
                return self.return_token(Token(RBRACKET, ']'))
            if self.current_char == ':':
                self.advance()
                return self.return_token(Token(COLON, ':'))
            if self.current_char == ',':
                self.advance()
                return self.return_token(Token(COMMA, ','))
            if self.current_char == '#':
                self.advance()
                start_pos = self.pos
                if self.current_char == '-':
                    self.advance()
                while self.current_char.isdigit():
                    self.advance()
                value = self.text[start_pos:self.pos]
                return self.return_token(Token(INTEGER, value))
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return self.return_token(Token(EQ, '=='))
                else:
                    return self.return_token(Token(ASSIGN, '='))
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return self.return_token(Token(NE, '!='))
                else:
                    return self.return_token(Token(NOT, '!'))
            if self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return self.return_token(Token(AND, '&&'))
                else:
                    return self.return_token(Token(BAND, '&'))
            if self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return self.return_token(Token(OR, '||'))
                else:
                    return self.return_token(Token(BOR, '|'))
            if self.current_char == '^':
                self.advance()
                return self.return_token(Token(BXOR, '^'))
            if self.current_char == '~':
                self.advance()
                return self.return_token(Token(BNOT, '~'))
            if self.current_char.isalpha() or self.current_char == '_' or self.current_char.isdigit():
                start_pos = self.pos
                while self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '_' :
                    self.advance()
                value = self.text[start_pos:self.pos]
                if value == 'if':
                    return self.return_token(Token(IF, 'if'))
                elif value == 'break':
                    return self.return_token(Token(BREAK, 'break'))
                elif value == 'case':
                    return self.return_token(Token(CASE, 'case'))
                elif value == 'continue':
                    return self.return_token(Token(CONTINUE, 'continue')       )
                elif value == 'default':
                    return self.return_token(Token(DEFAULT, 'default'))
                elif value == 'do':
                    return self.return_token(Token(DO, 'do'))
                elif value == 'else':
                    return self.return_token( Token(ELSE, 'else'))
                elif value == 'for':
                    return self.return_token(Token(FOR, 'for'))
                elif value == 'False' or value == 'false':
                    return self.return_token(Token(BOOL, 'false'))
                elif value == 'True' or value == 'true':
                    return self.return_token(Token(BOOL, 'true'))
                elif value == 'func':
                    return self.return_token(Token(FUNC, 'func'))
                elif value == 'None':
                    return self.return_token(Token(NONE,'None'))
                elif value == 'return':
                    return self.return_token(Token(RETURN, 'return'))
                elif value == 'switch':
                    return self.return_token(Token(SWITCH, 'switch'))
                elif value == 'while':
                    return self.return_token(Token(WHILE, 'while'))
                elif self.text[start_pos].isalpha() or self.text[start_pos] == '_':
                    if self.text[self.pos] == '(':
                        return self.return_token(Token(FUNCID, value))
                    else:
                        return self.return_token(Token(VAR, value))
                elif re.match(r'[0-9a-fA-F\s]', value):
                    while re.match(r'[0-9a-fA-F\s]', self.current_char):
                        self.advance()
                    value = self.text[start_pos:self.pos]
                    value = value.replace(" ","")
                    if len(value) % 2 == 0:
                        return self.return_token(Token(HEXSTR, value))
            self.error()

        return Token(EOF, None)
