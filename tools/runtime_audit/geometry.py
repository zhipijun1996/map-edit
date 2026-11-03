"""Exact AABB exclusions for the supplied closure; not a movement simulator."""


def owned_point(source, bounds):
    return [source[0] - bounds["x"], source[1] - bounds["y"]]


def excluded_centers(rect, actor_size):
    x, y, w, h = rect
    hx, hy = actor_size[0] / 2, actor_size[1] / 2
    return [x - hx, y - hy, w + 2 * hx, h + 2 * hy]


def fully_blocked_claim_region(region, seal, actor_size):
    x, y, w, h = region
    xx, yy, ww, hh = excluded_centers(seal, actor_size)
    return x > xx and y > yy and x + w <= xx + ww and y + h <= yy + hh
