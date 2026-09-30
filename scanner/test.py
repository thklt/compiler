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

   