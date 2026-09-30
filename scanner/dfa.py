"""
Implementation of the Subset Construction to construct DFAs from NFAs. This makes
the simulation easier.
"""

from nfa import *

class DFA:

    def __init__(self):
        self.start = ""
        self.accept = set()
        self.states = set()
        self.transitions = dict()

    def printTransitions(self) -> str:
        out = ""
        for (source, symbol), destination in self.transitions.items():
            out += f"{source}, {symbol} -> {str(destination)}\n"
        return out

    def __str__(self) -> str:
        out = ""
        out += f"states: {str(self.states)}\n"
        out += f"start: {self.start}\n"
        out += f"accept: {self.accept}\n\n"
        out += self.printTransitions()
        return out

    def transition(self, currentState: str, char: str) -> str | None:
        if (currentState, char) in self.transitions:
            return self.transitions[(currentState, char)]
        return None

    def match(self, s: str) -> bool:
        currentState = self.start

        for char in s:
            nextState = self.transition(currentState, char)
            if not nextState: # pattern matching failed
                return False
            currentState = nextState
        # input fully consumed

        if not currentState in self.accept: # must end in accepting state
            return False

        return True
    

class DFAGenerator:

    def __init__(self, nfa: NFA):
        self.nfa = nfa
        self.nextState = 0

    def newState(self):
        state = f"s_{self.nextState}"
        self.nextState += 1
        return state

    """
    This function returns a set of all NFA states reachable from the input set 
    following only epsilon transitions.
    """
    def epsClosure(self, nfaStates: set[str]) -> set[str]:
        reachable = set(nfaStates)
        stack = list(nfaStates)

        while stack:
            state = stack.pop()

            for (_state, symbol), destinations in self.nfa.transitions.items():

                if _state != state or symbol != "eps":
                    continue

                for destination in destinations:
                    if destination not in reachable:
                        reachable.add(destination)
                        stack.append(destination)

        return reachable

    """
    This function simulates the delta transition function of an NFA, the input 
    NFA states should encode one configuration of the automaton.
    """
    def delta(self, nfaStates: frozenset[str], char: str) -> set:
        reachable = set()
        for state in nfaStates:
            key = (state, char)
            if key in self.nfa.transitions:
                reachable |= self.nfa.transitions[key]
        return reachable

    """
    This function builds the DFA and returns it. It uses the Subset Construction.
    """
    def generateDFA(self) -> DFA:
        dfa = DFA()

        Q, T = self.subsetConstruction()

        # build the states
        dfaStates = {}
        for q in Q:
            d = self.newState()
            dfaStates[q] = d # create a mapping from configurations to new DFA states
            dfa.states.add(d)
            if self.nfa.start in q: # is start configuration?
                dfa.start = d
            if self.nfa.accept in q: # is accepting configuration?
                dfa.accept.add(d)

        # build the transitions
        for (q, char), qNext in T.items():
            d = dfaStates[q]
            dNext = dfaStates[qNext]
            dfa.transitions[(d, char)] = dNext

        return dfa

    """
    The Subset Construction.
    """
    def subsetConstruction(self) -> tuple[set, dict]:
        q_0 = frozenset(self.epsClosure({self.nfa.start})) # the start configuration
        
        Q = {q_0}
        T = {}
        worklist = [q_0]
        alphabet = self.nfa.getAlphabet()

        while worklist:
            q = worklist.pop()

            for char in alphabet:
                t = frozenset(self.epsClosure(self.delta(q, char)))
                T[(q,char)] = t

                if t not in Q:
                    Q.add(t)
                    worklist.append(t)

        return (Q, T)

def createDFA(regex: str) -> DFA:
    scanner = RegexScanner(regex)
    parser = RegexParser(scanner.scan())
    ast = parser.parseRegex()
    nfa = NFAGenerator(ast).generateNFA(ast)
    dfa = DFAGenerator(nfa).generateDFA()

    return dfa
    
