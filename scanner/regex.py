"""
Implementation of a regex parser that validates a regular expression based on
the below specification. The result of a valid regex will be its syntax tree.

A regex can be built through the hierachically ordered operations closure, 
concatenation, and alternation. The precedence of some operation can also be
enforced by using enclosing parentheses.
"""

from enum import Enum
from sys import stderr

def error(msg: str):
    print(msg, file=stderr)
    exit(1)

class TokenType(Enum):
    ASTERISK = 1 # Closure
    CONCAT = 2 # Concatenation 
    ALTERNATE = 3 # Alternation
    LEFT_PAR = 4 # '('
    RIGHT_PAR = 5 # ')'
    SYMBOL = 6 # some case-sensitive symbol, such as 'a' and 'b'
    EOF = 7 # end of file

class Token:

    def __init__(self, type: TokenType, lexeme: str):
        self.type = type
        self.lexeme = lexeme

    def __str__(self) -> str:
        return f"{self.type.name} '{self.lexeme}'"

class RegexScanner: 

    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.tokens = []

    def scan(self) -> list[Token]:
        while self.index < len(self.text):
            self.tokens.append(self.nextToken())

        self.tokens.append(Token(TokenType.EOF, ""))
        return self.tokens

    def nextChar(self) -> str:
        char = self.text[self.index]
        self.index += 1
        return char

    def nextToken(self) -> Token: # type: ignore

        match self.nextChar():
            case '*':
                return Token(TokenType.ASTERISK, '*')
            # case '.':
            #     return Token(TokenType.CONCAT, '.')
            case '|':
                return Token(TokenType.ALTERNATE, '|')
            case '(':
                return Token(TokenType.LEFT_PAR, '(')
            case ')': 
                return Token(TokenType.RIGHT_PAR, ')')
            case x:
                if x != '.':
                    return Token(TokenType.SYMBOL, x)
                else:
                    error(f"Could not resolve character {x}.")

class RegexAST:

    def __init__(self, token: Token, children: list["RegexAST"]):
        self.token = token
        self.children = children

    def __str__(self) -> str:
        out = ""
        match len(self.children):
            case 0:
                out += str(self.token)
            case 1:
                out += "(" + str(self.token) + str(self.children[0]) + ")"
            case 2:
                out += "(" + str(self.token) + str(self.children[0]) + " " + str(self.children[1]) + ")"
        return out


class RegexParser:

    """
    The regex syntax is as follows:

    regex = alternate
    alternate = concat ('|' concat)*
    # concat = closure ('.' closure)*
    concat = closure (closure)*
    closure = atomic ('*')*
    atomic = symbol | '(' alternate ')'
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def advance(self) -> Token:
        if not self.index < len(self.tokens):
            error("Could not resolve end of input.")
        token = self.tokens[self.index]
        self.index += 1
        return token

    def consume(self, type: TokenType, message: str):
        if not self.advance().type == type:
            print(message)
            exit(1)

    def peek(self) -> Token: # type: ignore
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        error("Peek exceeds boundaries.")

    def parseRegex(self) -> RegexAST:
        ast = self.parseAlternate()

        if self.peek().type != TokenType.EOF:
            error(f"Unexpected token {self.peek()}")

        return ast

    def parseAlternate(self) -> RegexAST:
        left = self.parseConcat()

        while (self.peek().type == TokenType.ALTERNATE):
            operator = self.advance()
            left = RegexAST(operator, [left, self.parseConcat()])

        return left

    def parseConcat(self) -> RegexAST:
        left = self.parseClosure()

        while (
            self.peek().type == TokenType.SYMBOL) or (self.peek().type == TokenType.LEFT_PAR
        ):
            operator = Token(TokenType.CONCAT, "")
            left = RegexAST(operator, [left, self.parseClosure()])

        return left

    def parseClosure(self) -> RegexAST:
        left = self.parseAtomic()

        while self.peek().type == TokenType.ASTERISK:
            operator = self.advance()
            left = RegexAST(operator, [left])

        return left

    def parseAtomic(self) -> RegexAST: # type: ignore
        if self.peek().type == TokenType.LEFT_PAR:
            self.consume(TokenType.LEFT_PAR, "Expected '('")
            ast = self.parseAlternate()
            self.consume(TokenType.RIGHT_PAR, "Expected ')'")
            return ast

        if self.peek().type == TokenType.SYMBOL:
            return RegexAST(self.advance(), [])

        error(f"Expected symbol or '(', got {self.peek()}")

if __name__ == "__main__":
    re1 = "A(B|C)*D"
    scan1 = RegexScanner(re1)
    tokens1 = scan1.scan()
    #print([str(x) for x in tokens1])
    parser1 = RegexParser(tokens1)
    ast = parser1.parseRegex()
    print(ast)

