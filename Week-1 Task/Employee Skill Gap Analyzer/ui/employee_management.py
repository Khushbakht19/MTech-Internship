"""
employee_management.py
-----------------------
Employee Management page: lets HR staff view, search, filter, sort, add,
edit and delete employees, plus assign skill proficiency levels to each
employee. This page is the primary data-entry point for the whole system.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QDateEdit, QMessageBox, QSpinBox, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate

from algorithms.analyzer import SkillGapAnalyzer


class EmployeeFormDialog(QDialog):
    """Modal dialog used for both 'Add Employee' and 'Edit Employee'."""

    def __init__(self, db_manager, employee=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.employee = employee  # None means "add mode"
        self.setWindowTitle("Add Employee" if employee is None else "Edit Employee")
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.position_input = QLineEdit()

        self.department_combo = QComboBox()
        self.departments = self.db.get_departments()
        for dept in self.departments:
            self.department_combo.addItem(dept["name"], dept["department_id"])

        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())

        layout.addRow("Full Name:", self.name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Position:", self.position_input)
        layout.addRow("Department:", self.department_combo)
        layout.addRow("Hire Date:", self.hire_date_input)

        if self.employee:
            self.name_input.setText(self.employee["full_name"])
            self.email_input.setText(self.employee.get("email") or "")
            self.position_input.setText(self.employee["position"])
            idx = self.department_combo.findData(self.employee["department_id"])
            if idx >= 0:
                self.department_combo.setCurrentIndex(idx)
            if self.employee.get("hire_date"):
                self.hire_date_input.setDate(QDate.fromString(self.employee["hire_date"], "yyyy-MM-dd"))

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
        position = self.position_input.text().strip()
        if not name or not position:
            QMessageBox.warning(self, "Missing Information", "Name and Position are required.")
            return

        department_id = self.department_combo.currentData()
        email = self.email_input.text().strip()
        hire_date = self.hire_date_input.date().toString("yyyy-MM-dd")

        if self.employee is None:
            self.db.add_employee(name, email, position, department_id, hire_date)
        else:
            self.db.update_employee(
                self.employee["employee_id"], name, email, position, department_id, hire_date
            )
        self.accept()


class SkillAssignmentDialog(QDialog):
    """
    Dialog that lets HR assign / update proficiency levels (0-5) for every
    skill in the system, for one specific employee.
    """

    def __init__(self, db_manager, employee, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.employee = employee
        self.setWindowTitle(f"Manage Skills - {employee['full_name']}")
        self.setMinimumSize(480, 520)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel(f"Skill Proficiency for {self.employee['full_name']}")
        title.setObjectName("SectionHeader")
        layout.addWidget(title)

        hint = QLabel("Set proficiency level for each skill (0 = None, 5 = Expert).")
        hint.setObjectName("MutedLabel")
        layout.addWidget(hint)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Skill", "Category", "Proficiency (0-5)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        all_skills = self.db.get_skills()
        existing = {row["skill_id"]: row["proficiency_level"] for row in self.db.get_employee_skills(self.employee["employee_id"])}

        self.table.setRowCount(len(all_skills))
        self.spin_boxes = {}
        for row_idx, skill in enumerate(all_skills):
            self.table.setItem(row_idx, 0, QTableWidgetItem(skill["name"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(skill["category"] or ""))

            spin = QSpinBox()
            spin.setRange(0, 5)
            spin.setValue(existing.get(skill["skill_id"], 0))
            self.spin_boxes[skill["skill_id"]] = spin
            self.table.setCellWidget(row_idx, 2, spin)

        button_row = QHBoxLayout()
        save_btn = QPushButton("Save All")
        save_btn.clicked.connect(self._save_all)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("SecondaryButton")
        close_btn.clicked.connect(self.reject)
        button_row.addWidget(close_btn)
        button_row.addWidget(save_btn)
        layout.addLayout(button_row)

    def _save_all(self):
        for skill_id, spin in self.spin_boxes.items():
            self.db.set_employee_skill(self.employee["employee_id"], skill_id, spin.value())
        QMessageBox.information(self, "Saved", "Employee skills updated successfully.")
        self.accept()


class EmployeeManagementPage(QWidget):
    """Main page: searchable / filterable / sortable employee table + CRUD actions."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_sort_key = "full_name"
        self.current_sort_desc = False
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        header = QLabel("Employee Management")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        # ---- Toolbar: search, filters, sort, actions ----
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name, position, department, email...")
        self.search_input.textChanged.connect(self.refresh_data)
        toolbar.addWidget(self.search_input, stretch=2)

        self.department_filter = QComboBox()
        self.department_filter.addItem("All Departments")
        self.department_filter.currentTextChanged.connect(self.refresh_data)
        toolbar.addWidget(self.department_filter, stretch=1)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort: Name", "Sort: Position", "Sort: Department", "Sort: Hire Date"])
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        toolbar.addWidget(self.sort_combo, stretch=1)

        add_btn = QPushButton("+ Add Employee")
        add_btn.clicked.connect(self._add_employee)
        toolbar.addWidget(add_btn)

        layout.addLayout(toolbar)

        # ---- Table ----
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Position", "Department", "Email", "Hire Date", "", ""]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def _on_sort_changed(self, index):
        mapping = {0: "full_name", 1: "position", 2: "department_name", 3: "hire_date"}
        self.current_sort_key = mapping.get(index, "full_name")
        self.refresh_data()

    def refresh_data(self):
        """Reloads the employee list applying current search/filter/sort settings."""
        employees = self.db.get_employees()

        # Populate department filter combo once (avoid duplicate entries)
        if self.department_filter.count() == 1:
            departments = self.db.get_departments()
            for dept in departments:
                self.department_filter.addItem(dept["name"])

        # SEARCH
        keyword = self.search_input.text()
        employees = SkillGapAnalyzer.search_employees(employees, keyword)

        # FILTER
        dept_name = self.department_filter.currentText()
        employees = SkillGapAnalyzer.filter_employees(employees, department_name=dept_name)

        # SORT
        employees = SkillGapAnalyzer.sort_records(
            employees, self.current_sort_key, descending=self.current_sort_desc
        )

        self._populate_table(employees)

    def _populate_table(self, employees):
        self.table.setRowCount(len(employees))
        for row_idx, emp in enumerate(employees):
            self.table.setItem(row_idx, 0, QTableWidgetItem(emp["full_name"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(emp["position"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(emp["department_name"]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(emp.get("email") or ""))
            self.table.setItem(row_idx, 4, QTableWidgetItem(emp.get("hire_date") or ""))

            skills_btn = QPushButton("Skills")
            skills_btn.setObjectName("SecondaryButton")
            skills_btn.clicked.connect(lambda _, e=emp: self._manage_skills(e))
            self.table.setCellWidget(row_idx, 5, skills_btn)

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            edit_btn = QPushButton("Edit")
            edit_btn.setObjectName("SecondaryButton")
            edit_btn.clicked.connect(lambda _, e=emp: self._edit_employee(e))
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("DangerButton")
            delete_btn.clicked.connect(lambda _, e=emp: self._delete_employee(e))
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(row_idx, 6, actions_widget)

        self.table.resizeRowsToContents()

    def _add_employee(self):
        dialog = EmployeeFormDialog(self.db, employee=None, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def _edit_employee(self, employee):
        dialog = EmployeeFormDialog(self.db, employee=employee, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def _delete_employee(self, employee):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{employee['full_name']}'? "
            "This will also remove their skill records.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.db.delete_employee(employee["employee_id"])
            self.refresh_data()

    def _manage_skills(self, employee):
        dialog = SkillAssignmentDialog(self.db, employee, parent=self)
        dialog.exec_()
