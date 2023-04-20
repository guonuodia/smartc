import _lexer
from _lexer import *

class String(object):
    def __init__(self, token,lineno):
        self.token = token
        self.value = token.value
        self.lineno = lineno

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()
class HexStr(object):
    def __init__(self, token,lineno):
        self.token = token
        self.value = token.value
        self.lineno = lineno

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()
class Num(object):
    def __init__(self, token,lineno):
        self.token = token
        self.value = token.value
        self.lineno = lineno

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()
class Bool(object):
    def __init__(self, token,lineno):
        self.token = token
        self.value = token.value
        self.lineno = lineno

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()
class Var(object):
    def __init__(self, token,lineno):
        self.token = token
        self.value = token.value
        self.lineno = lineno

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()
class HexStrArray(object):
    def __init__(self, token, lineno, start, end,colon = True):
        self.token = token
        self.value = token.value
        self.start = start
        self.end = end
        self.colon = colon
        self.lineno = lineno

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()
class BinOp(object):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return '({left} {op} {right})'.format(
            left=str(self.left),
            op=self.op.value,
            right=str(self.right)
        )

    def __repr__(self):
        return self.__str__()
class SysFunCall(object):
    def __init__(self, sysFun_name, args):
        self.sysFun_name = sysFun_name
        self.args = args

    def __str__(self):
        return '{sysFun_name}({args})'.format(
            sysFun_name=self.sysFun_name,
            args=', '.join(str(arg) for arg in self.args)
        )

    def __repr__(self):
        return self.__str__()
