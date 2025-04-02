from typing import Union


def _dict(d: Union[dict, int, float]) -> Union[dict, int, float]:
    """ Returns dictionary or numeric value. """
    return dict(d) if hasattr(d, "__iter__") else d


def _sum(d1: Union[dict, int, float], d2: Union[dict, int, float]):
    """ Returns sum of two numbers or dictionary values. """
    if type(d1) == dict or type(d2) == dict:
        return {v: d1.get(v, 0) + d2.get(v, 0) for v in set(d for d in {**d1, **d2})}
    return (d1 or 0) + (d2 or 0)
