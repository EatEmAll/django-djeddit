import uuid
from math import sqrt


def gen_uuid():
    return uuid.uuid4()


def wsi_confidence(ups, downs):
    """Implementation of Wilson score interval used for scoring posts"""
    n = ups + downs
    if n:
        z = 1.96 # 1.44 = 85%, 1.96 = 95%
        phat = float(ups) / n
        return (phat + z * z / (2 * n) - z * sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)
    return 0
