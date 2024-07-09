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

## Building the Documentation

You can build the documentation locally by (in your desired Python environment);

- Installing [sphinx](https://www.sphinx-doc.org/en/master/) via `pip install sphinx`.
- Installing the documentation requirements listed in `docs/requirements.txt`, via `pip install -r docs/requirements.txt`.
- Running (at the repository root), `sphinx-build -M html docs/source docs/build`.
- This will place the rendered documentation in `.html` format inside `docs/build.html`.

CI will check that the documentation can always be built successfully whenever a PR is opened and on a push to `main`.
When a new version is released (tag on `main`) or a push to `main` occurs with changes to the documentation, it will be rebuilt and published to the repository's github pages site.

## Contributing

We follow the same [contribution guidelines](https://napari.org/stable/developers/index.html) as the napari project.
Contributions are welcome to any of the plugins via pull request, and will be subject to review from appropriate maintainers.

## Indices and Tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
