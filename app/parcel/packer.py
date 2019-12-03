import itertools
import random
from typing import Dict, List, Tuple

from .container import CONTAINER_TYPES_BY_SIZE, CompartmentMeta, ContainerMeta
from .parcel import ParcelMeta


def calculate_smallest_needed_container(
    parcels: List[ParcelMeta],
    advanced_packing=False,
) -> ContainerMeta:
    """Calculates the smallest `Container` that can ship the provided
    `Parcel`s. Returns None if we cannot find a `Container` that can fit all
    the packages.
    """
    if len(parcels) == 0:
        raise ValueError("Must provide at least one Parcel")

    for cont in CONTAINER_TYPES_BY_SIZE:
        meets_basic_weight_req = cont.can_carry_all_by_weight(parcels)
        meets_basic_size_req = cont.can_fit_all_individually(parcels)

        if not meets_basic_weight_req or not meets_basic_size_req:
            # Shortcircuit having to use our more expensive bin-packing logic
            continue
        if len(parcels) == 1:
            # We already know we can fit the parcel
            return cont

        if advanced_packing and _can_fit_container_advanced(cont, parcels):
            return cont
        elif not advanced_packing and _can_fit_container_simple(cont, parcels):
            return cont

    # Does not fit into any Containers
    return None


def _can_fit_container_simple(cont: ContainerMeta, parcels: List[ParcelMeta]
                              ) -> bool:
    """Uses a naiive approach to determine if we can fit all Parcels in the
    `Container` based on the `Container`s total volume."""
    return cont.can_fit_all_by_volume(parcels)


def _can_fit_container_advanced(cont: ContainerMeta, parcels: List[ParcelMeta]
                                ) -> bool:
    """Uses a more advanced 3D bin-packing solution to determine if we can fit
    all parcels in the `Container` by testing different arrangements and
    orientations of the boxes.

    NOTE: At time of writing, this approach is not reliable and the simple
    solution should be preferred, instead.
    """
    # Use a greedy approach to calculate if we can fit all parcels into the
    # compartments, starting by trying to pack all items into the first
    # compartment, then all remaining parcels into the next, etc.
    remaining = parcels
    for compt in cont.compartments:
        bins, rest = bin_pack(remaining, compt)
        if rest:
            break
        if len(bins) == 1:
            # We successfully fit all Parcels
            return True
        else:
            # Join overflow bins to get remaining packages
            remaining = list(itertools.chain.from_iterable(bins[1:]))
    return False


"""////////////////////////////////////////////////////////////////////////////

The logic below attempts to pack the `Parcel`s into multiple `Compartment`s of
the same size. We know we can fit all `Parcel`s in the `Container` when we
receive a list of `Container`s == 1 and no `Parcel`s remaining to pack.

The code below has been taken from the pyShipping-python3 module and adapted
to work within our constraints. Documentation in the original package is
lacking, so I did my best to better detail the intentions of each function
through code.

The original pyShipping package still does not seem to achieve perfect results
from my tests. However, due to the fact that this problem is the subject of
many academic papers and I have a limited time for the project, pyShipping's
solution is used as a stand-in solution.

A possible change could be to try heuristics other than `volume` for sorting
the parcels, or even adding more randomness with a fixed seed for consistency.
Though, these suggestions would require further testing.

You can read up more on the module at
https://github.com/joncombe/pyShipping-python3.

///////////////////////////////////////////////////////////////////////////////
"""

# TODO: add arg typehints
# TODO: add return typehints


class Timeout(Exception):
    """Exception thrown when we reach either our iteration limit or our optimal
    solution.
    """
    pass


def _pack_strip(compt: CompartmentMeta, parcels: List[ParcelMeta]):
    """Creates a `Strip` which fits into a `Layer`"""
    strip = []
    rest = []
    strip_length = strip_width = strip_size = 0
    while parcels and (strip_size <= compt.height):
        parcel = parcels.pop(0)
        if strip_size + parcel.height <= compt.height:
            strip_size += parcel.height
            strip.append(parcel)
            strip_width = max(strip_width, parcel.width)
            strip_length = max(strip_length, parcel.length)
        else:
            rest.append(parcel)
    return strip, (strip_size, strip_width, strip_length), rest + parcels


