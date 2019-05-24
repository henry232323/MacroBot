import ply.yacc as yacc
import math
import random

from lexer import tokens, precedence

cvars = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "pi": math.pi,

    "int": int,
    "float": float,
    "str": str,

    "rand": random.random,
    "None": None,
    "nil": lambda *args: None,
}

uvars = None


def p_stmt_assign(p):
    'statement : VAR EQUALS expression'
    uvars[p[1]] = p[3]
    p[0] = p[3]
    # print(uvars, p[3])


def p_stmt_exp(p):
    '''statement : expression'''
    if p[1] != None:
        print(repr(p[1]))
    p[0] = p[1]


def p_expr_cassign(p):
    'expression : VAR CEQUALS expression'
    # print(p[1], p[3], uvars)
    uvars[p[1]] = p[3]
    p[0] = p[3]
    # print(uvars)


def p_expression_var(p):
    'expression : VAR'
    try:
        # print(cvars)
        p[0] = uvars[p[1]]
    except KeyError:
        raise NameError(f"Name '{p[1]}' is not defined!") from None


def p_itemlist(p):
    '''itemlist : expression
                | itemlist COMMA expression
                | itemlist COMMA
    '''
    pl = len(p)
    if pl <= 3:
        p[0] = [p[1]]
    elif pl == 4:
        p[1].append(p[3])
        p[0] = p[1]


def p_values(p):
    """tuple : LPAREN itemlist RPAREN
             | LPAREN RPAREN"""
    if len(p) != 3:
        p[0] = tuple(p[2])
    else:
        p[0] = tuple()


def p_call(p):
    """expression : expression tuple %prec CALL"""
    p[0] = p[1](*p[2])


def p_tuple(p):
    """expression : tuple"""
    p[0] = p[1]


def p_expr_uminus(p):
    'expression : SUB expression %prec UMINUS'
    p[0] = -p[2]


def p_expr_uplus(p):
    'expression : ADD expression %prec UPLUS'
    p[0] = +p[2]


def p_expression_add(p):
    'expression : expression ADD expression'
    p[0] = p[1] + p[3]


def p_expression_SUB(p):
    'expression : expression SUB expression'
    p[0] = p[1] - p[3]


def p_expression_mul(p):
    'expression : expression MUL expression'
    if hasattr(p[0], "__iter__"):
        raise TypeError
    if len(str(int(p[1])) + str(int(p[3]))) > 10:
        raise ValueError("Math domain error")
    p[0] = p[1] * p[3]


def p_expression_div(p):
    'expression : expression DIV expression'
    p[0] = p[1] / p[3]


def p_expression_intdiv(p):
    'expression : expression INTDIV expression'
    p[0] = p[1] // p[3]


def p_expression_mod(p):
    'expression : expression MOD expression'
    p[0] = p[1] % p[3]


def p_expression_lt(p):
    'expression : expression LT expression'
    p[0] = p[1] < p[3]


def p_expression_gt(p):
    'expression : expression GT expression'
    p[0] = p[1] > p[3]


def p_expression_le(p):
    'expression : expression LE expression'
    p[0] = p[1] <= p[3]


def p_expression_ge(p):
    'expression : expression GE expression'
    p[0] = p[1] >= p[3]


def p_expression_eq(p):
    'expression : expression EQ expression'
    p[0] = p[1] == p[3]


def p_expression_num(p):
    '''expression : INT
                  | FLOAT
    '''
    p[0] = p[1]


def p_expression_paren(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]


def p_expression(p):
    '''expression : STRING
    '''
    p[0] = p[1]


def p_body(p):
    '''body : body NEWLINE statement
            | statement
            | body NEWLINE
            | NEWLINE body
    '''
    p[0] = p[len(p) - 1]


def p_error(t):
    # print(t)
    raise SyntaxError(f"Syntax error in input! {t}")  # , t[1])


def getparser():
    return yacc.yacc(start="body")


if __name__ == "__main__":
    parser = getparser()
    uvars = {}
    uvars.update(cvars)
    while True:
        try:
            s = input('calc > ') + "\n"
            # print(uvars)
        except EOFError:
            break
        if not s:
            continue
        parser.parse(s)
