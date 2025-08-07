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
We also recommend you read the docstrings for `Group`s and `Node`s [in the napari codebase](https://github.com/napari/napari/blob/main/napari/utils/tree), for context on how napari currently handles such structures.
You may also want to [review this article](https://refactoring.guru/design-patterns/composite) on composite design patterns.

The docstrings, plus the explanations in this section, should then afford you enough information into how the plugin is operating.

Additionally, the "enter debugger" button has been left within the plugin.
This is intended for developer use and should be removed when the plugin is ready for release!
Adding a breakpoint within the `GroupLayerWidget._enter_debug` method allows a developer to enter a debug context with the plugin's widget as `self`, whilst running napari.

### Key Classes

The key classes implemented in this plugin are

- `GroupLayerNode`, `GroupLayer`: These are the Python classes that provide the tree-structure that group layers require. We expand on these below.
- `QtGroupLayerControls`, `QtGroupLayerControlsContainer`: These classes are used to build the "control box" that the plugin provides when selecting a layer within the plugin. For all intents and purposes it mimics the existing napari layer viewer context window, but also reacts when selecting a group layer.
- `QtGroupLayerModel`, `QtGroupLayerView`: These subclass from the appropriate Qt abstract classes, and provide the model/tree infrastructure for working with `GroupLayers`. Beyond this, they do not contain any remarkable functionality beyond patching certain methods for consistency with the data being handled / displayed.

#### `Group`s and `Node`s

`GroupLayerNode`  (GLN) and `GroupLayer`  (GL) inherit from the base napari classes `Node` and `Group` (respectively).
The GLNs act as wrappers for `Layer`s - each one tracks (a pointer to) one particular `Layer` through the `.layer` attribute and uses its information when rendering in the GUI.
GLs allow us to organise GLNs into groups, but they themselves must also be instances of GLN.
For this reason, the convention we have adopted is that GLs have the `.layer` attribute set to `None` (since they do not track an individual layer that is associated to _them_ specifically).
Furthermore, the `is_group` method is explicitly defined on both GLNs and GLs, which provides a way to distinguish between the two classes when traversing the tree structure.

It should also be noted that we have made the decision not to make GLNs inherit from `Layer`, nor make the existing `Layer` class subclass from `Node`.

- The latter would require changes to core napari code, so is outside the scope of this plugin.
- The former option then introduces event conflicts (within the constructors) when GL inherits from both `Group` and `Layer`. Again, fixing these issues requires either edits to the core napari codebase, or regurgitating a lot of the core napari codebase inside a new class for just a couple of line changes.
- From a separation of concerns perspective, it is cleaner to have the group layer functionality impose a structure on top of the existing `LayerList` that napari tracks, rather than duplicate this information so it can be stored in the GL, and then have to deal with changes to one of the objects being reflected back on the "original" it came from.

#### Differences in Indexing Conventions

A key difference between a flat `LayerList` and our GL structure is how they are indexed, and how the structures are rendered in the napari viewer based on this indexing.
`LayerList` is indexed from 0 ascending, and renders in the napari viewer with the layer at index 0 at the _bottom_ of the `LayerList`.
`Layer`s with higher indices are rendered _on top_ of those with a lower index, with the item assigned the highest index appearing at the top of the layer viewer window.

By contrast, GL uses `NestedIndex`es to track the position of GLNs; these are tuples of integers that can be of arbitrary length (so long as the GL has the structure to match), and should be interpreted as subsequent accesses of objects in the tree:

- (0, 1) refers to the item at index 1 of the (sub)-GL at index 0 of the root GL.
- (2,) refers to the item at index 2 of the root GL.

Note that an "item" can be a GLN or a GL (use the `is_group` method to distinguish if necessary)!
Again, items are added to a GL using the lowest available index.
GLs can also assign a flat index order to their elements by starting from the root tree and counting upwards from 0, descending into sub-GLs and exhausting their items when they are encountered (see `GroupLayer.flat_index_order`).

However GLs render with index 0 _at the top_ of the view, and higher indices below them.
In order to preserve the user's intuitive understanding of "layers higher up in the display appear on top of lower layers", it is thus necessary to pass the _reversed_ order of layers back to the viewer after a rearrangement event in the GL viewer.

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
