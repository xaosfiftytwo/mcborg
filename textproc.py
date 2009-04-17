#!/usr/bin/env python

# detect matching pairs of brackets in a string
# if matching brackets found, delete them from string
# if no match, then retain the bracket (smiley?)

# define the matching pairs
bm = { '}': '{', 
       ']': '[', 
       ')': '(', 
       '>': '<' }

def bracket_balance(s):
    # initialize the stack to an empty list
    blist = []
    balanced = True
    # ilist is list of indexes in the original string of matching brackets
    ilist = []
    for (index, c) in enumerate(s):
        # If c is an open bracket of any type, place on stack
        if c in bm.values():
            blist.append((index,c))
	# If it is a close bracket, pull one off the stack and
	# see if they are matching open-close pairs.  If the stack
	# is empty, there was no matching open.  Return false in that
	# case, or if they don't match.
        if c in bm.keys():
            try:
                (spam, foo) = blist.pop()
                if foo != bm[c]:
                    balanced = False
                else:
                    ilist.append(spam)
                    ilist.append(index)
            except IndexError: 
                balanced = False
    # End of the line: if we still have brackets on the stack, we
    # didn't have enough close brackets.  Return false.
    if blist != []: 
        balanced = False
    # If we got here, the stack is empty, and there are no brackets
    # left unmatched.  we're good!
    return (balanced, ilist)

def removed_balanced_brackets(s):
    (balanced, ilist) = bracket_balance(s)
    silist = sorted(ilist)
    del ilist

    pieces=[]
    oldspam = -1
    for spam in silist:
        pieces.append(s[oldspam+1:spam])
        oldspam = spam
    pieces.append(s[oldspam+1:])
    return ''.join(pieces)

import re
def multiple_replace(text, adict):
    """
    Replace muliple patterns in a single pass over a string
    """
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)


if __name__ == '__main__':
    tests="""
  { this is a test  BAD
  < this is a test > OK
  { this is a test } { this is a test } OK
  { this is a test } [ this { this is a test } is a test ] OK
  { this is a test  { this { this is a test } is a test } missing close BAD
  { a test  BAD
  { a test } OK
  { a test ] [ a test } BAD
  { a test } { this { a test } is a test } OK
  { a test  { this { a test ] is a test } missing close [}} BAD
  { a test  { this { a test ] is a test } missing close } BAD
  { a test  ] this { a test } is a test } missing close [ BAD
  a test } { this { a test } is a test } BAD
  { a test } this { a test } is a test } BAD
""".splitlines()[1:]

    for test in tests:
        print "Testing %s:" % test
        print "        %s" % removed_balanced_brackets(test)
        print "\n-------\n"
