import sys
import os
import re
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QMessageBox,
    QComboBox, QTextEdit, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QProcess, QTextStream, QIODevice, QTimer, QProcessEnvironment
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

class YouTubeDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.video_process = None
        self.audio_process = None
        self.current_process_type = None  # 'video' or 'audio'
        self.setup_icons()
        self.init_ui()
        self.setup_dark_mode()
        self.setup_styles()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

    def setup_icons(self):
        """Set up application and window icons"""
        icon_path = os.path.join(self.script_dir, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        icon_path = os.path.join(self.script_dir, "icon.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            QApplication.setWindowIcon(app_icon)

    def sanitize_text(self, text):
        """Remove special characters that might cause encoding issues"""
        if not text:
            return text
            
        # Replace common problematic characters with space
        text = re.sub(r'[:：/\\|?*<>"]', ' ', text)
        # Remove other non-ASCII characters if needed
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Collapse multiple spaces into one
        text = ' '.join(text.split())
        return text.strip()

    def init_ui(self):
        self.setWindowTitle('YouTube Downloader')
        
        # Window sizing and centering
        screen = QApplication.primaryScreen().availableGeometry()
        width = max(int(screen.width() * 0.5), 800)
        height = max(int(screen.height() * 0.6), 600)
        self.setGeometry(int((screen.width() - width) / 2), 
                        int((screen.height() - height) / 2), 
                        width, height)
        self.setMinimumSize(700, 550)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Instruction label
        instruction = QLabel("Paste the YouTube video URL and select the format to download.")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #a6a6a6;
                padding: 10px;
            }
        """)
        layout.addWidget(instruction)

        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("border: 1px solid #333333;")
        layout.addWidget(separator)

        # URL Input Section
        url_layout = QHBoxLayout()
        url_label = QLabel('YouTube URL:')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Resolution Selection Section
        self.resolution_layout = QVBoxLayout()
        resolution_label = QLabel('Select resolution:')
        self.resolution_combo = QComboBox()
        # Added 240p and 144p to the existing options
        self.resolution_combo.addItems(["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"])
        self.resolution_layout.addWidget(resolution_label)
        self.resolution_layout.addWidget(self.resolution_combo)
        layout.addLayout(self.resolution_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Output will appear here...")
        layout.addWidget(self.log_output, 1)

        # Button Layout
        button_layout = QHBoxLayout()
        
        self.download_video_btn = QPushButton('DOWNLOAD VIDEO')
        self.download_video_btn.clicked.connect(lambda: self.start_download('video'))
        self.download_video_btn.setObjectName("downloadVideoButton")
        
        self.download_audio_btn = QPushButton('DOWNLOAD AUDIO')
        self.download_audio_btn.clicked.connect(lambda: self.start_download('audio'))
        self.download_audio_btn.setObjectName("downloadAudioButton")
        
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        button_layout.addWidget(self.download_video_btn)
        button_layout.addWidget(self.download_audio_btn)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        layout.addLayout(button_layout)

    def setup_dark_mode(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(32, 32, 32))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        QApplication.setPalette(palette)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #202020;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
                color: #ffffff;
                selection-background-color: #0078d7;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border-left: 1px solid #3a3a3a;
                border-radius: 0 4px 4px 0;
            }
            QComboBox::down-arrow {
                image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12"><path fill="white" d="M6 9L1 2h10z"/></svg>');
                width: 12px;
                height: 12px;
            }
            QComboBox::down-arrow:on {
                top: 1px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                min-width: 120px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1081dd;
            }
            QPushButton:pressed {
                background-color: #005499;
            }
            QPushButton:disabled {
                background-color: #454545;
                color: #808080;
            }
            #downloadVideoButton, #downloadAudioButton {
                background-color: #e74c3c;
            }
            #downloadVideoButton:hover, #downloadAudioButton:hover {
                background-color: #c0392b;
            }
            #downloadVideoButton:pressed, #downloadAudioButton:pressed {
                background-color: #992d22;
            }
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d2d;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 3px;
            }
            QTextEdit {
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #0078d7;
                border: 1px solid #3a3a3a;
                outline: none;
                padding: 4px;
            }
            QMessageBox {
                background-color: #252525;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1081dd;
            }
        """)

    def validate_inputs(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Warning', 'Please enter a YouTube URL')
            return False
        if "youtube.com" not in url and "youtu.be" not in url:
            QMessageBox.warning(self, 'Warning', 'Please enter a valid YouTube URL')
            return False
        return True

    def start_download(self, download_type):
        if not self.validate_inputs():
            return

        self.current_process_type = download_type
        self.download_video_btn.setEnabled(False)
        self.download_audio_btn.setEnabled(False)
        self.log_output.clear()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        url = self.url_input.text().strip()

        if download_type == 'video':
            script_path = os.path.join(self.script_dir, "Video.py")
            resolution = self.resolution_combo.currentText().rstrip('p')
        else:
            script_path = os.path.join(self.script_dir, "Audio.py")
        
        if not os.path.exists(script_path):
            QMessageBox.critical(self, 'Error', f'{download_type.capitalize()} script not found in the same directory!')
            self.reset_buttons()
            self.progress_bar.setRange(0, 1)
            return

        # Create and configure the process with UTF-8 environment
        process = QProcess()
        process.setWorkingDirectory(self.script_dir)
        
        # Set UTF-8 encoding environment
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUTF8", "1")
        process.setProcessEnvironment(env)
        
        process.readyReadStandardOutput.connect(self.handle_stdout)
        process.readyReadStandardError.connect(self.handle_stderr)
        process.finished.connect(self.process_finished)

        if download_type == 'video':
            self.video_process = process
        else:
            self.audio_process = process

        # Start the process with UTF-8 mode
        process.start(sys.executable, ["-X", "utf8", script_path])
        
        if not process.waitForStarted():
            QMessageBox.critical(self, 'Error', f'Failed to start {download_type.capitalize()} process')
            self.reset_buttons()
            self.progress_bar.setRange(0, 1)
            return

        # Send URL to the process
        self.send_input_to_process(process, url)
        
        # For video downloads, send resolution
        if download_type == 'video':
            QTimer.singleShot(100, lambda: self.send_input_to_process(process, resolution))

    def send_input_to_process(self, process, text):
        """Send text to the process followed by a newline"""
        if process and process.state() == QProcess.ProcessState.Running:
            process.write(f"{text}\n".encode('utf-8'))
            process.waitForBytesWritten()

    def handle_stdout(self):
        process = self.sender()
        if process:
            data = process.readAllStandardOutput().data()
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                text = data.decode(sys.getdefaultencoding(), errors='replace')
            sanitized = self.sanitize_text(text)
            self.log_output.append(sanitized)

    def handle_stderr(self):
        process = self.sender()
        if process:
            data = process.readAllStandardError().data()
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                text = data.decode(sys.getdefaultencoding(), errors='replace')
            sanitized = self.sanitize_text(text)
            self.log_output.append(f'<font color="orange">{sanitized}</font>')

    def process_finished(self, exit_code, exit_status):
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.reset_buttons()
        
        process = self.sender()
        process_type = 'video' if process == self.video_process else 'audio'
        
        if exit_code == 0:
            self.log_output.append(f'<font color="green">{process_type.capitalize()} download completed successfully!</font>')
            QMessageBox.information(self, "Success", f"{process_type.capitalize()} download completed successfully!")
        else:
            self.log_output.append(f'<font color="red">{process_type.capitalize()} process failed with code {exit_code}</font>')
            QMessageBox.warning(self, "Error", f"{process_type.capitalize()} download failed with error code {exit_code}")

    def reset_buttons(self):
        self.download_video_btn.setEnabled(True)
        self.download_audio_btn.setEnabled(True)

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    window = YouTubeDownloaderGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()