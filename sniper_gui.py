import threading
import subprocess
import sys
import io

# sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')


import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QTextEdit, QCheckBox,
    QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer, QProcess, pyqtSignal, QObject
from dotenv import dotenv_values





class NFTBotUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFT Sniper Bot")
        self.showMaximized()  # Start maximized
        self.setMinimumSize(700, 400)
        
        # Modern dark theme styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                font-weight: 500;
                color: #e0e0e0;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #333;
                border-radius: 8px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #0078D7;
            }
            QPushButton {
                padding: 12px 20px;
                border-radius: 8px;
                border: none;
                font-weight: 600;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton#startBtn {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#startBtn:hover {
                background-color: #45a049;
            }
            QPushButton#stopBtn {
                background-color: #f44336;
                color: white;
            }
            QPushButton#stopBtn:hover {
                background-color: #da190b;
            }
            QPushButton#clearBtn {
                background-color: #ff9800;
                color: white;
            }
            QPushButton#clearBtn:hover {
                background-color: #e68900;
            }
            QCheckBox {
                padding-left: 5px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QTextEdit {
                background-color: #0d1117;
                color: #58a6ff;
                border: 2px solid #30363d;
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
            QFrame#separator {
                background-color: #333;
                border: none;
                height: 1px;
            }
        """)
        self.bot_process = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Left: Configuration Form ---
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Title
        title = QLabel("🚀 NFT Sniper Bot")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("color: #58a6ff; margin-bottom: 5px;")
        form_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Configure your bot settings and monitor NFT listings")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitle.setStyleSheet("color: #8b949e; margin-bottom: 10px;")
        form_layout.addWidget(subtitle)

        # Configuration section
        config_frame = QFrame()
        config_frame.setStyleSheet("QFrame { background-color: #21262d; border-radius: 10px; padding: 15px; }")
        config_vbox = QVBoxLayout(config_frame)
        config_title = QLabel("📋 Configuration")
        config_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        config_title.setStyleSheet("color: #58a6ff; margin-bottom: 10px;")
        config_vbox.addWidget(config_title)

        self.fields = {}
        field_names = [
            ("COLLECTION_SLUG", "Collection Slug"),
            ("CONTRACT_ADDRESS", "Contract Address"),
            ("TELEGRAM_BOT_TOKEN", "Telegram Bot Token"),
            ("TELEGRAM_USER_ID", "Telegram User ID"),
            ("OPENSEA_API_KEY", "OpenSea API Key"),
            ("MIN_SCORE_THRESHOLD", "Min Score Threshold"),
        ]
        existing_env = dotenv_values(".env") if os.path.exists(".env") else {}
        for key, label_text in field_names:
            config_vbox.addLayout(self.create_input_row(key, label_text, existing_env.get(key, "")))
        config_vbox.addStretch()
        form_layout.addWidget(config_frame)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.start_btn = QPushButton("▶ Start Bot")
        self.stop_btn = QPushButton("⏹ Stop Bot")
        self.clear_btn = QPushButton("🗑 Clear Output")
        self.start_btn.setObjectName("startBtn")
        self.stop_btn.setObjectName("stopBtn")
        self.clear_btn.setObjectName("clearBtn")
        self.start_btn.clicked.connect(self.save_and_start)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.clear_btn.clicked.connect(self.clear_output)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)

        # --- Right: Output Area ---
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)
        output_title = QLabel("📊 Bot Output")
        output_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        output_title.setStyleSheet("color: #58a6ff; margin-bottom: 10px;")
        output_layout.addWidget(output_title, alignment=Qt.AlignmentFlag.AlignTop)
        output_frame = QFrame()
        output_frame.setStyleSheet("QFrame { background-color: #21262d; border-radius: 10px; padding: 15px; }")
        output_vbox = QVBoxLayout(output_frame)
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setMinimumWidth(350)
        self.output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_box.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #58a6ff;
                border: 2px solid #30363d;
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        output_vbox.addWidget(self.output_box)
        output_frame.setLayout(output_vbox)
        output_layout.addWidget(output_frame)

        # Add both panels to main layout, align tops
        main_layout.addLayout(form_layout, 1)
        main_layout.addLayout(output_layout, 2)
        main_layout.setAlignment(form_layout, Qt.AlignmentFlag.AlignTop)
        main_layout.setAlignment(output_layout, Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)


    def create_input_row(self, key, label_text, default_value):
        row = QHBoxLayout()
        row.setSpacing(15)
        
        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: #e0e0e0;")

        field = QLineEdit()
        field.setText(default_value)
        field.setPlaceholderText(f"Enter {label_text}...")
        field.setMinimumWidth(300)

        # Mask sensitive fields
        if key in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_USER_ID", "OPENSEA_API_KEY"]:
            field.setEchoMode(QLineEdit.Password)

            # Show/hide checkbox
            toggle = QCheckBox("Show characters")
            toggle.setStyleSheet("color: #8b949e; font-size: 11px;")
            def toggle_visibility():
                field.setEchoMode(QLineEdit.Normal if toggle.isChecked() else QLineEdit.Password)
            toggle.stateChanged.connect(toggle_visibility)

            row.addWidget(label)
            row.addWidget(field)
            row.addWidget(toggle)
            row.addStretch()

        else:
            row.addWidget(label)
            row.addWidget(field)
            row.addStretch()

        self.fields[key] = field
        return row


    def save_and_start(self):
        try:
            # Validate required fields
            missing_fields = []
            for key, field in self.fields.items():
                if not field.text().strip():
                    missing_fields.append(key)
            
            if missing_fields:
                QMessageBox.warning(
                    self, 
                    "Missing Fields", 
                    f"Please fill in the following fields:\n\n• " + "\n• ".join(missing_fields)
                )
                return

            # Save to .env file
            env_content = ""
            for key, field in self.fields.items():
                value = field.text().strip()
                env_content += f"{key}={value}\n"

            with open(".env", "w", encoding='utf-8') as f:
                f.write(env_content)

            QMessageBox.information(
                self, 
                "Configuration Saved", 
                "✅ Configuration saved successfully!\n\nStarting the bot..."
            )
            self.start_bot_process()

        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save configuration:\n\n{str(e)}"
            )


    def start_bot_process(self):
        if self.bot_process:
            QMessageBox.warning(
                self, 
                "Bot Already Running", 
                "⚠️ The bot is already running.\n\nPlease stop the current bot before starting a new one."
            )
            return

        # Check if bot.py exists
        if not os.path.exists("bot.py"):
            QMessageBox.critical(
                self, 
                "Missing Bot File", 
                "❌ bot.py file not found in the current directory."
            )
            return

        self.bot_process = QProcess()
        self.bot_process.setProgram(sys.executable)
        self.bot_process.setArguments(["-u", "bot.py"])  # -u = unbuffered
        self.bot_process.readyReadStandardOutput.connect(self.read_output)
        self.bot_process.readyReadStandardError.connect(self.read_output)
        self.bot_process.finished.connect(self.bot_finished)
        
        try:
            self.bot_process.start()
            self.output_box.append("🚀 Bot started successfully!\n")
            self.output_box.append("📡 Monitoring for new NFT listings...\n")
            self.output_box.append("-" * 50 + "\n")
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Startup Error", 
                f"❌ Failed to start bot:\n\n{str(e)}"
            )

    def read_output(self):
        if self.bot_process:
            data = self.bot_process.readAllStandardOutput().data().decode(errors="replace")
            error = self.bot_process.readAllStandardError().data().decode(errors="replace")
            
            if data:
                self.output_box.append(data.strip())
            if error:
                self.output_box.append(f"❌ ERROR: {error.strip()}")
            
            # Auto-scroll to bottom
            cursor = self.output_box.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.output_box.setTextCursor(cursor)

    def stop_bot(self):
        if self.bot_process:
            self.bot_process.terminate()
            self.bot_process.kill()
            self.output_box.append("⏹ Bot stopped by user.\n")
            self.output_box.append("-" * 50 + "\n")
            self.bot_process = None
        else:
            self.output_box.append("ℹ️ No bot process running.\n")

    def clear_output(self):
        self.output_box.clear()
        self.output_box.append("📊 Output cleared.\n")

    def bot_finished(self):
        self.output_box.append("🏁 Bot process finished.\n")
        self.output_box.append("-" * 50 + "\n")
        self.bot_process = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NFTBotUI()
    window.show()
    sys.exit(app.exec_())
