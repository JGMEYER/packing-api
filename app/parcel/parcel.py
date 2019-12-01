from pydantic import BaseModel


class ParcelMeta(BaseModel):
    """Meta class for storing `Parcel` data.

    A `Parcel` is a package of fixed dimensions and weight that can be shipped
    within a `Container`.
    """
    length: float
    width: float
    height: float
    weight: float
