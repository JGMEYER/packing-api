# Setup

Install all packages (including dev):
```
$ pipenv install --dev
```

Run the project with:
```
$ pipenv run uvicorn app.main:app --reload
```
OR just run the following from the pipenv shell.
```
$ uvicorn app.main:app --reload
```
