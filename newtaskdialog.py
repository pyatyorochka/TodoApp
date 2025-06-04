from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QColorDialog, QTextEdit, QToolBar, QDialogButtonBox, QInputDialog, QWidget
)
from PySide6.QtGui import QFont, QAction, QTextCharFormat
from PySide6.QtCore import Qt

class NewTaskDialog(QDialog):
    def __init__(self, parent=None, init_data: dict = None):
        super().__init__(parent)
        print("NewTaskDialog: initializing")
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
            "QLineEdit { background-color: #2d2d2d; border: 1px solid #3c3c3c; "
            "border-radius: 5px; color: white; padding: 4px; }"
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
            "QTextEdit { background-color: #2d2d2d; border: 1px solid #3c3c3c; "
            "border-radius: 5px; color: white; padding: 4px; }"
        )
        main_layout.addWidget(self.desc_edit, 1)

        tag_layout = QHBoxLayout()
        tag_label = QLabel("Теги:")
        tag_label.setStyleSheet("font-size: 14px; color: white;")
        tag_layout.addWidget(tag_label)

        self.add_tag_button = QPushButton("Добавить тег")
        self.add_tag_button.setFixedHeight(24)
        self.add_tag_button.setStyleSheet(
            "QPushButton { background-color: #3c3c3c; color: white; border: none; "
            "border-radius: 4px; font-size: 12px; padding: 2px 6px; }"
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
        print("NewTaskDialog: initialized successfully")

    def _populate_initial_data(self, data: dict):
        self.title_edit.setText(data.get("title", ""))
        self.desc_edit.setHtml(data.get("description", ""))
        for tag in data.get("tags", []):
            tag_label = QLabel(tag["name"])
            tag_label.setStyleSheet(
                f"background-color: {tag['color']}; color: white; "
                f"padding: 2px 8px; border-radius: 4px; font-size: 12px;"
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
                    f"background-color: {color.name()}; color: white; "
                    f"padding: 2px 8px; border-radius: 4px; font-size: 12px;"
                )
                self.tags_layout.addWidget(tag_label)
                self.task_data["tags"].append({"name": name, "color": color.name()})

    def get_task_data(self):
        self.task_data["title"] = self.title_edit.text()
        self.task_data["description"] = self.desc_edit.toHtml()
        return self.task_data
