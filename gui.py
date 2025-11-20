import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QPushButton, QTabWidget, QLabel, QHBoxLayout,
                             QToolButton)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from prover import resolution_prover, parse_clauses
from formalizer import formalize, explain_proof


class Worker(QThread):
    sig_formalization_done = pyqtSignal(str)
    sig_proof_done = pyqtSignal(list, bool)
    sig_explanation_done = pyqtSignal(str)
    sig_all_finished = pyqtSignal()

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        clauses_text = formalize(self.task)
        self.sig_formalization_done.emit(clauses_text)

        clauses = parse_clauses(clauses_text)
        proved, steps = resolution_prover(clauses)
        self.sig_proof_done.emit(steps, proved)

        if proved:
            explanation = explain_proof(self.task, clauses_text, steps)
            self.sig_explanation_done.emit(explanation)
        else:
            self.sig_explanation_done.emit("Доказательство не найдено, объяснение невозможно.")

        self.sig_all_finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Резольвент первого порядка (с Gemini)")
        self.resize(1250, 900)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addWidget(QLabel("<b>Введите логическую задачу:</b>"))
        self.input = QTextEdit()
        self.input.setPlaceholderText("Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.")
        self.input.setFont(QFont("Arial", 12))
        layout.addWidget(self.input)

        self.btn = QPushButton("Доказать теорему")
        self.btn.setStyleSheet("""
            QPushButton { background-color: #1976D2; color: white; font-weight: bold; 
                         padding: 14px; font-size: 16px; border-radius: 8px; }
            QPushButton:disabled { background-color: #555; }
        """)
        self.btn.clicked.connect(self.start_proof)
        layout.addWidget(self.btn)

        self.tabs = QTabWidget()
        self.tab_clauses = QTextEdit()
        self.tab_proof = QTextEdit()
        self.tab_explain = QTextEdit()

        self.font_proof = QFont("Consolas", 14)
        self.font_explain = QFont("Segoe UI", 15)

        self.tab_clauses.setFont(QFont("Consolas", 13))
        self.tab_proof.setFont(self.font_proof)
        self.tab_explain.setFont(self.font_explain)

        for tab in (self.tab_clauses, self.tab_proof, self.tab_explain):
            tab.setReadOnly(True)
            tab.setStyleSheet("background-color: #2b2b2b; color: #e0e0e0; padding: 12px; border: none;")

        self.tabs.addTab(self.tab_clauses, "Клаузы")
        self.tabs.addTab(self.tab_proof, "Доказательство")
        self.tabs.addTab(self.tab_explain, "Объяснение")
        layout.addWidget(self.tabs)

        font_control = QHBoxLayout()
        font_control.addStretch()

        btn_style = """
            QToolButton { 
                background: #404040; 
                border: 1px solid #555; 
                border-radius: 8px; 
                padding: 6px; 
                font-size: 18px; 
                min-width: 36px; 
                color: white;
            }
            QToolButton:hover { background: #505050; }
            QToolButton:pressed { background: #606060; }
        """
        label_style = "color: #bbbbbb; font-size: 13px; padding: 0 8px;"

        font_control.addWidget(QLabel("Доказательство:"), alignment=Qt.AlignmentFlag.AlignRight)
        btn_dec_p = QToolButton(); btn_dec_p.setText("−"); btn_dec_p.setStyleSheet(btn_style)
        self.lbl_proof_size = QLabel("14 pt"); self.lbl_proof_size.setStyleSheet(label_style)
        btn_inc_p = QToolButton(); btn_inc_p.setText("+"); btn_inc_p.setStyleSheet(btn_style)

        btn_dec_p.clicked.connect(lambda: self.change_font("proof", -2))
        btn_inc_p.clicked.connect(lambda: self.change_font("proof", +2))

        font_control.addWidget(btn_dec_p)
        font_control.addWidget(self.lbl_proof_size)
        font_control.addWidget(btn_inc_p)

        font_control.addSpacing(30)

        font_control.addWidget(QLabel("Объяснение:"), alignment=Qt.AlignmentFlag.AlignRight)
        btn_dec_e = QToolButton(); btn_dec_e.setText("−"); btn_dec_e.setStyleSheet(btn_style)
        self.lbl_explain_size = QLabel("15 pt"); self.lbl_explain_size.setStyleSheet(label_style)
        btn_inc_e = QToolButton(); btn_inc_e.setText("+"); btn_inc_e.setStyleSheet(btn_style)

        btn_dec_e.clicked.connect(lambda: self.change_font("explain", -2))
        btn_inc_e.clicked.connect(lambda: self.change_font("explain", +2))

        font_control.addWidget(btn_dec_e)
        font_control.addWidget(self.lbl_explain_size)
        font_control.addWidget(btn_inc_e)

        font_control.addStretch()
        layout.addLayout(font_control)


        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
            QTextEdit { background-color: #2b2b2b; color: #ffffff; }
            QLabel { color: #cccccc; }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { background: #333; padding: 12px; border-radius: 6px; margin: 2px; }
            QTabBar::tab:selected { background: #1976D2; }
        """)

    def change_font(self, target: str, delta: int):
        if target == "proof":
            size = self.font_proof.pointSize() + delta
            size = max(10, min(36, size))
            self.font_proof.setPointSize(size)
            self.tab_proof.setFont(self.font_proof)
            self.lbl_proof_size.setText(f"{size} pt")
        elif target == "explain":
            size = self.font_explain.pointSize() + delta
            size = max(10, min(40, size))
            self.font_explain.setPointSize(size)
            self.tab_explain.setFont(self.font_explain)
            self.lbl_explain_size.setText(f"{size} pt")

    def start_proof(self):
        task = self.input.toPlainText().strip()
        if not task:
            return

        self.btn.setEnabled(False)
        self.tab_clauses.setPlainText("Формализация через Gemini...")
        self.tab_proof.setPlainText("Ожидание...")
        self.tab_explain.setPlainText("Ожидание...")

        self.worker = Worker(task)
        self.worker.sig_formalization_done.connect(self.on_formalization)
        self.worker.sig_proof_done.connect(self.on_proof)
        self.worker.sig_explanation_done.connect(self.on_explanation)
        self.worker.sig_all_finished.connect(self.on_finished)
        self.worker.start()

    def on_formalization(self, text):
        if not text.strip():
            self.tab_clauses.setPlainText("Ошибка: пустой ответ от Gemini")
            return

        clauses = []
        current = []
        depth = 0
        for char in text + ",":
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            if char == ',' and depth == 0:
                clause = "".join(current).strip()
                if clause:
                    clauses.append(clause)
                current = []
            else:
                current.append(char)
        formatted = ",\n".join(clauses)
        self.tab_clauses.setPlainText(formatted)

    def on_proof(self, steps, proved):
        self.tab_proof.setPlainText("\n".join(steps))
        if not proved:
            self.tab_explain.setPlainText("Доказательство не найдено.")
        else:
            self.tab_explain.setPlainText("Генерация объяснения...")

    def on_explanation(self, text):
        self.tab_explain.setPlainText(text)

    def on_finished(self):
        self.btn.setEnabled(True)