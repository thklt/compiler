import regex
import nfa
import dfa

if __name__ == "__main__":
    re = "AB(CD)*E"
    ast = regex.RegexParser(regex.RegexScanner(re).scan()).parseRegex()
    print(ast)
    nfaGen = nfa.NFAGenerator(ast)
    nfa = nfaGen.generateNFA(nfaGen.root)
    print(nfa)
    dfaGen = dfa.DFAGenerator(nfa)
    # eps = _dfa.epsClosure(set([_nfa.start]))
    # states = set(["s_6", "s_7", "s_8"])
    # delta = _dfa.delta(nfaStates=states, char="B")
    dfa = dfaGen.generateDFA()
    print(dfa)
    

