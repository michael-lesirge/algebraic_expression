def sort_dict(d: dict) -> dict:
    """
    sorted a dict by keys
    """
    return dict(sorted(d.items()))


def if_print(*args, condition, **kwargs) -> None:
    """
    print if a condition is true
    """
    if condition:
        print(*args, **kwargs)


def common_keys(dicts: list[dict]) -> set:
    """
    returns a set of all common keys
    """
    if len(dicts) == 0:
        return set()

    keys = set(dicts[0].keys())

    for dictionary in dicts:
        keys &= set(dictionary)

    return keys


def min_common_num(dicts: list[dict]) -> dict:
    """
    returns a dict with only the minimum number in it
    """
    return {
        key: min(d[key] for d in dicts) for key in dicts[0] if all((key in d) for d in dicts)
    }


def str_list(s: list["Term" or "Expression"], join=False, sep="", **kwargs):
    """
    helpful for testing function to convert a list of objects to there custom string representation
    """
    new_list = [val.str_plus(**kwargs) for val in s]
    if join:
        return sep.join(new_list)
    return new_list


def mul_add(multipy_to, add_to) -> tuple:
    """
    returns 2 number that multiply to first arg and add to second arg, used in simplifying Expression
    """
    if multipy_to > 0:
        pos = 1
    elif multipy_to < 0:
        pos = -1
    else:
        return 0, add_to

    for i in range(pos, multipy_to, pos):
        if multipy_to % i == 0:
            x = multipy_to // i
            if x + i == add_to:
                return i, int(x)
            elif x + i == -add_to:
                return -i, -int(x)


def safe_int(x):
    """
    converts a number to an int if it only has a .0 on it making it a float
    """
    if isinstance(x, str):
        x = float(x)
    if isinstance(x, float):
        if x.is_integer():
            return int(x)
    elif isinstance(x, (tuple, list, set)):
        return type(x)([safe_int(i) for i in x])
    return x


def combine_like_terms(terms: list["Term"]) -> list["Term"]:
    """
    combines like terms and removes zero terms
    """
    d = {}
    new = []
    i = 0
    for term in terms:
        hash_dict = tuple(term.bases_exponents.keys())
        if hash_dict in d:
            new[d[hash_dict]] += term
        elif not term.is_zero_term():
            new.append(term)
            d[hash_dict] = i
            i += 1

    return new


def sum_dict(d1: dict, d2: dict) -> dict:
    """
    sums all the keys in 2 dicts
    """
    return {k: (d1.get(k, 0) + d2.get(k, 0)) for k in set(d1) | set(d2)}


def subtract_dict(d1: dict, d2: dict) -> dict:
    """
    opposite of sum_dict
    """
    return {k: (d1.get(k, 0) - d2.get(k, 0)) for k in (set(d1) | set(d2))}


# used as utils
from math import gcd