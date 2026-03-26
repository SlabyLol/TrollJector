import sys
import psutil
import json
import base64
import time
import datetime
import os
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QLineEdit, QLabel, QTextEdit, 
                             QFileDialog, QMessageBox, QProgressBar, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

# Offizielle DarkFox Co. Signatur
OFFICIAL_SIG = "DFX-9A27-K8RL-P3XQ-5VNW-7M2B-1ZTY"

def resource_path(relative_path):
    """ Helping functions for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LoaderThread(QThread):
    progress = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        steps = ["Validating Signature...", "Checking TrollJector License...", "Unpacking Assets..."]
        for i in range(101):
            time.sleep(0.01)
            if i % 34 == 0 and i > 0:
                self.log_signal.emit(f"SECURITY: {steps[min(int(i/34), 2)]}")
            self.progress.emit(i)
        self.finished.emit(self.data)

class TrollJector(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def log_action(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.console.append(log_entry)
        with open("trolljector_audit.log", "a") as f:
            f.write(log_entry + "\n")

    def init_ui(self):
        self.setWindowTitle('TrollJector (V4.8)')
        self.setFixedSize(550, 950) 
        
        # STEALTH: Icon aus der Taskleiste entfernen
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.Tool)
        
        # Pfade zu den Ressourcen
        icon_path = resource_path("tj-icon-ori.ico")
        image_path = resource_path("IMG_0678.jpeg")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("""
            QWidget { background-color: #020202; color: #00ff00; font-family: 'Consolas'; }
            QLineEdit, QTextEdit, QComboBox { background-color: #0a0a0a; border: 1px solid #00ff00; color: #00ff00; padding: 4px; }
            QPushButton { background-color: #00ff00; color: #000; font-weight: bold; border-radius: 0px; }
            QProgressBar { border: 1px solid #00ff00; text-align: center; height: 12px; }
            QProgressBar::chunk { background-color: #00ff00; }
            QLabel#warn { color: #ff0000; font-weight: bold; font-size: 10px; }
            QLabel#copyright { color: #004400; font-size: 10px; font-style: italic; }
        """)

        layout = QVBoxLayout()
        
        # Visual Branding Logo
        if os.path.exists(image_path):
            logo_label = QLabel()
            pixmap = QPixmap(image_path).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)

        layout.addWidget(QLabel(">>DARKFOX CO."), alignment=Qt.AlignmentFlag.AlignCenter)

        # Fields
        h_id = QHBoxLayout()
        self.s_name = QLineEdit(); self.s_name.setPlaceholderText("Script Name")
        self.s_auth = QLineEdit("DarkFox Co.") 
        h_id.addWidget(QLabel("Name:")); h_id.addWidget(self.s_name)
        h_id.addWidget(QLabel("By:")); h_id.addWidget(self.s_auth)
        layout.addLayout(h_id)

        self.mode_select = QComboBox()
        self.mode_select.addItems(["Browser (.tjb)", "Program (.tjp)"])
        layout.addWidget(self.mode_select)

        layout.addWidget(QLabel("> PAYLOAD EDITOR:"))
        self.editor = QTextEdit(); layout.addWidget(self.editor)
        
        layout.addWidget(QLabel("> SYSTEM LOG:"))
        self.console = QTextEdit(); self.console.setReadOnly(True); self.console.setFixedHeight(120)
        layout.addWidget(self.console)

        self.pbar = QProgressBar(); layout.addWidget(self.pbar)

        h_btns = QHBoxLayout()
        btn_exp = QPushButton("EXPORT & SIGN"); btn_exp.clicked.connect(self.export_file)
        btn_imp = QPushButton("IMPORT & VERIFY"); btn_imp.clicked.connect(self.import_file)
        h_btns.addWidget(btn_exp); h_btns.addWidget(btn_imp)
        layout.addLayout(h_btns)

        self.proc_box = QComboBox(); layout.addWidget(QLabel("Target Environment:")); layout.addWidget(self.proc_box)
        
        btn_exec = QPushButton("DEPLOY PAYLOAD")
        btn_exec.setFixedHeight(45); btn_exec.clicked.connect(self.execute_payload)
        layout.addWidget(btn_exec)

        # Footer
        w = QLabel("WARNING: WHEN YOU USE IT TO HARM SOMEONE WE'RE GONNA FIND YOU")
        w.setObjectName("warn"); w.setWordWrap(True); w.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(w)
        cp = QLabel("© DarkFox Co. - Web & Program Injector")
        cp.setObjectName("copyright"); cp.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(cp)

        self.setLayout(layout)
        self.scan_procs()
        self.log_action("DarkFox Kernel Initialized. Stealth Mode Active.")

    def scan_procs(self):
        self.proc_box.clear()
        for p in psutil.process_iter(['name']):
            try: self.proc_box.addItem(p.info['name'])
            except: pass

    def export_file(self):
        ext = ".tjb" if "Browser" in self.mode_select.currentText() else ".tjp"
        data = {"name": self.s_name.text() or "Payload", "creator": self.s_auth.text(), "type": "browser" if ext == ".tjb" else "exe", "signature": OFFICIAL_SIG, "code": base64.b64encode(self.editor.toPlainText().encode()).decode()}
        path, _ = QFileDialog.getSaveFileName(self, "Export", f"{data['name']}{ext}", f"TrollJector (*{ext})")
        if path:
            with open(path, 'w') as f: json.dump(data, f)
            self.log_action(f"Signed file created: {os.path.basename(path)}")

    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "TrollJector (*.tjb *.tjp)")
        if not path: return
        with open(path, 'r') as f:
            try:
                data = json.load(f)
                if data.get("signature") != OFFICIAL_SIG:
                    QMessageBox.critical(self, "Access Denied", "Unauthorized License key. Deleted for Safety.")
                    os.remove(path) 
                    self.log_action(f"PURGE: Illegal file {os.path.basename(path)} removed.")
                    return
                self.loader = LoaderThread(data)
                self.loader.progress.connect(self.pbar.setValue)
                self.loader.log_signal.connect(self.log_action)
                self.loader.finished.connect(self.finalize_import)
                self.loader.start()
            except Exception: pass

    def finalize_import(self, data):
        self.s_name.setText(data['name']); self.s_auth.setText(data['creator'])
        self.mode_select.setCurrentIndex(0 if data['type'] == "browser" else 1)
        self.editor.setText(base64.b64decode(data['code']).decode())
        self.log_action("Payload operational.")

    def execute_payload(self):
        target = self.proc_box.currentText()
        self.log_action(f"DEPLOYING to {target}...")
        for _ in range(3):
            bits = "".join(random.choice("01") for _ in range(25))
            self.log_action(f"STREAM: {bits}")
        QMessageBox.information(self, "TrollJector", f"Injection successful in {target}.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TrollJector()
    window.show()
    sys.exit(app.exec())