class Assign(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return '({left} = {right})'.format(
            left=str(self.left),
            right=str(self.right)
        )

    def __repr__(self):
        return self.__str__()
class IfStatement(object):
    def __init__(self, condition, if_body,else_body):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

    def __str__(self):
        return 'if ({condition}) {{\n{if_body}\n}} else {{\n{else_body}\n}}'.format(
            condition=str(self.condition),
            if_body=str(self.if_body),
            else_body=str(self.else_body)
        )

    def __repr__(self):
        return self.__str__()
class ForStatement(object):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __str__(self):
        return 'for ({init}; {condition}; {update}) {{\n{body}\n}}'.format(
            init=str(self.init),
            condition=str(self.condition),
            update=str(self.update),
            body=str(self.body)
        )

    def __repr__(self):
        return self.__str__()
class DoWhileStatement(object):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __str__(self):
        return 'do {{\n{body}\n}} while ({condition})'.format(
            condition=str(self.condition),
            body=str(self.body)
        )

    def __repr__(self):
        return self.__str__()
class WhileStatement(object):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __str__(self):
        return 'while ({condition}) {{\n{body}\n}}'.format(
            condition=str(self.condition),
            body=str(self.body)
        )

    def __repr__(self):
        return self.__str__()
class BreakStatement(object):
    def __str__(self):
        return 'break'

    def __repr__(self):
        return self.__str__()

class ContinueStatement(object):
    def __str__(self):
        return 'continue'

    def __repr__(self):
        return self.__str__()

class SwitchStatement(object):
    def __init__(self, condition, cases, default_case=None):
        self.condition = condition
        self.cases = cases
        self.default_case = default_case

    def __str__(self):
        case_str = ""
        for case in self.cases:
            case_str += "case {}: {}\n".format(case[0], str(case[1]))
        if self.default_case:
            case_str += "default: {}\n".format(str(self.default_case))
        return "switch ({}) {{\n{}\n}}".format(str(self.condition), case_str)

    def __repr__(self):
        return self.__str__()

class ReturnStatement(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'return {}'.format(str(self.value))

    def __repr__(self):
        return self.__str__()

class StatementList(object):
    def __init__(self):
        self.statements = []

    def add(self, statement):
        self.statements.append(statement)

class FuncDef:
    def __init__(self, name, args, body, defaults=None):
        self.name = name
        self.args = args
        self.body = body
        self.defaults = [] if defaults is None else defaults

    def __str__(self):
        default_str = ', '.join(str(default) for default in self.defaults)
        if default_str:
            default_str = ', ' + default_str
        return "def {}({}{}):\n{}".format(self.name, ', '.join(self.args), default_str, self.body)

    def __repr__(self):
        return self.__str__()

class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return "FuncCall({}, {})".format(self.name,self.args)

    def __repr__(self):
        return self.__str__()
class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __str__(self):
        return '({op}{expr})'.format(
            op=self.op,
            expr=str(self.expr)
        )

    def __repr__(self):
        return self.__str__()
precedence = {
    '=':2,
    '+=':2,
    '-=':2,
    '*=':2,
    '/=':2,
    '%=':2,
    '||':3,
    '&&':4,
    '|':5,
    '^':6,
    '&':7,
    '==':8,
    '!=':8,
    '>':9,
    '>=':9,
    '<':9,
    '<=':9,
    '<<':10,
    '>>':10,
    '+': 11,
    '-': 11,
    '*': 12,
    '/': 12,
    '%': 12,
}
OPERATORS=[PLUS,MINUS,MUL,DIV,MOD,ASSIGN,PLUSASSIGN,MINUSASSIGN,MULASSIGN,DIVASSIGN,MODASSIGN, EQ,NE,LT,GT,LE,GE,BOR,BXOR,BNOT,BAND,OR,AND,SHIFTLEFT,SHIFTRIGHT]
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.lineno = 1

    def error(self):
        print("Invalid syntax at lineNum: {},position:{},char:{}".format(self.lexer.lineNum,self.lexer.pos - self.lexer.linesPos,self.lexer.current_char))
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
            self.lineno = self.lexer.lineNum
        else:
            self.error()

    def statement(self):
        if self.current_token.type == IF:
            return self.if_statement()
        elif self.current_token.type == FOR:
            return self.for_statement()
        elif self.current_token.type == WHILE:
            return self.while_statement()
        elif self.current_token.type == DO:
            return self.do_while_statement()
        elif self.current_token.type == SWITCH:
            return self.switch_statement()
        else:
            if self.current_token.type == BREAK:
                node = self.break_statement()
            elif self.current_token.type == CONTINUE:
                node = self.continue_statement()
            elif self.current_token.type == RETURN:
                node = self.return_statement()
            else:
                node = self.expr()
            self.eat(SEMI)
            return node
    def return_statement(self):
        self.eat(RETURN)
        value = self.expr()
        return ReturnStatement(value)


    def if_statement(self):
        self.eat(IF)
        self.eat(LPAREN)
        condition = self.expr()
        self.eat(RPAREN)
        if self.current_token.type == LBRACE:
            if_body = self.brace_statement_list()
        else:
            if_body = self.statement()
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            if self.current_token.type == LBRACE:
                else_body = self.brace_statement_list()
            else:
                else_body = self.statement()
        else:
            else_body = None
        return IfStatement(condition, if_body,else_body)

    def for_statement(self):
        self.eat(FOR)
        self.eat(LPAREN)
        init = self.expr()
        self.eat(SEMI)
        condition = self.expr()
        self.eat(SEMI)
        update = self.expr()
        self.eat(RPAREN)
        if self.current_token.type == LBRACE:
            body = self.brace_statement_list()
        else:
            body = self.statement()
            self.eat(SEMI)
        return ForStatement(init, condition, update, body)

    def do_while_statement(self):
        self.eat(DO)
        if self.current_token.type == LBRACE:
            body = self.brace_statement_list()
        else:
            body = self.statement()
        self.eat(WHILE)
        self.eat(LPAREN)
        condition = self.expr()
        self.eat(RPAREN)
        self.eat(SEMI)
        return DoWhileStatement(condition, body)

    def while_statement(self):
        self.eat(WHILE)
        self.eat(LPAREN)
        condition = self.expr()
        self.eat(RPAREN)
        if self.current_token.type == LBRACE:
            body = self.brace_statement_list()
        else:
            body = self.statement()
        return WhileStatement(condition, body)

    def break_statement(self):
        self.eat(BREAK)
        return BreakStatement()
    def continue_statement(self):
        self.eat(CONTINUE)
        return ContinueStatement()
    def switch_statement(self):
        self.eat(SWITCH)
        self.eat(LPAREN)
        condition = self.expr()
        self.eat(RPAREN)
        self.eat(LBRACE)
        cases = []
        default_case = None
        while self.current_token.type != RBRACE:
            if self.current_token.type == CASE:
                self.eat(CASE)
                case_expr = self.expr()
                self.eat(COLON)
                case_body = StatementList()
                while self.current_token.type != CASE and self.current_token.type != DEFAULT and self.current_token.type != RBRACE:
                    case_body.add(self.statement())
                cases.append((case_expr, case_body))
            elif self.current_token.type == DEFAULT:
                self.eat(DEFAULT)
                self.eat(COLON)
                default_case = StatementList()
                while self.current_token.type != RBRACE:
                    default_case.add(self.statement())
            else:
                self.error()
        self.eat(RBRACE)
        return SwitchStatement(condition, cases, default_case)
    def factor(self):
        token = self.current_token
        if token.type == NOT:
            self.eat(NOT)
            return UnaryOp(token, self.factor())
        elif token.type == BNOT:
            self.eat(BNOT)
            return UnaryOp(token, self.factor())
        elif token.type == PPP:
            self.eat(PPP)
            return UnaryOp(token, self.factor())
        elif token.type == MMP:
            self.eat(MMP)
            return UnaryOp(token, self.factor())
        elif token.type == BOOL:
            self.eat(BOOL)
            return Bool(token,self.lineno)
        elif token.type == NONE:
            self.eat(NONE)
            return HexStr(Token(HEXSTR,''),self.lineno)
        elif token.type == STRING:
            self.eat(STRING)
            return String(token,self.lineno)
        elif token.type == HEXSTR:
            self.eat(HEXSTR)
            return HexStr(token,self.lineno)
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token,self.lineno)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        elif token.type == FUNCID:
            self.eat(FUNCID)
            if self.current_token.type == LPAREN:
                self.eat(LPAREN)
                args = []
                if self.current_token.type != RPAREN:
                    args.append(self.expr())
                    while self.current_token.type == COMMA:
                        self.eat(COMMA)
                        args.append(self.expr())
                self.eat(RPAREN)
                return FuncCall(token.value, args)
        elif token.type == VAR and self.lexer.peek_next_token().type == LBRACKET:
            self.eat(VAR)
            self.eat(LBRACKET)
            start = self.expr()
            colon = True
            if self.current_token.type == COLON:
                self.eat(COLON)
                end = self.expr()
            else:
                end = None
                colon = False
            self.eat(RBRACKET)
            return HexStrArray(token, self.lineno, start, end,colon)
        elif token.type == VAR:
            self.eat(VAR)
            return Var(token,self.lineno)
        elif token.type in (ENTER,COMMA,SEMI,COLON,RBRACKET):
            return None
        else:
            self.error()
    def expr(self,pre=0):
        # 解析表达式
        left = self.factor()
        while True:
            token = self.current_token
            if token.type == PPS:
                self.eat(PPS)
                left = UnaryOp(token, left)
                token = self.current_token
            elif token.type == MMS:
                self.eat(MMS)
                left = UnaryOp(token, left)
                token = self.current_token
            elif token.type == ASSIGN:
                self.eat(ASSIGN)
                right = self.expr(0)
                left = Assign(left, right)
                token = self.current_token
            if token.type not in OPERATORS or pre >= precedence[token.value]:
                break
            self.eat(token.type)
            right = self.expr(pre=precedence[token.value])
            left = BinOp(left, token, right)
        return left

    def brace_statement_list(self):
        self.eat(LBRACE)
        node = StatementList()
        while self.current_token.type != RBRACE:
            node.add(self.statement())
        self.eat(RBRACE)
        return node

    def function_definition(self):
        self.eat(FUNC)
        func_name = self.current_token.value
        self.eat(FUNCID)
        self.eat(LPAREN)
        args = []
        kwargs = {}
        if self.current_token.type != RPAREN:
            args.append(self.current_token.value)
            self.eat(VAR)
            if self.current_token.type == ASSIGN:
                self.eat(ASSIGN)
                kwargs[args[-1]] = self.expr()
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                args.append(self.current_token.value)
                self.eat(VAR)
                if self.current_token.type == ASSIGN:
                    self.eat(ASSIGN)
                    kwargs[args[-1]] = self.expr()
        self.eat(RPAREN)
        statements = self.brace_statement_list()
        return FuncDef(func_name, args, statements, kwargs)

    def parse(self):
        node = StatementList()
        while self.current_token.type != EOF:
            if self.current_token.type == FUNC:
                node.add(self.function_definition())
            else:
                node.add(self.statement())
        return node