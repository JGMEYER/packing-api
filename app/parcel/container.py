from typing import List

from pydantic import BaseModel


class CompartmentMeta(BaseModel):
    """Meta class for storing `Compartment` data.

    A `Compartment` is a storage area in a `Container` that can fit `Parcels`.
    """
    length: float
    width: float
    height: float


class ContainerMeta(BaseModel):
    """Meta class for storing `Container` data.

    A `Container` is a vehicle or vessel that can be used to fit and transport
    `Parcels` inside its various `Compartment`s.
    """
    compartments: List[CompartmentMeta]
    max_single_weight: float
    max_total_weight: float


# Container types

COMPACT = ContainerMeta([CompartmentMeta(24, 24, 36)], 50, 150)
SEDAN = ContainerMeta(
    [CompartmentMeta(24, 24, 36), CompartmentMeta(24, 24, 48)], 50, 250)
VAN = ContainerMeta([CompartmentMeta(120, 60, 60)], 70, 500)
TRUCK = ContainerMeta([CompartmentMeta(150, 96, 84)], 500, 2000)

CONTAINER_TYPES = ContainerMeta.__subclasses__()
