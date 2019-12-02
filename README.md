# Description

An API for retrieving the smallest `Container` needed to fit a set of `Parcels`
based on size and weight requirements.

`Parcels` are packages of a fixed dimension and weight. A `Container` is a vehicle or vessel that can be used to fit and transport `Parcels` inside its various `Compartment`s.

`Parcels` have a constraint in that they must be placed upright in a `Compartment`.

# Design decisions and tradeoffs

* 3D packing with 3 axis rotation is NP-hard, many companies invest heavily on a solution, and many papers are written on the topic - while this problem is made simpler in our case by constraining rotation, I still ended up going with a heuristic approach on `Parcel` volume, based on the existing bin-packing package, `pyShipping`.
* Floating point precision is an issue when we allow for non-integer dimensions of our `Parcels`.
* Because we can expect our bin-packing logic to take a significant amount of time with large requests and API timeouts could become an issue, we use short-polling to dispatch a job in the background instead of returning a response immediately. The API user can then poll on the status of the dispatched job.

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

# Testing

Run unit tests with:
```
$ pipenv run pytest
```
OR, from the pipenv shell:
```
$ pytest
```
