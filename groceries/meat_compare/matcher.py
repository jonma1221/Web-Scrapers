"""Fuzzy product matching across stores for meat deals.

Pairs products by normalized name, meat-specific attributes (cut, bone,
fat ratio, size), and RapidFuzz token similarity. Emits confidence tiers
so the HTML renderer can weight uncertain matches appropriately.

When `category` is falsy (None or ""), generic mode is used: the
meat-specific attribute guards are skipped entirely and matching relies
only on RapidFuzz token similarity against the standard thresholds.
"""

import re
from collections import defaultdict
from dataclasses import dataclass

from rapidfuzz import fuzz

from meat_compare.matcher_data import CUT_SYNONYMS
from meat_compare.models.MeatDeal import MeatDeal

# Confidence tiers (best -> worst)
EXACT = "exact"
FUZZY_HIGH = "fuzzy_high"
FUZZY_LOW = "fuzzy_low"
NO_MATCH = "no_match"

# token_set_ratio thresholds on normalized names
HIGH_THRESHOLD = 85.0
LOW_THRESHOLD = 72.0

# Informational tokens stripped during normalization (not cut-defining)
FILLER_TOKENS = {
    "per", "fresh", "usda", "choice", "premium", "select", "grade",
}

# Unit token expansion (applied before filler filtering)
UNIT_EXPANSIONS = {
    "lbs": "lb", "pound": "lb", "pounds": "lb", "lb": "lb",
    "ounce": "oz", "ounces": "oz", "oz": "oz",
    "each": "ea", "ea": "ea",
}

_RATIO_RE = re.compile(r"(\d{1,2})/(\d{1,2})")
_SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(lb|lbs|oz|pack)", re.IGNORECASE)

_BONE_BONELESS = (["boneless"], ["b", "s"], ["bs"])
_BONE_IN = (["bone", "in"], ["bone"])
_BONE_SKINLESS = (["skinless"],)
_BONE_SKIN_ON = (["skin", "on"],)


@dataclass
class MatchedProduct:
    """A group of deals that represent the same product across stores."""

    deals: list[MeatDeal]
    confidence: str = NO_MATCH
    display_name: str = ""


def _tokenize(name: str) -> list[str]:
    """Lowercase, strip punctuation, expand units, drop filler tokens."""
    tokens = re.findall(r"[a-z0-9]+", name.lower())
    cleaned = []
    for tok in tokens:
        tok = UNIT_EXPANSIONS.get(tok, tok)
        if tok in FILLER_TOKENS:
            continue
        cleaned.append(tok)
    return cleaned


def normalize(name: str) -> str:
    """Return a canonical, token-joined form of a product name."""
    return " ".join(_tokenize(name))


def _has_token_sequence(tokens: list[str], seq: list[str]) -> bool:
    """True if seq appears as a contiguous subsequence of tokens."""
    n, m = len(tokens), len(seq)
    if m == 0 or m > n:
        return False
    for i in range(n - m + 1):
        if tokens[i : i + m] == seq:
            return True
    return False


def extract_ratio(name: str) -> str | None:
    """Extract a fat ratio like '80/20' from a product name."""
    m = _RATIO_RE.search(name.lower())
    if m:
        return f"{int(m.group(1))}/{int(m.group(2))}"
    return None


def extract_bone(name: str) -> str | None:
    """Classify bone/skin modifier: boneless, bone-in, skinless, skin-on."""
    tokens = _tokenize(name)
    for seq in _BONE_BONELESS:
        if _has_token_sequence(tokens, seq):
            return "boneless"
    for seq in _BONE_IN:
        if _has_token_sequence(tokens, seq):
            return "bone-in"
    for seq in _BONE_SKINLESS:
        if _has_token_sequence(tokens, seq):
            return "skinless"
    for seq in _BONE_SKIN_ON:
        if _has_token_sequence(tokens, seq):
            return "skin-on"
    return None


def extract_size(name: str) -> tuple[float, str] | None:
    """Extract pack weight, normalized to pounds. e.g. '16 oz' -> (1.0, 'lb')."""
    m = _SIZE_RE.search(name)
    if not m:
        return None
    qty = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "oz":
        qty = qty / 16.0
    return (qty, "lb")


def extract_cut(name: str, category: str) -> str | None:
    """Resolve a product name to a canonical cut using the synonym map.

    Uses longest-alias-wins matching on whole-word token sequences so
    that 'sirloin tip roast' resolves to 'sirloin tip', not 'sirloin steak'.
    """
    syn = CUT_SYNONYMS.get(category, {})
    if not syn:
        return None
    tokens = _tokenize(name)
    best_canonical = None
    best_len = 0
    for canonical, aliases in syn.items():
        for alias in aliases:
            alias_tokens = _tokenize(alias)
            if len(alias_tokens) > best_len and _has_token_sequence(tokens, alias_tokens):
                best_canonical = canonical
                best_len = len(alias_tokens)
    return best_canonical


