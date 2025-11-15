import sys
import os
import shutil
from pathlib import Path
from typing import List, Tuple
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QFileDialog,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont


class ExactMatchWorker(QThread):
    """Worker thread for exact-match ROM file moving"""
    progress = pyqtSignal(int, int)  # current, total
    status = pyqtSignal(str)
    finished = pyqtSignal(list)  # list of results
    
    def __init__(self, source_dir: str, target_dir: str, rom_names: List[str]):
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.rom_names = rom_names
        self.is_running = True
        
    def stop(self):
        self.is_running = False
        
    def run(self):
        results = []
        total = len(self.rom_names)
        moved_count = 0
        failed_count = 0
        not_found_count = 0
        
        # Build file index for fast lookup (filename without extension -> full path)
        file_index = self.build_file_index()
        
        for idx, rom_name_with_dot in enumerate(self.rom_names):
            if not self.is_running:
                break
            
            # Remove trailing dot from ROM name
            rom_name = rom_name_with_dot.rstrip('.')
            
            self.status.emit(f"Processing: {rom_name}")
            self.progress.emit(idx + 1, total)
            
            # Try to find exact match
            matched_file, candidates = self.find_exact_match(rom_name, file_index)
            
            if matched_file:
                matched_filename = os.path.basename(matched_file)
                success = self.move_file(matched_file)
                if success:
                    results.append(f"✓ MOVED: {rom_name}")
                    results.append(f"  └─ File: {matched_filename}")
                    moved_count += 1
                else:
                    results.append(f"✗ FAILED TO MOVE: {rom_name}")
                    results.append(f"  └─ File: {matched_filename}")
                    failed_count += 1
            else:
                results.append(f"✗ NOT FOUND: {rom_name}")
                if candidates:
                    results.append(f"  └─ Similar files found (but not exact matches):")
                    for candidate in candidates[:3]:
                        results.append(f"     • {candidate}")
                not_found_count += 1
            
            results.append("")  # Blank line between entries
        
        # Summary
        results.append(f"{'='*60}")
        results.append(f"✓ Successfully moved: {moved_count}")
        results.append(f"✗ Failed to move: {failed_count}")
        results.append(f"✗ Not found: {not_found_count}")
        results.append(f"{'='*60}")
        
        self.finished.emit(results)
    
    def build_file_index(self) -> dict:
        """Build index of files: {name_without_ext: full_path}"""
        file_index = {}
        
        if not os.path.exists(self.source_dir):
            return file_index
        
        try:
            for filename in os.listdir(self.source_dir):
                filepath = os.path.join(self.source_dir, filename)
                
                # Skip directories
                if os.path.isdir(filepath):
                    continue
                
                # Remove extension from filename
                name_without_ext = os.path.splitext(filename)[0]
                file_index[name_without_ext] = filepath
        
        except Exception as e:
            self.status.emit(f"Error building file index: {e}")
        
        return file_index
    
    def find_exact_match(self, rom_name: str, file_index: dict) -> Tuple[str, List[str]]:
        """Find exact match for ROM name (ignoring file extension)
        Returns: (matched_file_path, list_of_similar_candidates)
        """
        # Direct exact match
        if rom_name in file_index:
            return file_index[rom_name], []
        
        # No exact match - find similar candidates for debugging
        candidates = []
        rom_name_lower = rom_name.lower()
        
        for name_without_ext in file_index.keys():
            if rom_name_lower in name_without_ext.lower() or name_without_ext.lower() in rom_name_lower:
                candidates.append(name_without_ext)
        
        return None, candidates
    
    def move_file(self, source_file: str) -> bool:
        """Move file from source to target directory"""
        try:
            # Create target directory if it doesn't exist
            os.makedirs(self.target_dir, exist_ok=True)
            
            # Get filename
            filename = os.path.basename(source_file)
            target_path = os.path.join(self.target_dir, filename)
            
            # Move the file
            shutil.move(source_file, target_path)
            return True
            
        except Exception as e:
            self.status.emit(f"Error moving file: {e}")
            return False


