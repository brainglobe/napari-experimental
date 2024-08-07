from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from napari._qt.containers._base_item_model import ItemRole
from napari._qt.containers._layer_delegate import LayerDelegate
from napari._qt.containers.qt_layer_model import ThumbnailRole
from napari._qt.qt_resources import QColoredSVGIcon
from qtpy.QtCore import QPoint, QSize, Qt
from qtpy.QtGui import QMouseEvent, QPainter, QPixmap

from napari_experimental.group_layer_actions import (
    ContextMenu,
    GroupLayerActions,
)

if TYPE_CHECKING:
    from qtpy import QtCore
    from qtpy.QtWidgets import QStyleOptionViewItem

    from napari_experimental.group_layer_qt import (
        QtGroupLayerModel,
        QtGroupLayerView,
    )


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

    def _paint_thumbnail(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        """paint the layer thumbnail - same as in LayerDelegate, but allows
        there to be no thumbnail for group layers"""
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
        """Called when an event has occurred in the editor"""
        # if the user clicks quickly on the visibility checkbox, we *don't*
        # want it to be interpreted as a double-click. Ignore this event.
        if event.type() == QMouseEvent.MouseButtonDblClick:
            self.initStyleOption(option, index)
            style = option.widget.style()
            check_rect = style.subElementRect(
                style.SubElement.SE_ItemViewItemCheckIndicator,
                option,
                option.widget,
            )
            if check_rect.contains(event.pos()):
                return True

        # refer all other events to LayerDelegate
        return super().editorEvent(event, model, option, index)

    def show_context_menu(
        self,
        index: QtCore.QModelIndex,
        model: QtGroupLayerModel,
        pos: QPoint,
        parent: QtGroupLayerView,
    ):
        """Show the group layer context menu.
        To add a new item to the menu, update the GroupLayerActions.
        """
        if not hasattr(self, "_context_menu"):
            self._group_layer_actions = GroupLayerActions(model._root)
            self._context_menu = ContextMenu(
                self._group_layer_actions, parent=parent
            )

        self._context_menu.exec_(pos)
