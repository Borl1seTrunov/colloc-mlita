from utils import Clause, Literal, parse_clauses
from typing import List, Tuple, Dict, Set
from collections import deque

initial_clauses = []

def mgu(l1: Literal, l2: Literal) -> Dict[str, str] | None:
    if l1.pred != l2.pred or len(l1.args) != len(l2.args) or l1.neg == l2.neg:
        return None
    sub = {}
    for a, b in zip(l1.args, l2.args):
        aa = sub.get(a, a)
        bb = sub.get(b, b)
        if aa == bb: continue
        if aa.islower():
            sub[aa] = bb
        elif bb.islower():
            sub[bb] = aa
        else:
            return None
    return sub

def resolve(c1: Clause, c2: Clause, next_id: int) -> Tuple[Clause, str, int]:
    for l1 in c1.literals:
        for l2 in c2.literals:
            if l1.pred == l2.pred and l1.neg != l2.neg:
                sub = mgu(l1, l2)
                if sub is not None:
                    new_lits = [lit.substitute(sub) for lit in c1.literals if lit is not l1] + \
                               [lit.substitute(sub) for lit in c2.literals if lit is not l2]
                    unique_lits = []
                    seen = set()
                    for lit in new_lits:
                        if lit.text not in seen:
                            unique_lits.append(lit)
                            seen.add(lit.text)
                    resolvent = Clause(unique_lits, f"R{next_id}")
                    step = (f"Шаг {next_id - len(initial_clauses) + 1}: "
                            f"Возьмём {c1.id} и {c2.id} "
                            f"по {l1.substitute(sub)} и {l2.substitute(sub)} "
                            f"(подстановка {sub if sub else '∅'}) → {resolvent.id}: {resolvent}")
                    return resolvent, step, next_id + 1
    return None, "", next_id

def resolution_prover(clauses: List[Clause]) -> Tuple[bool, List[str]]:
    global initial_clauses
    initial_clauses = clauses

    output = ["Исходные клаузы:"]
    for c in clauses:
        output.append(f"  {c.id}: {c}")

    queue = deque(clauses)
    seen: Set[Clause] = set(clauses)
    all_clauses = {c.id: c for c in clauses}
    next_id = len(clauses)

    while queue:
        current = queue.popleft()
        for other in list(all_clauses.values()):
            if current.id <= other.id:
                continue
            resolvent, step, next_id = resolve(current, other, next_id)
            if resolvent is not None:
                output.append(step)
                if not resolvent.literals:
                    output.append("\nПОЛУЧЕНА ПУСТАЯ КЛАУЗА → ТЕОРЕМА ДОКАЗАНА!")
                    return True, output
                if resolvent not in seen:
                    seen.add(resolvent)
                    queue.append(resolvent)
                    all_clauses[resolvent.id] = resolvent

    output.append("Противоречие не найдено.")
    return False, output