def _pack_layer(compt: CompartmentMeta, parcels: List[ParcelMeta]):
    """Creates a `Layer` which fits into a `Compartment`"""
    strips = []
    layer_size = 0
    layer_x = 0
    layer_y = 0
    compt_size = compt.width
    while parcels:
        strip, (size_x, strip_size, size_z), rest = _pack_strip(compt, parcels)
        if layer_size + strip_size <= compt_size:
            parcels = rest
            if not strip:
                # Could not pack anything
                break
            layer_size += strip_size
            layer_x = max(size_x, layer_x)
            layer_y = max(size_z, layer_y)
            strips.extend(strip)
        else:
            # Next Layer please
            parcels = strip + rest
            break
    return strips, (layer_x, layer_size, layer_y), parcels


def _pack_compt(compt: CompartmentMeta, parcels: List[ParcelMeta]):
    """Attempt to pack `Compartment` with `Parcel`s."""
    layers = []
    content_height = 0
    content_x = 0
    content_y = 0
    compt_size = compt.length
    while parcels:
        layer, (size_x, size_y, layer_size), rest = _pack_layer(compt, parcels)
        if content_height + layer_size <= compt_size:
            parcels = rest
            if not layer:
                # Could not pack anything
                break
            content_height += layer_size
            content_x = max([content_x, size_x])
            content_y = max([content_y, size_y])
            layers.extend(layer)
        else:
            # Next Bin please
            parcels = layer + rest
            break
    return layers, (content_x, content_y, content_height), parcels


def _pack_it(compt: CompartmentMeta, parcels: List[ParcelMeta]
             ) -> Tuple[List[CompartmentMeta], List[ParcelMeta]]:
    """Attempt to pack `Compartment` with `Parcel`s, prioritizing `Parcel`s by
    their volume."""
    packed_compts = []
    remaining_parcels = sorted(parcels, key=lambda x: x.volume)
    while remaining_parcels:
        parcels_in_bin, (bin_x, bin_y, bin_z), rest = (
                _pack_compt(compt, remaining_parcels))
        if not parcels_in_bin:
            # Could not pack anything
            break
        packed_compts.append(parcels_in_bin)
        remaining_parcels = rest
    return packed_compts, rest


def _try_pack(compt: CompartmentMeta, parcels: List[ParcelMeta],
              best_pack: Dict) -> int:
    compts, rest = _pack_it(compt, parcels)
    if len(compts) < best_pack['compt_count']:
        best_pack['compt_count'] = len(compts)
        best_pack['compts'] = compts
        best_pack['rest'] = rest
    if best_pack['compt_count'] < 2:
        raise Timeout('optimal solution found')
    return len(parcels)


def _all_permutations_helper(permuted: List[ParcelMeta],
                             todo: List[ParcelMeta], iterlimit: int,
                             compt: CompartmentMeta,
                             best_pack: Dict, counter) -> int:
    if not todo:
        return counter + _try_pack(compt, permuted, best_pack)
    else:
        others = todo[1:]
        parcel = todo[0]
        # This is the most important difference between pyshipping and our
        # algorithm. We only allow certain parcel rotations.
        for orientation in parcel.legal_orientations():
            l, w, h = orientation
            # This could later be refactored to use tuples instead of objects
            rotated_parcel = ParcelMeta(l, w, h, parcel.weight)
            if compt.can_fit(rotated_parcel):
                counter = _all_permutations_helper(
                        permuted + [rotated_parcel], others, iterlimit, compt,
                        best_pack, counter)
            if counter > iterlimit:
                raise Timeout("Iteration limit reached (%d)" % counter)
        return counter


def _all_permutations(todo: List[ParcelMeta], compt: CompartmentMeta,
                      iterlimit: int = 5000
                      ) -> Tuple[List[List[ParcelMeta]], List[ParcelMeta]]:
    random.seed(1)
    random.shuffle(todo)
    best_pack = dict(compt_count=len(todo) + 1)
    try:
        # First try unpermuted
        _try_pack(compt, todo, best_pack)
        # Now try permutations
        _all_permutations_helper([], todo, iterlimit, compt, best_pack, 0)
    except Timeout:
        pass
    return best_pack['compts'], best_pack['rest']


def bin_pack(parcels: List[ParcelMeta], compt: CompartmentMeta,
             iterlimit: int = 5000
             ) -> Tuple[List[List[ParcelMeta]], List[ParcelMeta]]:
    """Attempts to pack the `Parcel`s into multiple `Compartment`s of the same
    size. We know we can fit all `Parcel`s in the `Container` when we receive a
    list of `Container`s == 1 and no `Parcel`s remaining to pack.
    """
    if not parcels:
        raise ValueError("must provide at least one package")
    if not compt:
        raise ValueError("compt cannot be None")
    compts, rest = _all_permutations(parcels, compt, iterlimit)
    return compts, rest
