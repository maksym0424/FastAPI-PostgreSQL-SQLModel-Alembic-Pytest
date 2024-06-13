# master-server

Master server for [oxyproxy](https://oxyproxy.io).

# Developers guide

## Setting up the development environment

1. Clone the repository
2. Make sure [poetry](https://python-poetry.org/docs/#installation) is installed.
3. Run: `poetry config virtualenvs.in-project true`
4. Ensure you are using supported python version: `poetry env use 3.12`
5. Run: `poetry install`

## Development with Docker & Local

This server is expected to run in a docker container. The included `docker-compose.dev.yml` file can be used to run the server in a container. It will setup a postgres database and run the server in a container.
To start the server run:

```bash
make runBuildDocker
# or
make runDocker
```

For rapid development you should run the docker container once for the database and then run the server locally.

```bash
make runLocal
```

By default the server will run on `http://localhost:1140`. Before creating a new PR make sure eveything works both in docker and locally.

## Environment variables

Environment variables are loaded from a `.env` file for docker and from `.env.local` for local development. To know which variables are required check the `.env.example` file.

## Migrations

When a new model is added or an existing model is modified a new migration should be created. To create a new migration run:

```bash
make createMigration
```

The migration will be automatically applied when the server starts.

## Formatting

We use [ruff](https://docs.astral.sh/ruff/) for formatting. To format the code run:

```bash
ruff format
```

## References

- https://testdriven.io/blog/fastapi-sqlmodel/
- https://fastapi.tiangolo.com/tutorial/bigger-applications/
