from typing import List

from .container import CONTAINER_TYPES_BY_SIZE, ContainerMeta
from .parcel import ParcelMeta


def calculate_smallest_needed_container(parcels: List[ParcelMeta]
                                        ) -> ContainerMeta:
    """Calculates the smallest `Container` that can ship the provided
    `Parcel`s. Returns `None` if no `Container` is found.
    """
    if len(parcels) == 0:
        raise ValueError("Must provide at least one Parcel")

    for cont in CONTAINER_TYPES_BY_SIZE:
        meets_basic_weight_req = cont.can_carry_all_by_weight(parcels)
        meets_basic_size_req = cont.can_fit_all_individually(parcels)
        if not meets_basic_weight_req or not meets_basic_size_req:
            continue
        if len(parcels) == 1:
            return cont
        else:
            # TODO Do intelligent calculation here
            pass

    return None
