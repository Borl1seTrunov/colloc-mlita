from typing import List, Dict, Tuple
from collections import deque

class Literal:
    def __init__(self, text: str):
        self.text = text.strip()
        self.neg = self.text.startswith("¬")
        core = self.text[1:] if self.neg else self.text
        if "(" in core:
            self.pred, args = core.split("(", 1)
            self.args = [a.strip() for a in args.rstrip(")").split(",")]
        else:
            self.pred = core
            self.args = []

    def __repr__(self): return self.text
    def __hash__(self): return hash(self.text)
    def __eq__(self, other): return isinstance(other, Literal) and self.text == other.text

    def substitute(self, sub: Dict[str, str]) -> 'Literal':
        if not sub: return self
        args = [sub.get(a, a) for a in self.args]
        core = self.pred + (f"({','.join(args)})" if args else "")
        return Literal(("¬" + core) if self.neg else core)


class Clause:
    def __init__(self, literals: List[Literal], clause_id: str = None):
        self.literals = literals
        self.id = clause_id

    def __repr__(self):
        if not self.literals:
            return "□ (пустая клауза)"
        return " ∨ ".join(repr(l) for l in self.literals)

    def __hash__(self):
        return hash(tuple(sorted(l.text for l in self.literals)))

    def __eq__(self, other):
        return isinstance(other, Clause) and {l.text for l in self.literals} == {l.text for l in other.literals}


def parse_clauses(text: str) -> List[Clause]:
    if not text: return []
    parts = []
    current = ""
    depth = 0
    for c in text + ",":
        if c == "(": depth += 1
        if c == ")": depth -= 1
        if c == "," and depth == 0:
            part = current.strip()
            if part: parts.append(part)
            current = ""
        else:
            current += c

    clauses = []
    for i, part in enumerate(parts):
        lits = [Literal(l.strip()) for l in part.split("∨") if l.strip()]
        clauses.append(Clause(lits, f"R{i}"))
    return clauses