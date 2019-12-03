import uuid
from decimal import Decimal
from enum import IntEnum
from typing import List, Dict

from pydantic import BaseModel
from fastapi import BackgroundTasks, FastAPI, HTTPException, Path, Query

from .parcel import packer
from .parcel.parcel import ParcelMeta


########
# Jobs #
########

# Ideally, we would move job tracking to Redis or some other persistent data
# store. For the sake of the project timeline, we track jobs in memory. This
# means that jobs are lost whenever the server crashes or reboots.
# Additionally, jobs are not automatically purged, meaning the size of our job
# tracker will grow indefinitely.
#
# FastAPI recommends Celery with Redis or RabbitMQ for heavy background
# computation.

# uses uuid4
JOB_ID_REGEX = (
    r"^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z"
)


class JobStatus(IntEnum):
    FAILED = -1
    RUNNING = 0
    COMPLETE = 1


JOB_FINAL_STATES = [JobStatus.FAILED, JobStatus.COMPLETE]


class Job:
    """Metadata for tracking background `Job`s"""

    def __init__(self, job_id):
        self.status = JobStatus.RUNNING
        self.result = None


jobs: Dict[str, Job] = {}


def new_job_id() -> str:
    """Returns unique job_id"""
    return str(uuid.uuid4())


async def dispatch_job(job_id, func, *args, **kwargs) -> None:
    """Dispatches function to `Job` queue"""
    job = Job(job_id)
    jobs[job_id] = job
    try:
        job.result = func(*args, **kwargs)
    except Exception as e:
        job.status = JobStatus.FAILED
        job.result = {"error": str(e)}
        return
    job.status = JobStatus.COMPLETE


#######
# API #
#######

app = FastAPI()


class ParcelRequest(BaseModel):
    """Meta class for receiving `Parcel` data and their quantities"""
    length: Decimal = Query(..., gt=0)
    width: Decimal = Query(..., gt=0)
    height: Decimal = Query(..., gt=0)
    weight: Decimal = Query(..., gt=0)
    quantity: int = Query(..., gt=0)


def _get_vehicle_size(parcels: List[ParcelMeta]):
    container = packer.calculate_smallest_needed_container(parcels)
    name = container.name if container else None
    return {"vehicle_size": name}


# TODO add docstring
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

    job_id = new_job_id()
    background_tasks.add_task(dispatch_job, job_id, _get_vehicle_size, parcels)
    return {"job_id": job_id}


@app.get("/job/{job_id}")
async def job_status(job_id: str = Path(..., regex=JOB_ID_REGEX)):
    """Retrieves the specified job from the queue."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return {"job_id": job_id, "job_status": job.status,
            "job_result": job.result}
