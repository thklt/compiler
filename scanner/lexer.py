from nfa import NFAGenerator, NFA
from dfa import DFAGenerator, DFA
from regex import createAST

"""
This module implements a lexer. It lets us generate a scanner based on some 
assignment of tokens to regexes.
"""

def error(msg: str):
    print(msg)
    exit(1)

class Lexer:

    def __init__(self, file: str):
        self.file = file # source file that specifies tokens and regexes
        self.assignment: dict[str, str] = {} # dict: regex -> token
        self.nfaGen = NFAGenerator() # need a global instance to have unique state names
        self.dfaGen: DFAGenerator
        self.acceptToToken: dict[str, set[str]] = {} # assign each accepting state in the dfa the token(s) it accepts

    """
    Example line:
    [0-9][0-9]* : INTEGER
    """
    def parseFile(self) -> dict[str, str]:
        file = open(self.file, "r")
        for line in file:
            split = line.split(":")
            if len(split) != 2:
                error("False input syntax.")
            regex = split[0].strip()
            token = split[1].strip()
            self.assignment[regex] = token
        return self.assignment

    """
    Returns DFA that represents all rules via alternation.
    Each sub accepting state gets linked with its token.
    """
    def combineRegexes(self) -> DFA:
        nfas: list[NFA] = []
        nfaAcceptToToken: dict[str, str] = {}

        # build the nfas for each rule
        for (regex, token) in self.assignment.items():
            ast = createAST(regex)
            nfa = self.nfaGen.generateNFA(ast)
            nfas.append(nfa)
            nfaAcceptToToken[nfa.accept] = token # link with token

        # combine all nfas via alternation
        newNfa = NFA(self.nfaGen.newState(), self.nfaGen.newState())
        for nfa in nfas:
            newNfa.addTransition(newNfa.start, "eps", nfa.start)
            nfa.addTransition(nfa.accept, "eps", newNfa.accept)

            newNfa.expand(nfa)

        # use the dfa generator's internal mapping to map each dfa state to its token
        self.dfaGen = DFAGenerator(newNfa)
        dfa = self.dfaGen.generateDFA()
        for (nfaState, token) in nfaAcceptToToken.items():
            for (nfaConfig, dfaState) in self.dfaGen.dfaStates.items():
                if nfaState in nfaConfig:
                    self.acceptToToken.setdefault(dfaState, set()).update([token])

        return dfa

        

if __name__ == "__main__":
    lexer = Lexer("testAssign.txt")
    assignment = lexer.parseFile()
    dfa = lexer.combineRegexes()
    print(lexer.acceptToToken)
    (succ, state) = dfa.match("test")
    if (succ):
        print(lexer.acceptToToken[state])

        
