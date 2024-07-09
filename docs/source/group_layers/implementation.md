# Implementation

```{contents}
---
local:
---
```

This section is intended as a bridge between the documentation and docstrings, and the implementation of the Group Layers plugin.
Before you begin, we recommend a few articles that provide an introduction to the concepts this plugin relies on:

- [Model/view programming](https://doc.qt.io/qt-6/model-view-programming.html), and in particular tree models and views.
- We recommend you read the docstrings for `Group`s and `Node`s [in the napari codebase](https://github.com/napari/napari/blob/main/napari/utils/tree), for context on how napari currently handles such structures.
- You may also want to [review this article](https://refactoring.guru/design-patterns/composite) on composite design patterns.

The docstrings, plus the explanations in this section, should then afford you enough information into how the plugin is operating.

Additionally, the "enter debugger" button has been left within the plugin.
This is intended for developer use and should be removed when the plugin is ready for release!
Adding a breakpoint within the `GroupLayerWidget._enter_debug` method allows a developer to enter a debug context with the plugin's widget as `self`, whilst running napari.

## Key Classes

The key classes implemented in this plugin are

- `GroupLayerNode`, `GroupLayer`: These are the Python classes that provide the tree-structure that group layers require. We expand on these below.
- `QtGroupLayerControls`, `QtGroupLayerControlsContainer`: These classes are used to build the "control box" that the plugin provides when selecting a layer within the plugin. For all intents and purposes it mimics the existing napari layer viewer context window, but also reacts when selecting a group layer.
- `QtGroupLayerModel`, `QtGroupLayerView`: These subclass from the appropriate Qt abstract classes, and provide the model/tree infrastructure for working with `GroupLayers`. Beyond this, they do not contain any remarkable functionality beyond patching certain methods for consistency with the data being handled / displayed.

You can navigate to the respective pages for further information on each of these classes:

```{toctree}
---
maxdepth: 1
---

classes/group_layer_and_nodes
```
