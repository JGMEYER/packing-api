from pydantic.dataclasses import dataclass


@dataclass
class ParcelMeta:
    """Meta class for storing `Parcel` data.

    A `Parcel` is a package of fixed dimensions and weight that can be shipped
    within a `Container`.
    """
    length: float
    width: float
    height: float
    weight: float

    def legal_orientations(self):
        """Returns all viable orientations for the `Parcel` when placed in a
        `Container`.
        """
        l, w, h = self.length, self.width, self.height
        # Parcels must be placed upright
        return [(l, w, h), (w, l, h)]
