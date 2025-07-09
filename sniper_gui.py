import threading
import subprocess
import sys
import io
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QStackedWidget, QMessageBox, QSpacerItem
)
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QProcess
from dotenv import dotenv_values

APP_VERSION = "1.0.0"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/usamaabbasi01/nft_sniper_bot/main/version.txt"
GITHUB_UPDATE_BASE_URL = "https://raw.githubusercontent.com/usamaabbasi01/nft_sniper_bot/main/"

class NFTBotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFT Sniper Bot")
        self.resize(1100, 700)
        self.center_on_screen()
        self.setMinimumSize(800, 500)
        self.setStyleSheet(self.get_stylesheet())
        self.bot_process = None
        self.init_ui()
        self.showMaximized()
        self.check_for_updates()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def get_stylesheet(self):
        return """
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
            background-color: #181c24;
            color: #e0e6ed;
        }
        QFrame#topbar {
            background-color: #232a36;
            border-bottom: 1px solid #232a36;
        }
        QLabel#appTitle {
            font-size: 22px;
            font-weight: bold;
            color: #58a6ff;
        }
        QLabel#versionLabel {
            color: #8b949e;
            font-size: 13px;
        }
        QPushButton#updateBtn {
            background: #0078D7;
            color: white;
            border-radius: 6px;
            padding: 7px 18px;
            font-weight: 600;
        }
        QPushButton#updateBtn:hover {
            background: #005fa3;
        }
        QPushButton.navBtn {
            background: transparent;
            color: #e0e6ed;
            font-size: 16px;
            font-weight: 600;
            border: none;
            padding: 10px 24px;
            border-radius: 8px;
        }
        QPushButton.navBtn[selected="true"] {
            background: #232a36;
            color: #58a6ff;
        }
        QPushButton.navBtn:hover {
            background: #232a36;
            color: #58a6ff;
        }
        QLineEdit {
            padding: 10px;
            border: 2px solid #333;
            border-radius: 8px;
            background-color: #232a36;
            color: #e0e6ed;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 2px solid #58a6ff;
        }
        QPushButton {
            padding: 12px 20px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            font-size: 15px;
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
        QTextEdit {
            background-color: #10131a;
            color: #58a6ff;
            border: 2px solid #232a36;
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            padding: 10px;
        }
        QCheckBox {
            color: #e0e6ed;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        """

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar with logo, nav, version, update
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 10, 20, 10)
        topbar_layout.setSpacing(10)
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        else:
            logo_label.setText("<b>NFT Sniper</b>")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            logo_label.setStyleSheet("font-size: 22px; color: #58a6ff; margin: 0 10px 0 0;")
        topbar_layout.addWidget(logo_label)
        # Nav buttons
        self.nav_btns = []
        nav_names = ["Dashboard", "Settings", "About"]
        for i, name in enumerate(nav_names):
            btn = QPushButton(name)
            btn.setProperty("selected", "true" if i == 0 else "false")
            btn.setObjectName("navBtn" + name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setStyleSheet("")  # Use global stylesheet
            btn.clicked.connect(lambda checked, idx=i: self.pages.setCurrentIndex(idx))
            btn.clicked.connect(lambda checked, idx=i: self.update_nav_selection(idx))
            self.nav_btns.append(btn)
            topbar_layout.addWidget(btn)
        topbar_layout.addStretch()
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setObjectName("versionLabel")
        update_btn = QPushButton("Check for Updates")
        update_btn.setObjectName("updateBtn")
        update_btn.clicked.connect(self.check_for_updates)
        topbar_layout.addWidget(version_label)
        topbar_layout.addWidget(update_btn)
        main_layout.addWidget(topbar)

        # Stacked widget for pages
        self.pages = QStackedWidget()
        self.dashboard_page = self.create_dashboard_page()
        self.settings_page = self.create_settings_page()
        self.about_page = self.create_about_page()
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.about_page)
        main_layout.addWidget(self.pages)

    def update_nav_selection(self, selected_idx):
        for i, btn in enumerate(self.nav_btns):
            btn.setProperty("selected", "true" if i == selected_idx else "false")
            btn.setStyleSheet("")  # Re-apply global stylesheet

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        # Output area
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setMinimumHeight(250)
        self.output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.output_box)
        # Controls
        controls = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start Bot")
        self.stop_btn = QPushButton("⏹ Stop Bot")
        self.clear_btn = QPushButton("🗑 Clear Output")
        self.start_btn.setObjectName("startBtn")
        self.stop_btn.setObjectName("stopBtn")
        self.clear_btn.setObjectName("clearBtn")
        self.start_btn.clicked.connect(self.save_and_start)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.clear_btn.clicked.connect(self.clear_output)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.clear_btn)
        controls.addStretch()
        layout.addLayout(controls)
        return page

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        config_title = QLabel("📋 Configuration")
        config_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        config_title.setStyleSheet("color: #58a6ff; margin-bottom: 10px;")
        layout.addWidget(config_title)
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
            layout.addLayout(self.create_input_row(key, label_text, existing_env.get(key, "")))
        layout.addStretch()
        return page

    def create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        about_title = QLabel("ℹ️ About NFT Sniper Bot")
        about_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        about_title.setStyleSheet("color: #58a6ff; margin-bottom: 10px;")
        layout.addWidget(about_title)
        about_text = QLabel(
            """
            <b>NFT Sniper Bot</b> is a modern, user-friendly tool for monitoring NFT listings and sniping rare items.<br><br>
            <b>Features:</b><br>
            - Real-time monitoring<br>
            - Telegram alerts<br>
            - Auto-update support<br>
            - Modern, responsive UI<br><br>
            <b>Version:</b> {ver}<br>
            <b>GitHub:</b> <a href='https://github.com/usamaabbasi01/nft_sniper_bot'>usamaabbasi01/nft_sniper_bot</a><br>
            <b>Support:</b> Contact the developer for help or suggestions.<br>
            """.format(ver=APP_VERSION)
        )
        about_text.setOpenExternalLinks(True)
        about_text.setWordWrap(True)
        layout.addWidget(about_text)
        layout.addStretch()
        return page

    def create_input_row(self, key, label_text, default_value):
        row = QHBoxLayout()
        row.setSpacing(15)
        label = QLabel(label_text)
        label.setMinimumWidth(180)
        label.setFont(QFont("Segoe UI", 12))
        label.setStyleSheet("color: #e0e6ed;")
        field = QLineEdit()
        field.setText(default_value)
        field.setPlaceholderText(f"Enter {label_text}...")
        field.setMinimumWidth(300)
        # Mask sensitive fields
        if key in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_USER_ID", "OPENSEA_API_KEY"]:
            field.setEchoMode(QLineEdit.Password)
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

    def check_for_updates(self):
        try:
            resp = requests.get(GITHUB_VERSION_URL, timeout=5)
            if resp.status_code == 200:
                latest_version = resp.text.strip()
                if latest_version != APP_VERSION:
                    reply = QMessageBox.question(
                        self,
                        "Update Available",
                        f"A new version ({latest_version}) is available.\nYou are running {APP_VERSION}.\n\nDo you want to update now?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    if reply == QMessageBox.Yes:
                        self.perform_update(latest_version)
                    else:
                        self.output_box.append("Update cancelled by user.\n")
                else:
                    QMessageBox.information(
                        self,
                        "No Updates",
                        f"You are already running the latest version ({APP_VERSION})."
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Update Check Failed",
                    f"Failed to check for updates. Server responded with status code: {resp.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Update Check Error",
                f"Update check failed: {e}"
            )

    def perform_update(self, latest_version):
        # For demonstration, let's say we only update bot.py and utils.py
        files_to_update = ["bot.py", "utils.py"]
        updated = []
        for fname in files_to_update:
            url = GITHUB_UPDATE_BASE_URL + fname
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(resp.text)
                    updated.append(fname)
            except Exception as e:
                self.output_box.append(f"Failed to update {fname}: {e}\n")
        if updated:
            self.output_box.append(f"Updated files: {', '.join(updated)}. Please restart the app to use the new version.\n")
        else:
            self.output_box.append("No files were updated.\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NFTBotUI()
    window.show()
    sys.exit(app.exec_())
