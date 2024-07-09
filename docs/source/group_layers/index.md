# Group Layers

This plugin allows [napari](https://github.com/napari/napari) layers to be organised into 'layer groups'.
Groups can hold any number of layers, in addition to further sub-groups.
This follows suggestions [from the corresponding issue](https://github.com/napari/napari/issues/6345) on the main napari repository.

Main features:

- Creation of group layers
- Drag and drop layers/groups to re-organise them
- Sync changes in layer order from the plugin to the main napari `LayerList`
- Toggle visibility of layers and entire groups through the 'eye' icon or right click menu

## Ethos and Outlook

The aim of this plugin is to provide an entirely separate way to interact with layers in napari.
While using it, the main `layer list` should only be used to add/remove layers, with all re-ordering, re-naming etc done directly within the plugin itself.
To aid this, the plugin contains its own independent layer controls, as well as right-click menus and other features.

Ultimately, the goal of this plugin is to provide a way to experiment with group layers independent from the main napari codebase.
Hopefully, parts of this plugin widget will be incorporated back into napari, replacing the existing `LayerList`.

## Installation

After installing `napari-experimental`, select the "Show Group Layers" plugin from the dropdown menu in `napari`.

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

:partying_face:
