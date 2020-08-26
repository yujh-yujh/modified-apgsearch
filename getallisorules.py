# get-all-iso-rules.py
# Rule computation script for use with Golly.
# Author: Nathaniel Johnston (nathaniel@nathanieljohnston.com), June 2009.
# Updated by: Peter, NASZVADI (), June 2017.
# Updated by: Arie Paap (), February 2018.

# Gives the maximal family of rules that a still life, oscillator, or spaceship
# works under. Must be called while the rule is set of one such family
# For example, to find out what rules a glider works in, first set the rule
# to Life or HighLife, not Seeds.
# Handles nontotalistic rules, too, so it needs Golly 2.8 or newer.
# Nontotalistic rules with B0 only supported by Golly 3.0 or newer.

import golly as g
from glife import validint
from string import replace

Hensel = [
    ['0'],
    ['1c', '1e'],
    ['2a', '2c', '2e', '2i', '2k', '2n'],
    ['3a', '3c', '3e', '3i', '3j', '3k', '3n', '3q', '3r', '3y'],
    ['4a', '4c', '4e', '4i', '4j', '4k', '4n', '4q', '4r', '4t', '4w', '4y', '4z'],
    ['5a', '5c', '5e', '5i', '5j', '5k', '5n', '5q', '5r', '5y'],
    ['6a', '6c', '6e', '6i', '6k', '6n'],
    ['7c', '7e'],
    ['8']
]

# --------------------------------------------------------------------

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

# --------------------------------------------------------------------

def rulestringopt(a):
    result = ''
    context = ''
    lastnum = ''
    lastcontext = ''
    for i in a:
        if i in 'BS':
            context = i
            result += i
        elif i in '012345678':
            if (i == lastnum) and (lastcontext == context):
                pass
            else:
                lastcontext = context
                lastnum = i
                result += i
        else:
            result += i
    result = replace(result, '4aceijknqrtwyz', '4')
    result = replace(result, '3aceijknqry', '3')
    result = replace(result, '5aceijknqry', '5')
    result = replace(result, '2aceikn', '2')
    result = replace(result, '6aceikn', '6')
    result = replace(result, '1ce', '1')
    result = replace(result, '7ce', '7')
    return result

def clearlayer():
    r = g.getrect()
    if r:
        g.select(r)
        g.clear(0)
    if withB0:
        # Needed with B0 rules to ensure pattern runs correctly
        g.setgen('0')
    
clist = []
rule = g.getrule().split(':')[0]

fuzzer = rule + '9'
oldrule = rule
rule = ''
context = ''
deletefrom = []
for i in fuzzer:
    if i == '-':
        deletefrom = [x[1] for x in Hensel[int(context)]]
    elif i in '0123456789/S':
        if deletefrom:
            rule += ''.join(deletefrom)
            deletefrom = []
        context = i
    if len(deletefrom) == 0:
        rule += i
    elif i in deletefrom:
        deletefrom.remove(i)
rule = rule.strip('9')

if not (rule[0] == 'B' and '/S' in rule):
    g.exit('Please set Golly to a Life-like rule.')

withB0 = ('B0' in rule)

if g.empty():
    g.exit('The pattern is empty.')

s = g.getstring('Enter the period:', '', 'Rules calculator')
if not validint(s):
    g.exit('Bad number: %s' % s)

numsteps = int(s)
if numsteps < 1:
    g.exit('Period must be at least 1.')

r = g.getrect()
patt = g.getcells(r)
g.new('')
g.putcells(patt)

for i in range(0, numsteps):
    g.run(1)
    clist.append(g.getcells(g.getrect()))

g.show('Processing...')

ruleArr = rule.split('/')
ruleArr[0] = ruleArr[0].lstrip('B')
ruleArr[1] = ruleArr[1].lstrip('S')

b_need = []
b_OK = []
s_need = []
s_OK = []

context = ''
fuzzed = ruleArr[0] + '9'
for i in fuzzed:
    if i in '0123456789':
        if len(context) == 1:
            b_need += Hensel[int(context)]
            b_OK += Hensel[int(context)]
        context = i
    elif context != '':
        b_need.append(context[0] + i)
        b_OK.append(context[0] + i)
        context += context[0]
context = ''
fuzzed = ruleArr[1] + '9'
for i in fuzzed:
    if i in '0123456789':
        if len(context) == 1:
            s_need += Hensel[int(context)]
            s_OK += Hensel[int(context)]
        context = i
    elif context != '':
        s_need.append(context[0] + i)
        s_OK.append(context[0] + i)
        context += context[0]

for i in [iter2 for iter1 in Hensel for iter2 in iter1]:
    if (not i in b_OK) and (not i == '0'):
        clearlayer()
        g.putcells(patt)
        b_OK.append(i)
        execfor = 1
        # B0 and nontotalistic rulestrings are mutually exclusive in Golly 2.8
        try:
            g.setrule('B' + ''.join(b_OK) + '/S' + ruleArr[1])
        except:
            b_OK.remove(i)
            execfor = 0
        for j in range(0, numsteps * execfor):
            g.run(1)
            try:
                dlist = g.getcells(g.getrect())
                if not(clist[j] == dlist):
                    b_OK.remove(i)
                    break
            except:
                b_OK.remove(i)
                break

    if not i in s_OK:
        clearlayer()
        g.putcells(patt)
        s_OK.append(i)
        g.setrule('B' + ruleArr[0] + '/S' + ''.join(s_OK))
        for j in range(0, numsteps):
            g.run(1)
            try:
                dlist = g.getcells(g.getrect())
                if not(clist[j] == dlist):
                    s_OK.remove(i)
                    break
            except:
                s_OK.remove(i)
                break

    if (i in b_need) and (not i == '0'):
        clearlayer()
        g.putcells(patt)
        b_need.remove(i)
        g.setrule('B' + ''.join(b_need) + '/S' + ruleArr[1])
        for j in range(0, numsteps):
            g.run(1)
            try:
                dlist = g.getcells(g.getrect())
                if not(clist[j] == dlist):
                    b_need.append(i)
                    break
            except:
                b_need.append(i)
                break

    if i in s_need:
        clearlayer()
        g.putcells(patt)
        s_need.remove(i)
        g.setrule('B' + ruleArr[0] + '/S' + ''.join(s_need))
        for j in range(0, numsteps):
            g.run(1)
            try:
                dlist = g.getcells(g.getrect())
                if not(clist[j] == dlist):
                    s_need.append(i)
                    break
            except:
                s_need.append(i)
                break

g.new('')
g.putcells(patt)
g.setrule(oldrule)
b_OK.sort()
s_OK.sort()
b_need.sort()
s_need.sort()
ruleres = 'B' + ''.join(b_need) + '/S' + ''.join(s_need) + \
    ' - B' + ''.join(b_OK) + '/S' + ''.join(s_OK)
ruleres = rulestringopt(ruleres)
numelems = len(b_OK) - len(b_need) + len(s_OK) - len(s_need)
g.show(ruleres)
g.getstring('Pattern works in 2^%d rules:' % numelems, ruleres, 'Rules calculator')