class MassFileMover(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("RomSort - by CodeKokeshi")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("RomSort")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Source directory selection
        source_layout = QHBoxLayout()
        source_label = QLabel("Source Directory:")
        source_label.setMinimumWidth(120)
        self.source_dir_input = QLineEdit()
        self.source_dir_input.setPlaceholderText("Select directory containing ROM files...")
        source_browse_btn = QPushButton("Browse")
        source_browse_btn.clicked.connect(self.browse_source_dir)
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_dir_input)
        source_layout.addWidget(source_browse_btn)
        layout.addLayout(source_layout)
        
        # Target directory selection
        target_layout = QHBoxLayout()
        target_label = QLabel("Target Directory:")
        target_label.setMinimumWidth(120)
        self.target_dir_input = QLineEdit()
        self.target_dir_input.setPlaceholderText("Select directory to move files to...")
        target_browse_btn = QPushButton("Browse")
        target_browse_btn.clicked.connect(self.browse_target_dir)
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_dir_input)
        target_layout.addWidget(target_browse_btn)
        layout.addLayout(target_layout)
        
        # ROM names input
        rom_names_label = QLabel("ROM Names (one per line):")
        layout.addWidget(rom_names_label)
        
        self.rom_names_input = QTextEdit()
        self.rom_names_input.setPlaceholderText(
            "Paste RetroAchievements ROM list here (one per line, ending with dot)...\n\n"
            "Example:\n"
            "Super Mario World (USA).\n"
            "Legend of Zelda, The - A Link to the Past (USA).\n"
            "Super Metroid (Japan, USA) (En,Ja).\n"
            "Mega Man X (USA) (Rev 1)."
        )
        self.rom_names_input.setMinimumHeight(200)
        layout.addWidget(self.rom_names_input)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setMinimumHeight(40)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        
        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setMinimumHeight(40)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # Results output
        results_label = QLabel("Results:")
        layout.addWidget(results_label)
        
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        self.results_output.setMinimumHeight(150)
        layout.addWidget(self.results_output)
        
        central_widget.setLayout(layout)
    
    def browse_source_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if directory:
            self.source_dir_input.setText(directory)
    
    def browse_target_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Target Directory")
        if directory:
            self.target_dir_input.setText(directory)
    
    def start_processing(self):
        # Validate inputs
        source_dir = self.source_dir_input.text().strip()
        target_dir = self.target_dir_input.text().strip()
        rom_names_text = self.rom_names_input.toPlainText().strip()
        
        if not source_dir or not os.path.exists(source_dir):
            QMessageBox.warning(self, "Error", "Please select a valid source directory.")
            return
        
        if not target_dir:
            QMessageBox.warning(self, "Error", "Please select a target directory.")
            return
        
        if not rom_names_text:
            QMessageBox.warning(self, "Error", "Please enter at least one ROM name.")
            return
        
        # Parse ROM names
        rom_names = [line.strip() for line in rom_names_text.split('\n') if line.strip()]
        
        if not rom_names:
            QMessageBox.warning(self, "Error", "Please enter at least one valid ROM name.")
            return
        
        # Disable start button, enable stop button
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Clear previous results
        self.results_output.clear()
        self.progress_bar.setValue(0)
        
        # Create and start worker thread
        self.worker = ExactMatchWorker(source_dir, target_dir, rom_names)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()
    
    def stop_processing(self):
        if self.worker:
            self.worker.stop()
            self.status_label.setText("Stopping...")
            self.stop_btn.setEnabled(False)
    
    def update_progress(self, current: int, total: int):
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
    
    def update_status(self, status: str):
        self.status_label.setText(status)
    
    def processing_finished(self, results: List[str]):
        # Display results
        self.results_output.append("\n=== PROCESSING COMPLETE ===\n")
        for result in results:
            self.results_output.append(result)
        
        # Re-enable buttons
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Complete")
        self.progress_bar.setValue(100)
        
        # Count moved files from results
        moved_count = sum(1 for r in results if r.startswith("✓ MOVED:"))
        
        # Show completion message
        QMessageBox.information(
            self, 
            "Processing Complete", 
            f"Finished processing!\n\n✓ {moved_count} files successfully moved\n\nCheck the results below for details."
        )
    
    def clear_results(self):
        self.results_output.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")


def main():
    app = QApplication(sys.argv)
    window = MassFileMover()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
