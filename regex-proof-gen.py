from dataclasses import dataclass

@dataclass(frozen=True)
class Regex:
    pass

@dataclass(frozen=True, order=True)
class EmptySet(Regex):
    def __str__(self):
        return 'empty'

@dataclass(frozen=True, order=True)
class Epsilon(Regex):
    def __str__(self):
        return 'epsilon'

@dataclass(frozen=True, order=True)
class Letter(Regex):
    name : str

    def __str__(self):
        return self.name

a = Letter('a')
b = Letter('b')

@dataclass(frozen=True, order=True)
class Concat(Regex):
    left: Regex
    right: Regex

    def __str__(self):
        return '[' + str(self.left) + ' ' + str(self.right) + ']'

@dataclass(frozen=True, order=True)
class Choice(Regex):
    left: Regex
    right: Regex

    def __str__(self):
        match self.left:
            case Not(l):
                return '(' + str(self.left) + ' -> ' + str(self.right) + ')'
            case _:
                return '(' + str(self.left) + ' + ' + str(self.right) + ')'

@dataclass(frozen=True, order=True)
class Kleene(Regex):
    exp: Regex

    def __str__(self):
        return '(' + str(self.exp) + ')*'

@dataclass(frozen=True, order=True)
class Not(Regex):
    exp: Regex

    def __str__(self):
        return '~' + str(self.exp)

def implies(l: Regex, r: Regex) -> Regex:
    return Choice(Not(l), r)


regex_types = [EmptySet, Epsilon, Letter, Concat, Choice, Kleene, Not, ]
def less_than(e1: Regex, e2: Regex) -> bool:
    t1 = type(e1)
    t2 = type(e2)
    assert t1 in regex_types
    assert t2 in regex_types
    if t1 == t2:
        return e1 < e2 # type: ignore
    return regex_types.index(t1) < regex_types.index(t2)


def has_ewp(exp: Regex) -> bool:
    match exp:
        case EmptySet(): return False
        case Epsilon(): return True
        case Letter(_): return False
        case Concat(l, r):  return has_ewp(l) and has_ewp(r)
        case Choice(l, r): return has_ewp(l) or has_ewp(r)
        case Kleene(_): return True
        case Not(e): return not has_ewp(e)
        case _: raise AssertionError(exp)

def left_assoc(exp: Regex) -> Regex:
    match exp:
        case Concat(Concat(e1, e2), e3):
            return left_assoc(Concat(e1, Concat(e2, e3)))
        case Concat(e1, e2):
            return Concat(e1, left_assoc(e2))

        case Choice(Choice(e1, e2), e3):
            return left_assoc(Choice(e1, Choice(e2, e3)))
        case Choice(e1, e2):
            return Choice(e1, left_assoc(e2))

        case Kleene(e): return Kleene(left_assoc(e))
        case Not(e): return Not(left_assoc(e))

        case _: return exp

def identities(exp: Regex) -> Regex:
    match exp:
        case Concat(EmptySet(), e2): return EmptySet()
        case Concat(e1, EmptySet()): return EmptySet()
        case Concat(Epsilon(), e2): return e2
        case Concat(e1, Epsilon()): return e1
        case Concat(e1, e2):
            return Concat(identities(e1), identities(e2))

        case Choice(e1, EmptySet()): return identities(e1)
        case Choice(EmptySet(), e1): return identities(e1)
        case Choice(e1, Choice(e2, e3)) if e1 == e2: return Choice(e1, e3)
        case Choice(e1, e2) if e1 == e2: return e1
        case Choice(e1, e2):
            return Choice(identities(e1), identities(e2))

        case Kleene(Kleene(e)): return identities(Kleene(e))
        case Kleene(e): return Kleene(identities(e))

        case Not(e): return Not(identities(e))

        case _: return exp

def sort_choice(exp: Regex) -> Regex:
    match exp:
        case Concat(e1, e2):
            return Concat(sort_choice(e1), sort_choice(e2))
        case Choice(e1, Choice(e2, e3)):
            if less_than(e1, e2):
                return Choice(e1, sort_choice(Choice(e2, e3)))
            else:
                return Choice(e2, sort_choice(Choice(e1, e3)))
        case Kleene(e): return Kleene(sort_choice(e))
        case Not(e): return Not(sort_choice(e))
        case _: return exp

def normalize(exp: Regex) -> Regex:
    prev = None
    ret = exp
    while prev != ret:
        prev = ret
        ret = left_assoc(ret)
        ret = identities(ret)
        ret = sort_choice(ret)
    return ret


def derivative(by: Letter, exp: Regex) -> Regex:
    match exp:
        case EmptySet():
            return EmptySet()
        case Epsilon():
            return EmptySet()
        case Letter(n):
            if n == by.name:
                return Epsilon()
            else:
                return EmptySet()
        case Concat(l, r):
            if has_ewp(l):
                return normalize(Choice(Concat(derivative(by, l), r), derivative(by, r)))
            else:
                return normalize(Concat(derivative(by, l), r))
        case Choice(l, r): return normalize(Choice(derivative(by, l), derivative(by, r)))
        case Kleene(e):
            return normalize(Concat(derivative(by, e), Kleene(e)))
        case Not(e):
            return normalize(Not(derivative(by, e)))
        case _: raise AssertionError


def brzozowski(exp: Regex, prev: set[Regex] | None = None) -> bool:
    if prev == None:
        prev = set()
    assert prev is not None
    if exp in prev:
        return True
    prev.add(exp)
    if not has_ewp(exp):
        return False
    return brzozowski(derivative(a, exp), prev=prev) and brzozowski(derivative(b, exp), prev=prev)

even = Kleene(Choice(Concat(a, a), Choice(Concat(a, b), Choice(Concat(b, a), Concat(b, b)))))
odd = Concat(Choice(a, b), even)
top = Kleene(Choice(a, b))

assert odd == derivative(a, even)

assert brzozowski(a) == False
assert brzozowski(b) == False
assert brzozowski(Choice(a, b)) == False
assert brzozowski(top) == True
assert brzozowski(implies(Kleene(Kleene(a)), Kleene(a))) == True
assert brzozowski(implies(Kleene(Kleene(a)), Kleene(Kleene(a)))) == True
assert brzozowski(implies(Kleene(Concat(a, a)), Choice(Concat(Kleene(a), a), Epsilon()))) == True
assert brzozowski(Choice(Kleene(Concat(Kleene(a), b)), Kleene(Concat(Kleene(b), a)))) == True
assert brzozowski(even) == False
assert brzozowski(Choice(even, odd)) == True
assert brzozowski(Choice(Not(Concat(top, Concat(a, top))), Not(Kleene(b))))
