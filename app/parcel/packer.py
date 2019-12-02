from typing import List

from .container import CONTAINER_TYPES_BY_SIZE, CompartmentMeta, ContainerMeta
from .parcel import ParcelMeta


def calculate_smallest_needed_container(parcels: List[ParcelMeta]
                                        ) -> ContainerMeta:
    """Calculates the smallest `Container` that can ship the provided
    `Parcel`s. Returns `None` if no `Container` is found.
    """
    if len(parcels) == 0:
        raise ValueError("Must provide at least one Parcel")

    for cont in CONTAINER_TYPES_BY_SIZE:
        # Shortcut having to use our expensive bin packing logic
        meets_basic_weight_req = cont.can_carry_all_by_weight(parcels)
        meets_basic_size_req = cont.can_fit_all_individually(parcels)
        if not meets_basic_weight_req or not meets_basic_size_req:
            continue
        if len(parcels) == 1:
            # We already know we can fit the parcel
            return cont

        # TODO Do intelligent calculation here

    return None


"""////////////////////////////////////////////////////////////////////////////
The code below has been taken from the pyShipping-python3 module and adapted
to work within our constraints. Tradeoffs were also made for readability over
performance.

You can read up more on the module at
https://github.com/joncombe/pyShipping-python3.
///////////////////////////////////////////////////////////////////////////////
"""
# TODO: move to top
# TODO: bin -> container
# TODO rename variables to split words with '_'
import random

# TODO: add typehints


class Timeout(Exception):
    pass


def packstrip(bin, parcels):
    """Creates a Strip which fits into bin.
    Returns the Packages to be used in the strip, the dimensions of the strip as a 3-tuple
    and a list of "left over" packages.
    """
    strip = []
    rest = []
    strip_length = strip_width = strip_size = 0
    while parcels and (strip_size <= bin.height):
        parcel = parcels.pop(0)
        if strip_size + parcel.height <= bin.height:
            strip_size += parcel.height
            strip.append(parcel)
            strip_width = max(strip_width, parcel.width)
            strip_length = max(strip_length, parcel.length)
        else:
            rest.append(parcel)
    return strip, (strip_size, strip_width, strip_length), rest + parcels


def packlayer(bin, parcels):
    strips = []
    layersize = 0
    layerx = 0
    layery = 0
    binsize = bin.width  # TODO should this logically be bin.length?
    while parcels:
        strip, (sizex, stripsize, sizez), rest = packstrip(bin, parcels)
        if layersize + stripsize <= binsize:
            parcels = rest
            if not strip:
                # we were not able to pack anything
                break
            layersize += stripsize
            layerx = max([sizex, layerx])
            layery = max([sizez, layery])
            strips.extend(strip)
        else:
            # Next Layer please
            parcels = strip + rest
            break
    return strips, (layerx, layersize, layery), parcels


def packbin(bin, parcels):
    parcels.sort(key=lambda x: x.volume)
    layers = []
    contentheigth = 0
    contentx = 0
    contenty = 0
    binsize = bin.length
    while parcels:
        layer, (sizex, sizey, layersize), rest = packlayer(bin, parcels)
        if contentheigth + layersize <= binsize:
            parcels = rest
            if not layer:
                # we were not able to pack anything
                break
            contentheigth += layersize
            contentx = max([contentx, sizex])
            contenty = max([contenty, sizey])
            layers.extend(layer)
        else:
            # Next Bin please
            parcels = layer + rest
            break
    return layers, (contentx, contenty, contentheigth), parcels


def packit(bin, parcels):
    packedbins = []
    sorted_parcels = sorted(parcels, key=lambda x: x.volume)
    while sorted_parcels:
        parcels_in_bin, (bin_x, bin_y, bin_z), rest = packbin(bin,
                                                              sorted_parcels)
        if not parcels_in_bin:
            # we were not able to pack anything
            break
        packedbins.append(parcels_in_bin)
        sorted_parcels = rest
    # we now have a result, try to get a better result by rotating some bins

    return packedbins, rest


