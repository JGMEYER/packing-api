from dataclasses import field
from decimal import Decimal
from typing import List

from pydantic.dataclasses import dataclass

from .parcel import ParcelMeta


@dataclass
class CompartmentMeta:
    """Meta class for storing `Compartment` data.

    A `Compartment` is a storage area in a `Container` that can fit `Parcels`.
    """
    length: Decimal
    width: Decimal
    height: Decimal
    volume: Decimal = field(init=False)

    def __post_init__(self):
        # BUG: For some reason we have to reinitialize each as Decimals to
        # retain our precision?
        self.volume = (Decimal(self.length) * Decimal(self.width)
                       * Decimal(self.height))

    def can_fit(self, parcel: ParcelMeta) -> bool:
        """Returns whether the `Compartment` can fit the `Parcel`, assuming
        it's empty.
        """
        for l, w, h in parcel.legal_orientations():
            if l <= self.length and w <= self.width and h <= self.height:
                return True
        return False


@dataclass
class ContainerMeta:
    """Meta class for storing `Container` data.

    A `Container` is a vehicle or vessel that can be used to fit and transport
    `Parcels` inside its various `Compartment`s.
    """
    name: str
    compartments: List[CompartmentMeta]
    max_single_weight: Decimal
    max_total_weight: Decimal

    def can_carry_all_by_weight(self, parcels: List[ParcelMeta]) -> bool:
        """Returns whether the `Container` can support the weight of the
        supplied `Parcel`s.
        """
        total_parcel_weight = 0
        for p in parcels:
            if p.weight > self.max_single_weight:
                return False
            total_parcel_weight += p.weight
            if total_parcel_weight > self.max_total_weight:
                return False
        return True

    def can_fit(self, parcel: ParcelMeta) -> bool:
        """Returns whether the `Container` can fit the `Parcel` in one of its
        `Compartments`, assuming each `Compartment` is empty.
        """
        for comp in self.compartments:
            if comp.can_fit(parcel):
                return True
        return False

    def can_fit_all_individually(self, parcels: List[ParcelMeta]) -> bool:
        """Returns whether all `Parcel`s can individually fit within the
        `Contaniner`, assuming each `Compartment` is empty. Can be used as an
        optimization before packing.
        """
        for p in parcels:
            if not self.can_fit(p):
                return False
        return True

    def can_fit_all_by_volume(self, parcels: List[ParcelMeta]) -> bool:
        """Returns whether the `Container` can fit all `Parcels` purely by
        volume. This response is naiive, to get an accurate response, we need
        to attempt a form of 3D bin-packing."""
        parcels_volume = sum([p.volume for p in parcels])
        compartments_volume = sum([c.volume for c in self.compartments])
        return parcels_volume <= compartments_volume


# Container types

COMPACT = ContainerMeta('compact', [CompartmentMeta(24, 24, 36)], 50, 150)
SEDAN = ContainerMeta('sedan', [CompartmentMeta(24, 24, 36),
                                CompartmentMeta(24, 24, 48)], 50, 250)
VAN = ContainerMeta('van', [CompartmentMeta(120, 60, 60)], 70, 500)
TRUCK = ContainerMeta('truck', [CompartmentMeta(150, 96, 84)], 500, 2000)

# Ordered list of container types by relative size
CONTAINER_TYPES_BY_SIZE = [COMPACT, SEDAN, VAN, TRUCK]
