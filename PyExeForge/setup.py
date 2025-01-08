import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        return False

def create_virtual_environment(venv_path):
    """Create a virtual environment."""
    print(f"Creating virtual environment at {venv_path}...")
    venv.create(venv_path, with_pip=True)

def get_activate_command():
    """Get the appropriate activation command based on OS."""
    if sys.platform == "win32":
        return str(Path("venv/Scripts/activate.bat"))
    return "source venv/bin/activate"

def setup():
    # Get the current directory
    current_dir = Path.cwd()
    venv_path = current_dir / "venv"

    # Remove existing virtual environment if it exists
    if venv_path.exists():
        print("Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)

    # Create new virtual environment
    create_virtual_environment(venv_path)
    print("Virtual environment created successfully!")

    # Activation command varies by OS
    activate_cmd = get_activate_command()

    # List of commands to run in the virtual environment
    commands = [
        # Upgrade pip
        f"{activate_cmd} && python -m pip install --upgrade pip",
        
        # Install required packages
        f"{activate_cmd} && pip install --no-cache-dir PyQt5==5.15.9",
        f"{activate_cmd} && pip install --no-cache-dir pyinstaller==6.1.0",
        
        # Create requirements.txt
        f"{activate_cmd} && pip freeze > requirements.txt"
    ]

    # Execute commands
    for command in commands:
        print(f"\nExecuting: {command}")
        if not run_command(command):
            print("Setup failed!")
            return False

    # Create the converter script
    converter_content = '''import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QProgressBar, QMessageBox, QTextEdit, QComboBox,
                            QStyle, QStyleFactory)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Python to EXE Converter")
        self.setMinimumSize(800, 600)
        
        # Set the dark emerald theme
        self.setup_theme()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Title label
        title_label = QLabel("Python to EXE Converter")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # File selection section
        file_section = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        select_button = QPushButton("Select Python File")
        select_button.setStyleSheet(self.get_button_style())
        select_button.clicked.connect(self.select_file)
        file_section.addWidget(self.file_label)
        file_section.addWidget(select_button)
        layout.addLayout(file_section)
        
        # Output directory section
        output_section = QHBoxLayout()
        self.output_label = QLabel("No output directory selected")
        output_button = QPushButton("Select Output Directory")
        output_button.setStyleSheet(self.get_button_style())
        output_button.clicked.connect(self.select_output_dir)
        output_section.addWidget(self.output_label)
        output_section.addWidget(output_button)
        layout.addLayout(output_section)
        
        # Options section
        options_section = QHBoxLayout()
        
        # Mode selection
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["One File", "One Directory"])
        self.mode_combo.setStyleSheet(self.get_combobox_style())
        options_section.addWidget(QLabel("Mode:"))
        options_section.addWidget(self.mode_combo)
        
        # Console selection
        self.console_combo = QComboBox()
        self.console_combo.addItems(["Console Based", "Window Based"])
        self.console_combo.setStyleSheet(self.get_combobox_style())
        options_section.addWidget(QLabel("Type:"))
        options_section.addWidget(self.console_combo)
        
        layout.addLayout(options_section)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(self.get_progressbar_style())
        layout.addWidget(self.progress_bar)
        
        # Progress section
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setStyleSheet(self.get_textedit_style())
        layout.addWidget(self.progress_text)
        
        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.setStyleSheet(self.get_button_style())
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)
        
        # Initialize variables
        self.selected_file = None
        self.output_dir = None
        self.worker = None

    def setup_theme(self):
        self.setStyle(QStyleFactory.create("Fusion"))
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(0, 128, 0))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 255, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(dark_palette)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #006400;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
            QPushButton:disabled {
                background-color: #2F4F4F;
            }
        """

    def get_combobox_style(self):
        return """
            QComboBox {
                background-color: #006400;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:drop-down {
                border: none;
            }
            QComboBox:down-arrow {
                color: white;
            }
        """

    def get_progressbar_style(self):
        return """
            QProgressBar {
                border: 2px solid #006400;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #006400;
            }
        """

    def get_textedit_style(self):
        return """
            QTextEdit {
                background-color: #1E1E1E;
                color: #00FF00;
                border: 1px solid #006400;
                border-radius: 3px;
            }
        """

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python File",
            "",
            "Python Files (*.py)"
        )
        if file_name:
            self.selected_file = file_name
            self.file_label.setText(os.path.basename(file_name))
            self.update_convert_button()

    def select_output_dir(self):
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )
        if dir_name:
            self.output_dir = dir_name
            self.output_label.setText(dir_name)
            self.update_convert_button()

    def update_convert_button(self):
        self.convert_button.setEnabled(
            bool(self.selected_file and self.output_dir)
        )

    def start_conversion(self):
        if not self.selected_file or not self.output_dir:
            return
        
        self.convert_button.setEnabled(False)
        self.progress_text.clear()
        self.progress_bar.setValue(0)
        
        mode = "onefile" if self.mode_combo.currentText() == "One File" else "onedir"
        console = self.console_combo.currentText() == "Console Based"
        
        self.worker = ConversionWorker(
            self.selected_file,
            self.output_dir,
            mode,
            console
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()

    def update_progress(self, message):
        self.progress_text.append(message)

    def conversion_finished(self, success, message):
        self.convert_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

class ConversionWorker(QThread):
    progress = pyqtSignal(str)
    status = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, script_path, output_dir, mode="onefile", console=True):
        super().__init__()
        self.script_path = script_path
        self.output_dir = output_dir
        self.mode = mode
        self.console = console

    def run(self):
        try:
            self.progress.emit("Starting conversion process...")
            self.status.emit(10)

            # Create PyInstaller command
            pyinstaller_path = os.path.join(os.path.dirname(sys.executable), "Scripts", "pyinstaller.exe")
            
            cmd = [
                pyinstaller_path,
                "--clean",
                "--noconfirm",
            ]
            
            if self.mode == "onefile":
                cmd.append("--onefile")
            else:
                cmd.append("--onedir")
            
            if not self.console:
                cmd.append("--windowed")
            
            # Add paths
            cmd.extend([
                "--distpath", self.output_dir,
                "--workpath", os.path.join(self.output_dir, "build"),
                "--specpath", self.output_dir,
                self.script_path
            ])
            
            self.progress.emit(f"Running command: {' '.join(cmd)}")
            self.status.emit(20)
            
            # Use CREATE_NO_WINDOW flag on Windows
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            # Read output in real-time
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.strip()
                    self.progress.emit(line)
                    
                    # Update progress based on stages
                    if "Analyzing" in line:
                        self.status.emit(40)
                    elif "Processing" in line:
                        self.status.emit(60)
                    elif "Copying" in line:
                        self.status.emit(80)
                    elif "Building" in line:
                        self.status.emit(90)

            # Get the return code
            returncode = process.poll()
            
            # Check for errors
            if returncode != 0:
                error = process.stderr.read()
                self.progress.emit(f"Error: {error}")
                self.finished.emit(False, f"Conversion failed: {error}")
                return

            # Verify the executable was created
            exe_name = os.path.splitext(os.path.basename(self.script_path))[0]
            exe_path = os.path.join(self.output_dir, exe_name + '.exe')
            
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                success_message = f"Conversion completed successfully!\\nExecutable location: {exe_path}\\nSize: {size_mb:.2f} MB"
                self.status.emit(100)
                self.finished.emit(True, success_message)
            else:
                self.finished.emit(False, "Conversion completed but executable not found")
                
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(False, f"Error during conversion: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''

    # Write the converter script
    with open('python-to-exe_converter.py', 'w') as f:
        f.write(converter_content)

    # Create the launcher script
    launcher_content = """@echo off
call venv\\Scripts\\activate
python python-to-exe_converter.py
pause
""" if sys.platform == "win32" else """#!/bin/bash
source venv/bin/activate
python python-to-exe_converter.py
"""

    launcher_name = "launch_converter.bat" if sys.platform == "win32" else "launch_converter.sh"
    
    with open(launcher_name, "w") as f:
        f.write(launcher_content)

    if sys.platform != "win32":
        os.chmod(launcher_name, 0o755)

    print("\nSetup completed successfully!")
    print(f"\nTo start the converter, run: {launcher_name}")

if __name__ == "__main__":
    try:
        setup()
    except Exception as e:
        print(f"An error occurred during setup: {str(e)}")
        sys.exit(1)