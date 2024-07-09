# napari-experimental

```{contents}
---
local:
---
```

`napari-experimental` is a project that allows for experimental implementation of non-core napari features, separate from the napari codebase.
New features are implemented as plugins, with a view to later being incorporated into the core napari code once the features they provide are stable and widely-used enough to warrant integration.

At present, the project provides the following plugins:

```{toctree}
---
maxdepth: 1
---

group_layers/index
```

## Installation

You can install `napari-experimental` via [pip](https://pypi.org/project/pip/):

```bash
pip install napari-experimental
```

Or to install the latest development version:

```bash
pip install git+https://github.com/brainglobe/napari-experimental.git
```

You can also install a version of the package that uses the latest version of napari (fetched from <https://github.com/napari/napari>):

```bash
pip install napari-experimental[napari-latest]
```

## Building the Documentation

You can build the documentation locally by (in your desired Python environment);

- Installing [sphinx](https://www.sphinx-doc.org/en/master/) via `pip install sphinx`.
- Installing the documentation requirements listed in `docs/requirements.txt`, via `pip install -r docs/requirements.txt`.
- Running (at the repository root), `sphinx-build -M html docs/source docs/build`.
- This will place the rendered documentation in `.html` format inside `docs/build.html`.

CI will check that the documentation can always be built successfully whenever a PR is opened and on a push to `main`.
When a new version is released (tag on `main`) or a push to `main` occurs with changes to the documentation, it will be rebuilt and published to the repository's github pages site.

## Contributing

You can report bugs and request features by [raising an issue](https://github.com/brainglobe/napari-experimental/issues/23) on the GitHub repository - we have a few templates to help you fill out an issue if you haven't done so before.

We follow the same [contribution guidelines](https://napari.org/stable/developers/index.html) as the napari project.
Contributions are welcome to any of the plugins via pull request, and will be subject to review from appropriate maintainers.
Tests can be run with [tox](https://tox.readthedocs.io/en/latest/), please ensure the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license, "napari-experimental" is free and open source software

## Indices and Tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
