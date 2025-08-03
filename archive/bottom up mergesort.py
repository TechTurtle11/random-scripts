def mergesort(lst):

    if not lst:
        return []
    elif len(lst) == 2:
        return [min(lst), max(lst)]
    elif len(lst) == 1:
        return lst
    else:
        return merge([], mergesort(lst[:len(lst)/2]), mergesort(lst[len(lst)/2:]))


def merge(merged, a, b):

    if a and b:
        return merge(merged + [min(a[0], b[0])],
                     a[1:] if min(a[0], b[0]) == a[0] else a,
                     b[1:] if min(a[0], b[0]) == b[0] and not a[0] == b[0] else b
                     )

    elif a and not b and len(a) > 1:
        return merged + merge([], a[:len(a)/2], a[len(a)/2:])
    elif a and not b:
        return merged + a
    elif b and not a  and len(b) > 1:
        return merged + merge([], b[:len(b)/2], b[len(b)/2:])
    elif b and not a:
        return merged + b
    else:
        return merged

mergesort([6,3,2,8,1,3,6])