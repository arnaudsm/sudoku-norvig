## Solveur de Sudokus

##   ligne     exemple: 'A'
##   colonne   exemple: '3'
##   carre     exemple: 'A3'
##   chiffre   exemple: '9'
##   case      exemple: ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grille    exemple: '.18...7....................'
##   valeurs est un dict des valeurs possibles, exemple: {'A1':'12349', 'A2':'8', ...}

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

chiffres   = '123456789'
lignes     = 'ABCDEFGHI'
cols     = chiffres
carres  = cross(lignes, cols)
caselist = ([cross(lignes, colonne) for colonne in cols] +
            [cross(ligne, cols) for ligne in lignes] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
cases = dict((carre, [case for case in caselist if carre in case])
             for carre in carres)
peers = dict((carre, set(sum(cases[carre],[]))-set([carre]))
             for carre in carres)

################ Lecture de Grille ################

def parse_grille(grille):
    """Convertir une grille en dict de valeurs possibles, 
    ou retourner False si une contradiction est detectee"""
    ## Pour commencer, chaque carre peut etre n'importe quel chiffre,
    ## puis on assigne des valeurs depuis la grille
    valeurs = dict((carre, chiffres) for carre in carres)
    for carre,chiffre in grille_valeurs(grille).items():
        if chiffre in chiffres and not assign(valeurs, carre, chiffre):
            return False ## Echec si on ne peut ne peut assigner de chiffre
    return valeurs

def grille_valeurs(grille):
    "Convert grille into a dict of {carre: char} with '0' or '.' for empties."
    chars = [colonne for colonne in grille if colonne in chiffres or colonne in '0.']
    assert len(chars) == 81
    return dict(zip(carres, chars))

################ Propagation de Contrainte  ################

def assign(valeurs, carre, chiffre):
    """ Eliminer toutes les autres valeurs et propager.
    Retourner valeurs, ou False si une contradication est detectee """
    autres_valeurs = valeurs[carre].replace(chiffre, '')
    if all(eliminer(valeurs, carre, d2) for d2 in autres_valeurs):
        return valeurs
    else:
        return False

def eliminer(valeurs, carre, chiffre):
    """ Eliminer le chiffre de valeurs[carre]; propager si valeurs ou places<=2 """
    if chiffre not in valeurs[carre]:
        return valeurs ## Deja elimine
    valeurs[carre] = valeurs[carre].replace(chiffre,'')
    ## (1) If a carre carre is reduced to one value d2, then eliminer d2 from the peers.
    if len(valeurs[carre]) == 0:
        return False ## Contradiction: removed last value
    elif len(valeurs[carre]) == 1:
        d2 = valeurs[carre]
        if not all(eliminer(valeurs, s2, d2) for s2 in peers[carre]):
            return False
    ## (2) If a case case is reduced to only one place for a value d, then put it there.
    for case in cases[carre]:
        dplaces = [carre for carre in case if chiffre in valeurs[carre]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # chiffre can only be in one place in case; assign it there
            if not assign(valeurs, dplaces[0], chiffre):
                return False
    return valeurs

################ Affichage joli  ################

def display(valeurs):
    width = 1+max(len(valeurs[carre]) for carre in carres)
    line = '+'.join(['-'*(width*3)]*3)
    for ligne in lignes:
        print ''.join(valeurs[ligne+colonne].center(width)+('|' if colonne in '36' else '')
                      for colonne in cols)
        if ligne in 'CF': print line
    print

################ Search ################

def solve(grille): return search(parse_grille(grille))

def search(valeurs):
    """ En utilisant une recherche-propagation, essayer toutes les valeurs possibles """
    if valeurs is False:
        return False ## Failed earlier
    if all(len(valeurs[carre]) == 1 for carre in carres):
        return valeurs ## Solved!
    ## Chose the unfilled carre carre with the fewest possibilities
    n,carre = min((len(valeurs[carre]), carre) for carre in carres if len(valeurs[carre]) > 1)
    return some(search(assign(valeurs.copy(), carre, chiffre))
                for chiffre in valeurs[carre])

################ Utilities ################

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False

def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return file(filename).read().strip().split(sep)

def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

import time, random

def solve_all(grilles, name='', showif=0.0):
    """Attempt to solve a sequence of grilles. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""
    def time_solve(grille):
        start = time.clock()
        valeurs = solve(grille)
        t = time.clock()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grille_valeurs(grille))
            if valeurs: display(valeurs)
            print '(%.2f secondes)\n' % t
        return (t, solved(valeurs))
    times, results = zip(*[time_solve(grille) for grille in grilles])
    N = len(grilles)
    if N > 1:
        print "%d / %d puzzles %s resolus (total. %.2fs, moy. %.2f secs (%d Hz), max %.2f secs)." % (
            sum(results), N, name,sum(times), sum(times)/N, N/sum(times), max(times))

def solved(valeurs):
    "A puzzle is solved if each case is a permutation of the chiffres 1 to 9."
    def casesolved(case): return set(valeurs[carre] for carre in case) == set(chiffres)
    return valeurs is not False and all(casesolved(case) for case in caselist)

def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    valeurs = dict((carre, chiffres) for carre in carres)
    for carre in shuffled(carres):
        if not assign(valeurs, carre, random.choice(valeurs[carre])):
            break
        ds = [valeurs[carre] for carre in carres if len(valeurs[carre]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(valeurs[carre] if len(valeurs[carre])==1 else '.' for carre in carres)
    return random_puzzle(N) ## Laisser tomber et refaire un puzzle

grille1  = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grille2  = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1  = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
    