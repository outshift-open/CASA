# Developer notes
A number of developer tools are used in this repo. The configuration for all tools are integrated into the `pyproject.toml` file. We use:

* Managing Python environment using standard conforming `.venv`
* Dependency management relying exclusively on `pyproject.toml`
* Extremely fast dependency resolution using [uv](https://docs.astral.sh/uv/)
* GitHub workflows for linting, checking code formatting, and running unit tests (on both Linux and Mac)
* Testing using [pytest](https://docs.pytest.org/en/latest/).
* Extremely fast source code formatting and linting using [Ruff](https://docs.astral.sh/ruff/).

* Automation of running linters and code formatters using git [pre-commit](https://pre-commit.com/) hooks.
  * mypy: for checking type annotations
  * ruff: for source formatting (`isort` + `black` + `flake8`)
  * nb-clean: to minify notebooks before commits
  * checks for common issues: line-endings, large files, private keys, etc.
* standardizing IDE/Editor basic config (tab sizes, number of characters per line, etc.) using [EditorConfig](https://editorconfig.org/).


## Quick summary
Note: We use `make` to solidify most commonly used operations. However, using `make` is only to simplify typing repetitive commands. Most operations are simle one-line commands using cli tools.

Notice: in a modern Python package/program, there is no need for a `requirement.txt` or `setup.py` files as everything is handled by [pyproject.toml](pyproject.toml)

You need to run `make init` once, typically right after cloning the repo, to create the git repo as well as the Python environment.

From then on, if there is a change in the dependencies, use `make update` to update the Python environment.

When making commits, `pre-commit` hooks will automatically run the code formatter and linter tools. This potentially reformats the `.py` files (and notebooks) accordingly. This way, we ensure nothing will be pushed to the repository unless it meets the needs for style and linting; reducing the overheads in code review.

Finally, when ready to build the package, run `make build`. The standard wheel files will be stored in `dist/` folder.

## Dealing with Python environments and package's dependencies
We use `uv` to manage Python environments as in addition to Python packages, it can also install and manage Python itself. `uv` is extremely fast and conforms fully to PEP standards.

As for the package or project dependencies, everything is managed in the [pyproject.toml](pyproject.toml). Notice that in that file, there are different sections for what is needed for the running the program/package and what is needed during the development in the local Python environment (e.g. linter tools such Ruff).

Please feel free to edit the [pyproject.toml](pyproject.toml) to manage the dependencies. Alternatively, you can use `uv` directly at command line to add dependecites: e.g. `uv add numpy` will add `numpy` to the environment and upadate the `pyproject.toml` accordingly.

To manage Pytorch in different development environments, with and without CUDA, we use a configuration based on extra depenedncies. If you are using `make init` and `make update`, you don't need to deal with this part as the MakeFile already knows how to handle that. For more details, have a look the [uv documentation](https://docs.astral.sh/uv/guides/integration/pytorch/)

# Daily operations
## Initialization

Right after creating the template (i.e. after using cookiecutter) initialize `git`. For example:

```shell
git init
git branch -m main
git add .
git commit -m "Initial commit"
```

Next, initialize the environment by running the following command:

```shell
make init
```

Note: this step needs to be done only once. Running it a second time is harmless but could be slow: it will simply delete the existing conda environment and recreate it.

## activating the environment
Since we use a standard `.venv` environment, you may activate the environment the usual way:

```shell
source .venv/bin/activate
```

## Changing dependencies
Modify `pyproject.toml` to change the needed dependencies. Afterward, use the following command to update the Python environment:

```shell
make update
```

## Building the package
Once you are ready to build the package, you can run:

```shell
make build
```

This will create the `.whl` as well as the source distribution of the package (the `.gz` file) in the `dist` older

## Running unit tests
You could simply run

```shell
pytest
```

 or

 ```
 make test
 ```
at the root repo of the repo of the folder. Notice that the project's conda environment should be active if you want to run `pytest` manually (the `make` version automatically activates the right environment itself)

## Running the code formatters and linters
The `make init` command while initializing the project already should have installed the needed git hooks to run all the needed tools for linting and formatting the Python file. These will be done as soon as you commit changes to the repository.

In case you want to manually run those tools, you can run:

```shell
pre-commit run --all-files
```

Otherwise, just to run the tools without making any changes to files (e.g. to check formatting), you can run:

```shell
make check
```

## Recreating the Python enviroment
In rare cases, you might want to delete and recreate the Python environment. To do so, you may run:

```shell
make clean
```
