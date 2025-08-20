[![pytest](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pytest.yml) [![pre-commit](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/cisco-eti/identity-auth-server/actions/workflows/pre-commit.yml)

# identity-auth-server
Initial commit for the identity-auth-server project. **Please edit this file to add the relevant information.**

## Notes
To manage Python environment, we use [uv](https://docs.astral.sh/uv/). Make sure it is installed in your system!

If no upstream repo is defined yet and you are starting from scratch, initialize git and make the initial commit:
```shell
git init
git branch -m main
git add .
git commit -m "Initial commit"
```

### Creating the Python environment
After cloning the repo, run the following command to create the corresponding Python environment and to install project's `pre-commit` hooks:

```shell
make init
```

To activate the environment, run:

```shell
source .venv/bin/activate
```

Please notice that using `uv`, the project's package(s) conveniently get installed in the Python environment in [editable mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html).

Note: The project structure is based on the [Accord Python Project Template](https://github.com/cisco-eti/Accord-Python-Template). The template makes linting and environment management easy. Look at [developer notes](docs/Developer_notes.md) for more details.
