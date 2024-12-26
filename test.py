import sys
import json
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

class JsonTreeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Tree with Checkboxes and Logging")
        self.setGeometry(100, 100, 500, 600)

        # Example hierarchical and diverse JSON data with greater depth (now a dict)
        self.json_data = {
            "Parent 1": {
                "id": 1,
                "name": "Parent 1",
                "item1": "aa",
                "type": "Folder",
                "is_active": True,
                "children": {
                    "Child 1.1": {
                        "id": 2,
                        "name": "Child 1.1",
                        "item2": "bb",
                        "type": "File",
                        "is_active": False,
                        "children": {
                            "Grandchild 1.1.1": {
                                "id": 7,
                                "name": "Grandchild 1.1.1",
                                "item3": "cc",
                                "type": "File",
                                "is_active": True
                            },
                            "Grandchild 1.1.2": {
                                "id": 8,
                                "name": "Grandchild 1.1.2",
                                "item4": "dd",
                                "type": "Folder",
                                "is_active": True
                            }
                        }
                    },
                    "Child 1.2": {
                        "id": 3,
                        "name": "Child 1.2",
                        "item5": "ee",
                        "type": "Folder",
                        "is_active": True
                    }
                }
            },
            "Parent 2": {
                "id": 4,
                "name": "Parent 2",
                "item6": "ff",
                "type": "Folder",
                "is_active": True,
                "children": {
                    "Child 2.1": {
                        "id": 5,
                        "name": "Child 2.1",
                        "item7": "gg",
                        "type": "File",
                        "is_active": False
                    },
                    "Child 2.2": {
                        "id": 6,
                        "name": "Child 2.2",
                        "item8": "hh",
                        "type": "Folder",
                        "is_active": True,
                        "children": {
                            "Grandchild 2.2.1": {
                                "id": 9,
                                "name": "Grandchild 2.2.1",
                                "item9": "ii",
                                "type": "File",
                                "is_active": True
                            }
                        }
                    }
                }
            }
        }

        # Main layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Select Items")
        self.populate_tree(self.json_data, self.tree)
        self.tree.itemChanged.connect(self.handle_item_changed)

        # Add tree widget to layout
        self.layout.addWidget(self.tree)

        # Button for dumping selected entries
        self.dump_button = QPushButton("Dump Selected Entries")
        self.dump_button.clicked.connect(self.dump_selected_entries)
        self.layout.addWidget(self.dump_button)

        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def populate_tree(self, data, parent_widget):
        """Recursively populate the tree widget with JSON data."""
        for key, value in data.items():
            if isinstance(value, dict):
                item = QTreeWidgetItem(parent_widget)
                item.setText(0, f"{key} (dict)")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)
                self.populate_tree(value, item)  # Recursively add child items
            elif isinstance(value, list):
                item = QTreeWidgetItem(parent_widget)
                item.setText(0, f"{key} (list)")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)
                for idx, sub_item in enumerate(value):
                    self.populate_tree({f"Item {idx + 1}": sub_item}, item)  # Add list items
            else:
                item = QTreeWidgetItem(parent_widget)
                item.setText(0, f"{key}: {value}")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)

    def handle_item_changed(self, item, column):
        """Handles changes in item check states."""
        # Block signals to avoid feedback loop
        self.tree.blockSignals(True)

        if item.parent() is None:
            # Parent item: Update all children
            logging.info(f"Parent '{item.text(0)}' changed to {item.checkState(0)}")
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, item.checkState(0))
                logging.debug(f"  Child '{child.text(0)}' set to {child.checkState(0)}")
        else:
            # Child item: Update parent if necessary
            logging.info(f"Child '{item.text(0)}' changed to {item.checkState(0)}")
            parent = item.parent()
            all_checked = all(parent.child(i).checkState(0) == Qt.Checked for i in range(parent.childCount()))
            any_checked = any(parent.child(i).checkState(0) == Qt.Checked for i in range(parent.childCount()))

            if all_checked:
                parent.setCheckState(0, Qt.Checked)
            elif any_checked:
                parent.setCheckState(0, Qt.PartiallyChecked)
            else:
                parent.setCheckState(0, Qt.Unchecked)

            logging.debug(f"Parent '{parent.text(0)}' updated to {parent.checkState(0)}")

        # Unblock signals
        self.tree.blockSignals(False)

    def dump_selected_entries(self):
        """Collect selected entries and dump them as a formatted JSON."""
        selected_entries = {}
        self.collect_selected_data(self.tree, selected_entries)

        # Print the selected entries in a nicely formatted JSON
        print(json.dumps(selected_entries, indent=4))

    def collect_selected_data(self, parent_item, selected_entries):
        """Recursively collect selected entries from the tree."""
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            if item.checkState(0) == Qt.Checked:
                # The key will be the text of the item without the type descriptor
                key_text = item.text(0).split(" (")[0]
                value = item.text(0).split(": ")[1] if ": " in item.text(0) else item.text(0)

                if "{" in value or "[" in value:  # Handle nested values
                    nested_data = {}
                    self.collect_selected_data(item, nested_data)
                    selected_entries[key_text] = nested_data
                else:
                    selected_entries[key_text] = value

    def flatten_json(self, entry):
        """Recursively flattens the nested dictionary into more rows."""
        flat = {}
        for key, value in entry.items():
            if isinstance(value, dict):
                flat[key] = self.flatten_json(value)
            elif isinstance(value, list):
                flat[key] = [self.flatten_json(item) if isinstance(item, dict) else item for item in value]
            else:
                flat[key] = value
        return flat

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JsonTreeApp()
    window.show()
    sys.exit(app.exec_())
