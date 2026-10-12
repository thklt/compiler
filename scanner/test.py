from dfa import createDFA, DFAMinimizer
from lexer import Lexer, Token

def testRegex(regex: str, inputOutput: dict[str, bool]):
    dfa = createDFA(regex)
    minimizer = DFAMinimizer(dfa)
    minimizer.minimize()
    minimizer.generateNewDfa()
    dfa = minimizer.newDfa

    for input, output in inputOutput.items():
        (result, _) = dfa.match(input)
        assert result == output, f"Regex {regex} with expected {input} -> {output} failed."

def testLexer(rules: str, text: str, expected: list[Token]):
    lexer = Lexer(text=rules)
    tokens = lexer.tokenize(text)

    if len(tokens) != len(expected):
        print(f"{text}: Missmatching lengths: given has length {len(tokens)} and expected has length {len(expected)}.")
        exit(1)
    for i, (token, expect) in enumerate(zip(tokens, expected)):
        assert (
            token.type == expect.type and token.lexeme == expect.lexeme
        ), (
            f"{text}: Expected {expect.type}({expect.lexeme}) but found {token.type}({token.lexeme}) at position {i}."
        )

testOnRegex = False
testOnLexer = False

if __name__ == "__main__":

    if testOnRegex:
        testRegex(
            r"ABC",
            {
                "" : False,
                "ABC" : True,
                "AB" : False,
                "ABCD" : False,
            }
        )

        testRegex(
            r"A*",
            {
                "" : True,
                "A" : True,
                "AA" : True,
                "AB" : False
            }
        )

        testRegex(
            r"A|B",
            {
                "" : False,
                "A" : True,
                "AB" : False,
                "B" : True
            }
        )

        testRegex(
            r"(A|B)*",
            {
                "" : True,
                "A" : True,
                "AB" : True,
                "B" : True,
                "AABABABB" : True
            }
        )

        testRegex(
            r"(AA)*",
            {
                "" : True,
                "A" : False,
                "B" : False,
                "AAAAAA" : True,
                "AAA" : False
            }
        )

        testRegex(
            r"(A|AA)",
            {
                "" : False,
                "AA" : True,
                "A" : True,
                "AAA" : False
            }
        )

        testRegex(
            r"AB*(C|A)*",
            {
                "" : False,
                "A" : True,
                "AA" : True,
                "ABCA" : True,
                "AC" : True
            }
        )

        testRegex(
            r"[ABC]",
            {
                "" : False,
                "A" : True,
                "B" : True,
                "C" : True,
                "D" : False
            }
        )

        testRegex(
            r"[ABC]*",
            {
                "" : True,
                "A" : True,
                "ABCCA" : True
            }
        )

        testRegex(
            r"AB*(C|A)*[123]*a+b?",
            {
                "" : False,
                "Aa" : True,
                "AAa" : True,
                "ABCAab" : True,
                "ABCAabb" : False,
                "ACaa" : True,
                "AC123a" : True
            }
        )

        testRegex(
            r"[1234567890]*",
            {
                "" : True,
                "001" : True,
                "92291283" : True,
                "0x" : False
            }
        )

        testRegex(
            r"[0-9]*",
            {
                "" : True,
                "001" : True,
                "92291283" : True,
                "0x" : False
            }
        )

        testRegex(
            r"[a-z]*",
            {
                "" : True,
                "hello" : True,
                "world" : True,
                "!" : False
            }
        )

        testRegex(
            r"[ ]*",
            {
                "" : True,
                " " : True,
                "  " : True,
                "!" : False,
                " a " : False,
            }
        )

        testRegex(
            r"a+",
            {
                "" : False,
                "b" : False,
                "a" : True,
                "aaa" : True,
            }
        )

        testRegex(
            r"(a+)*",
            {
                "" : True,
                "b" : False,
                "a" : True,
                "aaa" : True,
            }
        )

        testRegex(
            r"a?",
            {
                "" : True,
                "b" : False,
                "a" : True,
                "aaa" : False,
            }
        )

    if testLexer:
        testLexer(
            r"""
                [A-Za-z][A-Za-z0-9]* : IDENTIFIER
                [.!] : DELIMITER
                [ ]* : WHITE
            """,

            "This is just one test sentence.!",
            [
                Token("IDENTIFIER", "This"),
                Token("IDENTIFIER", "is"),
                Token("IDENTIFIER", "just"),
                Token("IDENTIFIER", "one"),
                Token("IDENTIFIER", "test"),
                Token("IDENTIFIER", "sentence"),
                Token("DELIMITER", "."),
                Token("DELIMITER", "!"),
            ]
        )

        testLexer(
            r"""
                int : INT
                [A-Za-z][A-Za-z0-9]* : IDENTIFIER
                ; : SEMICOLON
                [0-9]* : INTEGER
                = : EQUALS
                == : EQUALS_EQUALS
                [ \n]+ : WHITE
            """,
            """int x = 42; x == x;
int""",
            [
                Token("INT", "int"),
                Token("IDENTIFIER", "x"),
                Token("EQUALS", "="),
                Token("INTEGER", "42"),
                Token("SEMICOLON", ";"),
                Token("IDENTIFIER", "x"),
                Token("EQUALS_EQUALS", "=="),
                Token("IDENTIFIER", "x"),
                Token("SEMICOLON", ";"),
                Token("INT", "int")
            ]
        )

lexer = Lexer(file="CTokens")
with open("test.src", "r") as f:
    tokens = lexer.tokenize(f.read())
    for token in tokens:
        print(token)