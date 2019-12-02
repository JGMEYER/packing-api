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
