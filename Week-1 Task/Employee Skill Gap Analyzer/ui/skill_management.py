"""
skill_management.py
--------------------
Skill Management page: two tabs -
  1. Skills Catalog - manage the master list of skills the company tracks.
  2. Required Skills - define which proficiency level is required for a
     given department + position combination (the "target" employees are
     measured against during Gap Analysis).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QMessageBox, QSpinBox, QTabWidget
)


class SkillFormDialog(QDialog):
    """Dialog for adding a new skill to the catalog."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Add Skill")
        self.setMinimumWidth(360)
        layout = QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(
            ["Technical", "Management", "Soft Skill", "HR", "Marketing", "Finance"]
        )

        layout.addRow("Skill Name:", self.name_input)
        layout.addRow("Category:", self.category_input)

        button_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        layout.addRow(button_row)

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Information", "Skill name is required.")
            return
        self.db.add_skill(name, self.category_input.currentText().strip())
        self.accept()


class RequiredSkillFormDialog(QDialog):
    """Dialog for defining a required skill level for a department + position."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Add Required Skill")
        self.setMinimumWidth(380)
        layout = QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.department_combo = QComboBox()
        for dept in self.db.get_departments():
            self.department_combo.addItem(dept["name"], dept["department_id"])

        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("e.g. Software Engineer")

        self.skill_combo = QComboBox()
        for skill in self.db.get_skills():
            self.skill_combo.addItem(skill["name"], skill["skill_id"])

        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 5)
        self.level_spin.setValue(3)

        layout.addRow("Department:", self.department_combo)
        layout.addRow("Position:", self.position_input)
        layout.addRow("Skill:", self.skill_combo)
        layout.addRow("Required Level (1-5):", self.level_spin)

        button_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        layout.addRow(button_row)

    def _save(self):
        position = self.position_input.text().strip()
        if not position:
            QMessageBox.warning(self, "Missing Information", "Position is required.")
            return
        self.db.add_required_skill(
            self.department_combo.currentData(),
            position,
            self.skill_combo.currentData(),
            self.level_spin.value(),
        )
        self.accept()


class SkillManagementPage(QWidget):
    """Container page holding the Skills Catalog tab and Required Skills tab."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        header = QLabel("Skill Management")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._build_catalog_tab()
        self._build_requirements_tab()

    # ------------------------------------------------------------------
    # TAB 1: SKILLS CATALOG
    # ------------------------------------------------------------------
    def _build_catalog_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        tab_layout.setSpacing(10)

        toolbar = QHBoxLayout()
        self.skill_search_input = QLineEdit()
        self.skill_search_input.setPlaceholderText("🔍 Search skills...")
        self.skill_search_input.textChanged.connect(self._refresh_catalog_table)
        toolbar.addWidget(self.skill_search_input, stretch=1)

        add_skill_btn = QPushButton("+ Add Skill")
        add_skill_btn.clicked.connect(self._add_skill)
        toolbar.addWidget(add_skill_btn)
        tab_layout.addLayout(toolbar)

        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(3)
        self.catalog_table.setHorizontalHeaderLabels(["Skill Name", "Category", "Action"])
        self.catalog_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.catalog_table.verticalHeader().setVisible(False)
        self.catalog_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.catalog_table.setAlternatingRowColors(True)
        tab_layout.addWidget(self.catalog_table)

        self.tabs.addTab(tab, "Skills Catalog")

    def _add_skill(self):
        dialog = SkillFormDialog(self.db, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def _delete_skill(self, skill):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete skill '{skill['name']}'? This removes all related requirements and employee records.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.db.delete_skill(skill["skill_id"])
            self.refresh_data()

    def _refresh_catalog_table(self):
        skills = self.db.get_skills()
        keyword = self.skill_search_input.text().strip().lower()
        if keyword:
            skills = [s for s in skills if keyword in s["name"].lower() or keyword in (s["category"] or "").lower()]

        self.catalog_table.setRowCount(len(skills))
        for row_idx, skill in enumerate(skills):
            self.catalog_table.setItem(row_idx, 0, QTableWidgetItem(skill["name"]))
            self.catalog_table.setItem(row_idx, 1, QTableWidgetItem(skill["category"] or ""))
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("DangerButton")
            delete_btn.clicked.connect(lambda _, s=skill: self._delete_skill(s))
            self.catalog_table.setCellWidget(row_idx, 2, delete_btn)

    # ------------------------------------------------------------------
    # TAB 2: REQUIRED SKILLS
    # ------------------------------------------------------------------
    def _build_requirements_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        tab_layout.setSpacing(10)

        toolbar = QHBoxLayout()
        self.req_department_filter = QComboBox()
        self.req_department_filter.addItem("All Departments")
        self.req_department_filter.currentTextChanged.connect(self._refresh_requirements_table)
        toolbar.addWidget(self.req_department_filter, stretch=1)

        add_req_btn = QPushButton("+ Add Requirement")
        add_req_btn.clicked.connect(self._add_requirement)
        toolbar.addWidget(add_req_btn)
        tab_layout.addLayout(toolbar)

        self.requirements_table = QTableWidget()
        self.requirements_table.setColumnCount(5)
        self.requirements_table.setHorizontalHeaderLabels(
            ["Department", "Position", "Skill", "Required Level", "Action"]
        )
        self.requirements_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.requirements_table.verticalHeader().setVisible(False)
        self.requirements_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.requirements_table.setAlternatingRowColors(True)
        tab_layout.addWidget(self.requirements_table)

        self.tabs.addTab(tab, "Required Skills")

    def _add_requirement(self):
        dialog = RequiredSkillFormDialog(self.db, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def _delete_requirement(self, requirement):
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Remove this skill requirement?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.db.delete_required_skill(requirement["requirement_id"])
            self.refresh_data()

    def _refresh_requirements_table(self):
        if self.req_department_filter.count() == 1:
            for dept in self.db.get_departments():
                self.req_department_filter.addItem(dept["name"])

        requirements = self.db.get_required_skills()
        selected_dept = self.req_department_filter.currentText()
        if selected_dept != "All Departments":
            requirements = [r for r in requirements if r["department_name"] == selected_dept]

        self.requirements_table.setRowCount(len(requirements))
        for row_idx, req in enumerate(requirements):
            self.requirements_table.setItem(row_idx, 0, QTableWidgetItem(req["department_name"]))
            self.requirements_table.setItem(row_idx, 1, QTableWidgetItem(req["position"]))
            self.requirements_table.setItem(row_idx, 2, QTableWidgetItem(req["skill_name"]))
            self.requirements_table.setItem(row_idx, 3, QTableWidgetItem(str(req["required_level"])))
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("DangerButton")
            delete_btn.clicked.connect(lambda _, r=req: self._delete_requirement(r))
            self.requirements_table.setCellWidget(row_idx, 4, delete_btn)

    # ------------------------------------------------------------------
    def refresh_data(self):
        self._refresh_catalog_table()
        self._refresh_requirements_table()
