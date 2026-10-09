"""
Implementation of the Thompson Construction to create an NFA based on the 
Regex AST.
"""

from regex import *

class NFA:

    def __init__(self, start, accept):
        self.states = set()
        self.transitions = dict()
        self.start = start
        self.accept = accept

    def addTransition(self, source, symbol, destination):
        self.states.update([source, destination])
        key = (source, symbol)
        if key not in self.transitions:
            self.transitions[key] = set()
        self.transitions[key].add(destination)

    def printTransitions(self) -> str:
        out = ""
        for (source, symbol), destinations in self.transitions.items():
            out += f"{source}, {symbol} -> {str(destinations)}\n"
        return out

    def __str__(self) -> str:
        out = ""
        out += f"states: {str(self.states)}\n"
        out += f"start: {self.start}\n"
        out += f"accept: {self.accept}\n\n"
        out += self.printTransitions()
        return out

    def getAlphabet(self) -> set[str]:
        alphabet = set()
        for (_, symbol), _ in self.transitions.items():
            alphabet.add(symbol)
        return alphabet - {"eps"}

    """
    Expand a child nfa in their parent.
    """
    def expand(self, child: "NFA"):
        for key, destinations in child.transitions.items():
            self.transitions.setdefault(key, set()).update(destinations)
        self.states |= child.states

            

class NFAGenerator:
    """
    Map each different node of the RegexAST to an NFA. Connect NFAs based on 
    the precedence learned in the AST.
    """

    def __init__(self):
        self.nextState = 0 # global state counter

    def newState(self):
        state = f"s_{self.nextState}"
        self.nextState += 1
        return state

    """
    The NFA is generated via a postorder walk through the AST.
    Each node type is assigned the right NFA structure.
    """
    def generateNFA(self, ast: RegexAST) -> NFA: # type: ignore

        start = self.newState()
        accept = self.newState()
        nfa = NFA(start, accept)

        match len(ast.children):

            case 0: 
                if ast.token.type == TokenType.SYMBOL:
                    # -> s_0 -char-> s_a

                    nfa.addTransition(start, ast.token.lexeme, accept)
                    return nfa

                elif ast.token.type == TokenType.SET:
                    # -> s_0 -char-> s_a for char in set
                    
                    for char in ast.token.lexeme:
                        nfa.addTransition(start, char, accept)
                    return nfa
                
                error("Expected Symbol or Set at Node with no child.")

            case 1:
                childNfa = self.generateNFA(ast.children[0])

                if ast.token.type == TokenType.ASTERISK:
                    #                   \/----eps-----/\
                    # -> s_0 -eps-> s_0_child -?> s_a_child -eps-> s_a
                    #     \/-----------------eps--------------------/\
                    
                    nfa.addTransition(start, "eps", childNfa.start)
                    nfa.addTransition(childNfa.accept, "eps", nfa.accept)
                    nfa.addTransition(nfa.start, "eps", nfa.accept)
                    nfa.addTransition(childNfa.accept, "eps", childNfa.start)

                    nfa.expand(childNfa)

                    return nfa

                error("Expected Closure at Node with no child.")

            case 2:
                leftChildNfa = self.generateNFA(ast.children[0])
                rightChildNfa = self.generateNFA(ast.children[1])

                if ast.token.type == TokenType.CONCAT:
                    # s_0 -eps-> s_0_l_child -?-> s_a_l_child -eps-> s_0_r_child -?-> s_a_r_child -eps-> s_a

                    nfa.addTransition(start, "eps", leftChildNfa.start)
                    nfa.addTransition(leftChildNfa.accept, "eps", rightChildNfa.start)
                    nfa.addTransition(rightChildNfa.accept, "eps", accept)

                    nfa.expand(leftChildNfa)
                    nfa.expand(rightChildNfa)

                    return nfa

                elif ast.token.type == TokenType.ALTERNATE:
                    #   /\-eps-> s_0_l_child -?-> s_a_l_child -eps->\/
                    #  s_0                                          s_a
                    #   \/-eps-> s_0_r_child -?-> s_a_r_child -eps->/\

                    nfa.addTransition(start, "eps", leftChildNfa.start)
                    nfa.addTransition(start, "eps", rightChildNfa.start)
                    nfa.addTransition(leftChildNfa.accept, "eps", accept)
                    nfa.addTransition(rightChildNfa.accept, "eps", accept)

                    nfa.expand(leftChildNfa)
                    nfa.expand(rightChildNfa)

                    return nfa
                    
                error(
                    f"Expected Concatination or Alternation at Node with exactly two children.\n"
                    f"Got {len(ast.children)} children with type {ast.token.type}."
                )

            case _:
                error("Unmatched children.")

if __name__ == "__main__":
    print("Test")