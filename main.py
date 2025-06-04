import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QDialog,
    QTextEdit
)
from PySide6.QtGui import QFontDatabase, QFont, QTextOption
from PySide6.QtCore import Qt, QPoint
from newtaskdialog import NewTaskDialog

class DraggableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._offset = event.pos()

    def mouseMoveEvent(self, event):
        if self._offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self._offset)

    def mouseReleaseEvent(self, event):
        self._offset = None

class MainWindow(DraggableWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ToDo Application")
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setStyleSheet("background-color: #1e1e1e;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel("  ToDo Application")
        title_label.setStyleSheet("color: white; font-size: 14px;")
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: white; border: none; font-size: 14px; }"
            "QPushButton:hover { background-color: #ff5c5c; }"
        )
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)
        left_layout.addLayout(title_bar)

        add_button = QPushButton("+ Добавить задачу")
        add_button.setFixedHeight(40)
        add_button.setStyleSheet(
            "QPushButton { background-color: #3c3c3c; color: white; border: none; border-radius: 5px; font-size: 14px; }"
            "QPushButton:hover { background-color: #505050; }"
        )
        add_button.clicked.connect(self.open_new_task_dialog)
        left_layout.addWidget(add_button)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setStyleSheet("color: #3c3c3c;")
        left_layout.addWidget(sep)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet(
            "QListWidget { background-color: transparent; color: white; border: none; }"
            "QListWidget::item:selected { background-color: #505050; }"
        )
        self.task_list.itemClicked.connect(self.display_task)
        self.task_list.itemDoubleClicked.connect(self.edit_task)
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_delete_button)
        left_layout.addWidget(self.task_list)

        main_layout.addWidget(left_panel, 1)

        self.delete_btn = QPushButton("🗑", self.task_list)
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet(
            "QPushButton { background-color: #e57373; color: white; border: none; border-radius: 4px; }"
            "QPushButton:hover { background-color: #ef5350; }"
        )
        self.delete_btn.hide()
        self.delete_btn.clicked.connect(self.delete_task)
        self.current_item_for_deletion = None

        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_panel.setStyleSheet("background-color: #2d2d2d;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)

        self.info_title = QLabel("Выберите задачу слева или добавьте новую")
        self.info_title.setWordWrap(True)
        self.info_title.setStyleSheet("color: white; font-size: 16px;")
        right_layout.addWidget(self.info_title)

        self.info_tags = QLabel("")
        self.info_tags.setStyleSheet("color: white; font-size: 12px;")
        right_layout.addWidget(self.info_tags)

        self.info_desc = QTextEdit()
        self.info_desc.setReadOnly(True)
        self.info_desc.setStyleSheet(
            "QTextEdit { background-color: #3c3c3c; border: none; color: white; padding: 4px; }"
        )
        self.info_desc.setWordWrapMode(QTextOption.WordWrap)
        right_layout.addWidget(self.info_desc, 1)

        main_layout.addWidget(right_panel, 2)

        self.setStyleSheet("background-color: #121212;")

    def open_new_task_dialog(self):
        dialog = NewTaskDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.add_task_to_list(dialog.get_task_data())

    def edit_task(self, item: QListWidgetItem):
        task_data = item.data(Qt.UserRole)
        dialog = NewTaskDialog(self, init_data=task_data)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_task_data()
            item.setData(Qt.UserRole, new_data)
            self.update_item_widget(item, new_data)
            if self.task_list.currentItem() == item:
                self.display_task(item)

    def show_delete_button(self, pos):
        item = self.task_list.itemAt(pos)
        if not item:
            self.delete_btn.hide()
            return
        rect = self.task_list.visualItemRect(item)
        x = rect.right() - self.delete_btn.width() - 2
        y = rect.top() + (rect.height() - self.delete_btn.height()) // 2
        self.delete_btn.move(x, y)
        self.delete_btn.show()
        self.current_item_for_deletion = item

    def delete_task(self):
        if self.current_item_for_deletion:
            row = self.task_list.row(self.current_item_for_deletion)
            self.task_list.takeItem(row)
            self.delete_btn.hide()
            self.current_item_for_deletion = None
            self.info_title.setText("Выберите задачу слева или добавьте новую")
            self.info_tags.setText("")
            self.info_desc.clear()

    def add_task_to_list(self, task_data: dict):
        title = task_data["title"]
        tags = task_data["tags"]
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 2, 5, 2)

        for tag in tags:
            tag_label = QLabel(tag["name"])
            tag_label.setStyleSheet(
                f"background-color: {tag['color']}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;"
            )
            item_layout.addWidget(tag_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px;")
        item_layout.addWidget(title_label)
        item_layout.addStretch()

        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        list_item.setData(Qt.UserRole, task_data)
        self.task_list.addItem(list_item)
        self.task_list.setItemWidget(list_item, item_widget)

    def update_item_widget(self, item: QListWidgetItem, task_data: dict):
        idx = self.task_list.row(item)
        widget = self.task_list.itemWidget(item)
        if not widget:
            return

        for i in reversed(range(widget.layout().count())):
            widget.layout().itemAt(i).widget().setParent(None)

        for tag in task_data["tags"]:
            tag_label = QLabel(tag["name"])
            tag_label.setStyleSheet(
                f"background-color: {tag['color']}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;"
            )
            widget.layout().addWidget(tag_label)

        title_label = QLabel(task_data["title"])
        title_label.setStyleSheet("color: white; font-size: 14px;")
        widget.layout().addWidget(title_label)
        widget.layout().addStretch()

    def display_task(self, item: QListWidgetItem):
        task_data = item.data(Qt.UserRole)
        self.info_title.setText(task_data["title"])

        html = ""
        for tag in task_data["tags"]:
            html += f"<span style='background-color:{tag['color']}; color:white; " \
                    f"padding:2px 6px; border-radius:3px; margin-right:4px;'>{tag['name']}</span>"
        self.info_tags.setText(html)

        self.info_desc.setHtml(task_data["description"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QColorDialog, QTextEdit, QToolBar, QDialogButtonBox, QInputDialog, QWidget
)
from PySide6.QtGui import QFont, QAction, QTextCharFormat
from PySide6.QtCore import Qt

class NewTaskDialog(QDialog):
    def __init__(self, parent=None, init_data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Новая задача")
        self.setMinimumSize(400, 350)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        if init_data:
            self.task_data = {
                "title": init_data.get("title", ""),
                "description": init_data.get("description", ""),
                "tags": init_data.get("tags", []).copy()
            }
        else:
            self.task_data = {"title": "", "description": "", "tags": []}

        main_layout = QVBoxLayout(self)

        title_label = QLabel("Название задачи:")
        title_label.setStyleSheet("font-size: 14px; color: white;")
        main_layout.addWidget(title_label)

        self.title_edit = QLineEdit()
        self.title_edit.setStyleSheet(
            "QLineEdit { background-color: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 5px; color: white; padding: 4px; }"
        )
        main_layout.addWidget(self.title_edit)

        desc_label = QLabel("Описание:")
        desc_label.setStyleSheet("font-size: 14px; color: white;")
        main_layout.addWidget(desc_label)

        toolbar = QToolBar()
        toolbar.setStyleSheet("background: #2d2d2d; border: none;")
        bold_action = QAction("B", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.make_bold)
        toolbar.addAction(bold_action)
        italic_action = QAction("I", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.make_italic)
        toolbar.addAction(italic_action)
        underline_action = QAction("U", self)
        underline_action.setCheckable(True)
        underline_action.triggered.connect(self.make_underline)
        toolbar.addAction(underline_action)
        color_action = QAction("Цвет", self)
        color_action.triggered.connect(self.change_color)
        toolbar.addAction(color_action)

        main_layout.addWidget(toolbar)

        self.desc_edit = QTextEdit()
        self.desc_edit.setStyleSheet(
            "QTextEdit { background-color: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 5px; color: white; padding: 4px; }"
        )
        main_layout.addWidget(self.desc_edit, 1)

        tag_layout = QHBoxLayout()
        tag_label = QLabel("Теги:")
        tag_label.setStyleSheet("font-size: 14px; color: white;")
        tag_layout.addWidget(tag_label)

        self.add_tag_button = QPushButton("Добавить тег")
        self.add_tag_button.setFixedHeight(24)
        self.add_tag_button.setStyleSheet(
            "QPushButton { background-color: #3c3c3c; color: white; border: none; border-radius: 4px; font-size: 12px; padding: 2px 6px; }"
            "QPushButton:hover { background-color: #505050; }"
        )
        self.add_tag_button.clicked.connect(self.add_tag)
        tag_layout.addWidget(self.add_tag_button)
        main_layout.addLayout(tag_layout)

        self.tags_container = QWidget()
        self.tags_container.setStyleSheet("background: transparent;")
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.tags_container)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        main_layout.addWidget(btn_box)

        if init_data:
            self._populate_initial_data(init_data)

    def _populate_initial_data(self, data: dict):
        self.title_edit.setText(data.get("title", ""))
        self.desc_edit.setHtml(data.get("description", ""))

        for tag in data.get("tags", []):
            tag_label = QLabel(tag["name"])
            tag_label.setStyleSheet(
                f"background-color: {tag['color']}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;"
            )
            self.tags_layout.addWidget(tag_label)

    def make_bold(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if checked else QFont.Normal)
        self._apply_format(fmt)

    def make_italic(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontItalic(checked)
        self._apply_format(fmt)

    def make_underline(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(checked)
        self._apply_format(fmt)

    def change_color(self):
        color = QColorDialog.getColor(parent=self, title="Выберите цвет текста")
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self._apply_format(fmt)

    def _apply_format(self, fmt: QTextCharFormat):
        cursor = self.desc_edit.textCursor()
        if not cursor.hasSelection():
            return
        cursor.mergeCharFormat(fmt)

    def add_tag(self):
        name, ok = QInputDialog.getText(self, "Имя тега", "Введите имя тега:")
        if ok and name:
            color = QColorDialog.getColor(parent=self, title="Выберите цвет тега")
            if color.isValid():
                tag_label = QLabel(name)
                tag_label.setStyleSheet(
                    f"background-color: {color.name()}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;"
                )
                self.tags_layout.addWidget(tag_label)
                self.task_data["tags"].append({"name": name, "color": color.name()})

    def get_task_data(self):
        self.task_data["title"] = self.title_edit.text()
        self.task_data["description"] = self.desc_edit.toHtml()
        return self.task_data
