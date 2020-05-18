# Queli Serrano
# Classes used in Thomson's Construction.

import argparse

class State:
    """A state with one or two edges, all edges labeled by label. """

    # Constructor for the class.
    def __init__(self, label=None, edges=[]):
        # Every state has 0,1, or 2 edges from it.
	self.edges = edges if edges else []
	# Label for the arrows. None means epsilon.
        self.label = label

class Fragment:
    """An NFA fragment with a start state and an accept state. """
    # Contructor
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept 

def shunt(infix):
    """Return the infix regular expression in postfix. """
    # Convert input to a stack-ish list.
    infix = list(infix)[::-1]

    # Operator stack and postfix regular expression
    opers, postfix = [], []

    # Operator precedence.
    prec = {'*' : 100, '.': 80, '|' : 60, '(' : 40, ')' : 20}

    # Loop through the input one character at a time.
    while infix:
        # Pop a character from the input.
        c = infix.pop()

        # Decide what to do based on the character.
        if c == '(':
            # Push an open bracket to the opers stack
            opers.append(c)
        elif c == ')':
            # Pop the operators stack until you find an (.
            while opers[-1] != '(':
                postfix.append(opers.pop())
            # Get rid of the '('.
            opers.pop()
        elif c in prec:
            # Push any operators on the opers stack with higher prec to the output.
            while opers and prec[c] < prec[opers[-1]]:
                postfix.append(opers.pop())
            # Push c to the operator stack.
            opers.append(c)
        else:
            # Typically, we just push the character to the output.
            postfix.append(c)

    # Pop all operators to the output.
    while opers:
        postfix.append(opers.pop())

    # Convert output list to string.
    return ''.join(postfix)

def compile(infix):
    """Return an NFA Fragment representing the infix regular expression."""
    # Convert to infix
    postfix = shunt(infix)
    # Make postfix a stack of characters
    postfix = list(postfix)[::-1]
    # A stack for NFA fragments.
    nfa_stack = []

    while postfix:
        # Pop a character from postfix.
        c = postfix.pop()
        if c == '.':
            # Pop two fragments off the stack
            frag1 = nfa_stack.pop()
            frag2 = nfa_stack.pop()
            # Point frag2 accept state at frag1 start state
            frag2.accept.edges.append(frag1.start)
	    # The new start state is frag2's
	    start = frag2.start
	    # The new accept state is frag1's
	    accept = frag1.accept
        elif c == '|':
            # Pop two fragments off the stack
            frag1 = nfa_stack.pop()
            frag2 = nfa_stack.pop();
            # Create new start and accept states.
            accept = State()
            start = State(edges=[frag2.start, frag1.start])
            # Point the old accept states at the new one
            frag2.accept.edges.append(accept)
            frag1.accept.edges.append(accept)
        elif c == '*':
            # Pop one fragment off the stack.
            frag = nfa_stack.pop()
            # Create new start and accept states.
            accept = State()
            start = State(edges=[frag.start, accept])
            # Point the arrows.
            frag.accept.edges.extend([frag.start, accept])
        else:
            accept = State()
            start = State(label=c,edges=[accept])
	
	# Create new instance of Fragment to represent the new NFA.
	newfrag = Fragment(start, accept)
        # Push the new NFA to the NFA stack.
        nfa_stack.append(newfrag)

    # The NFA stack should have extactly one NFA on it.
    return nfa_stack.pop()

def followes(state, current):
    """Add's a state to a set and follows all of the e(psilon) arrows. """
    # Only do something when we haven't already seen the state. 
    if state not in current:
        # Put the state itself into current.
        current.add(state)
        # See whether state is labelled by e(psilon)
        if state.label is None:
            # Loop through the states pointed to by this state.
            for x in state.edges:
                # Follow all of their e(psillon)s too.)
                followes(x, current)

def match(regex, s):
    """Returns True if and only if the regular expression
       regex fully matches the string s. Returns False otherwise.
    """
    # Compile the regular expression into an NFA.
    nfa = compile(regex)

    # Try to match the regular expression to the string s.
    
    # The current set of state.
    current = set()
    # Add the first state and follow all e(psillon) arrows.
    followes(nfa.start, current)
    # The previous set of states.
    previous = set()

    # Loop through characters in s
    for c in s:
        # Keep track of where we were.
        previous = current
        # Create a new empty set for states we're about to be in
        current = set()
        # Loop through the previous states.
        for state in previous:
            # Only follow arroes not labelled by e(psilon).
            if state.label is not None:
                # If the label of the state is equal to the character we've read.
                if state.label == c:
                    # Add the state at the end of the arrow to current.
                    followes(state.edges[0], current)
                            
    # Ask the NFA if it matches the string s.
    return nfa.accept in current

def Main():
	parser = argparse.ArgumentParser()
	parser.add_argument("regex", help="A regular expression for the string to match", type=str)
	parser.add_argument("strToMatch", help="A string to be compared against the regular expression",\
	 type=str)
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-v", "--verbose", help="Output a verbose version of the result", \
	action="store_true")
	group.add_argument("-q", "--quiet", help="Outputs a quiet version of the result",\
	action="store_true")
	args = parser.parse_args()

	result = match(args.regex,args.strToMatch)
	if args.verbose:
		if result:
			print("The string "+ str(args.strToMatch)+ " is a match for the regex " + str(args.regex))
		else:
			print("The string "+ str(args.strToMatch)+ " does not match the regex " + str(args.regex))
	elif args.quiet:
		print(str(result))
	else:
		print("Match "+args.strToMatch+ " to "+ args.regex +" = " + str(result))

# If module is runned as a script tests will run 
if __name__ == "__main__":
	Main()
	tests = [
	   ["a.b|b*", "bbbbb", True],
	   ["a.b|b*", "bbx", False],
	   ["a.b", "ab", True],
	   ["a.b", "ax", False], 
	   ["b**", "b", True],
	   ["b**", "x", False],
	   ["b*", "", True]
	]
	
	for test in tests:
		assert match(test[0], test[1]) == test[2], test[0] + \
		(" should match " if test[2] else " regex should not match the string") + test[1]
	

