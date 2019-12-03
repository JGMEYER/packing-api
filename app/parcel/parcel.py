from decimal import Decimal
from dataclasses import field
from typing import Set, Tuple

from pydantic.dataclasses import dataclass


@dataclass
class ParcelMeta:
    """Meta class for storing `Parcel` data.

    A `Parcel` is a package of fixed dimensions and weight that can be shipped
    within a `Container`.
    """
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal
    volume: Decimal = field(init=False)

    def __post_init__(self):
        # BUG: For some reason we have to reinitialize each as Decimals to
        # retain our precision?
        self.volume = (
            Decimal(self.length) * Decimal(self.width) * Decimal(self.height)
        )

    def legal_orientations(self) -> Set[Tuple[float, float, float]]:
        """Returns all viable orientations for the `Parcel` when placed in a
        `Container`.
        """
        l, w, h = self.length, self.width, self.height
        # Parcels must be placed upright
        return {(l, w, h), (w, l, h)}
