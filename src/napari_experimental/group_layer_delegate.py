from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from napari._app_model.constants import MenuId
from napari._app_model.context import get_context
from napari._qt._qapp_model import build_qmodel_menu
from napari._qt.containers._base_item_model import ItemRole
from napari._qt.containers._layer_delegate import LayerDelegate
from napari._qt.containers.qt_layer_model import ThumbnailRole
from napari._qt.qt_resources import QColoredSVGIcon
from qtpy.QtCore import QPoint, QSize, Qt
from qtpy.QtGui import QMouseEvent, QPixmap

if TYPE_CHECKING:
    from napari.components.layerlist import LayerList
    from qtpy import QtCore
    from qtpy.QtWidgets import QStyleOptionViewItem


class GroupLayerDelegate(LayerDelegate):
    """A QItemDelegate specialized for painting group layer objects."""

    def get_layer_icon(
        self, option: QStyleOptionViewItem, index: QtCore.QModelIndex
    ):
        """Add the appropriate QIcon to the item based on the layer type.
        Same as LayerDelegate, but pulls folder icons from inside this plugin.
        """
        item = index.data(ItemRole)
        if item is None:
            return
        if item.is_group():
            expanded = option.widget.isExpanded(index)
            icon_name = "folder-open" if expanded else "folder"
            icon_path = (
                Path(__file__).parent / "resources" / f"{icon_name}.svg"
            )
            icon = QColoredSVGIcon(str(icon_path))
        else:
            icon_name = f"new_{item.layer._type_string}"
            try:
                icon = QColoredSVGIcon.from_resources(icon_name)
            except ValueError:
                return
        # guessing theme rather than passing it through.
        bg = option.palette.color(option.palette.ColorRole.Window).red()
        option.icon = icon.colored(theme="dark" if bg < 128 else "light")
        option.decorationSize = QSize(18, 18)
        option.decorationPosition = (
            option.Position.Right
        )  # put icon on the right
        option.features |= option.ViewItemFeature.HasDecoration

    def _paint_thumbnail(self, painter, option, index):
        """paint the layer thumbnail - same as in LayerDelegate, but allows
        there to be no thumbnail for group layers"""
        # paint the thumbnail
        # MAGICNUMBER: numbers from the margin applied in the stylesheet to
        # QtLayerTreeView::item
        thumb_rect = option.rect.translated(-2, 2)
        h = index.data(Qt.ItemDataRole.SizeHintRole).height() - 4
        thumb_rect.setWidth(h)
        thumb_rect.setHeight(h)
        image = index.data(ThumbnailRole)
        if image is not None:
            painter.drawPixmap(thumb_rect, QPixmap.fromImage(image))

    def editorEvent(
        self,
        event: QtCore.QEvent,
        model: QtCore.QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> bool:
        """Called when an event has occured in the editor.

        This can be used to customize how the delegate handles mouse/key events
        """
        if (
            event.type() == QMouseEvent.MouseButtonRelease
            and event.button() == Qt.MouseButton.RightButton
        ):
            pnt = (
                event.globalPosition().toPoint()
                if hasattr(event, "globalPosition")
                else event.globalPos()
            )

            self.show_context_menu(index, model, pnt, option.widget)

        # if the user clicks quickly on the visibility checkbox, we *don't*
        # want it to be interpreted as a double-click. Ignore this event
        if event.type() == QMouseEvent.MouseButtonDblClick:
            return True
        # refer all other events to the QStyledItemDelegate
        return super().editorEvent(event, model, option, index)

    def show_context_menu(self, index, model, pos: QPoint, parent):
        """Show the layerlist context menu.
        To add a new item to the menu, update the _LAYER_ACTIONS dict.
        """
        if not hasattr(self, "_context_menu"):
            self._context_menu = build_qmodel_menu(
                MenuId.LAYERLIST_CONTEXT, parent=parent
            )

        layer_list: LayerList = model.sourceModel()._root
        self._context_menu.update_from_context(get_context(layer_list))
        self._context_menu.exec_(pos)
