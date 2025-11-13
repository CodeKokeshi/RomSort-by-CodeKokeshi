import sys
import os
import shutil
import re
import configparser
from pathlib import Path
from typing import List, Optional, Tuple
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QFileDialog,
    QProgressBar, QMessageBox, QDialog, QFormLayout, QSpinBox,
    QCheckBox, QDialogButtonBox, QGroupBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont


class Settings:
    """Manages application settings with INI file persistence"""
    
    def __init__(self):
        self.config_file = "romsort_settings.ini"
        self.config = configparser.ConfigParser()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from INI file or create defaults"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_settings()
    
    def create_default_settings(self):
        """Create default settings"""
        self.config['RegionPriority'] = {
            'europe_priority': '1000',
            'usa_priority': '800',
            'world_priority': '700',
            'english_priority': '650'
        }
        
        self.config['Filtering'] = {
            'reject_japan_only': 'true',
            'reject_single_country': 'true',  # Reject Germany, France, etc. alone
            'reject_beta': 'true',
            'reject_prototype': 'true',
            'reject_alpha': 'true',
            'reject_demo': 'true',
            'reject_virtual_console': 'true',
            'reject_alt_versions': 'true',
            'reject_revisions': 'true',
            'reject_samples': 'true'
        }
        
        self.config['AcceptableRegions'] = {
            'regions': 'Europe, USA, World, En, English'  # Comma-separated
        }
        
        self.config['RejectedCountries'] = {
            'countries': 'Germany, France, Spain, Italy, Japan, Australia, Brazil, Korea'  # When alone
        }
        
        self.save_settings()
    
    def save_settings(self):
        """Save settings to INI file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_int(self, section, key, default=0):
        return self.config.getint(section, key, fallback=default)
    
    def get_bool(self, section, key, default=False):
        return self.config.getboolean(section, key, fallback=default)
    
    def get_str(self, section, key, default=''):
        return self.config.get(section, key, fallback=default)
    
    def get_list(self, section, key, default=None):
        """Get comma-separated list as Python list"""
        if default is None:
            default = []
        value = self.get_str(section, key, '')
        if not value:
            return default
        return [item.strip().lower() for item in value.split(',')]
    
    def set_value(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)


class SettingsDialog(QDialog):
    """Dialog for configuring ROM filtering settings"""
    
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("RomSort Settings")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Region Priority Group
        priority_group = QGroupBox("Region Priority (Higher = Better)")
        priority_layout = QFormLayout()
        
        self.europe_spin = QSpinBox()
        self.europe_spin.setRange(0, 2000)
        self.europe_spin.setValue(self.settings.get_int('RegionPriority', 'europe_priority', 1000))
        priority_layout.addRow("Europe Priority:", self.europe_spin)
        
        self.usa_spin = QSpinBox()
        self.usa_spin.setRange(0, 2000)
        self.usa_spin.setValue(self.settings.get_int('RegionPriority', 'usa_priority', 800))
        priority_layout.addRow("USA Priority:", self.usa_spin)
        
        self.world_spin = QSpinBox()
        self.world_spin.setRange(0, 2000)
        self.world_spin.setValue(self.settings.get_int('RegionPriority', 'world_priority', 700))
        priority_layout.addRow("World Priority:", self.world_spin)
        
        self.english_spin = QSpinBox()
        self.english_spin.setRange(0, 2000)
        self.english_spin.setValue(self.settings.get_int('RegionPriority', 'english_priority', 650))
        priority_layout.addRow("English Priority:", self.english_spin)
        
        priority_group.setLayout(priority_layout)
        layout.addWidget(priority_group)
        
        # Filtering Options Group
        filter_group = QGroupBox("Filtering Options")
        filter_layout = QVBoxLayout()
        
        self.reject_japan_check = QCheckBox("Reject Japan-only ROMs")
        self.reject_japan_check.setChecked(self.settings.get_bool('Filtering', 'reject_japan_only', True))
        filter_layout.addWidget(self.reject_japan_check)
        
        self.reject_country_check = QCheckBox("Reject single-country ROMs (Germany, France, etc.)")
        self.reject_country_check.setChecked(self.settings.get_bool('Filtering', 'reject_single_country', True))
        filter_layout.addWidget(self.reject_country_check)
        
        self.reject_beta_check = QCheckBox("Reject Beta versions")
        self.reject_beta_check.setChecked(self.settings.get_bool('Filtering', 'reject_beta', True))
        filter_layout.addWidget(self.reject_beta_check)
        
        self.reject_proto_check = QCheckBox("Reject Prototype/Proto versions")
        self.reject_proto_check.setChecked(self.settings.get_bool('Filtering', 'reject_prototype', True))
        filter_layout.addWidget(self.reject_proto_check)
        
        self.reject_alpha_check = QCheckBox("Reject Alpha versions")
        self.reject_alpha_check.setChecked(self.settings.get_bool('Filtering', 'reject_alpha', True))
        filter_layout.addWidget(self.reject_alpha_check)
        
        self.reject_demo_check = QCheckBox("Reject Demo versions")
        self.reject_demo_check.setChecked(self.settings.get_bool('Filtering', 'reject_demo', True))
        filter_layout.addWidget(self.reject_demo_check)
        
        self.reject_vc_check = QCheckBox("Reject Virtual Console versions")
        self.reject_vc_check.setChecked(self.settings.get_bool('Filtering', 'reject_virtual_console', True))
        filter_layout.addWidget(self.reject_vc_check)
        
        self.reject_alt_check = QCheckBox("Reject Alt versions (Alt 1, Alt 2, etc.)")
        self.reject_alt_check.setChecked(self.settings.get_bool('Filtering', 'reject_alt_versions', True))
        filter_layout.addWidget(self.reject_alt_check)
        
        self.reject_rev_check = QCheckBox("Reject Revision versions (Rev 1, V1.0, etc.)")
        self.reject_rev_check.setChecked(self.settings.get_bool('Filtering', 'reject_revisions', True))
        filter_layout.addWidget(self.reject_rev_check)
        
        self.reject_sample_check = QCheckBox("Reject Samples/Promos")
        self.reject_sample_check.setChecked(self.settings.get_bool('Filtering', 'reject_samples', True))
        filter_layout.addWidget(self.reject_sample_check)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Advanced Group
        advanced_group = QGroupBox("Advanced (Comma-separated lists)")
        advanced_layout = QFormLayout()
        
        self.acceptable_regions = QLineEdit()
        self.acceptable_regions.setText(self.settings.get_str('AcceptableRegions', 'regions', 'Europe, USA, World, En, English'))
        advanced_layout.addRow("Acceptable Regions:", self.acceptable_regions)
        
        self.rejected_countries = QLineEdit()
        self.rejected_countries.setText(self.settings.get_str('RejectedCountries', 'countries', 'Germany, France, Spain, Italy, Japan, Australia, Brazil, Korea'))
        advanced_layout.addRow("Reject When Alone:", self.rejected_countries)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """Save all settings and close dialog"""
        # Region priorities
        self.settings.set_value('RegionPriority', 'europe_priority', self.europe_spin.value())
        self.settings.set_value('RegionPriority', 'usa_priority', self.usa_spin.value())
        self.settings.set_value('RegionPriority', 'world_priority', self.world_spin.value())
        self.settings.set_value('RegionPriority', 'english_priority', self.english_spin.value())
        
        # Filtering options
        self.settings.set_value('Filtering', 'reject_japan_only', self.reject_japan_check.isChecked())
        self.settings.set_value('Filtering', 'reject_single_country', self.reject_country_check.isChecked())
        self.settings.set_value('Filtering', 'reject_beta', self.reject_beta_check.isChecked())
        self.settings.set_value('Filtering', 'reject_prototype', self.reject_proto_check.isChecked())
        self.settings.set_value('Filtering', 'reject_alpha', self.reject_alpha_check.isChecked())
        self.settings.set_value('Filtering', 'reject_demo', self.reject_demo_check.isChecked())
        self.settings.set_value('Filtering', 'reject_virtual_console', self.reject_vc_check.isChecked())
        self.settings.set_value('Filtering', 'reject_alt_versions', self.reject_alt_check.isChecked())
        self.settings.set_value('Filtering', 'reject_revisions', self.reject_rev_check.isChecked())
        self.settings.set_value('Filtering', 'reject_samples', self.reject_sample_check.isChecked())
        
        # Advanced
        self.settings.set_value('AcceptableRegions', 'regions', self.acceptable_regions.text())
        self.settings.set_value('RejectedCountries', 'countries', self.rejected_countries.text())
        
        self.settings.save_settings()
        self.accept()
    
    def restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore default settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.create_default_settings()
            self.close()
            # Reopen dialog with new defaults
            new_dialog = SettingsDialog(self.settings, self.parent())
            new_dialog.exec()


class ROMMatcherWorker(QThread):
    """Worker thread for matching and moving ROM files"""
    progress = pyqtSignal(int, int)  # current, total
    status = pyqtSignal(str)
    finished = pyqtSignal(list)  # list of results
    
    def __init__(self, source_dir: str, target_dir: str, rom_names: List[str], settings: Settings):
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.rom_names = rom_names
        self.settings = settings
        self.is_running = True
        
    def stop(self):
        self.is_running = False
        
    def run(self):
        results = []
        total = len(self.rom_names)
        moved_count = 0
        failed_count = 0
        not_found_count = 0
        
        for idx, rom_name in enumerate(self.rom_names):
            if not self.is_running:
                break
                
            self.status.emit(f"Processing: {rom_name}")
            self.progress.emit(idx + 1, total)
            
            matched_file, candidates = self.find_best_match(rom_name)
            
            if matched_file:
                matched_filename = os.path.basename(matched_file)
                success = self.move_file(matched_file)
                if success:
                    results.append(f"✓ MOVED: {rom_name}")
                    results.append(f"  └─ Selected: {matched_filename}")
                    
                    # Show other candidates if there were multiple options
                    if len(candidates) > 1:
                        results.append(f"  └─ Other candidates found: {len(candidates) - 1}")
                        for candidate_name, score in candidates[1:4]:  # Show top 3 alternatives
                            results.append(f"     • {candidate_name} (score: {score})")
                    
                    moved_count += 1
                else:
                    results.append(f"✗ FAILED: {rom_name}")
                    results.append(f"  └─ File: {matched_filename} (could not move)")
                    failed_count += 1
            else:
                results.append(f"✗ NOT FOUND: {rom_name}")
                if len(candidates) > 0:
                    results.append(f"  └─ Found {len(candidates)} matches but all were rejected:")
                    for candidate_name, score in candidates[:3]:  # Show why they were rejected
                        results.append(f"     • {candidate_name} (rejected: unwanted version/region)")
                else:
                    results.append(f"  └─ No files matching this name exist in the source directory")
                not_found_count += 1
            
            results.append("")  # Add blank line between entries
        
        # Add summary at the end
        results.append(f"{'='*50}")
        results.append(f"✓ Successfully moved: {moved_count}")
        results.append(f"✗ Failed to move: {failed_count}")
        results.append(f"✗ Not found: {not_found_count}")
        results.append(f"{'='*50}")
        
        self.finished.emit(results)
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for comparison by removing special characters and extra spaces"""
        # Remove content in parentheses for comparison
        name = re.sub(r'\([^)]*\)', '', name)
        # Remove ALL special characters and punctuation (including : - ' . etc)
        # This makes "Castlevania: Rondo" match "Castlevania - Rondo" or "Castlevania Rondo"
        name = re.sub(r'[^\w\s]', '', name)
        # Convert to lowercase and remove extra spaces
        name = ' '.join(name.lower().split())
        return name
    
    def get_name_variants(self, name: str) -> list:
        """Generate variants of a name to improve matching flexibility"""
        variants = []
        
        # Original normalized name
        normalized = self.normalize_name(name)
        variants.append(normalized)
        
        # Remove common subtitle separators and try matching just the main title
        # e.g., "Castlevania: Rondo of Blood" -> also try "Castlevania"
        main_parts = re.split(r'[:—–-]', name)
        if len(main_parts) > 1:
            main_title = self.normalize_name(main_parts[0])
            if main_title and main_title not in variants:
                variants.append(main_title)
        
        # Remove "The" from beginning
        if normalized.startswith('the '):
            variants.append(normalized[4:])
        
        return variants
    
    def calculate_region_priority(self, filename: str) -> int:
        """
        Calculate priority score for a ROM file based on region tags.
        Uses settings for customizable filtering and priorities.
        """
        filename_lower = filename.lower()
        score = 0
        
        # Extract all parentheses content
        parentheses = re.findall(r'\([^)]+\)', filename_lower)
        
        # Build unwanted tags list based on settings
        unwanted_tags = []
        if self.settings.get_bool('Filtering', 'reject_beta'):
            unwanted_tags.append('beta')
        if self.settings.get_bool('Filtering', 'reject_prototype'):
            unwanted_tags.extend(['proto', 'prototype'])
        if self.settings.get_bool('Filtering', 'reject_alpha'):
            unwanted_tags.append('alpha')
        if self.settings.get_bool('Filtering', 'reject_demo'):
            unwanted_tags.append('demo')
        if self.settings.get_bool('Filtering', 'reject_virtual_console'):
            unwanted_tags.extend(['switch online', 'wii u virtual console', 'wii virtual console', 'virtual console'])
        if self.settings.get_bool('Filtering', 'reject_alt_versions'):
            unwanted_tags.extend(['alt', 'alt 1', 'alt 2', 'alt 3'])
        if self.settings.get_bool('Filtering', 'reject_revisions'):
            unwanted_tags.extend(['rev ', 'rev 1', 'rev 2', 'v1.', 'v2.', 'v3.'])
        if self.settings.get_bool('Filtering', 'reject_samples'):
            unwanted_tags.extend(['sample', 'promo', 'unl', 'pirate', 'hack', 'homebrew'])
        
        # Check for unwanted tags
        for paren in parentheses:
            for tag in unwanted_tags:
                if tag in paren:
                    return -1000  # Reject unwanted versions
        
        # If there are 2+ parentheses, check if second one is valid
        if len(parentheses) >= 2:
            second_paren = parentheses[1]
            acceptable_regions_lower = [r.lower() for r in self.settings.get_list('AcceptableRegions', 'regions')]
            valid_second = any(region in second_paren for region in acceptable_regions_lower)
            if not valid_second:
                return -1000  # Reject if second parentheses is not region-related
        
        # Get acceptable regions and rejected countries from settings
        acceptable_regions = self.settings.get_list('AcceptableRegions', 'regions', ['europe', 'usa', 'world', 'en', 'english'])
        rejected_countries = self.settings.get_list('RejectedCountries', 'countries', ['germany', 'france', 'spain', 'italy', 'japan'])
        
        # Check for single-country rejection
        if self.settings.get_bool('Filtering', 'reject_single_country', True):
            # Check if ROM only has a rejected country and no acceptable regions
            has_rejected_country_only = False
            for country in rejected_countries:
                if any(country in p for p in parentheses):
                    # Check if it also has an acceptable region
                    has_acceptable = any(
                        any(region in p for region in acceptable_regions)
                        for p in parentheses
                    )
                    if not has_acceptable:
                        has_rejected_country_only = True
                        break
            
            if has_rejected_country_only:
                return -1000  # Reject single-country ROMs
        
        # Special handling for Japan-only
        if self.settings.get_bool('Filtering', 'reject_japan_only', True):
            has_japan = any('japan' in p for p in parentheses)
            has_acceptable_region = any(
                any(region in p for region in acceptable_regions)
                for p in parentheses
            )
            if has_japan and not has_acceptable_region:
                return -1000  # Reject Japan-only ROMs
        
        # Region priority scoring (from settings)
        europe_priority = self.settings.get_int('RegionPriority', 'europe_priority', 1000)
        usa_priority = self.settings.get_int('RegionPriority', 'usa_priority', 800)
        world_priority = self.settings.get_int('RegionPriority', 'world_priority', 700)
        english_priority = self.settings.get_int('RegionPriority', 'english_priority', 650)
        
        # Check for Europe
        if re.search(r'\(.*europe.*\)', filename_lower):
            score += europe_priority
        elif re.search(r'\(.*\beu\b.*\)', filename_lower):
            score += europe_priority - 50
        
        # Check for USA
        if re.search(r'\(.*usa.*\)', filename_lower):
            score += usa_priority
        elif re.search(r'\(.*\bus\b.*\)', filename_lower):
            score += usa_priority - 50
        
        # Check for World
        if re.search(r'\(.*world.*\)', filename_lower):
            score += world_priority
        
        # Check for English
        if re.search(r'\(.*\ben\b.*\)', filename_lower):
            score += english_priority
        elif re.search(r'\(.*english.*\)', filename_lower):
            score += english_priority
        
        # Bonus for Europe+USA combined
        if 'europe' in filename_lower and 'usa' in filename_lower:
            score += 100
        
        return score
    
    def find_best_match(self, rom_name: str) -> Tuple[Optional[str], list]:
        """Find the best matching ROM file in the source directory
        Returns: (best_match_path, list_of_all_candidates)
        """
        if not os.path.exists(self.source_dir):
            return None, []
        
        # Get all possible name variants to search for
        search_variants = self.get_name_variants(rom_name)
        best_match = None
        best_score = -1000
        all_candidates = []  # Track all potential matches
        
        # Get all files in source directory
        try:
            files = os.listdir(self.source_dir)
        except Exception as e:
            self.status.emit(f"Error reading directory: {e}")
            return None, []
        
        for filename in files:
            # Skip directories
            filepath = os.path.join(self.source_dir, filename)
            if os.path.isdir(filepath):
                continue
            
            # Normalize the filename for comparison
            normalized_file = self.normalize_name(filename)
            
            # Try matching against all variants
            match_found = False
            best_variant_match = 0
            
            for idx, variant in enumerate(search_variants):
                if variant in normalized_file:
                    match_found = True
                    # First variant (most specific) gets highest bonus
                    variant_bonus = 50 - (idx * 10)
                    
                    # Calculate how well it matches (word coverage)
                    variant_words = set(variant.split())
                    file_words = set(normalized_file.split())
                    if variant_words:
                        word_coverage = len(variant_words.intersection(file_words)) / len(variant_words)
                        coverage_score = int(word_coverage * 100)
                    else:
                        coverage_score = 0
                    
                    best_variant_match = max(best_variant_match, coverage_score + variant_bonus)
                    break
            
            if match_found:
                # Calculate region priority score
                region_score = self.calculate_region_priority(filename)
                
                # Additional scoring based on name similarity
                # Prefer exact matches or shorter names (less extra text)
                normalized_search = search_variants[0]  # Use primary variant for length calc
                length_diff = len(normalized_file) - len(normalized_search)
                similarity_score = 100 - min(length_diff, 100)
                
                # Combine all scores
                total_score = region_score + similarity_score + best_variant_match
                
                # Track this as a candidate if it's not rejected
                if total_score > -1000:
                    all_candidates.append((filename, total_score))
                
                if total_score > best_score:
                    best_score = total_score
                    best_match = filepath
        
        # Sort candidates by score (descending)
        all_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return best_match, all_candidates
    
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
        self.settings = Settings()
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
            "Enter ROM names here, one per line...\n\n"
            "Example:\n"
            "Castlevania: Rondo of Blood\n"
            "Dragon's Curse (Wonder Boy III)\n"
            "Bonk's Adventure\n"
            "Alien Crush"
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
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setMinimumHeight(40)
        
        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setMinimumHeight(40)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.settings_btn)
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
        self.worker = ROMMatcherWorker(source_dir, target_dir, rom_names, self.settings)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            # Settings were saved, reload them
            self.settings.load_settings()
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved and will be used for the next processing.")
    
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
