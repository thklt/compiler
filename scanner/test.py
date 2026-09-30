from dfa import createDFA

def testRegex(regex: str, inputOutput: dict[str, bool]):
    dfa = createDFA(regex)

    for input, output in inputOutput.items():
        result = dfa.match(input)
        assert result == output, f"Regex {regex} with expected {input} -> {output} failed."

if __name__ == "__main__":
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