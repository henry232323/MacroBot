import ply.lex as lex

tokens = (
    'INT',
    'FLOAT',
    'STRING',
    'VAR',

    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'INTDIV',
    'MOD',

    'LT',
    'GT',
    'LE',
    'GE',
    'EQ',

    'EQUALS',
    'CEQUALS',

    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',

    'COMMA',
    'COMMENT',
    'NEWLINE'
)

t_VAR = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_EQUALS = r'='
t_COMMA = r','
t_CEQUALS = r':='
t_EQ = r'=='
t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'/'
t_MOD = r'%'
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_INTDIV = r'//'

precedence = (
    ('nonassoc', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV', 'MOD', 'INTDIV'),
    ('right', 'UMINUS', 'UPLUS'),
    ('left', 'CALL'),
)

import re
import codecs

ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


paren_count = 0


def t_STRING(t):
    r'b?r?f?\'\'\'[\s\S]*?\'\'\'|b?r?f?\"\"\"[\s\S]*?\"\"\"|b?r?f?\"[^\n\r]*?\"|b?r?f?\'[^\n\r]*?\''
    t.value = decode_escapes(t.value)[1:-1]
    return t


def t_FLOAT(t):
    r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
    if '.' not in t.value and 'e' not in t.value and 'E' not in t.value:
        t.value = int(t.value)
    else:
        t.value = float(t.value)
    return t


def t_INT(t):
    r'[-+]?\d+'
    t.value = int(t.value)
    return t


def t_newline(t):
    r'[\n\r]+'
    t.lexer.lineno += t.value.count("\n")
    t.type = "NEWLINE"
    if paren_count == 0:
        return t


def t_LPAREN(t):
    r"""\("""
    global paren_count
    paren_count += 1
    return t


def t_RPAREN(t):
    r'\)'
    global paren_count
    paren_count -= 1
    return t


def t_LBRACE(t):
    r'\{\n*'
    global paren_count
    paren_count += 1
    return t


def t_RBRACE(t):
    r'\}'
    global paren_count
    paren_count -= 1
    return t


def t_LBRACKET(t):
    r'\['
    global paren_count
    paren_count += 1
    return t


def t_RBRACKET(t):
    r'\]'
    global paren_count
    paren_count -= 1
    return t


t_ignore = " \t"
t_ignore_COMMENT = r'\#.*'


def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' on line {t.lexer.lineno}")


lexer = lex.lex()
