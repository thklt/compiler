from nfa import NFAGenerator, NFA
from dfa import DFAGenerator, DFA, DFAMinimizer
from regex import createAST

"""
This module implements a lexer. It lets us generate a scanner based on some 
assignment of tokens to regexes.
"""

def error(msg: str):
    print(msg)
    exit(1)

class Token:

    def __init__(self, type: str, lexeme: str):
        self.type = type
        self.lexeme = lexeme

    def __str__(self) -> str:
        return f"{self.type}('{self.lexeme}')"

class Lexer:

    def __init__(self, file: str="", text: str=""):
        if not (file or text):
            error("Must provide lexing rules as file or as string.")
        if file:
            with open(file, "r") as f:
                ruleString = f.read()
        else:
            ruleString = text

        self.rules: dict[str, str] = {} # dict: regex -> token
        self.precedence: list[str] = [] # token precedence according to input file
        self.nfaGen = NFAGenerator() # need a global instance to have unique state names
        self.dfaGen: DFAGenerator
        self.minimizer: DFAMinimizer
        self.acceptToToken: dict[str, set[str]] = {} # assign each accepting state in the dfa the token(s) it accepts

        self.text: str
        self.index: int
        self.currentState: str
        self.stack: list[str] 

        self.parseRuleString(ruleString)
        self.dfa: DFA = self.combineRegexes()


    """
    Example line:
    [0-9][0-9]* : INTEGER
    The ordering of the rules determins the precedence in case more than one rule matches.
    """
    def parseRuleString(self, text: str) -> dict[str, str]:
        lines = text.splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            split = line.split(":")

            if len(split) != 2:
                error("False input syntax.")

            regex = split[0].strip()
            token = split[1].strip()

            self.rules[regex] = token
            self.precedence.append(token)
            
        return self.rules

    """
    Returns DFA that represents all rules via alternation.
    Each sub accepting state gets linked with its token.
    """
    def combineRegexes(self) -> DFA:
        nfas: list[NFA] = []
        nfaAcceptToToken: dict[str, str] = {}

        # build the nfas for each rule
        for (regex, token) in self.rules.items():
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

        # minimize dfa
        self.minimizer = DFAMinimizer(dfa)

        # custom initial partition that maintains same tokensets of accepting states
        # partition := s_acc | {s_nonacc} and s_acc := {q_0, ..., q_n} where 
        # q_0 to q_n are accepting states with different token sets
        partitionMap: dict[frozenset[str], set[str]] = {}
        for state in dfa.states:
            tokenSet = frozenset(self.acceptToToken.get(state, set()))
            partitionMap.setdefault(tokenSet, set()).add(state)
        partition = {
            frozenset(states) for states in partitionMap.values()
        }
        
        self.minimizer.minimize(startPartition=partition)
        self.minimizer.generateNewDfa()

        # map each dfa state to its token
        newMapping: dict[str, set[str]] = {}
        for (dfaState, tokenSet) in self.acceptToToken.items():
            for (p, newState) in self.minimizer.newDfaMapping.items():
                if dfaState in p:
                    newMapping.setdefault(newState, set()).update(tokenSet)
        self.acceptToToken = newMapping
        # print(len(dfa.states), len(self.minimizer.newDfa.states))
        self.dfa = self.minimizer.newDfa
        
        return self.dfa

    def getToken(self, state: str) -> str: # type: ignore
        if not state in self.dfa.accept:
            error("May only retrieve the token from an accepting state.")
        validTokens = self.acceptToToken[state]
        for token in self.precedence: # precedence
            if token in validTokens:
                return token
        error("Could not retrieve token from accepting state.")

    def nextChar(self) -> str:
        if self.index >= len(self.text):
            return ""
        return self.text[self.index]     
    
    def takeTransition(self, char: str) -> bool:
        if not char in self.dfa.alphabet:
            error(f"Char {repr(char)} not in alphabet {self.dfa.alphabet}.")
        nextState = self.dfa.transition(self.currentState, char)
        if self.dfa.isDeadState(nextState):
            return False
        if not nextState:
            error("Expected Transition.")

        self.currentState = nextState
        self.stack.append(self.currentState)
        self.index += 1
        return True

    def isAcceptingState(self) -> bool:
        return self.currentState in self.dfa.accept

    def rollBack(self):
        while self.stack:
            self.currentState = self.stack.pop()
            self.index -= 1
            if self.isAcceptingState():
                self.index += 1
                return
        error("Rollback failed.")

    """
    Repeatedly get the longest match out of the string.
    """
    def nextToken(self) -> Token: # type: ignore

        self.stack = [] # (char, state)
        self.currentState = self.dfa.start # start state    
        offset = self.index    

        while True:
            char = self.nextChar()

            if not char: # end of input, we can end on an accepting state
                if self.isAcceptingState():
                    return Token(
                        self.getToken(self.currentState), 
                        self.text[offset:self.index]
                    )
                error("Invalid end in input.")
            
            if not self.takeTransition(char): 
                # hit a dead state
                self.rollBack()
                return Token(
                    self.getToken(self.currentState), 
                    self.text[offset:self.index]
                )

    def tokenize(self, text: str) -> list[Token]:
        tokens = []
        self.index = 0
        self.text = text

        while True and self.index < len(self.text):
            token = self.nextToken()                

            if not token:
                break

            if token.type == "WHITE" or token.type == "COMMENT": # ignore white space and comments
                continue

            tokens.append(token)

        return tokens

        

if __name__ == "__main__":
    lexer = Lexer("testAssign.txt")
    dfa = lexer.combineRegexes()
    # print(dfa)
    # print(lexer.acceptToToken)
    text = "Hallo ich heise Thore 123 "
    tokens = lexer.tokenize(text)
    for token in tokens:
        print(f"{token.type}({token.lexeme}) ")
        
