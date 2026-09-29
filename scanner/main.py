import regex
import nfa

if __name__ == "__main__":
    re = "AB(CD)*E"
    ast = regex.RegexParser(regex.RegexScanner(re).scan()).parseRegex()
    print(ast)
    nfaGen = nfa.NFAGenerator(ast)
    nfa = nfaGen.generateNFA(nfaGen.root)

    print(nfa)

