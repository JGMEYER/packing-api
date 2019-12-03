# Description

An API for retrieving the smallest `Container` needed to fit a set of `Parcels`
based on size and weight requirements.

`Parcels` are packages of a fixed dimension and weight. A `Container` is a vehicle or vessel that can be used to fit and transport `Parcels` inside its various `Compartment`s.

`Parcels` have a constraint in that they must be placed upright in a `Compartment`.

# Design decisions and tradeoffs

* 3D packing with 3 axis rotation is NP-hard, many companies invest heavily on a solution, and many papers are written on the topic - while this problem is made simpler in our case by constraining rotation, I still ended up going with a heuristic approach on `Parcel` volume, based on the existing bin-packing package, `pyShipping`.
* Floating point precision is an issue when we allow for non-integer dimensions of our `Parcels`, so I ended up using the Decimal class to 4 degrees of precision (see `app/__init__.py`). This use of precision has not been propagated throughout the advanced bin-packing logic, however, and would take some additional work to do so.
* Because we can expect our bin-packing logic to take a significant amount of time with large requests and API timeouts could become an issue, we use short-polling to dispatch a job in the background instead of returning a response immediately. The API user can then poll on the status of the dispatched job.
* Job queuing is done in memory due to my time constraints. The tradeoffs with this solution are described in `main.py`.

# Setup

1. Install pipenv: https://pypi.org/project/pipenv/. Pipenv is an amazing tool for managing our virtualenv.

1. Install all packages (including dev):
```
$ pipenv install --dev
```

# Run Locally

Run the project with:
```
$ pipenv run uvicorn app.main:app --reload
```
OR, from the pipenv shell:
```
$ uvicorn app.main:app --reload
```

You can then view the Swagger docs by navigating to `127.0.0.1/docs` in your browser.

# Calling endpoints

## POST /vehicle_size

```
$ curl -X POST "http://localhost:8000/vehicle_size" -H  "accept: application/json" -H  "Content-Type: application/json" -d "[{\"length\":20,\"width\":20,\"height\":30,\"weight\":60,\"quantity\":1}]"
```

Example:

```
$ curl -X POST "http://localhost:8000/vehicle_size" -H  "accept: application/json" -H  "Content-Type: application/json" -d "[{\"length\":20,\"width\":20,\"height\":30,\"weight\":60,\"quantity\":1}]"

{"job_id":"c3946435-548b-47b1-9fd0-34cab0f3540f"}
```

## GET /job/{job_id}

Using job_id received from vehicle_size:

```
$ curl "http://localhost:8000/job/<jobid>"
```

Example:

```
$ curl "http://localhost:8000/job/c3946435-548b-47b1-9fd0-34cab0f3540f"

{"job_id":"c3946435-548b-47b1-9fd0-34cab0f3540f","job_status":1,"job_result":{"vehicle_size":"van"}}
```

# Testing

Run unit tests with:
```
$ pipenv run pytest
```
OR, from the pipenv shell:
```
$ pytest
```
