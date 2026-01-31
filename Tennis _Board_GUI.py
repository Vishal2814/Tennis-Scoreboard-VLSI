import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer

class TennisGUI(QWidget):
    def __init__(self, csv_file):
        super().__init__()
        self.csv_file = csv_file
        self.data = []
        self.index = 0
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_scoreboard)
        self.initUI()
        self.load_csv()

    def initUI(self):
        self.setWindowTitle("Tennis Scoreboard Simulator")
        self.resize(1200, 700)
        self.setStyleSheet("background-color: #1f3a46;")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # ----------------- Top Controls -----------------
        controls_layout = QHBoxLayout()
        self.start_btn = QPushButton(" Start ")
        self.stop_btn = QPushButton(" Stop ")
        self.reset_btn = QPushButton(" Reset ")
        for btn in [self.start_btn, self.stop_btn, self.reset_btn]:
            btn.setFont(QFont("Arial", 14))
            btn.setFixedHeight(41)
            btn.setStyleSheet("color: white; background-color: grey; border-radius: 5px;")  
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.reset_btn)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout, stretch=1)

        self.start_btn.clicked.connect(self.start_sim)
        self.stop_btn.clicked.connect(self.stop_sim)
        self.reset_btn.clicked.connect(self.reset_sim)

        # ----------------- Scoreboard Panel -----------------
        self.build_scoreboard(main_layout)

        # ----------------- Bottom Table + Log -----------------
        bottom_layout = QHBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Time_ns", "Phase", "State", "P1", "P2", "WIN1", "WIN2"])
        self.table.setStyleSheet("color: white; background-color: #0b1d23;")
        # Make header black
        header = self.table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { background-color: lightgray; color: black; }")
        header.setSectionResizeMode(QHeaderView.Stretch)
        bottom_layout.addWidget(self.table, stretch=3)  # smaller table

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Arial", 12))
        self.log_text.setStyleSheet("background-color: #0b1d23; color: white;")
        bottom_layout.addWidget(self.log_text, stretch=1)  # smaller log box

        main_layout.addLayout(bottom_layout, stretch=3)  # bottom 3, scoreboard 6

        self.setLayout(main_layout)

    def build_scoreboard(self, layout):
        font_big = QFont("Courier", 48, QFont.Bold)
        font_medium = QFont("Courier", 28, QFont.Bold)
        font_small = QFont("Arial", 22, QFont.Bold)

        grid = QGridLayout()
        grid.setSpacing(15)

        # Player labels
        self.p1_label = QLabel("PLAYER 1")
        self.p2_label = QLabel("PLAYER 2")
        for lbl in [self.p1_label, self.p2_label]:
            lbl.setFont(font_medium)
            lbl.setStyleSheet("color: white;")
            lbl.setAlignment(Qt.AlignCenter)

        # Serving indicators
        self.p1_serving = QLabel("●")
        self.p2_serving = QLabel("■")
        for lbl in [self.p1_serving, self.p2_serving]:
            lbl.setFont(font_small)
            lbl.setAlignment(Qt.AlignCenter)
        self.p1_serving.setStyleSheet("color: gray;")
        self.p2_serving.setStyleSheet("color: gray;")

        # Current game scores
        self.p1_score = QLabel("0")
        self.p2_score = QLabel("0")
        for lbl in [self.p1_score, self.p2_score]:
            lbl.setFont(font_big)
            lbl.setStyleSheet("color: red; background-color: #0b1d23; padding: 15px;")
            lbl.setAlignment(Qt.AlignCenter)

        # Set scores (3 sets)
        self.p1_sets = [QLabel("0"), QLabel("0"), QLabel("0")]
        self.p2_sets = [QLabel("0"), QLabel("0"), QLabel("0")]
        for lbl in self.p1_sets + self.p2_sets:
            lbl.setFont(font_big)
            lbl.setStyleSheet("color: yellow; background-color: #0b1d23; padding: 15px;")
            lbl.setAlignment(Qt.AlignCenter)

        # Win / Phase / State labels
        self.state_label = QLabel("State: NORMAL")
        self.phase_label = QLabel("Phase: 0")
        self.win_label = QLabel("Win: None")
        for lbl in [self.state_label, self.phase_label, self.win_label]:
            lbl.setFont(font_medium)
            lbl.setStyleSheet("color: white;")
            lbl.setAlignment(Qt.AlignCenter)

        # Row 0: PLAYER 1
        grid.addWidget(self.p1_label, 0, 0)
        grid.addWidget(self.p1_serving, 0, 1)
        grid.addWidget(self.p1_score, 0, 2)
        for i, s in enumerate(self.p1_sets):
            grid.addWidget(s, 0, 3 + i)

        # Row 1: PLAYER 2
        grid.addWidget(self.p2_label, 1, 0)
        grid.addWidget(self.p2_serving, 1, 1)
        grid.addWidget(self.p2_score, 1, 2)
        for i, s in enumerate(self.p2_sets):
            grid.addWidget(s, 1, 3 + i)

        # Row 2: Phase / State / Win
        grid.addWidget(self.phase_label, 2, 0, 1, 2)
        grid.addWidget(self.state_label, 2, 2, 1, 2)
        grid.addWidget(self.win_label, 2, 4, 1, 2)

        layout.addLayout(grid, stretch=6)

    # ----------------- CSV Loading -----------------
    def load_csv(self):
        with open(self.csv_file, "r") as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
            self.table.setRowCount(len(self.data))
            for i, row in enumerate(self.data):
                for j, key in enumerate(reader.fieldnames):
                    item = QTableWidgetItem(row[key])
                    item.setForeground(QBrush(QColor("white")))  # white text
                    self.table.setItem(i, j, item)

    # ----------------- Button Actions -----------------
    def start_sim(self):
        self.index = 0
        self.timer.start()
        self.log_text.append("Simulation started")

    def stop_sim(self):
        self.timer.stop()
        self.log_text.append("Simulation stopped")

    def reset_sim(self):
        self.timer.stop()
        self.index = 0
        self.p1_score.setText("0")
        self.p2_score.setText("0")
        for s in self.p1_sets + self.p2_sets:
            s.setText("0")
        self.p1_serving.setStyleSheet("color: gray;")
        self.p2_serving.setStyleSheet("color: gray;")
        self.state_label.setText("State: NORMAL")
        self.phase_label.setText("Phase: 0")
        self.win_label.setText("Win: None")
        self.table.clearSelection()
        self.log_text.append("Simulation reset")

    # ----------------- Update Scoreboard -----------------
    def update_scoreboard(self):
        if self.index >= len(self.data):
            self.timer.stop()
            self.log_text.append("Simulation complete")
            return

        row = self.data[self.index]
        self.phase_label.setText(f"Phase: {row.get('Phase', '0')}")
        self.state_label.setText(f"State: {row.get('State', 'NORMAL')}")
        self.p1_score.setText(str(row.get('P1_Score', '0')))
        self.p2_score.setText(str(row.get('P2_Score', '0')))

        state_lower = row.get('State', '').lower()
        if "p1" in state_lower:
            self.p1_serving.setStyleSheet("color: red;")
            self.p2_serving.setStyleSheet("color: gray;")
        elif "p2" in state_lower:
            self.p1_serving.setStyleSheet("color: gray;")
            self.p2_serving.setStyleSheet("color: red;")
        else:
            self.p1_serving.setStyleSheet("color: gray;")
            self.p2_serving.setStyleSheet("color: gray;")

        win_text = ""
        if row.get('WIN1') == '1':
            win_text = "Player 1 Wins!"
        elif row.get('WIN2') == '1':
            win_text = "Player 2 Wins!"
        self.win_label.setText(f"Win: {win_text}")
        if win_text:
            self.log_text.append(win_text)

        self.table.selectRow(self.index)
        self.index += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TennisGUI(r"D:\VLSI\Tennis Score Board\CSV_of_Scores.csv")
    gui.show()
    sys.exit(app.exec_())
