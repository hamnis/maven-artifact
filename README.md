# maven-artifact
A python library to download and resolve maven artifacts.

# Installation and Usage

 * Install using pip: `pip install maven-artifact'
 * Usage: run `maven-artifact` 

# Requirements

 * See `pyproject.toml` for details on required Python versions, pip packages etc.

# Contributing

 * Fork repo
 * Before submitting a PR
   * Perform formatting (black):  `hatch run lint:black src tests`
   * Run linter (flake8): `hatch run lint:flake8`
   * Run tests:
     * all: `hatch run test:pytest --cov=maven_artifact`
     * unit only: `hatch run test:pytest --cov=maven_artifact  tests/unit`
     * integration only: `hatch run test:pytest --cov=maven_artifact  tests/integration`
