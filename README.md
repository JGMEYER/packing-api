# Setup

Install all packages (including dev):
```
$ pipenv install --dev
```

# Run Locally

Run the project with:
```
$ pipenv run uvicorn app.main:app --reload
```
OR just run the following from the pipenv shell.
```
$ uvicorn app.main:app --reload
```

You can then view the docs by navigating to `127.0.0.1/docs` in your brower.
