"""Step 4: the fact ledger ("series bible"). Pure code: merge character aliases and
pick which earlier facts are relevant to each new episode."""
import re
from collections import defaultdict

from .schemas import CharacterOut, Fact

TITLES = re.compile(r"^(mr|mrs|ms|miss|dr|sir|madam|mister|lady|lord|young master|master)\.?\s+")
# Words that refer to different people depending on who is speaking: never merge on these alone.
GENERIC = {
    "mom", "mother", "mum", "dad", "father", "mommy", "daddy", "sir", "madam", "ma'am", "boss", "honey", "babe",
    "baby", "darling", "sweetheart", "grandma", "grandpa", "son", "daughter", "brother", "sister", "husband",
    "wife", "uncle", "aunt", "you", "him", "her", "ceo", "the ceo", "president", "doctor", "officer",
}


def norm_name(name: str) -> str:
    n = name.lower().strip().replace("’", "'")
    n = re.sub(r"[^\w' ]+", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    stripped = TITLES.sub("", n).strip()
    # "Mr. Ashford" and "Mrs. Ashford" are different people: keep the title when only a surname would remain
    return stripped if " " in stripped or stripped == n else n


def _distinct_people(a: str, b: str) -> bool:
    """Two full names with different first names (e.g. 'julian ashford' / 'celeste ashford') never merge."""
    if TITLES.match(a) or TITLES.match(b):  # "mr grant" may well be "alexander grant"
        return False
    pa, pb = a.split(), b.split()
    return len(pa) > 1 and len(pb) > 1 and "'" not in a + b and pa[0] != pb[0]


class EntityResolver:
    """Union-find over character names and aliases."""

    def __init__(self):
        self.parent: dict[str, str] = {}
        self.display: dict[str, str] = {}

    def _find(self, k: str) -> str:
        self.parent.setdefault(k, k)
        while self.parent[k] != k:
            self.parent[k] = self.parent[self.parent[k]]
            k = self.parent[k]
        return k

    def _union(self, a: str, b: str) -> None:
        ra, rb = self._find(a), self._find(b)
        if ra != rb and _distinct_people(ra, rb):
            return
        if ra != rb:
            # keep the longer (more complete) name as the root
            if len(rb) > len(ra):
                ra, rb = rb, ra
            self.parent[rb] = ra

    def add(self, name: str, aliases: list[str] = ()) -> None:
        k = norm_name(name)
        if not k or k in GENERIC:
            return
        self._find(k)
        self.display.setdefault(k, name.strip())
        for a in aliases:
            ka = norm_name(a)
            if ka and ka not in GENERIC and ka != k:
                self._union(k, ka)
                self.display.setdefault(ka, a.strip())

    def link_first_names(self) -> None:
        """'Alex' -> 'Alex Grant' when exactly one full name starts with that first name."""
        keys = list(self.parent)
        full = [k for k in keys if " " in k and "'" not in k]
        for k in keys:
            if " " in k:
                continue
            matches = {self._find(f) for f in full if f.split()[0] == k}
            if len(matches) == 1:
                self._union(matches.pop(), k)

    def key(self, name: str | None) -> str:
        if not name:
            return ""
        k = norm_name(name)
        if k in self.parent:
            return self._find(k)
        # possessives like "Ethan's mother" -> resolve the owner part
        m = re.match(r"^(.+?)'s (.+)$", k)
        if m and m.group(1) in self.parent:
            return f"{self._find(m.group(1))}'s {m.group(2)}"
        return k

    def label(self, key: str) -> str:
        return self.display.get(key, key.title())


def build_resolver(chars_by_ep: dict[int, list[CharacterOut]], manual_aliases: dict[str, list[str]] | None = None) -> EntityResolver:
    r = EntityResolver()
    for name, aliases in (manual_aliases or {}).items():
        r.add(name, aliases)
    for chars in chars_by_ep.values():
        for c in chars:
            r.add(c.name, c.aliases)
    r.link_first_names()
    return r


def assign_keys(facts: list[Fact], r: EntityResolver) -> None:
    for f in facts:
        f.entity_key = r.key(f.entity)


def _owner(key: str) -> str:
    return key.split("'s ", 1)[0] if "'s " in key else ""


def relevant_prior(facts_by_ep: dict[int, list[Fact]], ep: int, r: EntityResolver, max_facts: int = 300) -> list[Fact]:
    """Earlier facts that mention any entity appearing in episode `ep`."""
    keys = set()
    for f in facts_by_ep.get(ep, []):
        keys |= {f.entity_key, r.key(f.target), _owner(f.entity_key)}
    keys.discard("")
    prior = [
        f
        for e, fs in facts_by_ep.items()
        if e < ep
        for f in fs
        if f.entity_key in keys or r.key(f.target) in keys or _owner(f.entity_key) in keys
    ]
    prior.sort(key=lambda f: (f.episode, f.id))
    return prior[-max_facts:]


def bible(facts: list[Fact], r: EntityResolver) -> dict[str, list[dict]]:
    """Per-character fact sheet, ordered by episode."""
    out: dict[str, list[dict]] = defaultdict(list)
    for f in sorted(facts, key=lambda f: (f.episode, f.id)):
        out[r.label(f.entity_key)].append(
            {"episode": f.episode, "category": f.category, "target": f.target, "value": f.value, "quote": f.quote, "id": f.id}
        )
    return dict(sorted(out.items(), key=lambda kv: -len(kv[1])))
