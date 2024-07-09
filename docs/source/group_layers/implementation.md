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

```

## `Group`s and `Node`s

`GroupLayerNode`  (GLN) and `GroupLayer`  (GL) inherit from the base napari classes `Node` and `Group` (respectively).
The GLNs act as wrappers for `Layer`s - each one tracks (a pointer to) one particular `Layer` through the `.layer` attribute and uses its information when rendering in the GUI.
GLs allow us to organise GLNs into groups, but they themselves must also be instances of GLN.
For this reason, the convention we have adopted is that GLs have the `.layer` attribute set to `None` (since they do not track an individual layer that is associated to _them_ specifically).
Furthermore, the `is_group` method is explicitly defined on both GLNs and GLs, which provides a way to distinguish between the two classes when traversing the tree structure.

It should also be noted that we have made the decision not to make GLNs inherit from `Layer`, nor make the existing `Layer` class subclass from `Node`.

- The latter would require changes to core napari code, so is outside the scope of this plugin.
- The former option then introduces event conflicts (within the constructors) when GL inherits from both `Group` and `Layer`. Again, fixing these issues requires either edits to the core napari codebase, or regurgitating a lot of the core napari codebase inside a new class for just a couple of line changes.
- From a separation of concerns perspective, it is cleaner to have the group layer functionality impose a structure on top of the existing `LayerList` that napari tracks, rather than duplicate this information so it can be stored in the GL, and then have to deal with changes to one of the objects being reflected back on the "original" it came from.

### Differences in Indexing Conventions

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
