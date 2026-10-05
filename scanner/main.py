import regex
import nfa
import dfa

if __name__ == "__main__":
    re = "[Z-B]"
    ast = regex.RegexParser(regex.RegexScanner(re).scan()).parseRegex()
    print(ast)
    nfa = nfa.NFAGenerator().generateNFA(ast)
    print(nfa)
    # dfaGen = dfa.DFAGenerator(nfa)
    # # eps = _dfa.epsClosure(set([_nfa.start]))
    # # states = set(["s_6", "s_7", "s_8"])
    # # delta = _dfa.delta(nfaStates=states, char="B")
    # dfa = dfaGen.generateDFA()
    # print(dfa)

    # print(dfa.match("AB"))
    

