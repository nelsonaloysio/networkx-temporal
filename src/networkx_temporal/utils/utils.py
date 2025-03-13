from typing import Union


def _dict(d: Union[dict, int, float]) -> Union[dict, int, float]:
    """ Returns dictionary or numeric value. """
    return dict(d) if hasattr(d, "__iter__") else d


def _sum(d1: Union[int, dict], d2: Union[int, dict]):
    """ Returns sum of two integers or dictionary values. """
    if type(d1) == int or type(d2) == int:
        return (d1 if type(d1) == int else 0) + (d2 if type(d2) == int else 0)

    d1, d2 = dict(d1), dict(d2)
    return {v: d1.get(v,0) + d2.get(v,0) for v in set(d for d in {**d1, **d2})}
