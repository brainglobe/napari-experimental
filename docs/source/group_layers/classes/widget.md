# The `GroupLayerWidget`

```{currentmodule} napari_experimental._widget
```

The `GroupLayerWidget` instance is the parent of everything concerning the plugin.
It contains the `GroupLayer` data structure which informs the corresponding model and view, a reference to the standard `LayerList` (through it's `.global_layers` property), and is responsible for linking relevant events.

```{contents}
---
local:
---
```

## Linking Events Back to the Main `LayerList`

A number of the widget's functions and interactions with the event system are in place to ensure that the standard `LayerList` and the corresponding `GroupLayer` data structure do not go out of sync, as the napari viewer still uses the `LayerList` ordering to render the display.
As such, whilst the intention is that the user will not interact with the standard `LayerList` controls whilst using this plugin, the necessary functionality is there to ensure that anything they do does not introduce any breakages or inconsistencies:

- Adding a new layer via the `LayerList` will result in it appearing in the `GroupLayer` view. Note that the new item in the `GroupLayer` tree will be placed in a position consistent with the ordering of the `LayerList`.
- Deleting a layer from either view will remove the corresponding item from the other.
- Re-ordering layers in the `GroupLayer` view will cause the `LayerList` to reorder, in turn updating the view. Note that the converse direction does not have changes applied, since there is an ambiguity when applying a reordering that does not care for the group structure.

If this plugin gets incorporated into core napari, these functions will become obsolete since the plugin will replace the standard `LayerList` display.
The underlying `LayerList` will need to be preserved to store the `Layer`s themselves, but the user will no longer be able to interact with it.

## Debugging

The `tests/blobs.py` file in the repository contains a script that starts a napari instance with a few layers populated, and the plugin activated;

```python
import os

import napari
import numpy as np
from skimage import data

os.environ["ALLOW_LAYERGROUPS"] = "1"

points = np.random.rand(10, 3) * (1, 2, 3) * 100
colors = np.random.rand(10, 3)

blobs = data.binary_blobs(length=100, volume_fraction=0.05, n_dim=2)

viewer = napari.Viewer(ndisplay=3)

pl = napari.layers.Points(points, face_color=colors)
il = napari.layers.Image(blobs, scale=(1, 2), translate=(20, 15))

viewer.add_layer(pl)
viewer.add_layer(il)

dock_widget, plugin_widget = viewer.window.add_plugin_dock_widget(
    "napari-experimental", "Show Grouped Layers"
)

napari.run()
```

Running this script using a debugger will allow you to place breakpoints in your code for testing features that you are adding or changing.
Additionally, the plugin still retains its "enter debugger" button and corresponding function (`GroupLayerWidget._enter_debug`) which can have a breakpoint placed within it to allow you to enter a debug context with the widget as `self`.

If you are using VSCode, you can add the following configuration to your `launch.json` to launch the script above in the integrated debugger:

```json
"configurations": [
    {
        "name": "Python Debugger: Blobs.py",
        "type": "debugpy",
        "request": "launch",
        "program": "tests/blobs.py",
        "console": "integratedTerminal",
        "justMyCode": false,
    },
]
```

## API Reference

```{eval-rst}
.. autoclass:: napari_experimental._widget.GroupLayerWidget
    :members:
    :private-members:
```