def _evaluate_pair(group_a: dict, group_b: dict, category: str | None) -> tuple[str, float]:
    """Score a candidate pair of single-store groups.

    Returns (confidence, score). Hard guards block conflicting
    attributes; synonym-resolved equal cuts guarantee at least a
    fuzzy_low pairing. In generic mode (falsy category) the cut/ratio/
    bone/size guards are skipped and only token similarity is used.
    """
    name_a = group_a["deals"][0].name
    name_b = group_b["deals"][0].name

    cut_a = extract_cut(name_a, category)
    cut_b = extract_cut(name_b, category)
    if cut_a and cut_b and cut_a != cut_b:
        return NO_MATCH, 0.0

    if category:
        ratio_a = extract_ratio(name_a)
        ratio_b = extract_ratio(name_b)
        if ratio_a and ratio_b and ratio_a != ratio_b:
            return NO_MATCH, 0.0

        bone_a = extract_bone(name_a)
        bone_b = extract_bone(name_b)
        if bone_a and bone_b and bone_a != bone_b:
            return NO_MATCH, 0.0

        size_a = extract_size(name_a)
        size_b = extract_size(name_b)
        if size_a and size_b and abs(size_a[0] - size_b[0]) > 0.05:
            return NO_MATCH, 0.0

    norm_a = normalize(name_a)
    norm_b = normalize(name_b)
    score = float(fuzz.token_set_ratio(norm_a, norm_b))

    if cut_a and cut_b and cut_a == cut_b:
        # Synonym map says same cut and no attribute conflict -> at least a match.
        if score >= HIGH_THRESHOLD:
            return FUZZY_HIGH, score
        return FUZZY_LOW, score

    if score >= HIGH_THRESHOLD:
        return FUZZY_HIGH, score
    if score >= LOW_THRESHOLD:
        return FUZZY_LOW, score
    return NO_MATCH, score


def match_products_in_category(deals: list[MeatDeal], category: str | None) -> list[MatchedProduct]:
    """Pair deals across stores within one category.

    1. Groups identical normalized names -> exact matches.
    2. Pairs remaining single-store groups greedily (best score first)
       with attribute guards and RapidFuzz token similarity.
    3. Leftovers become no_match ('only at X') products.

    In generic mode (falsy category) the attribute guards are skipped and
    pairing relies solely on token similarity.
    """
    groups: dict[str, list[MeatDeal]] = defaultdict(list)
    for deal in deals:
        groups[normalize(deal.name)].append(deal)

    results: list[MatchedProduct] = []
    single_store_groups: list[dict] = []

    for key in groups:
        group_deals = groups[key]
        stores = {d.store_name for d in group_deals}
        display = group_deals[0].name
        if len(stores) > 1:
            results.append(
                MatchedProduct(deals=group_deals, confidence=EXACT, display_name=display)
            )
        else:
            single_store_groups.append(
                {
                    "key": key,
                    "deals": group_deals,
                    "store": next(iter(stores)),
                    "display": display,
                }
            )

    if len(single_store_groups) <= 1:
        results.extend(
            MatchedProduct(deals=g["deals"], display_name=g["display"])
            for g in single_store_groups
        )
        return results

    # Bucket single-store groups by store
    by_store: dict[str, list[dict]] = defaultdict(list)
    for g in single_store_groups:
        by_store[g["store"]].append(g)

    # Cross-store candidate pairs
    candidates: list[tuple[float, str, dict, dict]] = []
    store_names = list(by_store)
    for i in range(len(store_names)):
        for j in range(i + 1, len(store_names)):
            for ga in by_store[store_names[i]]:
                for gb in by_store[store_names[j]]:
                    conf, score = _evaluate_pair(ga, gb, category)
                    if conf != NO_MATCH:
                        candidates.append((score, conf, ga, gb))

    candidates.sort(key=lambda c: c[0], reverse=True)

    used_ids: set[int] = set()
    for score, conf, ga, gb in candidates:
        id_a, id_b = id(ga), id(gb)
        if id_a in used_ids or id_b in used_ids:
            continue
        used_ids.add(id_a)
        used_ids.add(id_b)
        results.append(
            MatchedProduct(
                deals=ga["deals"] + gb["deals"],
                confidence=conf,
                display_name=ga["display"],
            )
        )

    for g in single_store_groups:
        if id(g) not in used_ids:
            results.append(MatchedProduct(deals=g["deals"], display_name=g["display"]))

    return results
