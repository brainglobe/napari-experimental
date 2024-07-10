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
