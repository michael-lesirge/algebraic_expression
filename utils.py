def gcd(x, *nums):
    """
    finds greatest common factor of numbers
    """
    if len(nums) == 0:
        return x
    y, *nums = nums
    while y:
        x, y = y, x % y
    return abs(gcd(x, *nums))


def min_common_num(dicts: list[dict]) -> dict:
    """
    returns a dict with only the minimum number in it
    """
    return {
        key: min(d[key] for d in dicts) for key in dicts[0] if all((key in d) for d in dicts)
    }

def safe_int(x, *, round_to=None):
    """
    converts a number to an int if it only has a .0 on it making it a float
    """
    if isinstance(x, str):
        x = float(x)

    if isinstance(x, float):
        if x.is_integer():
            x = int(x)

    elif round_to is not None:
        x = round(x, round_to)

    return x


def sort_dict(d: dict) -> dict:
    """
    sorted a dict by keys
    """
    return dict(sorted(d.items()))


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


def sum_dict(d1: dict, d2: dict) -> dict:
    """
    sums all the keys in 2 dicts
    """
    return {k: (d1.get(k, 0) + d2.get(k, 0)) for k in set(d1) | set(d2)}

def subtract_dict(d1: dict, d2: dict) -> dict:
    """
    sums all the keys in 2 dicts
    """
    return {k: (d1.get(k, 0) - d2.get(k, 0)) for k in set(d1) | set(d2)}

def sqrt(x):
    if x < 0:
        raise Exception("can not square negative number")
    return x ** 0.5
