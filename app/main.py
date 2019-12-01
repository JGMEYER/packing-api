from typing import List

from fastapi import FastAPI

from .parcel.parcel import ParcelMeta


app = FastAPI()


# TODO should this really extend ParcelMeta?
class ParcelRequest(ParcelMeta):
    quantity: int


@app.post("/vehicle_size")
async def vehicle_size(request: List[ParcelRequest]):
    return {"message": "ok then"}