def trypack(bin, parcels, bestpack):
    bins, rest = packit(bin, parcels)
    if len(bins) < bestpack['bincount']:  # TODO this may need to be altered
        bestpack['bincount'] = len(bins)
        bestpack['bins'] = bins
        bestpack['rest'] = rest
    if bestpack['bincount'] < 2:
        raise Timeout('optimal solution found')
    return len(parcels)


# TODO just call 'trypack' directly instead of passing a callback
def allpermutations_helper(permuted, todo, maxcounter, callback, bin, bestpack,
                           counter):
    if not todo:
        return counter + callback(bin, permuted, bestpack)
    else:
        others = todo[1:]
        parcel = todo[0]
        for orientation in parcel.legal_orientations():
            l, w, h = orientation
            rotated_parcel = ParcelMeta(l, w, h, parcel.weight)
            if bin.can_fit(rotated_parcel):
                counter = allpermutations_helper(permuted + [rotated_parcel],
                                                 others, maxcounter, callback,
                                                 bin, bestpack, counter)
            if counter > maxcounter:
                raise Timeout('more than %d iterations tries' % counter)
        return counter


def allpermutations(todo, bin, iterlimit=5000):
    random.seed(1)
    random.shuffle(todo)
    bestpack = dict(bincount=len(todo) + 1)  # TODO this may need to be altered
    try:
        # First try unpermuted
        trypack(bin, todo, bestpack)
        # Now try permutations
        allpermutations_helper([], todo, iterlimit, trypack, bin, bestpack, 0)
    except Timeout:
        pass
    return bestpack['bins'], bestpack['rest']


def binpack(parcels: List[ParcelMeta], bin: CompartmentMeta,
            iterlimit: int = 5000):
    if not parcels:
        raise ValueError("must provide at least one package")
    if not bin:
        raise ValueError("bin cannot be None")
    return allpermutations(parcels, bin, iterlimit)


###############################################################################
# Their code (TODO rm)
###############################################################################


