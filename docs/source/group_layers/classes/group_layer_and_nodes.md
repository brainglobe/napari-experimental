# `GroupLayer`s and `GroupLayerNode`s

`GroupLayerNode`  (GLN) and `GroupLayer`  (GL) inherit from the base napari classes `Node` and `Group` (respectively).
The GLNs act as wrappers for `Layer`s - each one tracks (a pointer to) one particular `Layer` through the `.layer` attribute and uses its information when rendering in the GUI.
GLs allow us to organise GLNs into groups, but they themselves must also be instances of GLN.
For this reason, the convention we have adopted is that GLs have the `.layer` attribute set to `None` (since they do not track an individual layer that is associated to _them_ specifically).
Furthermore, the `is_group` method is explicitly defined on both GLNs and GLs, which provides a way to distinguish between the two classes when traversing the tree structure.

It should also be noted that we have made the decision not to make GLNs inherit from `Layer`, nor make the existing `Layer` class subclass from `Node`.

- The latter would require changes to core napari code, so is outside the scope of this plugin.
- The former option then introduces event conflicts (within the constructors) when GL inherits from both `Group` and `Layer`. Again, fixing these issues requires either edits to the core napari codebase, or regurgitating a lot of the core napari codebase inside a new class for just a couple of line changes.
- From a separation of concerns perspective, it is cleaner to have the group layer functionality impose a structure on top of the existing `LayerList` that napari tracks, rather than duplicate this information so it can be stored in the GL, and then have to deal with changes to one of the objects being reflected back on the "original" it came from.

```{contents}
---
local:
---
```

## Differences from the `LayerList` Indexing Convention

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

## API Reference

### `GroupLayerNode`

```{currentmodule} napari_experimental.group_layer_node
```

```{eval-rst}
.. autoclass:: GroupLayerNode
    :members:
```

### `GroupLayer`

```{currentmodule} napari_experimental.group_layer
```

```{eval-rst}
.. autoclass:: GroupLayer
    :members:
```
