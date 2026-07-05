"""
reports.py
----------
Reports page - lets HR export the full workforce readiness analysis to
either an Excel workbook (.xlsx, via pandas/openpyxl) or a formatted PDF
report (via reportlab).
"""

import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QMessageBox, QFrame
)

from algorithms.analyzer import SkillGapAnalyzer

import pandas as pd


class ReportsPage(QWidget):
    """Report generation and export page."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)

        header = QLabel("Reports & Export")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        subtitle = QLabel(
            "Generate a complete workforce readiness report including employee "
            "readiness scores, classifications, and department summaries."
        )
        subtitle.setObjectName("MutedLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("ContentCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        info_label = QLabel(
            "📄 The report includes:\n\n"
            "  •  Full employee list with readiness scores and classification\n"
            "  •  Department-wide readiness averages\n"
            "  •  Company-wide statistical summary (mean, median, std. deviation)\n"
            "  •  Skill gap breakdown per employee"
        )
        info_label.setStyleSheet("font-size: 13px; color: #e8eaf0;")
        card_layout.addWidget(info_label)

        button_row = QHBoxLayout()
        excel_btn = QPushButton("⬇  Export to Excel (.xlsx)")
        excel_btn.clicked.connect(self._export_excel)
        pdf_btn = QPushButton("⬇  Export to PDF")
        pdf_btn.setObjectName("SecondaryButton")
        pdf_btn.clicked.connect(self._export_pdf)
        button_row.addWidget(excel_btn)
        button_row.addWidget(pdf_btn)
        button_row.addStretch()
        card_layout.addLayout(button_row)

        layout.addWidget(card)
        layout.addStretch()

        self.status_label = QLabel("")
        self.status_label.setObjectName("MutedLabel")
        layout.addWidget(self.status_label)

    def _get_report_data(self):
        """Runs the analysis algorithms fresh so the report is always up to date."""
        matrix = self.db.get_all_employee_skill_matrix()
        analyzer = SkillGapAnalyzer(matrix)
        classified = analyzer.classify_all_employees()
        dept_summary = analyzer.department_readiness()
        stats = analyzer.readiness_statistics()
        gaps = analyzer.compute_skill_gaps()
        return classified, dept_summary, stats, gaps

    def _export_excel(self):
        default_name = f"Skills_Gap_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", default_name, "Excel Files (*.xlsx)")
        if not path:
            return
        try:
            classified, dept_summary, stats, gaps = self._get_report_data()

            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                classified.to_excel(writer, sheet_name="Employee Readiness", index=False)
                dept_summary.to_excel(writer, sheet_name="Department Summary", index=False)

                stats_df = pd.DataFrame([
                    {"Metric": "Mean Readiness", "Value": stats["mean"]},
                    {"Metric": "Median Readiness", "Value": stats["median"]},
                    {"Metric": "Std. Deviation", "Value": stats["std_dev"]},
                    {"Metric": "Minimum", "Value": stats["minimum"]},
                    {"Metric": "Maximum", "Value": stats["maximum"]},
                ])
                stats_df.to_excel(writer, sheet_name="Statistics", index=False)

                if not gaps.empty:
                    gap_export = gaps[[
                        "full_name", "department_name", "position", "skill_name",
                        "required_level", "actual_level", "gap"
                    ]]
                    gap_export.to_excel(writer, sheet_name="Skill Gap Details", index=False)

            self.status_label.setText(f"✅ Excel report saved to: {path}")
            QMessageBox.information(self, "Export Successful", "Excel report generated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not generate Excel report:\n{str(e)}")

    def _export_pdf(self):
        default_name = f"Skills_Gap_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", default_name, "PDF Files (*.pdf)")
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            classified, dept_summary, stats, gaps = self._get_report_data()

            doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#1a1d29")
            )
            heading_style = ParagraphStyle(
                "HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#3b82f6")
            )

            elements = []
            elements.append(Paragraph("Employee Skills Gap Analysis Report", title_style))
            elements.append(Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y %H:%M')}", styles["Normal"]
            ))
            elements.append(Spacer(1, 16))

            # Statistical summary
            elements.append(Paragraph("Company-Wide Statistical Summary", heading_style))
            stats_table_data = [["Metric", "Value"]] + [
                ["Mean Readiness", f"{stats['mean']}%"],
                ["Median Readiness", f"{stats['median']}%"],
                ["Standard Deviation", str(stats["std_dev"])],
                ["Minimum", f"{stats['minimum']}%"],
                ["Maximum", f"{stats['maximum']}%"],
            ]
            elements.append(self._make_pdf_table(stats_table_data))
            elements.append(Spacer(1, 16))

            # Department summary
            elements.append(Paragraph("Department Readiness Summary", heading_style))
            dept_table_data = [["Department", "Avg Readiness", "Employees", "Need Training"]]
            for _, row in dept_summary.iterrows():
                dept_table_data.append([
                    row["department_name"], f"{row['avg_readiness']}%",
                    str(int(row["employee_count"])), str(int(row["needs_training_count"])),
                ])
            elements.append(self._make_pdf_table(dept_table_data))
            elements.append(Spacer(1, 16))

            # Employee readiness
            elements.append(Paragraph("Employee Readiness & Classification", heading_style))
            emp_table_data = [["Employee", "Department", "Readiness", "Classification"]]
            for _, row in classified.iterrows():
                emp_table_data.append([
                    row["full_name"], row["department_name"],
                    f"{row['readiness_score']}%", row["classification"],
                ])
            elements.append(self._make_pdf_table(emp_table_data))

            doc.build(elements)

            self.status_label.setText(f"✅ PDF report saved to: {path}")
            QMessageBox.information(self, "Export Successful", "PDF report generated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not generate PDF report:\n{str(e)}")

    @staticmethod
    def _make_pdf_table(data):
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors

        table = Table(data, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4fa")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return table