# def packstrip(bin, p):
#     """Creates a Strip which fits into bin.
#     Returns the Packages to be used in the strip, the dimensions of the strip as a 3-tuple
#     and a list of "left over" packages.
#     """
#     # This code is somewhat optimized and somewhat unreadable
#     s = []                # strip
#     r = []                # rest
#     ss = sw = sl = 0      # stripsize
#     bs = bin.heigth       # binsize
#     sapp = s.append       # speedup
#     rapp = r.append       # speedup
#     ppop = p.pop          # speedup
#     while p and (ss <= bs):
#         n = ppop(0)
#         nh, nw, nl = n.size
#         if ss + nh <= bs:
#             ss += nh
#             sapp(n)
#             if nw > sw:
#                 sw = nw
#             if nl > sl:
#                 sl = nl
#         else:
#             rapp(n)
#     return s, (ss, sw, sl), r + p
#
#
# def packlayer(bin, packages):
#     strips = []
#     layersize = 0
#     layerx = 0
#     layery = 0
#     binsize = bin.width
#     while packages:
#         strip, (sizex, stripsize, sizez), rest = packstrip(bin, packages)
#         if layersize + stripsize <= binsize:
#             packages = rest
#             if not strip:
#                 # we were not able to pack anything
#                 break
#             layersize += stripsize
#             layerx = max([sizex, layerx])
#             layery = max([sizez, layery])
#             strips.extend(strip)
#         else:
#             # Next Layer please
#             packages = strip + rest
#             break
#     return strips, (layerx, layersize, layery), packages
#
#
# def packbin(bin, packages):
#     packages.sort(key=lambda x: x.volume)
#     layers = []
#     contentheigth = 0
#     contentx = 0
#     contenty = 0
#     binsize = bin.length
#     while packages:
#         layer, (sizex, sizey, layersize), rest = packlayer(bin, packages)
#         if contentheigth + layersize <= binsize:
#             packages = rest
#             if not layer:
#                 # we were not able to pack anything
#                 break
#             contentheigth += layersize
#             contentx = max([contentx, sizex])
#             contenty = max([contenty, sizey])
#             layers.extend(layer)
#         else:
#             # Next Bin please
#             packages = layer + rest
#             break
#     return layers, (contentx, contenty, contentheigth), packages
#
#
# def packit(bin, originalpackages):
#     packedbins = []
#     packages = sorted(originalpackages, key=lambda x: x.volume)
#     while packages:
#         packagesinbin, (binx, biny, binz), rest = packbin(bin, packages)
#         if not packagesinbin:
#             # we were not able to pack anything
#             break
#         packedbins.append(packagesinbin)
#         packages = rest
#     # we now have a result, try to get a better result by rotating some bins
#
#     return packedbins, rest
#
#
# # In newer Python versions these van be imported:
# # from itertools import permutations
# def product(*args, **kwds):
#     # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
#     # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
#     pools = list(map(tuple, args)) * kwds.get('repeat', 1)
#     result = [[]]
#     for pool in pools:
#         result = [x + [y] for x in result for y in pool]
#     for prod in result:
#         yield tuple(prod)
#
#
# def permutations(iterable, r=None):
#     pool = tuple(iterable)
#     n = len(pool)
#     r = n if r is None else r
#     for indices in product(range(n), repeat=r):
#         if len(set(indices)) == r:
#             yield tuple(pool[i] for i in indices)
#
#
# class Timeout(Exception):
#     pass
#
#
# def allpermutations_helper(permuted, todo, maxcounter, callback, bin, bestpack, counter):
#     if not todo:
#         return counter + callback(bin, permuted, bestpack)
#     else:
#         others = todo[1:]
#         thispackage = todo[0]
#         for dimensions in set(permutations((thispackage[0], thispackage[1], thispackage[2]))):
#             thispackage = Package(dimensions, nosort=True)
#             if thispackage in bin:
#                 counter = allpermutations_helper(permuted + [thispackage], others, maxcounter, callback,
#                                                  bin, bestpack, counter)
#             if counter > maxcounter:
#                 raise Timeout('more than %d iterations tries' % counter)
#         return counter
#
#
# def trypack(bin, packages, bestpack):
#     bins, rest = packit(bin, packages)
#     if len(bins) < bestpack['bincount']:
#         bestpack['bincount'] = len(bins)
#         bestpack['bins'] = bins
#         bestpack['rest'] = rest
#     if bestpack['bincount'] < 2:
#         raise Timeout('optimal solution found')
#     return len(packages)
#
#
# def allpermutations(todo, bin, iterlimit=5000):
#     random.seed(1)
#     random.shuffle(todo)
#     bestpack = dict(bincount=len(todo) + 1)
#     try:
#         # First try unpermuted
#         trypack(bin, todo, bestpack)
#         # now try permutations
#         allpermutations_helper([], todo, iterlimit, trypack, bin, bestpack, 0)
#     except Timeout:
#         pass
#     return bestpack['bins'], bestpack['rest']
#
#
# def binpack(packages, bin=None, iterlimit=5000):
#     """Packs a list of Package() objects into a number of equal-sized bins.
#     Returns a list of bins listing the packages within the bins and a list of packages which can't be
#     packed because they are to big."""
#     if not bin:
#         bin = Package("600x400x400")
#     return allpermutations(packages, bin, iterlimit)
#
#
# def test():
#     fd = open('testdata.txt')
#     vorher = 0
#     nachher = 0
#     start = time.time()
#     for line in fd:
#         packages = [Package(pack) for pack in line.strip().split()]
#         if not packages:
#             continue
#         bins, rest = binpack(packages)
#         if rest:
#             print("invalid data", rest, line)
#         else:
#             vorher += len(packages)
#             nachher += len(bins)
#     print(time.time() - start)
#     print(vorher, nachher, float(nachher) / vorher * 100)
