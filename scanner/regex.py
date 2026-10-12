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

    LEFT_BRACK = 8 # '['
    RIGHT_BRACK = 9 # ']'
    SET = 10 # holds a set of possible chars

    PLUS = 11 # finite closure
    QUESTIONMARK = 12 # allow once

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
        char = self.nextChar()

        if char == "\\": # escape character
            if not self.index < len(self.text):
                error("Missing escape character after \\.")

            nextChar = self.nextChar()
            escapeMap = {
                "n" : "\n",
                "t" : "\t",
                "+" : "+"
            }

            if not nextChar in escapeMap:
                error(f"Unknown escape sequence \\{nextChar}.")

            return Token(TokenType.SYMBOL, escapeMap[nextChar])

        match char:
            case '*':
                return Token(TokenType.ASTERISK, '*')
            case '|':
                return Token(TokenType.ALTERNATE, '|')
            case '(':
                return Token(TokenType.LEFT_PAR, '(')
            case ')': 
                return Token(TokenType.RIGHT_PAR, ')')
            case '[':
                return Token(TokenType.LEFT_BRACK, '[')
            case ']':
                return Token(TokenType.RIGHT_BRACK, ']')
            case '+':
                return Token(TokenType.PLUS, '+')
            case '?':
                return Token(TokenType.QUESTIONMARK, '?')
            case x:
                return Token(TokenType.SYMBOL, x)
            

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
    concat = closure (closure)*
    closure = atomic ( ('*')* | ('+')* | ('?')* )
    atomic = symbol | '(' alternate ')' | '[' set ']'
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

    def peek(self, ahead: int = 0) -> Token: # type: ignore
        if 0 <= self.index + ahead < len(self.tokens):
            return self.tokens[self.index + ahead]
        error("Peek exceeds boundaries.")

    def previous(self) -> Token: # type: ignore
        if 0 < self.index <= len(self.tokens):
            return self.tokens[self.index - 1]
        error("Previous exceeds boundaries.")

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

        # because concatenation is encoded symbollessly we must check valid
        # next tokens at this point
        while self.peek().type in {
            TokenType.SYMBOL,
            TokenType.LEFT_PAR,
            TokenType.LEFT_BRACK,
        }:
            operator = Token(TokenType.CONCAT, "")
            left = RegexAST(operator, [left, self.parseClosure()])

        return left

    def parseClosure(self) -> RegexAST:
        left = self.parseAtomic()

        if self.peek().type == TokenType.ASTERISK:
            while self.peek().type == TokenType.ASTERISK:
                operator = self.advance()
                left = RegexAST(operator, [left])
        elif self.peek().type == TokenType.PLUS:
            while self.peek().type == TokenType.PLUS:
                self.advance()
                # x+ = xx*
                atomic = left
                left = RegexAST(
                    Token(TokenType.CONCAT, ""), [
                        atomic, RegexAST(Token(TokenType.ASTERISK, "*"), [
                            atomic
                    ])
                ])
        elif self.peek().type == TokenType.QUESTIONMARK:
            while self.peek().type == TokenType.QUESTIONMARK:
                self.advance()
                # x? = x | eps 
                atomic = left
                left = RegexAST(
                    Token(TokenType.ALTERNATE, "|"), [atomic, RegexAST(Token(TokenType.SYMBOL, "eps"), [])]
                )

        return left

    def parseAtomic(self) -> RegexAST: # type: ignore
        if self.peek().type == TokenType.LEFT_PAR:
            self.consume(TokenType.LEFT_PAR, "Expected '('")
            ast = self.parseAlternate()
            self.consume(TokenType.RIGHT_PAR, "Expected ')'")
            return ast

        elif self.peek().type == TokenType.SYMBOL:           
            return RegexAST(self.advance(), [])

        elif self.peek().type == TokenType.LEFT_BRACK:
            self.consume(TokenType.LEFT_BRACK, "Expected '['")
            ast = self.parseSet()
            self.consume(TokenType.RIGHT_BRACK, "Expected ']'")
            return ast

        error(f"Expected symbol or '(' or '[', got {self.peek()}")

    # the node stores the valid chars in the lexeme
    def parseSet(self) -> RegexAST:
        if self.peek().type == TokenType.RIGHT_BRACK:
            error("Character set cannot be empty.")

        lexeme = ""
        while self.peek().type != TokenType.RIGHT_BRACK:
            if self.peek().type != TokenType.SYMBOL:
                error("Expected only symbols in set.")

# yes, this part is a little "crafty" and I should probably do it better
# better idea: in a loop, parse with max. lookahead of 3, if there was a '-', or return after first char
            if self.peek().lexeme == '-': # ranged character set
                previous = self.previous()
                next = self.peek(ahead=1)
                if previous.type != TokenType.SYMBOL or next.type != TokenType.SYMBOL:
                    error(f"Invalid range in character set '{self.peek().lexeme}'.")

                chars = [ 
                    chr(i) for i in 
                    range(ord(previous.lexeme[0]), ord(next.lexeme[0]) + 1)
                ]
                for char in chars:
                    lexeme += char

                self.advance()
                self.advance()

                continue
            
            lexeme += self.advance().lexeme

        return RegexAST(Token(TokenType.SET, lexeme), [])

def createAST(regex: str) -> RegexAST:
    return RegexParser(RegexScanner(regex).scan()).parseRegex()

if __name__ == "__main__":
    re1 = "A(B|C)*D"
    scan1 = RegexScanner(re1)
    tokens1 = scan1.scan()
    #print([str(x) for x in tokens1])
    parser1 = RegexParser(tokens1)
    ast = parser1.parseRegex()
    print(ast)

