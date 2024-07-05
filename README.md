# napari-experimental

[napari]: https://github.com/napari/napari
[file an issue]: https://github.com/brainglobe/napari-experimental/issues
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/

[![License BSD-3](https://img.shields.io/pypi/l/napari-experimental.svg?color=green)](https://github.com/brainglobe/napari-experimental/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-experimental.svg?color=green)](https://pypi.org/project/napari-experimental)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-experimental.svg?color=green)](https://python.org)
[![tests](https://github.com/brainglobe/napari-experimental/workflows/tests/badge.svg)](https://github.com/brainglobe/napari-experimental/actions)
[![codecov](https://codecov.io/gh/brainglobe/napari-experimental/branch/main/graph/badge.svg)](https://codecov.io/gh/brainglobe/napari-experimental)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-experimental)](https://napari-hub.org/plugins/napari-experimental)

## Overview

### Features

This plugin allows [napari] layers to be organised into 'layer groups'.
Groups can hold any number of layers, in addition to further sub-groups.
This follows suggestions [from the corresponding issue](https://github.com/napari/napari/issues/6345) on the main napari repository.

Main features:

- Creation of group layers
- Drag and drop layers/groups to re-organise them
- Sync changes in layer order from the plugin to the main napari `LayerList`
- Toggle visibility of layers and entire groups through the 'eye' icon or right click menu

### Ethos

The aim of this plugin is to provide an entirely separate way to interact with layers in napari.
While using it, the main `layer list` should only be used to add/remove layers, with all re-ordering,  re-naming etc done directly within the plugin itself.

To aid this, the plugin contains its own independent layer controls, as well as right click menus and other features.

### Outlook

Ultimately, the goal of this plugin is to provide a way to experiment with group layers independent from the main napari codebase.
Hopefully, parts of this plugin widget will be incorporated back into napari, replacing the existing `LayerList`.

## Implementation Details

This section is a halfway point between full developer documentation and throwing docstrings in a contributor's face.
We have been diligent in adding docstrings to our methods, however we recommend you first read about [model/view programming](https://doc.qt.io/qt-6/model-view-programming.html) and in particular tree models and views.
The docstrings, plus the explanations in this section, should then afford you enough information into how the plugin is operating.

### Key Classes

## Todo

### Desirable features

- Expand right click menu options to include:
  - Add selected items to new group
  - Add selected items to existing group
  - All existing right-click options for layers from the main `LayerList`
- Add independent buttons to add/remove layers to the plugin (this would make it fully independent of the main `LayerList`). Also, style the `Add empty layer group` button to match these.

### Known bugs and issues (non-breaking, but poor UX)

- The open/closed state of group layers doesn't persist on drag and drop <https://github.com/brainglobe/napari-experimental/issues/23>

### Known bugs and issues (breaking)

- Seg-fault when adding an empty group to another empty group <https://github.com/brainglobe/napari-experimental/issues/12>

### Development Tasks

- Create a standalone docs site that expands on the implementation details section.
  - Remove said section and transfer its contents to the docs site
  - Link to the docs site in the README.

## Installation

You can install `napari-experimental` via [pip]:

```bash
pip install napari-experimental
```

To install the latest development version:

```bash
pip install git+https://github.com/brainglobe/napari-experimental.git
```

You can also install a version of the package that uses the latest version of napari (fetched from <https://github.com/napari/napari>):

```bash
pip install napari-experimental[napari-latest]
```

## Contributing

Contributions are very welcome.
Tests can be run with [tox], please ensure the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license, "napari-experimental" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.
