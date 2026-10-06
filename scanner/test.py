from dfa import createDFA
from lexer import Lexer, Token

def testRegex(regex: str, inputOutput: dict[str, bool]):
    dfa = createDFA(regex)

    for input, output in inputOutput.items():
        (result, _) = dfa.match(input)
        assert result == output, f"Regex {regex} with expected {input} -> {output} failed."

def testLexer(rules: str, text: str, expected: list[Token]):
    lexer = Lexer(text=rules)
    tokens = lexer.tokenize(text)

    for i, (token, expect) in enumerate(zip(tokens, expected)):
        assert (
            token.type == expect.type and token.lexeme == expect.lexeme
        ), (
            f"Expected {expect.type}({expect.lexeme}) but found {token.type}({token.lexeme}) at position {i}."
        )

testOnRegex = False
testOnLexer = True

if __name__ == "__main__":

    if testOnRegex:
        testRegex(
            "ABC",
            {
                "" : False,  
                "ABC" : True,
                "AB" : False,
                "ABCD" : False,
            }
        )

        testRegex(
            "A*",
            {
                "" : True,
                "A" : True,
                "AA" : True,
                "AB" : False
            }
        )

        testRegex(
            "A|B",
            {
                "" : False,
                "A" : True,
                "AB" : False,
                "B" : True
            }
        )

        testRegex(
            "(A|B)*",
            {
                "" : True,
                "A" : True,
                "AB" : True,
                "B" : True,
                "AABABABB" : True
            }
        )

        testRegex(
            "(AA)*",
            {
                "" : True,
                "A" : False,
                "B" : False,
                "AAAAAA" : True,
                "AAA" : False
            }
        )

        testRegex(
            "(A|AA)",
            {
                "" : False,
                "AA" : True,
                "A" : True,
                "AAA" : False
            }
        )

        testRegex(
            "AB*(C|A)*",
            {
                "" : False,
                "A" : True,
                "AA" : True,
                "ABCA" : True,
                "AC" : True
            }
        )

        testRegex(
            "[ABC]",
            {
                "" : False,
                "A" : True,
                "B" : True,
                "C" : True,
                "D" : False
            }
        )

        testRegex(
            "[ABC]*",
            {
                "" : True,
                "A" : True,
                "ABCCA" : True
            }
        )

        testRegex(
            "AB*(C|A)*[123]*",
            {
                "" : False,
                "A" : True,
                "AA" : True,
                "ABCA" : True,
                "AC" : True,
                "AC123" : True
            }
        )

        testRegex(
            "[1234567890]*",
            {
                "" : True,
                "001" : True,
                "92291283" : True,
                "0x" : False
            }
        )

        testRegex(
            "[0-9]*",
            {
                "" : True,
                "001" : True,
                "92291283" : True,
                "0x" : False
            }
        )

        testRegex(
            "[a-z]*",
            {
                "" : True,
                "hello" : True,
                "world" : True,
                "!" : False
            }
        )

        testRegex(
            "[ ]*",
            {
                "" : True,
                " " : True,
                "  " : True,
                "!" : False,
                " a " : False,
            }
        )

    if testLexer:
        testLexer(
            "[A-Za-z][A-Za-z0-9]* : IDENTIFIER\n"
            "[.?!] : DELIMITER\n"
            "[ ]* : WHITE",

            "This is just one test sentence.!?",
            [
                Token("IDENTIFIER", "This"),
                Token("WHITE", " "),
                Token("IDENTIFIER", "is"),
                Token("WHITE", " "),
                Token("IDENTIFIER", "just"),
                Token("WHITE", " "),
                Token("IDENTIFIER", "one"),
                Token("WHITE", " "),
                Token("IDENTIFIER", "test"),
                Token("WHITE", " "),
                Token("IDENTIFIER", "sentence"),
                Token("DELIMITER", "."),
                Token("DELIMITER", "!"),
                Token("DELIMITER", "?"),
            ]
        )

        testLexer(
                    "int : INT\n"
                    "[A-Za-z][A-Za-z0-9]* : IDENTIFIER\n"
                    "; : SEMICOLON\n"
                    "[0-9]* : INTEGER\n"
                    "= : EQUALS\n"
                    "== : EQUALS_EQUALS\n"
                    "[ ]* : WHITE",
        
                    "int x = 42; x == x;",
                    [
                        Token("INT", "int"),
                        Token("WHITE", " "),
                        Token("IDENTIFIER", "x"),
                        Token("WHITE", " "),
                        Token("EQUALS", "="),
                        Token("WHITE", " "),
                        Token("INTEGER", "42"),
                        Token("SEMICOLON", ";"),
                        Token("WHITE", " "),
                        Token("IDENTIFIER", "x"),
                        Token("WHITE", " "),
                        Token("EQUALS_EQUALS", "=="),
                        Token("WHITE", " "),
                        Token("IDENTIFIER", "x"),
                        Token("SEMICOLON", ";"),
                    ]
                )