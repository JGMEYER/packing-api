from typing import List

from pydantic import BaseModel
from fastapi import BackgroundTasks, FastAPI, Query

from .parcel.packer import calculate_smallest_needed_container
from .parcel.parcel import ParcelMeta


app = FastAPI()


class ParcelRequest(BaseModel):
    """Meta class for receiving `Parcel` data and their quantities"""
    length: float = Query(..., gt=0)
    width: float = Query(..., gt=0)
    height: float = Query(..., gt=0)
    weight: float = Query(..., gt=0)
    quantity: int = Query(..., gt=0)


@app.post("/vehicle_size")
async def vehicle_size(parcel_list: List[ParcelRequest],
                       background_tasks: BackgroundTasks):
    parcels = []

    for parcel_request in parcel_list:
        for i in range(parcel_request.quantity):
            parcel = ParcelMeta(
                length=parcel_request.length,
                width=parcel_request.width,
                height=parcel_request.height,
                weight=parcel_request.weight,
            )
            parcels.append(parcel)

    container = calculate_smallest_needed_container(parcels)

    return {"vehicle_size": container.name}
