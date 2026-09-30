from dfa import createDFA

def testRegex(regex: str, inputOutput: dict[str, bool]):
    dfa = createDFA(regex)

    for input, output in inputOutput.items():
        result = dfa.match(input)
        assert result == output, f"Regex {regex} with expected {input} -> {output} failed."

if __name__ == "__main__":
    testRegex(
        "(1|2|3)*", {
            "1" : True,
            "2" : True,
            "12": True
        }
    )