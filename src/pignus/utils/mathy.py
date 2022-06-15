"""Mathy
A collection of random math related utils

Testing
Unit Tests at automox/pignus/tests/unit/utils/test_mathy.py
4/7 methods currently unit tested.

"""
# from operator import itemgetter
# from functools import cmp_to_key


def percentage(piece: float, whole: float, round_int: int = 2) -> float:
    """Get the percentage between the piece and whole of two given arguments.
    :unit-test: TestMathy.test__percentage
    """
    ret = round(((piece * 100) / whole), round_int)
    if round_int == 0:
        ret = int(ret)
    return ret


def get_avg(items_to_avg: list, round_result_to: int = 0) -> int:
    """Get the average of a list of ints/floats, rounded out.
    :unit-test: TestMathy.test__get_avg
    """
    sum_items = 0
    for item in items_to_avg:
        sum_items += item
    the_avg = sum_items / len(items_to_avg)
    the_avg = round(the_avg, round_result_to)
    return the_avg


def get_unique(items: list) -> list:
    """Get only the unique items from a list.
    :unit-test: test__get_unique
    """
    ret_items = []
    for items in items:
        if items not in ret_items:
            ret_items.append(items)

    return ret_items


def cmp(x, y):
    """Replaces built-in function cmp that was removed from Python 3"""
    return (x > y) - (x < y)


# def multikeysort(items: list, columns: list):
#     """Sort a list of dicts by one or more values within the dict. Note each dictionary must contain
#     all the comparison keys, and contain a not None value.
#     """
#     comparers = [
#         ((itemgetter(col[1:].strip()), - 1) if col.startswith('-') else (itemgetter(col.strip()), 1))
#         for col in columns
#     ]

#     def comparer(left, right):
#         comparer_iter = (
#             cmp(fn(left), fn(right)) * mult
#             for fn, mult in comparers
#         )
#         return next((result for result in comparer_iter if result), 0)
#     return sorted(items, key=cmp_to_key(comparer), reverse=True)


# def order_images_by_cves(images: list) -> list:
#     """Takes a list of Image objects and sorts them by cve_critical_int, cve_medium_int,
#     cve_high_int, cve_low_int.
#     """
#     tmp_images = []
#     # Put the Images into a temporary new list with the values needed to sort.
#     for image in images:
#         cve_critical_int = image.cve_critical_int
#         if not cve_critical_int:
#             cve_critical_int = 0
#         cve_high_int = image.cve_high_int
#         if not cve_high_int:
#             cve_high_int = 0
#         cve_medium_int = image.cve_medium_int
#         if not cve_medium_int:
#             cve_medium_int = 0
#         cve_low_int = image.cve_low_int
#         if not cve_low_int:
#             cve_low_int = 0
#         tmp_image = {
#             "name": image.name,
#             "cve_critical_int": cve_critical_int,
#             "cve_high_int": cve_high_int,
#             "cve_medium_int": cve_medium_int,
#             "cve_low_int": cve_low_int
#         }
#         tmp_images.append(tmp_image)

#     sorted_images = multikeysort(
#         tmp_images, ["cve_critical_int", "cve_high_int", "cve_medium_int", "cve_low_int"])

#     # Put the Images back together in the new order.
#     new_images = []
#     old_images = images
#     for s_image in sorted_images:
#         for o_image in old_images:
#             if s_image["name"] == o_image.name:
#                 new_images.append(o_image)
#                 break
#     return new_images


# End File: automox/pignus/src/pignus/utils/mathy.py
