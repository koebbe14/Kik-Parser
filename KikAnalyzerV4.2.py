import pandas as pd
import datetime
import os
import html
import csv
import urllib.request
import urllib.error
import cv2
import numpy as np
import ssl
import webbrowser
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict, OrderedDict
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QMenu,
    QMessageBox, QDialog, QCheckBox, QDialogButtonBox, QLineEdit, QLabel,
    QDateEdit, QToolBar, QGroupBox, QScrollArea, QFrame, QHeaderView,
    QStatusBar, QTextEdit, QListWidget, QGraphicsBlurEffect, QKeySequenceEdit,
    QShortcut, QStyledItemDelegate, QProgressDialog, QTableView, QStyle,
    QColorDialog, QTabWidget
)
from PyQt5.QtCore import (
    Qt,
    QDate,
    QUrl,
    QTimer,
    QThread,
    pyqtSignal,
    QAbstractTableModel,
    QModelIndex,
    QVariant,
    QSize,
    QRunnable,
    QThreadPool,
    QObject,
)
from PyQt5.QtGui import QBrush, QColor, QFont, QPixmap, QImage, QKeySequence, QTextDocument, QAbstractTextDocumentLayout, QPen
from PyQt5.Qt import QDesktopServices, QRectF
import sys
import urllib.parse
import shutil
import hashlib
import tempfile
from functools import lru_cache
import re
from PyQt5.QtWidgets import QInputDialog

# Set up logging (disabled by default)
# Get user's home directory for storing configuration and data files
USER_HOME = os.path.expanduser("~")
if not USER_HOME or not os.path.exists(USER_HOME):
    # Fallback to USERPROFILE on Windows if expanduser fails
    USER_HOME = os.environ.get('USERPROFILE', os.getcwd())

log_file = os.path.join(USER_HOME, 'kik_analyzer.log')
logging_enabled = False  # Logging is off by default

# Create logger but don't configure handlers yet
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Add a null handler to prevent "No handler found" warnings when logging is disabled
logger.addHandler(logging.NullHandler())

def enable_logging():
    """Enable logging to file."""
    global logging_enabled
    if not logging_enabled:
        # Remove null handler
        logger.handlers.clear()
        # Add file handler
        handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logging_enabled = True
        logger.info("Logging enabled.")

def disable_logging():
    """Disable logging to file."""
    global logging_enabled
    if logging_enabled:
        logger.handlers.clear()
        logger.addHandler(logging.NullHandler())
        logging_enabled = False

APP_VERSION = "4.2"  # Updated with delete keyword list feature
GITHUB_OWNER = "Koebbe14"
GITHUB_REPO  = "Kik-Parser"
GITHUB_LATEST_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES_PAGE = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases"

# Constants for configuration
BLUR_KERNEL_SIZE = (401, 401)
BLUR_SIGMA = 93
SEARCH_DEBOUNCE_MS = 600  # Increased from 300ms to reduce unnecessary refreshes while typing
DATE_DEBOUNCE_MS = 1000   # Longer delay for date changes since they're less frequent
THUMBNAIL_SIZE = (100, 100)
MAX_CACHE_SIZE = 200  # Increased from 50 for better performance with large datasets
PROGRESS_UPDATE_INTERVAL = 100  # Update progress dialog every N items


class ThemeManager:
    """Manages light and dark theme colors for the application."""
    
    LIGHT_THEME = {
        # Background colors
        'bg_main': '#f8f9fa',  # Very light gray (slightly warmer than pure white)
        'bg_widget': '#ffffff',  # Pure white for contrast
        'bg_alternate': '#e9ecef',  # Light gray for headers/alternates
        'bg_dialog': '#f8f9fa',  # Match main background
        'bg_table': '#ffffff',  # White for table
        'bg_table_alternate': '#f5f5f5',  # Unused, kept for compatibility
        'bg_table_hover': '#e7f3ff',  # Light blue tint for hover
        'bg_groupbox': '#ffffff',  # White
        'bg_legend': '#f1f3f5',  # Slightly darker for legend section
        
        # Text colors
        'text_primary': '#212529',  # Near black, high contrast
        'text_secondary': '#495057',  # Medium gray for secondary text
        'text_white': '#ffffff',  # Unused, kept for compatibility
        'text_black': '#000000',  # Unused, kept for compatibility
        
        # Border colors
        'border': '#dee2e6',  # Light gray border
        'cell_border': '#ff0000',  # Bold red for cell borders
        
        # Button colors
        'button_hover': '#e9ecef',  # Light gray hover
        'button_bg': '#ffffff',  # White buttons
        
        # Tag colors (High visibility, professional)
        'tag_csam': '#dc3545',  # Professional red (Bootstrap danger)
        'tag_evidence': '#fd7e14',  # Professional orange (Bootstrap warning)
        'tag_interest': '#ffc107',  # Professional yellow (Bootstrap warning)
        'tag_custom': '#d1ecf1',  # Light blue/cyan
        
        # Keyword colors
        'keyword_hit': '#fff3cd',  # Light yellow highlight
        'keyword_hit_alt': '#9fe780',  # Unused, kept for compatibility
        
        # Sender colors (Subtle differentiation)
        'sender1': '#f3f6f4',
        'sender2': '#9fc5e8',
        
        # Default row colors
        'row_default': '#ffffff',  # White
        'row_alternate': '#f8f9fa',  # Very light gray
    }
    
    DARK_THEME = {
        # Background colors
        'bg_main': '#2b2b2b',
        'bg_widget': '#3c3c3c',
        'bg_alternate': '#404040',
        'bg_dialog': '#2b2b2b',
        'bg_table': '#3c3c3c',
        'bg_table_alternate': '#404040',
        'bg_table_hover': '#4a4a4a',
        'bg_groupbox': '#3c3c3c',
        'bg_legend': '#404040',
        
        # Text colors
        'text_primary': '#e0e0e0',
        'text_secondary': '#d0d0d0',
        'text_white': '#ffffff',
        'text_black': '#000000',
        
        # Border colors
        'border': '#555555',
        'cell_border': '#ff0000',  # Bold red for cell borders
        
        # Button colors
        'button_hover': '#505050',
        'button_bg': '#3c3c3c',
        
        # Tag colors (adjusted for dark mode but still visible)
        'tag_csam': '#cc0000',
        'tag_evidence': '#cc6600',
        'tag_interest': '#cccc00',
        'tag_custom': '#4a6a4a',
        
        # Keyword colors
        'keyword_hit': '#6a6a4a',
        'keyword_hit_alt': '#5a8a4a',
        
        # Sender colors
        'sender1': '#4a4c4a',
        'sender2': '#4a5a6a',
        
        # Default row colors
        'row_default': '#3c3c3c',
        'row_alternate': '#404040',
    }
    
    def __init__(self, dark_mode=False):
        self.dark_mode = dark_mode
        self.colors = self.DARK_THEME if dark_mode else self.LIGHT_THEME
        # Custom colors override defaults
        self.custom_colors_light = {}
        self.custom_colors_dark = {}
    
    def get_color(self, key):
        """Get a color value by key, checking custom colors first."""
        # Check custom colors first
        if self.dark_mode:
            if key in self.custom_colors_dark:
                return self.custom_colors_dark[key]
        else:
            if key in self.custom_colors_light:
                return self.custom_colors_light[key]
        # Fall back to default theme colors
        return self.colors.get(key, '#000000')
    
    def set_custom_color(self, key, color, dark_mode=None):
        """Set a custom color for a specific key.
        
        Args:
            key: Color key (e.g., 'bg_main', 'text_primary')
            color: Color value as hex string (e.g., '#ff0000')
            dark_mode: If None, uses current dark_mode. If True/False, sets for that mode.
        """
        if dark_mode is None:
            dark_mode = self.dark_mode
        
        if dark_mode:
            self.custom_colors_dark[key] = color
        else:
            self.custom_colors_light[key] = color
    
    def reset_custom_colors(self, dark_mode=None):
        """Reset custom colors to defaults.
        
        Args:
            dark_mode: If None, resets both. If True/False, resets only that mode.
        """
        if dark_mode is None:
            self.custom_colors_light = {}
            self.custom_colors_dark = {}
        elif dark_mode:
            self.custom_colors_dark = {}
        else:
            self.custom_colors_light = {}
    
    def get_all_color_keys(self):
        """Return list of all color keys that can be customized."""
        return list(self.LIGHT_THEME.keys())
    
    def load_custom_colors(self, custom_colors_light=None, custom_colors_dark=None):
        """Load custom colors from dictionaries.
        
        Args:
            custom_colors_light: Dictionary of custom light mode colors
            custom_colors_dark: Dictionary of custom dark mode colors
        """
        if custom_colors_light is not None:
            self.custom_colors_light = custom_colors_light.copy()
        if custom_colors_dark is not None:
            self.custom_colors_dark = custom_colors_dark.copy()
    
    def get_custom_colors(self):
        """Get current custom colors as dictionaries."""
        return {
            'light': self.custom_colors_light.copy(),
            'dark': self.custom_colors_dark.copy()
        }
    
    def get_stylesheet(self):
        """Get the main application stylesheet."""
        if self.dark_mode:
            return """
                QMainWindow { background-color: %s; color: %s; }
                QWidget { background-color: %s; color: %s; }
                QPushButton { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px; 
                    border: 1px solid %s;
                }
                QPushButton:hover { background-color: %s; }
                QComboBox { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px; 
                    border: 1px solid %s;
                }
                QLineEdit { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px; 
                    border: 1px solid %s;
                }
                QGroupBox { 
                    background-color: %s;
                    border: 1px solid %s; 
                    border-radius: 5px; 
                    padding: 10px; 
                    color: %s;
                }
                QTableWidget, QTableView { 
                    background-color: %s; 
                    color: %s; 
                    gridline-color: %s;
                }
                QTableView::item:hover {
                    background-color: %s;
                }
                QHeaderView::section { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px;
                }
                QTextEdit { 
                    background-color: %s; 
                    color: %s; 
                    border: 1px solid %s;
                }
                QLabel { color: %s; }
                QStatusBar { background-color: %s; color: %s; }
            """ % (
                self.get_color('bg_main'), self.get_color('text_primary'),
                self.get_color('bg_widget'), self.get_color('text_primary'),
                self.get_color('button_bg'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('button_hover'),
                self.get_color('bg_widget'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('bg_widget'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('bg_groupbox'), self.get_color('border'), self.get_color('text_primary'),
                self.get_color('bg_table'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('bg_table_hover'),
                self.get_color('bg_alternate'), self.get_color('text_primary'),
                self.get_color('bg_widget'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('text_primary'),
                self.get_color('bg_main'), self.get_color('text_primary'),
            )
        else:
            return """
                QMainWindow { background-color: %s; color: %s; }
                QWidget { background-color: %s; color: %s; }
                QPushButton { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px; 
                    border: 1px solid %s;
                }
                QPushButton:hover { background-color: %s; }
                QComboBox { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px; 
                    border: 1px solid %s;
                }
                QLineEdit { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px; 
                    border: 1px solid %s;
                }
                QGroupBox { 
                    background-color: %s;
                    border: 1px solid %s; 
                    border-radius: 5px; 
                    padding: 10px; 
                    color: %s;
                }
                QTableWidget, QTableView { 
                    background-color: %s; 
                    color: %s; 
                    gridline-color: %s;
                }
                QTableView::item:hover {
                    background-color: %s;
                }
                QHeaderView::section { 
                    background-color: %s; 
                    color: %s; 
                    padding: 5px;
                }
                QTextEdit { 
                    background-color: %s; 
                    color: %s; 
                    border: 1px solid %s;
                }
                QLabel { color: %s; }
                QStatusBar { background-color: %s; color: %s; }
            """ % (
                self.get_color('bg_main'), self.get_color('text_primary'),
                self.get_color('bg_widget'), self.get_color('text_primary'),
                self.get_color('button_bg'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('button_hover'),
                self.get_color('bg_widget'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('bg_widget'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('bg_groupbox'), self.get_color('border'), self.get_color('text_primary'),
                self.get_color('bg_table'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('bg_table_hover'),
                self.get_color('bg_alternate'), self.get_color('text_primary'),
                self.get_color('bg_widget'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('text_primary'),
                self.get_color('bg_main'), self.get_color('text_primary'),
            )
    
    def get_dialog_stylesheet(self):
        """Get stylesheet for dialogs."""
        if self.dark_mode:
            return """
                QDialog { background-color: %s; color: %s; }
                QTableWidget { font-size: 14px; background-color: %s; color: %s; }
                QLabel { font-size: 14px; color: %s; }
                QPushButton { 
                    padding: 8px; 
                    font-size: 14px; 
                    min-width: 100px; 
                    min-height: 30px; 
                    background-color: %s;
                    color: %s;
                    border: 1px solid %s;
                }
                QPushButton:hover { background-color: %s; }
                QTextEdit { 
                    padding: 8px; 
                    font-size: 14px; 
                    background-color: %s;
                    color: %s;
                    border: 1px solid %s;
                }
                QDialogButtonBox QPushButton { 
                    font-size: 14px; 
                    padding: 8px; 
                    min-width: 100px; 
                    min-height: 30px; 
                    background-color: %s;
                    color: %s;
                    border: 1px solid %s;
                }
                QDialogButtonBox QPushButton:hover { background-color: %s; }
            """ % (
                self.get_color('bg_dialog'), self.get_color('text_primary'),
                self.get_color('bg_table'), self.get_color('text_primary'),
                self.get_color('text_primary'),
                self.get_color('button_bg'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('button_hover'),
                self.get_color('bg_widget'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('button_bg'), self.get_color('text_primary'), self.get_color('border'),
                self.get_color('button_hover'),
            )
        else:
            return """
                QDialog { background-color: %s; }
                QTableWidget { font-size: 14px; }
                QLabel { font-size: 14px; }
                QPushButton { padding: 8px; font-size: 14px; min-width: 100px; min-height: 30px; }
                QPushButton:hover { background-color: %s; }
                QTextEdit { padding: 8px; font-size: 14px; }
                QDialogButtonBox QPushButton { 
                    font-size: 14px; 
                    padding: 8px; 
                    min-width: 100px; 
                    min-height: 30px; 
                }
                QDialogButtonBox QPushButton:hover { background-color: %s; }
            """ % (
                self.get_color('bg_dialog'),
                self.get_color('button_hover'),
                self.get_color('button_hover'),
            )


class ColorSettingsDialog(QDialog):
    """Dialog for customizing application colors."""
    
    # Color key descriptions for user-friendly labels
    COLOR_DESCRIPTIONS = {
        # Background colors
        'bg_main': 'Main Background',
        'bg_widget': 'Widget Background',
        'bg_alternate': 'Alternate Background',
        'bg_dialog': 'Dialog Background',
        'bg_table': 'Table Background',
        'bg_table_hover': 'Table Hover',
        'bg_groupbox': 'Group Box Background',
        'bg_legend': 'Legend Background',
        # Text colors
        'text_primary': 'Primary Text',
        'text_secondary': 'Secondary Text',
        # Border colors
        'border': 'Border',
        'cell_border': 'Cell Border',
        # Button colors
        'button_hover': 'Button Hover',
        'button_bg': 'Button Background',
        # Tag colors
        'tag_csam': 'CSAM Tag',
        'tag_evidence': 'Evidence Tag',
        'tag_interest': 'Of Interest Tag',
        'tag_custom': 'Custom Tag',
        # Keyword colors
        'keyword_hit': 'Keyword Hit',
        # Sender colors
        'sender1': 'Sender 1',
        'sender2': 'Sender 2',
        # Row colors
        'row_default': 'Default Row',
        'row_alternate': 'Alternate Row',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Color Settings")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(800, 600)
        self.resize(850, 700)
        
        # Store pending changes (not applied until Apply is clicked)
        self.pending_light = {}
        self.pending_dark = {}
        
        # Store references to preview widgets for easy access
        self.preview_widgets = {}  # key: (key, dark_mode) -> (preview_label, color_label)
        
        # Initialize with current custom colors
        if parent and hasattr(parent, 'theme_manager'):
            custom_colors = parent.theme_manager.get_custom_colors()
            self.pending_light = custom_colors['light'].copy()
            self.pending_dark = custom_colors['dark'].copy()
        
        self.init_ui()
        
        # Apply theme stylesheet
        if parent and hasattr(parent, 'theme_manager'):
            self.setStyleSheet(parent.theme_manager.get_dialog_stylesheet())
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)  # More horizontal margin
        
        # Create tab widget for light/dark mode
        self.tabs = QTabWidget()
        
        # Light mode tab
        light_tab = self.create_color_tab(False)
        self.tabs.addTab(light_tab, "Light Mode")
        
        # Dark mode tab
        dark_tab = self.create_color_tab(True)
        self.tabs.addTab(dark_tab, "Dark Mode")
        
        layout.addWidget(self.tabs)
        
        # Update all previews after UI is fully set up
        QApplication.processEvents()
        self.update_all_previews()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset to Default")
        reset_button.setToolTip("Reset all colors in the current tab to default values")
        reset_button.clicked.connect(lambda: self.reset_current_tab(self.tabs.currentIndex()))
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        button_layout.addWidget(buttons)
        
        layout.addLayout(button_layout)
    
    def create_color_tab(self, dark_mode):
        """Create a tab with color settings for a specific mode."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Allow horizontal scroll if needed
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        # Get all color keys
        if self.parent and hasattr(self.parent, 'theme_manager'):
            color_keys = self.parent.theme_manager.get_all_color_keys()
        else:
            color_keys = list(ThemeManager.LIGHT_THEME.keys())
        
        # Group colors by category (only include colors that are used in GUI or HTML)
        categories = {
            'Background Colors': ['bg_main', 'bg_widget', 'bg_alternate', 'bg_dialog', 'bg_table', 
                                'bg_table_hover', 'bg_groupbox', 'bg_legend'],
            'Text Colors': ['text_primary', 'text_secondary'],
            'Border Colors': ['border', 'cell_border'],
            'Button Colors': ['button_hover', 'button_bg'],
            'Tag Colors': ['tag_csam', 'tag_evidence', 'tag_interest', 'tag_custom'],
            'Keyword Colors': ['keyword_hit'],
            'Sender Colors': ['sender1', 'sender2'],
            'Row Colors': ['row_default', 'row_alternate'],
        }
        
        # Create color rows grouped by category
        for category, keys in categories.items():
            group = QGroupBox(category)
            # Style group box to prevent title truncation
            group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            group_layout = QVBoxLayout()
            group_layout.setSpacing(5)
            group_layout.setContentsMargins(10, 20, 10, 10)  # Extra top margin for title
            
            for key in keys:
                if key not in color_keys:
                    continue
                
                row = QHBoxLayout()
                
                # Label
                label = QLabel(self.COLOR_DESCRIPTIONS.get(key, key))
                label.setMinimumWidth(180)
                label.setWordWrap(False)
                row.addWidget(label)
                
                # Color preview
                preview = QLabel()
                preview.setMinimumSize(50, 30)
                preview.setMaximumSize(50, 30)
                preview.setStyleSheet("border: 1px solid #000000;")
                row.addWidget(preview)
                
                # Current color label
                color_label = QLabel()
                color_label.setMinimumWidth(110)
                color_label.setFont(QFont("Courier", 9))  # Monospace font for hex codes
                row.addWidget(color_label)
                
                # Store references for easy access
                self.preview_widgets[(key, dark_mode)] = (preview, color_label)
                
                row.addStretch()
                
                # Change color button
                change_btn = QPushButton("Change Color")
                change_btn.clicked.connect(lambda checked, k=key, d=dark_mode: self.change_color(k, d))
                row.addWidget(change_btn)
                
                group_layout.addLayout(row)
            
            group.setLayout(group_layout)
            layout.addWidget(group)
        
        layout.addStretch()
        scroll.setWidget(widget)
        
        return scroll
    
    def update_all_previews(self):
        """Update all color previews in all tabs."""
        if self.parent and hasattr(self.parent, 'theme_manager'):
            color_keys = self.parent.theme_manager.get_all_color_keys()
        else:
            color_keys = list(ThemeManager.LIGHT_THEME.keys())
        
        for key in color_keys:
            # Update light mode preview
            if (key, False) in self.preview_widgets:
                self.update_color_preview(key, False)
            # Update dark mode preview
            if (key, True) in self.preview_widgets:
                self.update_color_preview(key, True)
    
    def update_color_preview(self, key, dark_mode):
        """Update the color preview and label for a specific key."""
        # Get current color - use actual theme manager to get the effective color
        if self.parent and hasattr(self.parent, 'theme_manager'):
            # Create a temporary theme manager to get the effective color
            temp_theme = ThemeManager(dark_mode)
            temp_theme.load_custom_colors(
                custom_colors_light=self.pending_light if not dark_mode else {},
                custom_colors_dark=self.pending_dark if dark_mode else {}
            )
            color = temp_theme.get_color(key)
        else:
            # Fallback to defaults
            if dark_mode:
                color = ThemeManager.DARK_THEME.get(key, '#000000')
            else:
                color = ThemeManager.LIGHT_THEME.get(key, '#000000')
        
        # Update preview using stored reference
        widget_key = (key, dark_mode)
        if widget_key in self.preview_widgets:
            preview, color_label = self.preview_widgets[widget_key]
            preview.setStyleSheet(f"background-color: {color}; border: 1px solid #000000;")
            color_label.setText(color)
    
    def change_color(self, key, dark_mode):
        """Open color dialog to change a color."""
        # Get current color
        if dark_mode:
            pending = self.pending_dark
            default_theme = ThemeManager.DARK_THEME
        else:
            pending = self.pending_light
            default_theme = ThemeManager.LIGHT_THEME
        
        current_color = pending.get(key, default_theme.get(key, '#000000'))
        qcolor = QColor(current_color)
        
        # Open color dialog
        color = QColorDialog.getColor(qcolor, self, f"Select Color for {self.COLOR_DESCRIPTIONS.get(key, key)}")
        
        if color.isValid():
            # Store in pending changes
            if dark_mode:
                self.pending_dark[key] = color.name()
            else:
                self.pending_light[key] = color.name()
            
            # Update preview
            self.update_color_preview(key, dark_mode)
    
    def reset_current_tab(self, tab_index):
        """Reset colors in the current tab to defaults."""
        dark_mode = (tab_index == 1)  # 0 = light, 1 = dark
        
        if dark_mode:
            self.pending_dark = {}
        else:
            self.pending_light = {}
        
        # Update all previews in current tab
        if self.parent and hasattr(self.parent, 'theme_manager'):
            color_keys = self.parent.theme_manager.get_all_color_keys()
        else:
            color_keys = list(ThemeManager.LIGHT_THEME.keys())
        
        for key in color_keys:
            if (key, dark_mode) in self.preview_widgets:
                self.update_color_preview(key, dark_mode)
    
    def apply_changes(self):
        """Apply pending color changes to theme manager and save config."""
        if not self.parent or not hasattr(self.parent, 'theme_manager'):
            self.accept()
            return
        
        # Apply custom colors to theme manager
        self.parent.theme_manager.load_custom_colors(
            custom_colors_light=self.pending_light,
            custom_colors_dark=self.pending_dark
        )
        
        # Save to config
        self.parent.save_config()
        
        # Refresh UI
        self.parent.refresh_theme()
        
        self.accept()


def center_and_autosize_dialog(dialog, parent=None, width_ratio=0.5, height_ratio=0.5, min_width=500, min_height=350, max_width=1200, max_height=900):
    """
    Helper function to center and autosize a dialog window based on screen size.
    
    Args:
        dialog: The dialog widget to center and resize
        parent: Optional parent widget (used to determine which screen)
        width_ratio: Percentage of screen width to use (default 0.5 = 50%)
        height_ratio: Percentage of screen height to use (default 0.5 = 50%)
        min_width: Minimum dialog width (default 500)
        min_height: Minimum dialog height (default 350)
        max_width: Maximum dialog width (default 1200)
        max_height: Maximum dialog height (default 900)
    """
    # Get screen geometry - improved detection for multi-monitor setups
    screen = None
    if parent:
        try:
            # Try to get the parent's screen directly (more reliable than screenAt)
            parent_screen = parent.screen()
            if parent_screen:
                screen = parent_screen
            else:
                # Fallback: try to detect screen from parent geometry
                parent_geo = parent.geometry()
                if parent_geo.isValid() and parent_geo.width() > 0 and parent_geo.height() > 0:
                    parent_center = parent_geo.center()
                    screen = QApplication.screenAt(parent_center)
        except Exception:
            pass
    
    # Fallback to primary screen if parent screen detection failed
    if not screen:
        screen = QApplication.primaryScreen()
    
    # Get available screen geometry (excludes taskbar, etc.)
    screen_geo = screen.availableGeometry()
    
    # Get device pixel ratio for DPI-aware sizing (helps with high-DPI displays)
    try:
        dpr = screen.devicePixelRatio()
        # Adjust minimum sizes for better readability on high-DPI displays
        # But don't scale too aggressively - use a moderate adjustment
        dpi_scale = min(dpr, 1.5)  # Cap at 1.5x to avoid excessive scaling
    except:
        dpi_scale = 1.0
    
    # Adjust minimum sizes for better readability on smaller screens (laptops)
    # Increase minimums significantly for better laptop visibility
    # For laptops (screens < 1920px wide), use larger minimums
    if screen_geo.width() < 1920:
        adjusted_min_width = max(min_width, int(700 * dpi_scale))
        adjusted_min_height = max(min_height, int(550 * dpi_scale))
    else:
        adjusted_min_width = min_width
        adjusted_min_height = min_height
    
    # Log screen information for debugging (only if logging is enabled)
    try:
        if logging_enabled:
            logger.info(f"Dialog autosizing - Screen: {screen_geo.width()}x{screen_geo.height()}, "
                       f"Screen position: ({screen_geo.x()}, {screen_geo.y()}), "
                       f"DPI scale: {dpi_scale}, "
                       f"Ratios: {width_ratio}x{height_ratio}, "
                       f"Constraints: {adjusted_min_width}-{max_width} x {adjusted_min_height}-{max_height}")
    except:
        pass
    
    # Calculate dialog size as percentage of screen with constraints
    # Use adjusted minimums for better readability on smaller screens
    dialog_width = max(adjusted_min_width, min(int(screen_geo.width() * width_ratio), max_width))
    dialog_height = max(adjusted_min_height, min(int(screen_geo.height() * height_ratio), max_height))
    
    # Resize dialog
    dialog.resize(dialog_width, dialog_height)
    
    # Center the dialog horizontally and vertically on the screen
    # Use screen geometry coordinates (screen_geo.x() and screen_geo.y() account for multi-monitor setups)
    # Calculate center position relative to the available screen area
    center_x = screen_geo.x() + (screen_geo.width() - dialog_width) // 2
    center_y = screen_geo.y() + (screen_geo.height() - dialog_height) // 2
    
    # Ensure the dialog is positioned correctly
    dialog.move(center_x, center_y)
    
    # Set minimum size but allow resizing (removed maximum size restriction)
    # This makes all dialogs resizable for better usability on different screen sizes
    dialog.setMinimumSize(dialog_width, dialog_height)
    # Don't set maximum size - allow user to resize as needed
    
    # Log final dialog size and position for debugging
    try:
        if logging_enabled:
            logger.info(f"Dialog positioned - Size: {dialog_width}x{dialog_height}, "
                       f"Position: ({dialog.x()}, {dialog.y()}), "
                       f"Screen: {screen.name() if hasattr(screen, 'name') else 'unknown'}")
    except:
        pass


class ExportOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Options")
        # Remove question mark help button
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)


        # ----- Export Scope -----
        scope_group = QGroupBox("Export Scope (Select One)")
        # Style group box to prevent title truncation
        scope_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scope_layout = QVBoxLayout()
        scope_layout.setContentsMargins(10, 20, 10, 10)  # Extra top margin for title
        self.options = {
            'tagged_messages': QCheckBox("Tagged Messages", self),
            'selected_conversation': QCheckBox("Selected Conversation", self),
            'all_conversations': QCheckBox("All Conversations", self)
        }
        for checkbox in self.options.values():
            checkbox.setToolTip("Select the scope of messages to export: tagged messages, selected conversation, or all conversations")
            scope_layout.addWidget(checkbox)
        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)

        # ----- Sanitize / Blur options -----
        sanitize_group = QGroupBox("Sanitize Export")
        # Style group box to prevent title truncation
        sanitize_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
        """)
        sanitize_layout = QVBoxLayout()
        sanitize_layout.setContentsMargins(10, 20, 10, 10)  # Extra top margin for title
        self.blur_csam = QCheckBox("Blur Only Media Tagged as CSAM", self)
        self.blur_csam.setToolTip("Generate and include blurred thumbnails for media tagged as CSAM in the HTML export. This helps protect sensitive content when sharing reports.")
        sanitize_layout.addWidget(self.blur_csam)

        self.blur_all_media = QCheckBox("Blur All Media", self)
        self.blur_all_media.setToolTip("Generate and include blurred thumbnails for all media files in the HTML export. Useful for protecting all sensitive content.")
        sanitize_layout.addWidget(self.blur_all_media)

        sanitize_group.setLayout(sanitize_layout)
        layout.addWidget(sanitize_group)

        # ----- Export format -----
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        self.export_format = QComboBox()
        self.export_format.addItems(["HTML", "CSV"])
        self.export_format.setToolTip("Choose the output file format: HTML (includes embedded media and styling) or CSV (structured data for spreadsheet applications)")
        format_layout.addWidget(self.export_format)
        layout.addLayout(format_layout)

        # ----- Sort by -----
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Sort By:"))
        self.sort_by = QComboBox()
        self.sort_by.addItems(["User/Conversation (Default)", "Timestamp"])
        self.sort_by.setToolTip("Sort exported messages by conversation (groups messages by conversation) or timestamp (chronological order across all conversations)")
        sort_layout.addWidget(self.sort_by)
        layout.addLayout(sort_layout)

        # ----- Fields to Include (with scroll area) -----
        fields_group = QGroupBox("Fields to Include")
        # Style group box to prevent title truncation
        fields_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
        """)
        fields_group_layout = QVBoxLayout()
        fields_group_layout.setContentsMargins(10, 20, 10, 10)  # Extra top margin for title

        self.select_all = QCheckBox("Select All Fields", self)
        self.select_all.setChecked(True)
        self.select_all.setToolTip("Toggle selection of all export fields on or off. Uncheck to customize which fields are included in the export.")
        self.select_all.stateChanged.connect(self.toggle_fields)
        fields_group_layout.addWidget(self.select_all)

        # Scroll area just for the list of field checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # <<< make it a bit taller and always show vertical scrollbar >>>
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setMinimumHeight(240)
        scroll_area.setMaximumHeight(300)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(4)
        scroll_layout.setContentsMargins(2, 2, 2, 2)

        # Move source / line_number up a bit in the list
        self.fields = {
            'conversation': QCheckBox("Conversation", self),
            'msg_id': QCheckBox("Message ID", self),
            'sender': QCheckBox("Sender", self),
            'receiver': QCheckBox("Receiver", self),
            'message': QCheckBox("Message Content", self),
            'timestamp': QCheckBox("Timestamp", self),
            'content_id': QCheckBox("Content ID / Media", self),
            'ip': QCheckBox("IP Address", self),
            'port': QCheckBox("Port", self),
            'tags': QCheckBox("Tags", self),
            'source': QCheckBox("Source", self),
            'line_number': QCheckBox("Line Number", self),
            'notes': QCheckBox("Notes", self),
        }

        for checkbox in self.fields.values():
            checkbox.setChecked(True)
            scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_widget)

        fields_group_layout.addWidget(scroll_area)
        fields_group.setLayout(fields_group_layout)
        layout.addWidget(fields_group)

        # ----- Buttons -----
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # --- Auto-size dialog to screen height (from V3.18) ---
        screen = QApplication.primaryScreen()
        avail_geom = screen.availableGeometry()
        self.resize(700, int(avail_geom.height() * 0.9))        # 90% of screen height
        self.setMinimumSize(700, int(avail_geom.height() * 0.75)) # big minimum so no overlap issues
        # ---------------------------------------------------------

    # ----- Helper methods -----
    def toggle_fields(self, state):
        for checkbox in self.fields.values():
            checkbox.setChecked(state == Qt.Checked)

    def get_selected_options(self):
        return [opt for opt, checkbox in self.options.items() if checkbox.isChecked()]

    def get_selected_fields(self):
        return [field for field, checkbox in self.fields.items() if checkbox.isChecked()]

    def get_sort_by(self):
        return self.sort_by.currentText()

    def get_export_format(self):
        return self.export_format.currentText()

    def blur_csam_media(self):
        return self.blur_csam.isChecked()

    def blur_all_media_export(self):
        return self.blur_all_media.isChecked()



class BaseMessagesDialog(QDialog):
    """Shared UI scaffolding for dialogs that list messages in a table."""

    def __init__(self, title, headers, sort_options, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(title)
        # Remove question mark help button
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sort By:")
        sort_layout.addWidget(sort_label)
        self.sort_by = QComboBox()
        self.sort_by.addItems(sort_options)
        sort_layout.addWidget(self.sort_by)
        sort_layout.addStretch()
        layout.addLayout(sort_layout)

        self.table = self._create_table(headers)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        copy_button = QPushButton("Copy Selected")
        copy_button.setToolTip("Copy the selected message's details to the clipboard for pasting into other applications")
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        button_layout.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        button_layout.addWidget(buttons)
        layout.addLayout(button_layout)

        self.sort_by.currentIndexChanged.connect(self.populate_table)
        self.configure_table()

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setFont(QFont("Courier New", 11))
        table.setWordWrap(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QTableWidget.SingleSelection)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(600)
        return table

    def configure_table(self):
        """Allow subclasses to tweak table sizing/behavior."""
        pass

    def make_item(self, text, bg_color, tooltip="", user_role=None):
        # Replace NaN values and "nan" strings with empty string to prevent "nan" from displaying
        if pd.isna(text):
            text = ''
        else:
            text_str = str(text).strip()
            if text_str.lower() in ('nan', 'none', ''):
                text = ''
            else:
                text = text_str
        item = QTableWidgetItem(str(text))
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        item.setBackground(QBrush(QColor(bg_color)))
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if tooltip:
            item.setToolTip(tooltip)
        if user_role is not None:
            item.setData(Qt.UserRole, user_role)
        return item

    def copy_to_clipboard(self):
        selected = self.table.selectedItems()
        if not selected:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Info")
            msg.setText("No message selected.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        
        # Get unique rows from selected items
        selected_rows = sorted(set(item.row() for item in selected))
        
        # Build text for all selected rows
        lines = []
        for row in selected_rows:
            row_text = "\t".join(
                self.table.item(row, col).text() if self.table.item(row, col) else ""
                for col in range(self.table.columnCount())
            )
            lines.append(row_text)
        
        # Copy all selected rows to clipboard, separated by newlines
        text = "\n".join(lines)
        QApplication.clipboard().setText(text)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        if len(selected_rows) == 1:
            msg.setText("Message copied to clipboard.")
        else:
            msg.setText(f"{len(selected_rows)} messages copied to clipboard.")
        msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        logger.info(f"Copied {len(selected_rows)} selected message(s) to clipboard")


class TaggedMessagesDialog(BaseMessagesDialog):
    HEADERS = [
        "Date", "Time", "Sender", "Receiver", "Message", "Tags",
        "Media", "IP", "Port", "Source", "Line Number"
    ]
    SORT_OPTIONS = ["Timestamp (Default)", "User/Conversation"]

    def __init__(self, tagged_messages, parent=None):
        self.tagged_messages = tagged_messages
        super().__init__("Tagged Messages", self.HEADERS, self.SORT_OPTIONS, parent)
        # Bigger, resizable window instead of fixed size (from V3.18)
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.sort_by.setToolTip("Sort tagged messages by conversation (groups by conversation) or timestamp (chronological order)")
        self.table.setMinimumWidth(1000)
        # Enable multiple selection for TaggedMessagesDialog
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        # Apply theme stylesheet
        if self.parent and hasattr(self.parent, 'theme_manager'):
            self.setStyleSheet(self.parent.theme_manager.get_dialog_stylesheet())
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f4f4f9; }
                QTableWidget { font-size: 14px; }
                QLabel { font-size: 14px; }
                QPushButton { padding: 8px; font-size: 14px; min-width: 100px; min-height: 30px; }
                QPushButton:hover { background-color: #e0e0e0; }
            """)

        logger.info("TaggedMessagesDialog initialized")
        self.populate_table()
        # Center and autosize dialog (handled by BaseMessagesDialog)

    def configure_table(self):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 90)   # Date
        self.table.setColumnWidth(1, 80)   # Time
        self.table.setColumnWidth(2, 150)  # Sender
        self.table.setColumnWidth(3, 150)  # Receiver
        self.table.setColumnWidth(5, 150)  # Tags
        self.table.setColumnWidth(6, 150)  # Media
        self.table.setColumnWidth(7, 120)  # IP
        self.table.setColumnWidth(8, 80)   # Port
        self.table.setColumnWidth(9, 200)  # Source
        self.table.setColumnWidth(10, 100) # Line Number

    def populate_table(self):
        logger.info(f"Populating tagged messages table with {len(self.tagged_messages)} messages")
        self.table.setRowCount(0)
        messages = self.tagged_messages.copy()

        # Get the current sort option
        sort_option = self.sort_by.currentText()
        logger.info(f"Sorting tagged messages by: {sort_option}")
        
        if sort_option == "User/Conversation":
            # Sort by conversation ID first, then by timestamp within each conversation
            # conv_id is a tuple like (user1, user2) or (group_id,), so we need to handle it properly
            def sort_key(x):
                msg, conv_id = x
                # Create a sortable key from the conversation tuple
                # For tuples like (user1, user2), sort by the sorted tuple to ensure consistent ordering
                if isinstance(conv_id, tuple):
                    conv_key = tuple(sorted(conv_id)) if len(conv_id) > 1 else conv_id
                else:
                    conv_key = (conv_id,) if conv_id else ()
                # Get timestamp, handling NaN values
                timestamp = msg['sent_at'] if pd.notna(msg['sent_at']) else pd.Timestamp.min
                return (conv_key, timestamp)
            
            messages.sort(key=sort_key)
            logger.info(f"Sorted {len(messages)} messages by conversation")
        else:
            # Sort by timestamp (default)
            messages.sort(key=lambda x: x[0]['sent_at'] if pd.notna(x[0]['sent_at']) else pd.Timestamp.min)
            logger.info(f"Sorted {len(messages)} messages by timestamp")

        for _, (msg, conv_id) in enumerate(messages):
            row = self.table.rowCount()
            self.table.insertRow(row)
            # Use theme-aware default color
            if self.parent and hasattr(self.parent, 'theme_manager'):
                default_color = self.parent.theme_manager.get_color('tag_custom')
            else:
                default_color = '#e0ffe0'
            if self.parent:
                bg_color = self.parent.compute_row_color(
                    msg,
                    conv_id,
                    row_index=row,
                    enable_keyword=False,
                    enable_sender_colors=False,
                    alternate_colors=False,
                    default_color=default_color,
                    keyword_color=default_color
                )
            else:
                bg_color = default_color
            self.table.setItem(row, 0, self.make_item(msg['sent_at'].strftime('%Y-%m-%d'), bg_color))
            self.table.setItem(row, 1, self.make_item(msg['sent_at'].strftime('%H:%M:%S'), bg_color))
            self.table.setItem(row, 2, self.make_item(msg['sender'], bg_color))
            self.table.setItem(row, 3, self.make_item(msg['receiver'], bg_color))
            self.table.setItem(row, 4, self.make_item(msg['message'], bg_color))
            self.table.setItem(row, 5, self.make_item(', '.join(sorted(msg['tags'])), bg_color))

            # Media
            content_id = msg.get('content_id', '')
            content_path = self.parent.get_media_path(content_id) if content_id and self.parent else ''
            if content_path and os.path.exists(content_path):
                content_path = content_path.replace('\\', '/')
                ext = os.path.splitext(content_path)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.ogg']:
                    thumb_path = content_path if ext in ['.jpg', '.jpeg', '.png', '.gif'] else content_path + '_thumb.jpg'
                    if not os.path.exists(thumb_path) and ext in ['.mp4', '.webm', '.ogg']:
                        cap = None
                        try:
                            cap = cv2.VideoCapture(content_path)
                            if cap.isOpened():
                                ret, frame = cap.read()
                                if ret:
                                    cv2.imwrite(thumb_path, frame)
                        except Exception as e:
                            logger.error(f"Thumbnail generation failed: {e}")
                        finally:
                            if cap is not None:
                                cap.release()
                    if os.path.exists(thumb_path):
                        set_media_thumbnail_with_tag(self.table, row, 6, content_path, thumb_path)
                    else:
                        self.table.setItem(row, 6, self.make_item(f"(no preview): {content_id}", bg_color, "No thumbnail available"))
                else:
                    thumb = ClickableThumbnail(content_path)
                    thumb.setText("File: " + content_id)
                    thumb.setAlignment(Qt.AlignCenter)
                    thumb.clicked.connect(self.parent.open_media_file)
                    thumb.setStyleSheet(f"background-color: {bg_color};")
                    thumb.setToolTip(f"Media file: {os.path.basename(content_path)}\nDouble-click to open in default application")
                    self.table.setCellWidget(row, 6, thumb)
            else:
                self.table.setItem(row, 6, self.make_item(content_id or " ", bg_color, "No Media"))

            self.table.setItem(row, 7, self.make_item(msg['ip'], bg_color))
            self.table.setItem(row, 8, self.make_item(msg.get('port', ''), bg_color))

            # Source — pretty label + full path tooltip
            full_source = msg.get('source', 'Unknown')
            if 'content/text-msg-data' in full_source:
                pretty = ' CSV: ' + os.path.basename(full_source)
            elif 'logs/' in full_source:
                pretty = ' LOG: ' + os.path.basename(full_source)
            else:
                pretty = os.path.basename(full_source) or 'Unknown'
            source_item = self.make_item(pretty, bg_color, full_source)
            self.table.setItem(row, 9, source_item)

            # Line Number
            self.table.setItem(row, 10, self.make_item(msg.get('line_number', ''), bg_color))

        self.table.resizeRowsToContents()
        logger.info("Tagged messages table populated")


        
class ClickableThumbnail(QLabel):
    clicked = pyqtSignal(str)  # Emit the media path

    def __init__(self, media_path, parent=None):
        super().__init__(parent)
        self.media_path = media_path
        self.setMouseTracking(True)  # Enable hover events for tooltips
        self.local_blurred = False
        self.main_window = None
        for w in QApplication.topLevelWidgets():
            if isinstance(w, KikAnalyzerGUI):
                self.main_window = w
                break
        logger.info(f"Initialized ClickableThumbnail for {media_path}")

    def mousePressEvent(self, event):
        self.clearFocus()  # Clear focus always for hover consistency
        if event.button() == Qt.LeftButton and self.media_path:
            self.clicked.emit(self.media_path)
            logger.info(f"Left-clicked thumbnail: {self.media_path}")
            event.accept()
        else:
            if event.button() == Qt.RightButton:
                logger.info(f"Right-click detected on thumbnail: {self.media_path} - ignored for opening")
            event.accept()  # Accept to prevent propagation

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        action_text = "Unblur Media" if self.local_blurred else "Blur Media"
        blur_action = menu.addAction(action_text)
        action = menu.exec(event.globalPos())
        if action == blur_action:
            self.toggle_blur()

    def toggle_blur(self):
        self.local_blurred = not self.local_blurred
        self.update_effect()
        logger.info(f"Toggled local blur for {self.media_path} to {self.local_blurred}")

    def update_effect(self):
        blur_active = self.local_blurred or (self.main_window and self.main_window.blur_all)
        effect = QGraphicsBlurEffect() if blur_active else None
        if effect:
            effect.setBlurRadius(10)  # Adjust radius as needed for blur strength
        self.setGraphicsEffect(effect)
            
def set_media_thumbnail_with_tag(table, row, col, content_path, thumb_path):
    ext = os.path.splitext(content_path)[1].lower()
    is_video = ext in ['.mp4', '.webm', '.ogg']
    is_image = ext in ['.jpg', '.jpeg', '.png', '.gif']

    if is_video or is_image:
        pixmap = QPixmap(thumb_path).scaled(THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)

        thumb_label = ClickableThumbnail(content_path)
        thumb_label.setPixmap(pixmap)
        thumb_label.setAlignment(Qt.AlignCenter)
        thumb_label.clicked.connect(lambda path=content_path: QDesktopServices.openUrl(QUrl.fromLocalFile(path)))
        media_type = "Video" if is_video else "Image"
        thumb_label.setToolTip(f"{media_type}: {os.path.basename(content_path)}\nDouble-click to open in default application")
        logger.info(f"Set tooltip for {content_path}: {media_type}: {os.path.basename(content_path)}")
        thumb_label.update_effect()  # Apply initial blur state if any

        tag_label = QLabel("(VID)" if is_video else "(IMG)")
        tag_label.setAlignment(Qt.AlignCenter)
        tag_label.setStyleSheet("color: gray; font-size: 9pt;")

        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(thumb_label)
        layout.addWidget(tag_label)

        table.setCellWidget(row, col, container)
    
class KeywordHitsDialog(BaseMessagesDialog):
    HEADERS = ["Date", "Time", "Sender", "Receiver", "Message", "Tags", "Media", "IP", "Port", "Source", "Line Number"]
    SORT_OPTIONS = ["Timestamp (Default)", "User/Conversation"]

    def __init__(self, keyword_hits, parent=None):
        self.keyword_hits = keyword_hits
        super().__init__("Keyword Hits", self.HEADERS, self.SORT_OPTIONS, parent)
        self.setGeometry(100, 100, 1200, 800)
        self.sort_by.setToolTip("Sort keyword hits by conversation (groups by conversation) or timestamp (chronological order)")
        self.table.setMinimumWidth(1000)
        # Enable multiple selection for KeywordHitsDialog
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        # Apply theme stylesheet
        if self.parent and hasattr(self.parent, 'theme_manager'):
            self.setStyleSheet(self.parent.theme_manager.get_dialog_stylesheet())
        self.populate_table()

    def configure_table(self):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(5, 150)
        self.table.setColumnWidth(6, 150)

    def populate_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        messages = self.keyword_hits.copy()

        # Get the current sort option
        sort_option = self.sort_by.currentText()
        logger.info(f"Sorting keyword hits by: {sort_option}")
        
        # Sort
        if sort_option == "User/Conversation":
            # Sort by conversation ID first, then by timestamp within each conversation
            messages.sort(key=lambda x: (str(x[1]) if x[1] else '', x[0]['sent_at'] if pd.notna(x[0]['sent_at']) else pd.Timestamp.min))
        else:
            # Sort by timestamp (default)
            messages.sort(key=lambda x: x[0]['sent_at'] if pd.notna(x[0]['sent_at']) else pd.Timestamp.min)

        for _, (msg, conv_id) in enumerate(messages):
            row = self.table.rowCount()
            self.table.insertRow(row)
            # Use theme-aware default color
            if self.parent and hasattr(self.parent, 'theme_manager'):
                default_color = self.parent.theme_manager.get_color('keyword_hit')
            else:
                default_color = '#ffffe0'
            if self.parent:
                bg_color = self.parent.compute_row_color(
                    msg,
                    conv_id,
                    row_index=row,
                    enable_keyword=False,
                    enable_sender_colors=False,
                    alternate_colors=False,
                    default_color=default_color,
                    keyword_color=default_color
                )
            else:
                bg_color = default_color

            self.table.setItem(row, 0, self.make_item(msg['sent_at'].strftime('%Y-%m-%d'), bg_color))
            self.table.setItem(row, 1, self.make_item(msg['sent_at'].strftime('%H:%M:%S'), bg_color))
            self.table.setItem(row, 2, self.make_item(msg['sender'], bg_color))
            self.table.setItem(row, 3, self.make_item(msg['receiver'], bg_color))
            self.table.setItem(row, 4, self.make_item(msg['message'], bg_color, user_role=(msg['msg_id'], conv_id)))
            self.table.setItem(row, 5, self.make_item(', '.join(sorted(msg['tags'])), bg_color))
            content_id = msg.get('content_id', '')
            self.table.setItem(row, 6, self.make_item(content_id, bg_color))
            self.table.setItem(row, 7, self.make_item(msg['ip'], bg_color))
            self.table.setItem(row, 8, self.make_item(msg.get('port', ''), bg_color))
            source_value = msg.get('source', 'Unknown')
            self.table.setItem(row, 9, self.make_item(source_value, bg_color, tooltip=str(source_value)))
            line_number = msg.get('line_number', '')
            self.table.setItem(row, 10, self.make_item(line_number, bg_color))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.blockSignals(False)


    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if item and item.column() == 4:  # Message column
            selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
            if selected_rows:
                menu = QMenu(self)
                edit_tags_action = menu.addAction("Tag Message")
                action = menu.exec(self.table.mapToGlobal(position))
                if action == edit_tags_action:
                    # Get current tags from first selected (for multi, we'll apply changes to all)
                    first_row = selected_rows[0]
                    msg_id = self.table.item(first_row, 4).data(Qt.UserRole)[0]
                    current_tags = set()
                    for conv_id, messages in self.parent.conversations.items():
                        for msg in messages:
                            if msg['msg_id'] == msg_id:
                                current_tags = msg['tags'].copy()
                                break
                    dialog = MessageTagsDialog(self.parent.available_tags, current_tags, self)
                    if dialog.exec() == QDialog.Accepted:
                        new_tags = dialog.get_selected_tags()
                        self.parent.available_tags.update(new_tags)  # Add any custom to global
                        for row in selected_rows:
                            msg_id = self.table.item(row, 4).data(Qt.UserRole)[0]
                            for conv_id, messages in self.parent.conversations.items():
                                for msg in messages:
                                    if msg['msg_id'] == msg_id:
                                        msg['tags'] = new_tags.copy()
                                        self.table.item(row, 5).setText(', '.join(sorted(msg['tags'])))
                                        default_color = '#ffffe0'
                                        if self.parent:
                                            bg_color = self.parent.compute_row_color(
                                                msg,
                                                conv_id,
                                                row_index=row,
                                                enable_keyword=False,
                                                enable_sender_colors=False,
                                                alternate_colors=False,
                                                default_color=default_color,
                                                keyword_color=default_color
                                            )
                                        else:
                                            bg_color = default_color
                                        for col in range(11):
                                            cell_item = self.table.item(row, col)
                                            if cell_item:
                                                cell_item.setBackground(QBrush(QColor(bg_color)))
                                        break
                        self.parent.save_config()  # Update available_tags

class MessageTagsDialog(QDialog):
    def __init__(self, available_tags, current_tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Tags for Message")
        # Remove question mark help button
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(self)
        
        self.tag_checkboxes = {}
        for tag in sorted(available_tags):
            cb = QCheckBox(tag)
            cb.setChecked(tag in current_tags)
            self.tag_checkboxes[tag] = cb
            layout.addWidget(cb)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Resizable dialog (from V3.18 style, but made resizable)
        self.setMinimumSize(300, 400)
        self.resize(300, 400)
    
    def get_selected_tags(self):
        return {tag for tag, cb in self.tag_checkboxes.items() if cb.isChecked()}

class ManageTagsDialog(QDialog):
    def __init__(self, available_tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Available Tags")
        # Remove question mark help button
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(self)
        self.tag_list = QListWidget()
        for tag in sorted(available_tags):
            self.tag_list.addItem(tag)
        layout.addWidget(self.tag_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_tag)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_tag)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_tag)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Resizable dialog (from V3.18 style, but made resizable)
        self.setMinimumSize(300, 300)
        self.resize(300, 300)
    
    def add_tag(self):
        text, ok = QInputDialog.getText(self, "Add Tag", "Enter new tag label:")
        if ok and text.strip():
            text = text.strip()
            # Validate tag name
            if len(text) > 50:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Invalid Tag")
                msg.setText("Tag name too long (max 50 characters)")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return
            if not re.match(r'^[a-zA-Z0-9_\s-]+$', text):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Invalid Tag")
                msg.setText("Tag name contains invalid characters. Use only letters, numbers, spaces, underscores, and hyphens.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return
            if text not in [self.tag_list.item(i).text() for i in range(self.tag_list.count())]:
                self.tag_list.addItem(text)
    
    def edit_tag(self):
        item = self.tag_list.currentItem()
        if item:
            text, ok = QInputDialog.getText(self, "Edit Tag", "Edit tag label:", text=item.text())
            if ok and text.strip():
                text = text.strip()
                # Validate tag name
                if len(text) > 50:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Invalid Tag")
                    msg.setText("Tag name too long (max 50 characters)")
                    msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec()
                    return
                if not re.match(r'^[a-zA-Z0-9_\s-]+$', text):
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Invalid Tag")
                    msg.setText("Tag name contains invalid characters. Use only letters, numbers, spaces, underscores, and hyphens.")
                    msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec()
                    return
                item.setText(text)
    
    def delete_tag(self):
        item = self.tag_list.currentItem()
        if item:
            row = self.tag_list.row(item)
            self.tag_list.takeItem(row)
    
    def get_available_tags(self):
        return [self.tag_list.item(i).text() for i in range(self.tag_list.count())]
        
class ManageHotkeysDialog(QDialog):
    def __init__(self, available_tags, hotkeys, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Hotkeys")
        # Remove question mark help button
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(self)
        
        logger.info(f"Hotkeys in ManageHotkeysDialog: {hotkeys}")  # Debugging log
        self.hotkey_edits = {}
        # Add fields for each tag
        for tag in sorted(available_tags):
            hlayout = QHBoxLayout()
            hlayout.addWidget(QLabel(tag))
            edit = QKeySequenceEdit(QKeySequence(hotkeys.get(tag, '')))
            hlayout.addWidget(edit)
            self.hotkey_edits[tag] = edit
            layout.addLayout(hlayout)
        
        # Add single field for "Mark Reviewed"
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Mark Reviewed"))
        edit = QKeySequenceEdit(QKeySequence(hotkeys.get('Reviewed', '')))
        hlayout.addWidget(edit)
        self.hotkey_edits['Reviewed'] = edit
        layout.addLayout(hlayout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Resizable dialog (from V3.18 style, but made resizable)
        self.setMinimumSize(300, 400)
        self.resize(300, 400)

    def get_hotkeys(self):
        """Return a dictionary of tags and their corresponding hotkey sequences."""
        return {tag: edit.keySequence().toString() for tag, edit in self.hotkey_edits.items() if edit.keySequence().toString()}

class KeywordEditorDialog(QDialog):
    def __init__(self, keyword_lists, selected_list, is_new=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Keyword List" if is_new else "Edit Keyword List")
        # Remove question mark help button
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.keyword_lists = keyword_lists
        self.selected_list = selected_list
        self.is_new = is_new
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        name_layout = QHBoxLayout()
        name_label = QLabel("List Name:")
        name_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setText("" if is_new else selected_list)
        self.name_input.setToolTip("Enter a descriptive name for this keyword list (e.g., 'Drug Terms', 'Threats', 'Location Names')")
        self.name_input.setEnabled(is_new)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        self.keyword_edit = QTextEdit()
        self.keyword_edit.setFont(QFont("Courier New", 11))
        self.keyword_edit.setToolTip("Enter keywords, one per line. These will be used to highlight matching messages in the conversation view.")
        if not is_new:
            keywords = self.keyword_lists.get(selected_list, [])
            self.keyword_edit.setPlainText("\n".join(keywords))
        layout.addWidget(self.keyword_edit)

        # Added whole word matching option
        self.whole_word = QCheckBox("Exact Word Matching", self)
        self.whole_word.setToolTip("Enable to match keywords as complete words only. For example, searching 'hi' will not match 'high' or 'ship'. Disable to match partial words.")
        self.whole_word.setChecked(False)
        layout.addWidget(self.whole_word)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Add Delete button only when editing (not creating new)
        if not is_new and selected_list and selected_list != "Default":
            delete_button = QPushButton("Delete List")
            delete_button.setToolTip("Delete this keyword list permanently. This action cannot be undone.")
            delete_button.setStyleSheet("QPushButton { background-color: #ff4444; color: white; padding: 5px; }")
            delete_button.clicked.connect(self.delete_list)
            buttons.addButton(delete_button, QDialogButtonBox.DestructiveRole)
        
        layout.addWidget(buttons)
        
        # Resizable dialog (from V3.18 style, but made resizable)
        self.setMinimumSize(400, 300)
        self.setGeometry(200, 200, 400, 300)

    def get_keywords(self):
        return [kw.strip() for kw in self.keyword_edit.toPlainText().split("\n") if kw.strip()]

    def get_list_name(self):
        return self.name_input.text().strip()

    def get_whole_word(self):
        return self.whole_word.isChecked()
    
    def delete_list(self):
        """Delete the current keyword list after confirmation."""
        list_name = self.selected_list
        if list_name == "Default":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Cannot Delete")
            msg.setText("The 'default' keyword list cannot be deleted.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the keyword list '{list_name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Signal deletion to parent
            self.deleted_list = list_name
            self.accept()  # Close dialog with accepted status
        else:
            self.deleted_list = None

class CSVFileDialog(QDialog):
    def __init__(self, text_msg_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Kik Message CSV Files")
        self.setModal(True)
        # Remove question mark help button
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        instruction_label = QLabel(
            "<html><head><style>body { font-size: 26px; } h3 { font-size: 31px; } p { font-size: 26px; }</style></head><body>"
            "<h3>Select Kik Message CSV Files</h3>"
            "<br><br>"
            "<p>Please select one or more CSV files located in the '<b>text-msg-data</b>' folder inside the '<b>content</b>' folder.</p>"
            "<br>"
            "<p>These files contain the Kik message data.</p>"
            "</body></html>"
        )
        instruction_label.setWordWrap(True)
        # Set explicit font size for the label
        label_font = QFont()
        label_font.setPointSize(24)
        instruction_label.setFont(label_font)
        layout.addWidget(instruction_label)

        path_layout = QHBoxLayout()
        path_label = QLabel("Selected Files:")
        path_font = QFont()
        path_font.setPointSize(22)
        path_label.setFont(path_font)
        path_layout.addWidget(path_label)
        self.file_path_input = QTextEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("No files selected")
        path_layout.addWidget(self.file_path_input)
        layout.addLayout(path_layout)

        browse_button = QPushButton("Browse...")
        browse_button.setToolTip("Browse for CSV files in the 'text-msg-data' folder within the Kik content directory")
        browse_font = QFont()
        browse_font.setPointSize(22)
        browse_button.setFont(browse_font)
        browse_button.setMinimumSize(176, 55)
        browse_button.clicked.connect(lambda: self.browse_file(text_msg_dir))
        layout.addWidget(browse_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        # Set explicit font size for buttons to ensure they're readable
        button_font = QFont()
        button_font.setPointSize(22)
        for button in buttons.buttons():
            button.setFont(button_font)
            button.setMinimumSize(176, 55)
        layout.addWidget(buttons)

        self.selected_files = []

        # Override theme stylesheet with larger fonts for better readability on laptop displays
        # Use !important to ensure our styles override theme_manager styles
        self.setStyleSheet("""
            QDialog { background-color: #f4f4f9; }
            QLabel { 
                font-size: 26px !important; 
                font-weight: normal;
            }
            QPushButton { 
                font-size: 22px !important;
                padding: 18px 31px !important;
                min-width: 176px !important;
                min-height: 55px !important;
            }
            QDialogButtonBox QPushButton { 
                font-size: 22px !important;
                padding: 18px 31px !important;
                min-width: 176px !important;
                min-height: 55px !important;
            }
            QTextEdit { 
                padding: 10px; 
                font-size: 22px !important;
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QDialogButtonBox QPushButton:hover { background-color: #e0e0e0; }
        """)

        logger.info("CSVFileDialog initialized")
        # Resizable dialog with larger size for better readability on laptop displays
        self.setMinimumSize(1100, 800)
        self.resize(1200, 900)

    def browse_file(self, text_msg_dir):
        logger.info(f"Opening file dialog for directory: {text_msg_dir}")
        # Create QFileDialog instance for autosizing and centering
        open_dialog = QFileDialog(self)
        open_dialog.setWindowTitle("Select Kik Message CSV Files from 'text-msg-data' Folder")
        open_dialog.setFileMode(QFileDialog.ExistingFiles)
        open_dialog.setNameFilter("CSV Files (*.csv)")
        open_dialog.setDirectory(text_msg_dir)
        center_and_autosize_dialog(open_dialog, self, width_ratio=0.65, height_ratio=0.7, min_width=700, min_height=550)
        if open_dialog.exec() == QDialog.Accepted:
            file_names = open_dialog.selectedFiles()
        else:
            file_names = []
        if file_names:
            self.selected_files = file_names
            self.file_path_input.setText("\n".join(file_names))
            logger.info(f"Selected files: {file_names}")

    def get_selected_files(self):
        """Return the list of selected CSV files."""
        return self.selected_files
        
class SearchWorker(QThread):
    """Background thread for search processing."""
    results_ready = pyqtSignal(list, int)

    def __init__(self, conversations, search_text, search_all, date_from, date_to, keywords, whole_word, selected_conversation, search_whole_word):
        super().__init__()
        self.conversations = conversations
        self.search_text = search_text
        self.search_all = search_all
        self.date_from = date_from
        self.date_to = date_to
        self.keywords = keywords
        self.whole_word = whole_word
        self.selected_conversation = selected_conversation
        self.search_whole_word = search_whole_word

    def run(self):
        messages_to_display = []
        message_count = 0
        conv_count = 0
        matched_conversations = set()

        def matches_search(msg):
            if not self.search_text:
                return True
            text = self.search_text.lower()
            fields = [
                msg['sender'].lower(),
                msg['receiver'].lower(),
                msg['message'].lower(),
                msg['sent_at'].strftime('%Y-%m-%d %H:%M:%S').lower(),
                msg.get('content_id', '').lower()
            ]
            if self.search_whole_word:
                return any(re.search(r'\b' + re.escape(text) + r'\b', field) for field in fields)
            return any(text in field for field in fields)

        if self.search_all or self.selected_conversation == "All Conversations":
            for conv_id in sorted(self.conversations.keys(), key=lambda x: x[0]):
                filtered_messages = []
                for index, msg in enumerate(self.conversations[conv_id]):
                    if pd.isna(msg['sent_at']):
                        continue
                    # Safely handle timezone-aware timestamps
                    if hasattr(msg['sent_at'], 'tz') and msg['sent_at'].tz is not None:
                        msg_sent_at = msg['sent_at'].tz_localize(None)
                    else:
                        msg_sent_at = msg['sent_at']
                    if not (self.date_from <= msg_sent_at <= self.date_to):
                        continue
                    if not matches_search(msg):
                        continue
                    filtered_messages.append((msg, index, conv_id))
                if filtered_messages:
                    conv_str = f"Conversation: {conv_id[0]} <-> {conv_id[1]}" if len(conv_id) == 2 else f"Group: {conv_id[0]}"
                    matched_conversations.add(conv_str)
                    messages_to_display.append(('header', conv_str))
                    messages_to_display.extend(('message', msg, index, conv_id) for msg, index, _ in filtered_messages)
                    message_count += len(filtered_messages)
                    conv_count += 1
        else:
            conv_str = self.selected_conversation.replace("Conversation: ", "").replace("Group: ", "").replace(" [Reviewed]", "")
            conv_id = (conv_str,) if self.selected_conversation.startswith("Group: ") else tuple(sorted(conv_str.split(" <-> ")))
            if conv_id in self.conversations:
                header_text = f"Conversation: {conv_id[0]} <-> {conv_id[1]}" if len(conv_id) == 2 else f"Group: {conv_id[0]}"
                matched_conversations.add(header_text)
                messages_to_display.append(('header', header_text))
                filtered_messages = []
                for index, msg in enumerate(self.conversations[conv_id]):
                    if pd.isna(msg['sent_at']):
                        continue
                    # Safely handle timezone-aware timestamps
                    if hasattr(msg['sent_at'], 'tz') and msg['sent_at'].tz is not None:
                        msg_sent_at = msg['sent_at'].tz_localize(None)
                    else:
                        msg_sent_at = msg['sent_at']
                    if not (self.date_from <= msg_sent_at <= self.date_to):
                        continue
                    if not matches_search(msg):
                        continue
                    filtered_messages.append((msg, index, conv_id))
                messages_to_display.extend(('message', msg, index, conv_id) for msg, index, _ in filtered_messages)
                message_count = len(filtered_messages)

        self.results_ready.emit(messages_to_display, message_count)

class MessageTableModel(QAbstractTableModel):
    """QAbstractTableModel for virtual scrolling message table."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages_data = []  # List of (item_type, *args) tuples
        self.headers = ["Date", "Time", "Sender", "Receiver", "Message", "Tags", "Media", "IP", "Port", "Source", "Line Number"]
        self.keyword_state = {}
        self.compute_row_color_func = None
        self.get_media_path_func = None
        self.media_files = {}
        
    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows."""
        return len(self.messages_data)
    
    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns."""
        return len(self.headers)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self.messages_data):
            return None
        
        item_type, *args = self.messages_data[index.row()]
        
        if item_type == 'header':
            # Header rows - span across all columns
            if role == Qt.DisplayRole:
                if index.column() == 0:
                    return args[0]
                else:
                    return ''  # Empty for other columns in header row
            elif role == Qt.BackgroundRole:
                return QBrush(QColor('#d0d0d0'))
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignLeft | Qt.AlignVCenter
            return None
        
        # Message rows
        msg, index_val, conv_id = args
        col = index.column()
        
        if role == Qt.DisplayRole:
            # Helper function to normalize "nan" strings to empty
            def normalize_value(val):
                if pd.isna(val):
                    return ''
                val_str = str(val).strip()
                if val_str.lower() in ('nan', 'none'):
                    return ''
                return val_str
            
            if col == 0:  # Date
                return msg['sent_at'].strftime('%Y-%m-%d') if pd.notna(msg['sent_at']) else ''
            elif col == 1:  # Time
                return msg['sent_at'].strftime('%H:%M:%S') if pd.notna(msg['sent_at']) else ''
            elif col == 2:  # Sender
                return normalize_value(msg.get('sender', ''))
            elif col == 3:  # Receiver
                return normalize_value(msg.get('receiver', ''))
            elif col == 4:  # Message
                return normalize_value(msg.get('message', ''))
            elif col == 5:  # Tags
                tags = msg.get('tags', [])
                if tags:
                    return ', '.join(sorted(str(tag) for tag in tags if str(tag).strip().lower() not in ('nan', 'none')))
                return ''
            elif col == 6:  # Media
                content_id = msg.get('content_id', '')
                # Normalize: handle empty, None, 'nan' string, or actual NaN - return space instead of 'nan'
                normalized = normalize_value(content_id)
                return ' ' if normalized == '' else normalized
            elif col == 7:  # IP
                return normalize_value(msg.get('ip', ''))
            elif col == 8:  # Port
                return normalize_value(msg.get('port', ''))
            elif col == 9:  # Source
                source = msg.get('source', 'Unknown')
                source_str = normalize_value(source)
                return os.path.basename(source_str) if source_str else 'Unknown'
            elif col == 10:  # Line Number
                return normalize_value(msg.get('line_number', ''))
        
        elif role == Qt.BackgroundRole:
            # Compute background color
            if self.compute_row_color_func:
                bg_color = self.compute_row_color_func(
                    msg, conv_id, row_index=index.row(), keyword_state=self.keyword_state
                )
                return QBrush(QColor(bg_color))
        
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter
        
        elif role == Qt.ToolTipRole:
            if col == 6:  # Media
                content_id = msg.get('content_id', '')
                if content_id and self.get_media_path_func:
                    media_path = self.get_media_path_func(content_id)
                    if media_path and os.path.exists(media_path):
                        ext = os.path.splitext(media_path)[1].lower()
                        media_type = "Video" if ext in ['.mp4', '.webm', '.ogg'] else "Image" if ext in ['.jpg', '.jpeg', '.png', '.gif'] else "File"
                        return f"{media_type}: {os.path.basename(media_path)}\nDouble-click to open"
                return "No Media" if not content_id else str(content_id)
            elif col == 9:  # Source
                return msg.get('source', 'Unknown')
        
        elif role == Qt.UserRole:
            # Store msg_id in UserRole for row identification
            if col == 4:  # Message column
                return msg.get('msg_id', '')
            # Store media path info in UserRole for media column
            elif col == 6:  # Media column
                content_id = msg.get('content_id', '')
                if content_id and self.get_media_path_func:
                    media_path = self.get_media_path_func(content_id)
                    if media_path and os.path.exists(media_path):
                        return {
                            'content_id': content_id,
                            'media_path': media_path,
                            'content_path': media_path
                        }
                return None
        
        return None
    
    def flags(self, index):
        """Return item flags."""
        if not index.isValid():
            return Qt.NoItemFlags
        
        item_type, *args = self.messages_data[index.row()]
        if item_type == 'header':
            return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def setMessages(self, messages_to_display, keyword_state, compute_row_color_func, get_media_path_func, media_files):
        """Update the model with new messages."""
        self.beginResetModel()
        self.messages_data = messages_to_display
        self.keyword_state = keyword_state
        self.compute_row_color_func = compute_row_color_func
        self.get_media_path_func = get_media_path_func
        self.media_files = media_files
        self.endResetModel()
    
    def getMessageAtRow(self, row):
        """Get the message data at the given row."""
        if 0 <= row < len(self.messages_data):
            item_type, *args = self.messages_data[row]
            if item_type == 'message':
                return args[0]  # Return the message dict
        return None
    
    def getConvIdAtRow(self, row):
        """Get the conversation ID at the given row."""
        if 0 <= row < len(self.messages_data):
            item_type, *args = self.messages_data[row]
            if item_type == 'message':
                return args[2]  # Return the conv_id
        return None
        
class UpdateCheckWorker(QThread):
    result = pyqtSignal(object, object)  # (error, data)

    def run(self):
        try:
            # GitHub requires a User-Agent header
            req = urllib.request.Request(
                GITHUB_LATEST_API,
                headers={"User-Agent": f"KikAnalyzer/{APP_VERSION}"}
            )
            # Use strict SSL verification for security
            ctx = ssl.create_default_context()
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            self.result.emit(None, data)
        except Exception as e:
            self.result.emit(e, None)


class MediaThumbnailDelegate(QStyledItemDelegate):
    """Custom delegate for rendering media thumbnails in the table."""
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        # If main_window not provided, try to find it
        if not self.main_window:
            for w in QApplication.topLevelWidgets():
                if isinstance(w, KikAnalyzerGUI):
                    self.main_window = w
                    break
    
    def paint(self, painter, option, index):
        """Paint the thumbnail or content_id text."""
        # Get media info from UserRole
        media_info = index.data(Qt.UserRole)
        
        if not media_info or not isinstance(media_info, dict):
            # No media, just show text
            super().paint(painter, option, index)
            return
        
        content_path = media_info.get('content_path', '')
        if not content_path or not os.path.exists(content_path):
            super().paint(painter, option, index)
            return
        
        ext = os.path.splitext(content_path)[1].lower()
        is_video = ext in ['.mp4', '.webm', '.ogg']
        is_image = ext in ['.jpg', '.jpeg', '.png', '.gif']
        
        if not (is_video or is_image):
            # Not a supported media type, show as text
            super().paint(painter, option, index)
            return
        
        # Determine thumbnail path
        thumb_path = content_path if is_image else content_path + '_thumb.jpg'
        
        # Generate thumbnail for video if needed
        if is_video and not os.path.exists(thumb_path):
            cap = None
            try:
                cap = cv2.VideoCapture(content_path)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(thumb_path, frame)
            except Exception as e:
                if logging_enabled:
                    logger.error(f"Failed to generate thumbnail: {str(e)}")
            finally:
                if cap is not None:
                    cap.release()
        
        # Draw background
        painter.save()
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            bg_color = index.data(Qt.BackgroundRole)
            if bg_color:
                painter.fillRect(option.rect, bg_color)
        
        # Load and scale thumbnail
        if os.path.exists(thumb_path):
            pixmap = QPixmap(thumb_path)
            if not pixmap.isNull():
                # Calculate available space (leave room for label at bottom)
                cell_width = option.rect.width() - 4  # 2px padding on each side
                cell_height = option.rect.height() - 20  # Leave 20px for label
                
                # Scale to fit within cell while maintaining aspect ratio
                # Use the smaller of the two dimensions to ensure it fits
                scale_factor = min(
                    cell_width / pixmap.width(),
                    cell_height / pixmap.height()
                )
                scaled_width = int(pixmap.width() * scale_factor)
                scaled_height = int(pixmap.height() * scale_factor)
                
                scaled_pixmap = pixmap.scaled(
                    scaled_width, scaled_height,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                
                # Center the thumbnail horizontally, align to top with small padding
                x = option.rect.x() + (option.rect.width() - scaled_pixmap.width()) // 2
                y = option.rect.y() + 2  # 2px padding from top
                
                # Apply blur if needed - check both global blur and individual blur state
                content_id = media_info.get('content_id', '')
                global_blur = self.main_window and hasattr(self.main_window, 'blur_all') and self.main_window.blur_all
                individual_blur = self.main_window and hasattr(self.main_window, 'blurred_thumbnails') and content_id in self.main_window.blurred_thumbnails
                should_blur = global_blur or individual_blur
                
                if should_blur:
                    # Apply blur using OpenCV (same as export function)
                    # Use temp file approach for reliability
                    try:
                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                            tmp_path = tmp_file.name
                        
                        # Save pixmap to temp file
                        scaled_pixmap.save(tmp_path, 'JPG')
                        
                        # Load with OpenCV and blur
                        img = cv2.imread(tmp_path)
                        if img is not None:
                            blurred_img = cv2.GaussianBlur(img, BLUR_KERNEL_SIZE, BLUR_SIGMA)
                            
                            # Save blurred image back to temp file
                            cv2.imwrite(tmp_path, blurred_img)
                            
                            # Load back as QPixmap
                            scaled_pixmap = QPixmap(tmp_path)
                            
                            # Clean up temp file
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                    except Exception as e:
                        if logging_enabled:
                            logger.error(f"Failed to blur thumbnail: {str(e)}")
                        # If blur fails, just draw the original
                
                painter.drawPixmap(x, y, scaled_pixmap)
                
                # Draw media type tag at the bottom of the cell
                tag_text = "(VID)" if is_video else "(IMG)"
                font = painter.font()
                font.setPointSize(8)
                painter.setFont(font)
                painter.setPen(QColor('gray'))
                
                # Position tag at bottom of cell, centered
                tag_rect = option.rect
                tag_rect.setTop(tag_rect.bottom() - 16)  # 16px from bottom
                tag_rect.setHeight(14)
                painter.drawText(tag_rect, Qt.AlignCenter, tag_text)
        
        painter.restore()
    
    def sizeHint(self, option, index):
        """Return size hint for the thumbnail cell - this determines row height."""
        # Check if this cell has media
        media_info = index.data(Qt.UserRole)
        if media_info and isinstance(media_info, dict):
            content_path = media_info.get('content_path', '')
            if content_path and os.path.exists(content_path):
                ext = os.path.splitext(content_path)[1].lower()
                is_video = ext in ['.mp4', '.webm', '.ogg']
                is_image = ext in ['.jpg', '.jpeg', '.png', '.gif']
                if is_video or is_image:
                    # Return height that accommodates thumbnail + label
                    # THUMBNAIL_SIZE is (100, 100), so we need 100px for thumb + 20px for label + padding
                    return QSize(THUMBNAIL_SIZE[0] + 20, THUMBNAIL_SIZE[1] + 25)
        
        # Default size for non-media cells
        return super().sizeHint(option, index)
    
    def editorEvent(self, event, model, option, index):
        """Handle mouse events for opening media files."""
        if event.type() == event.MouseButtonDblClick and event.button() == Qt.LeftButton:
            media_info = index.data(Qt.UserRole)
            if media_info and isinstance(media_info, dict):
                content_path = media_info.get('content_path', '')
                if content_path and os.path.exists(content_path):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(content_path))
                    return True
        return super().editorEvent(event, model, option, index)

class RichReviewedDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Get the plain text the model already stores
        text = index.data()

        # Replace the plain marker with bold + yellow-highlighted HTML
        # Keep the space prefix to match your stored " [Reviewed]" exactly
        html = text.replace(
            " [Reviewed]",
            " <span style='background-color:#ffff00; font-weight:700;'>[Reviewed]</span>"
        )

        # Render as rich text
        doc = QTextDocument()
        doc.setHtml(html)

        # Make the background and selection look native
        painter.save()
        option.widget.style().drawControl(option.widget.style().CE_ItemViewItem, option, painter, option.widget)
        painter.restore()

        painter.save()
        painter.translate(option.rect.topLeft())
        clip = QRectF(0, 0, option.rect.width(), option.rect.height())
        doc.drawContents(painter, clip)
        painter.restore()

    def sizeHint(self, option, index):
        doc = QTextDocument()
        doc.setHtml(index.data())
        return doc.size().toSize()


class BorderedCellDelegate(QStyledItemDelegate):
    """Delegate to render custom borders on cells."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
    
    def paint(self, painter, option, index):
        # First, draw the normal cell content
        super().paint(painter, option, index)
        
        # Check if this cell should have a border
        if self.parent_window and hasattr(self.parent_window, 'cell_borders'):
            row = index.row()
            col = index.column()
            model = index.model()
            
            # Get border color from theme manager
            border_color = self.parent_window.theme_manager.get_color('cell_border')
            border_color_obj = QColor(border_color)
            painter.save()
            pen = QPen(border_color_obj, 5)  # 5px thick border for better visibility
            painter.setPen(pen)
            rect = option.rect
            
            # First check if this cell is part of a selection region border
            if hasattr(self.parent_window, 'selection_borders'):
                for (min_row, max_row, min_col, max_col) in self.parent_window.selection_borders:
                    if min_row <= row <= max_row and min_col <= col <= max_col:
                        # This cell is within a selection region
                        # Draw border edges based on position
                        # Top edge
                        if row == min_row:
                            painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
                        # Bottom edge
                        if row == max_row:
                            painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
                        # Left edge
                        if col == min_col:
                            painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())
                        # Right edge
                        if col == max_col:
                            painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
                        painter.restore()
                        return  # Don't check individual cell borders if part of selection
            
            # Check for individual cell border (original behavior)
            # Get msg_id from column 4 (message column) which stores msg_id in UserRole
            msg_index = model.index(row, 4)
            if msg_index.isValid():
                msg_id = model.data(msg_index, Qt.UserRole)
                if msg_id:
                    # Check if this (msg_id, column) combination has a border
                    if (msg_id, col) in self.parent_window.cell_borders:
                        # Draw border around the cell
                        painter.drawRect(rect.adjusted(1, 1, -1, -1))  # Adjust to avoid overlap with cell edges
            
            painter.restore()


class KikAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing KikAnalyzerGUI...")
        self.setWindowTitle("Kik Conversation Analyzer")
        self.setWindowFlags(Qt.Window)
        self.conversations = {}
        self.reviewed_conversations = set()
        self.reviewed_button = QPushButton("Mark as Reviewed")
        self.reviewed_button.setToolTip("Mark or unmark the selected conversation as reviewed to track analysis progress")
        self.reviewed_button.clicked.connect(self.toggle_reviewed_status)
        self.df = None
        self.recently_processed = set()
        self.content_folder = None
        self.logs_folder = None
        self.media_files = {}
        self.keyword_lists = {}
        self.keyword_whole_word = {}
        self.selected_keyword_list = "Default"
        self.stats_visible = False
        self.prebuilt_tags = ["Evidence", "CSAM", "Of Interest"]
        self.available_tags = set(self.prebuilt_tags)
        self.tag_priorities = {
            "Evidence": (3, '#ff8000'),  # bold orange
            "CSAM": (2, '#ff0000'),  # bold red
            "Of Interest": (1, '#ffff00'),  # bold yellow
        }
        self.hotkeys = {}  # Initialize empty, will be set in load_config
        
        # Undo/Redo system
        self.undo_stack = []  # List of actions that can be undone
        self.redo_stack = []  # List of actions that can be redone
        self.max_undo_history = 50  # Limit undo history size
        
        # Notes system - store notes for conversations
        self.conversation_notes = {}  # dict: conv_id (tuple) -> note (str)
        
        # Dark mode support
        self.dark_mode = False  # Default to light mode
        self.theme_manager = ThemeManager(self.dark_mode)
        
        self.init_ui()
        self.load_config()
        self.load_data()  # Calls load_config, which now calls create_shortcuts
        self.blur_all = False
        self.blurred_thumbnails = set()  # Track individually blurred thumbnails by content_id
        self.cell_borders = set()  # Store tuples of (msg_id, column_index) for cells with borders
        self.selection_borders = set()  # Store tuples of (min_row, max_row, min_col, max_col) for selection region borders
        self.showMaximized()
        logger.info("Initialization complete.")
        
        # Automatically check for updates after GUI is displayed
        # Use QTimer to delay slightly so GUI is fully rendered first
        QTimer.singleShot(1000, self.auto_check_for_updates)
        
    def get_tag_color(self, tags):
        if not tags:
            return None
        max_pri = -1
        # Use theme-aware default color
        default_custom_color = self.theme_manager.get_color('tag_custom')
        color = default_custom_color
        for tag in tags:
            # Get priority and color from tag_priorities, but use theme-aware colors
            pri, _ = self.tag_priorities.get(tag, (0, None))
            if pri > max_pri:
                max_pri = pri
                # Map tag names to theme colors
                if tag == "CSAM":
                    color = self.theme_manager.get_color('tag_csam')
                elif tag == "Evidence":
                    color = self.theme_manager.get_color('tag_evidence')
                elif tag == "Of Interest":
                    color = self.theme_manager.get_color('tag_interest')
                else:
                    color = default_custom_color
        return color

    def _get_keyword_state(self):
        return (
            self.keyword_lists.get(self.selected_keyword_list, []),
            self.keyword_whole_word.get(self.selected_keyword_list, False)
        )

    def is_keyword_match(self, message_text, keywords=None, whole_word=None):
        if not message_text:
            return False
        default_keywords, default_whole_word = self._get_keyword_state()
        if keywords is None:
            keywords = default_keywords
        if whole_word is None:
            whole_word = default_whole_word
        if not keywords:
            return False
        text = message_text.lower()
        for kw in keywords:
            kw_lower = kw.lower()
            if whole_word:
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', text):
                    return True
            else:
                if kw_lower in text:
                    return True
        return False

    def compute_row_color(
        self,
        msg,
        conv_id,
        row_index=0,
        *,
        enable_keyword=True,
        enable_sender_colors=True,
        alternate_colors=True,
        default_color=None,
        keyword_color=None,
        keyword_state=None
    ):
        # Use theme-aware defaults if not provided
        if default_color is None:
            default_color = self.theme_manager.get_color('row_default')
        if keyword_color is None:
            keyword_color = self.theme_manager.get_color('keyword_hit')
        
        tag_color = self.get_tag_color(msg['tags'])
        if tag_color:
            return tag_color

        keywords, whole_word = keyword_state if keyword_state is not None else self._get_keyword_state()
        if enable_keyword and self.is_keyword_match(msg['message'], keywords, whole_word):
            return keyword_color

        if enable_sender_colors:
            if len(conv_id) == 2:
                sender1, sender2 = conv_id
            else:
                sender1, sender2 = msg['sender'], None
            if msg['sender'] == sender1:
                return self.theme_manager.get_color('sender1')
            if sender2 and msg['sender'] == sender2:
                return self.theme_manager.get_color('sender2')

        if alternate_colors:
            return self.theme_manager.get_color('row_alternate') if row_index % 2 else self.theme_manager.get_color('row_default')

        return default_color
        
    def toggle_all_blur(self):
        self.blur_all = not self.blur_all
        self.blur_all_button.setText("Unblur Media" if self.blur_all else "Blur Media")
        self.apply_global_blur()
        logger.info(f"Global blur toggled to {self.blur_all}")
        self.status_bar.showMessage(f"Global media blur {'enabled' if self.blur_all else 'disabled'}")

    def apply_global_blur(self):
        # Trigger repaint of the table view to update thumbnails with blur effect
        if self.message_table and self.message_model:
            # Update all rows in the media column (column 6)
            row_count = self.message_model.rowCount()
            if row_count > 0:
                # Emit dataChanged for all cells in the media column to force repaint
                top_left = self.message_model.index(0, 6)
                bottom_right = self.message_model.index(row_count - 1, 6)
                self.message_model.dataChanged.emit(top_left, bottom_right, [])
            # Also trigger viewport update and repaint
            self.message_table.viewport().update()
            self.message_table.repaint()
            # Force update of visible items
            QApplication.processEvents()

    def load_keyword_lists(self):
        self.keyword_lists = {}
        self.keyword_whole_word = {}
        keywords_dir = os.path.join(USER_HOME, "Keywords")
        os.makedirs(keywords_dir, exist_ok=True)
        default_path = os.path.join(keywords_dir, "default.txt")
        if not os.path.exists(default_path):
            try:
                with open(default_path, 'w', encoding='utf-8') as f:
                    f.write("")
            except Exception as e:
                logger.error(f"Error creating default keyword file: {e}")
        for file in os.listdir(keywords_dir):
            if file.endswith(".txt"):
                list_name = os.path.splitext(file)[0]
                file_path = os.path.join(keywords_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        keywords = []
                        whole_word = False
                        for line in lines:
                            line = line.strip()
                            if line.startswith('#whole_word'):
                                whole_word = True
                            elif line:
                                keywords.append(line)
                        self.keyword_lists[list_name] = keywords
                        self.keyword_whole_word[list_name] = whole_word
                except Exception as e:
                    logger.error(f"Error loading keyword list {file_path}: {str(e)}")
        logger.info(f"Loaded {len(self.keyword_lists)} keyword lists.")

    def save_keyword_list(self, list_name, keywords, whole_word):
        keywords_dir = os.path.join(USER_HOME, "Keywords")
        os.makedirs(keywords_dir, exist_ok=True)
        file_path = os.path.join(keywords_dir, f"{list_name}.txt")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if whole_word:
                    f.write("#whole_word\n")
                f.write("\n".join(keywords))
            self.keyword_lists[list_name] = keywords
            self.keyword_whole_word[list_name] = whole_word
            self.populate_keyword_dropdown()
            self.keyword_selector.setCurrentText(list_name)
            self.save_config()
            logger.info(f"Saved keyword list: {list_name}, whole_word: {whole_word}")
        except Exception as e:
            logger.error(f"Error saving keyword list {list_name}: {str(e)}")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Error saving keyword list: {str(e)}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage(f"Error saving keyword list: {list_name}")

    def delete_keyword_list(self, list_name):
        """Delete a keyword list from memory, file system, and config."""
        if list_name == "Default":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Cannot Delete")
            msg.setText("The 'default' keyword list cannot be deleted.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        
        keywords_dir = os.path.join(USER_HOME, "Keywords")
        file_path = os.path.join(keywords_dir, f"{list_name}.txt")
        
        try:
            # Delete the .txt file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted keyword list file: {file_path}")
            
            # Remove from memory
            if list_name in self.keyword_lists:
                del self.keyword_lists[list_name]
            if list_name in self.keyword_whole_word:
                del self.keyword_whole_word[list_name]
            
            # If the deleted list was selected, switch to default or first available
            if self.selected_keyword_list == list_name:
                if "Default" in self.keyword_lists:
                    self.selected_keyword_list = "Default"
                elif self.keyword_lists:
                    self.selected_keyword_list = list(self.keyword_lists.keys())[0]
                else:
                    self.selected_keyword_list = None
            
            # Refresh dropdown
            self.populate_keyword_dropdown()
            
            # Save config to refresh config.json
            self.save_config()
            
            logger.info(f"Deleted keyword list: {list_name}")
            self.status_bar.showMessage(f"Deleted keyword list: {list_name}")
            
            # Show success message
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText(f"Keyword list '{list_name}' has been deleted.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
        except Exception as e:
            logger.error(f"Error deleting keyword list {list_name}: {str(e)}")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Error deleting keyword list: {str(e)}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage(f"Error deleting keyword list: {list_name}")

    def load_config(self):
        logger.info("Entering load_config")
        config_file = os.path.join(USER_HOME, "KikParser_config.json")
        keywords_dir = os.path.join(USER_HOME, "Keywords")
        logger.info(f"Config file path: {config_file}")
        logger.info(f"Keywords directory: {keywords_dir}")
        # Initialize defaults
        self.hotkeys = {'CSAM': 'Ctrl+1', 'Evidence': 'Ctrl+2', 'Of Interest': 'Ctrl+3', 'Reviewed': 'Ctrl+R'}
        self.selected_keyword_list = "Default"
        self.keyword_lists = {"Default": []}
        self.keyword_whole_word = {"Default": False}
        self.available_tags = set(self.prebuilt_tags)
        if os.path.exists(config_file):
            logger.info("Config file exists, loading...")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("JSON loaded successfully")
                    self.selected_keyword_list = config.get("selected_keyword_list", "Default")
                    self.keyword_lists = config.get("keyword_lists", {"Default": []})
                    self.keyword_whole_word = config.get("keyword_whole_word", {"Default": False})
                    self.available_tags = set(config.get("available_tags", self.prebuilt_tags))
                    self.hotkeys = config.get("hotkeys", self.hotkeys)
                    # Load logging setting (defaults to False if not present)
                    saved_logging_enabled = config.get("logging_enabled", False)
                    global logging_enabled
                    if saved_logging_enabled:
                        enable_logging()
                    else:
                        disable_logging()
                    # Load custom colors
                    custom_colors_light = config.get("custom_colors_light", {})
                    custom_colors_dark = config.get("custom_colors_dark", {})
                    # Validate color values (must be hex strings)
                    valid_keys = set(self.theme_manager.get_all_color_keys())
                    custom_colors_light = {k: v for k, v in custom_colors_light.items() if k in valid_keys and isinstance(v, str) and v.startswith('#')}
                    custom_colors_dark = {k: v for k, v in custom_colors_dark.items() if k in valid_keys and isinstance(v, str) and v.startswith('#')}
                    self.theme_manager.load_custom_colors(
                        custom_colors_light=custom_colors_light,
                        custom_colors_dark=custom_colors_dark
                    )
                    logger.info(f"Loaded hotkeys: {self.hotkeys}")
                    logger.info(f"Loaded config: selected_keyword_list={self.selected_keyword_list}, keyword_lists={self.keyword_lists}, keyword_whole_word={self.keyword_whole_word}, logging_enabled={saved_logging_enabled}")
                    logger.info(f"Loaded custom colors: light={len(custom_colors_light)}, dark={len(custom_colors_dark)}")
                    # Load cell borders
                    cell_borders_list = config.get("cell_borders", [])
                    # Convert list of lists to set of tuples
                    self.cell_borders = {tuple(border) for border in cell_borders_list if isinstance(border, list) and len(border) == 2}
                    logger.info(f"Loaded {len(self.cell_borders)} cell borders")
                    # Load selection borders
                    selection_borders_list = config.get("selection_borders", [])
                    if isinstance(selection_borders_list, list):
                        self.selection_borders = {tuple(border) for border in selection_borders_list if isinstance(border, list) and len(border) == 4}
                        logger.info(f"Loaded {len(self.selection_borders)} selection borders")
                    else:
                        self.selection_borders = set()
                    # Apply theme after loading custom colors (if UI is initialized)
                    if hasattr(self, 'message_table'):
                        self.apply_theme()
            except Exception as e:
                logger.error(f"Error loading KikParser_config.json: {str(e)}")
                logger.info("Falling back to default settings.")
        else:
            logger.info("No config file found, using default settings.")
            # Ensure logging is disabled by default if no config file exists
            global logging_enabled
            disable_logging()
        # Load keyword lists from Keywords folder
        if os.path.exists(keywords_dir):
            logger.info(f"Keywords directory exists, loading .txt files...")
            os.makedirs(keywords_dir, exist_ok=True)  # Ensure directory exists
            for file in os.listdir(keywords_dir):
                if file.lower().endswith('.txt'):
                    list_name = os.path.splitext(file)[0]
                    file_path = os.path.join(keywords_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            keywords = [line.strip() for line in f if line.strip()]
                            logger.info(f"Loaded keyword list '{list_name}' from {file_path}: {keywords}")
                            # Parse #whole_word flag if present as the first line
                            whole_word = False
                            if keywords and keywords[0] == '#whole_word':
                                whole_word = True
                                keywords = keywords[1:]  # Remove the flag from keywords
                                logger.info(f"Parsed #whole_word flag for '{list_name}'; set whole_word=True and removed flag from keywords.")
                            # Only update if the list is not already in config or is different
                            if list_name not in self.keyword_lists or self.keyword_lists[list_name] != keywords:
                                self.keyword_lists[list_name] = keywords
                            # Set or update whole_word (prefer parsed value over default/config if present)
                            self.keyword_whole_word[list_name] = whole_word if list_name not in self.keyword_whole_word else self.keyword_whole_word[list_name] or whole_word
                    except Exception as e:
                        logger.error(f"Error loading keyword file {file_path}: {str(e)}")
        else:
            logger.info("Keywords directory not found, skipping .txt file loading.")
        # Validate keyword lists to ensure all keywords are strings; remove invalid ones
        for list_name in list(self.keyword_lists.keys()):  # Use list() to avoid runtime modification issues
            keywords = self.keyword_lists[list_name]
            if not isinstance(keywords, list):
                logger.warning(f"Invalid format for keyword list '{list_name}' in KikParser_config.json (expected a list). Removing the list.")
                del self.keyword_lists[list_name]
                if list_name in self.keyword_whole_word:
                    del self.keyword_whole_word[list_name]
                continue
            valid_keywords = []
            for kw in keywords:
                if isinstance(kw, str):
                    valid_keywords.append(kw)
                else:
                    logger.warning(f"Removing non-string keyword '{kw}' (type: {type(kw)}) from list '{list_name}'.")
            self.keyword_lists[list_name] = valid_keywords
            if not valid_keywords:
                logger.info(f"Keyword list '{list_name}' is empty after validation; it will be retained but won't highlight anything.")
        # Handle case where selected_keyword_list references a removed or empty list
        if self.selected_keyword_list not in self.keyword_lists or not self.keyword_lists.get(self.selected_keyword_list):
            if self.keyword_lists:
                self.selected_keyword_list = list(self.keyword_lists.keys())[0]  # Default to the first valid list
                logger.info(f"Reset selected_keyword_list to '{self.selected_keyword_list}' after validation.")
            else:
                self.selected_keyword_list = None
                logger.info("No valid keyword lists after validation; selected_keyword_list reset to None.")
        logger.info(f"Final config: selected_keyword_list={self.selected_keyword_list}, keyword_lists={self.keyword_lists}, keyword_whole_word={self.keyword_whole_word}")
        # Populate the keyword_selector dropdown with loaded lists
        # Populate the keyword_selector dropdown with loaded lists (without firing a search)
        self.keyword_selector.blockSignals(True)
        self.keyword_selector.clear()
        for list_name in sorted(self.keyword_lists.keys()):
            self.keyword_selector.addItem(list_name)

        if self.selected_keyword_list:
            idx = self.keyword_selector.findText(self.selected_keyword_list)
            if idx >= 0:
                self.keyword_selector.setCurrentIndex(idx)
            else:
                # Fall back to first item if the saved list name isn't present
                self.keyword_selector.setCurrentIndex(0 if self.keyword_selector.count() > 0 else -1)
        else:
            # If nothing saved, but we have lists, select the first
            if self.keyword_selector.count() > 0:
                self.keyword_selector.setCurrentIndex(0)
        self.keyword_selector.blockSignals(False)

        self.create_shortcuts()  # Ensure shortcuts are created with loaded or default hotkeys


    def save_config(self):
        config_file = os.path.join(USER_HOME, "KikParser_config.json")
        global logging_enabled
        # Get custom colors from theme manager
        custom_colors = self.theme_manager.get_custom_colors()
        config = {
            "selected_keyword_list": self.selected_keyword_list,
            "available_tags": list(self.available_tags),
            "hotkeys": self.hotkeys,
            "keyword_lists": self.keyword_lists,
            "keyword_whole_word": self.keyword_whole_word,
            "logging_enabled": logging_enabled,
            "custom_colors_light": custom_colors['light'],
            "custom_colors_dark": custom_colors['dark'],
            "cell_borders": [list(border) for border in self.cell_borders],  # Convert set of tuples to list of lists for JSON
            "selection_borders": [list(border) for border in self.selection_borders]  # Convert set of tuples to list of lists for JSON
        }
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            logger.info("Saved config.")
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            
    def get_media_path(self, content_id):
        return self.media_files.get(content_id, '')

    def sanitize_path(self, file_path, base_dir):
        """
        Ensure file_path is within base_dir to prevent path traversal attacks.
        
        Args:
            file_path: The file path to sanitize
            base_dir: The base directory that file_path must be within
            
        Returns:
            The sanitized absolute path if valid, None otherwise
        """
        try:
            if not file_path or not base_dir:
                logger.error("Invalid input: file_path or base_dir is empty")
                return None
            
            # Normalize and resolve base directory
            real_base = os.path.realpath(os.path.normpath(base_dir))
            if not os.path.isdir(real_base):
                logger.error(f"Base directory does not exist: {real_base}")
                return None
            
            # Normalize the file path (remove any .. or . components)
            normalized_path = os.path.normpath(file_path)
            
            # Join and resolve to absolute path
            joined_path = os.path.join(real_base, normalized_path)
            real_path = os.path.realpath(joined_path)
            
            # Ensure the resolved path is within the base directory
            # Use os.path.commonpath for cross-platform compatibility
            try:
                common_path = os.path.commonpath([real_base, real_path])
                if os.path.normpath(common_path) != os.path.normpath(real_base):
                    logger.error(f"Path traversal detected: {file_path} -> {real_path}")
                    return None
            except ValueError:
                # Paths are on different drives (Windows) or invalid
                logger.error(f"Path traversal detected (different drives): {file_path}")
                return None
            
            return real_path
        except Exception as e:
            logger.error(f"Error sanitizing path {file_path}: {e}")
            return None

    def compute_file_hash(self, file_path):
        try:
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
            return md5_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for {file_path}: {str(e)}")
            return ''

    def open_media_file(self, media_path):
        import pathlib
        import subprocess

        if os.path.exists(media_path):
            url = pathlib.Path(media_path).absolute().as_uri()
            # Validate URL is a file:// URI for security
            if not url.startswith('file://'):
                logger.error(f"Invalid URL scheme: {url}")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Security")
                msg.setText("Invalid file URL")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, url], shell=False)
                self.log_message(f"Opened media in Chrome: {url}")
            elif os.path.exists(edge_path):
                subprocess.Popen([edge_path, url], shell=False)
                self.log_message(f"Opened media in Edge: {url}")
            else:
                webbrowser.open(url)
                self.log_message(f"Opened media with default browser: {url}")
            self.status_bar.showMessage(f"Opened media: {media_path}")
        else:
            self.log_message(f"Media file does not exist: {media_path}", "ERROR")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Media Not Found")
            msg.setText(f"File not found:\n{media_path}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage(f"File not found: {media_path}")

    def init_ui(self):
        logger.info("Setting up UI...")
        
        # Create menu bar with View menu for dark mode toggle
        menubar = self.menuBar()
        view_menu = menubar.addMenu('View')
        self.dark_mode_action = view_menu.addAction('Toggle Dark Mode')
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.dark_mode_action.setToolTip("Switch between light and dark theme")
        
        # Add separator
        view_menu.addSeparator()
        
        # Add Color Settings action
        color_settings_action = view_menu.addAction('Color Settings')
        color_settings_action.setToolTip("Customize colors for all UI elements, with separate settings for light and dark modes. Changes are saved and applied to both the GUI and HTML exports.")
        color_settings_action.triggered.connect(self.show_color_settings)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # NEW: Add "Check for updates" (right side, separate from the toolbar)
        self.update_button = QPushButton("Check for updates")
        self.update_button.setToolTip("Check GitHub for a newer version of the application. Opens the releases page in your default browser.")
        self.update_button.clicked.connect(self.check_for_updates)
        self.update_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
        self.status_bar.addPermanentWidget(self.update_button)

        control_group = QGroupBox()
        control_layout = QGridLayout()
        control_layout.setSpacing(5)

        self.search_label = QLabel("Search:")
        self.search_label.setToolTip("Search messages by sender name, receiver name, message content, or timestamp")
        control_layout.addWidget(self.search_label, 0, 0)
        
        # Create a vertical layout for checkboxes between label and search bar
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setSpacing(2)
        
        self.search_whole_word = QCheckBox("Exact Word Match")
        self.search_whole_word.setToolTip("Enable to match search terms as complete words only. Example: searching 'hi' will not match 'high' or 'ship'. Disable to match partial words anywhere in the text.")
        # Remove automatic search trigger - now requires Apply Search button
        # Set smaller font for professional look
        font = self.search_whole_word.font()
        font.setPointSize(font.pointSize() - 1)
        self.search_whole_word.setFont(font)
        checkbox_layout.addWidget(self.search_whole_word)
        
        self.search_all = QCheckBox("Search All Conversations")
        self.search_all.setToolTip("Enable to search across all conversations instead of just the currently selected conversation. Useful for finding messages across multiple conversations.")
        # Remove automatic search trigger - now requires Apply Search button
        # Set smaller font for professional look
        self.search_all.setFont(font)
        checkbox_layout.addWidget(self.search_all)
        
        control_layout.addWidget(checkbox_container, 0, 1)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter keywords...")
        self.search_bar.setToolTip("Enter search terms to filter messages. Searches sender, receiver, message content, and timestamps. Click 'Apply Search' button to apply the filter.")
        # Remove automatic search trigger - now requires Apply Search button
        control_layout.addWidget(self.search_bar, 0, 2, 1, 2)
        
        # Add "Apply Search" button to the right of the search bar
        self.apply_search_button = QPushButton("Apply Search")
        self.apply_search_button.setToolTip("Click to apply the search filter to the message table. The search will only be applied when this button is clicked.")
        self.apply_search_button.clicked.connect(self.apply_search)
        control_layout.addWidget(self.apply_search_button, 0, 4)
        
        # Add "Clear Search/Filters" button to the right of "Apply Search" button
        self.clear_filters_button = QPushButton("Clear Search/Filters")
        self.clear_filters_button.setToolTip("Clear all search terms and date filters. Resets dates to earliest and latest available dates, and clears the search bar.")
        self.clear_filters_button.clicked.connect(self.clear_all_filters)
        control_layout.addWidget(self.clear_filters_button, 0, 5)

        self.date_from_label = QLabel("From Date:")
        self.date_from_label.setToolTip("Filter messages to show only those sent on or after this date. Leave empty to include all messages from the beginning.")
        control_layout.addWidget(self.date_from_label, 1, 0)
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate(2024, 1, 1))
        self.date_from.setToolTip("Select the start date for filtering messages. Click 'Apply Date Filter' button to apply the date filter.")
        control_layout.addWidget(self.date_from, 1, 1)
        self.date_to_label = QLabel("To Date:")
        self.date_to_label.setToolTip("Filter messages to show only those sent on or before this date. Click 'Apply Date Filter' button to apply the date filter.")
        control_layout.addWidget(self.date_to_label, 1, 2)
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setToolTip("Select the end date for filtering messages. Click 'Apply Date Filter' button to apply the date filter.")
        control_layout.addWidget(self.date_to, 1, 3)
        # Add "Apply Date Filter" button next to the "To Date" field
        self.apply_date_filter_button = QPushButton("Apply Date Filter")
        self.apply_date_filter_button.setToolTip("Click to apply the selected date range filter to the message table. The filter will only be applied when this button is clicked.")
        self.apply_date_filter_button.clicked.connect(self.apply_date_filter)
        control_layout.addWidget(self.apply_date_filter_button, 1, 4)

        self.keyword_label = QLabel("Keyword List:")
        self.keyword_label.setToolTip("Select a keyword list to automatically highlight matching messages in the conversation view. Create or edit lists using the buttons below.")
        control_layout.addWidget(self.keyword_label, 2, 0)
        self.keyword_selector = QComboBox()
        self.keyword_selector.setToolTip("Select a keyword list from the dropdown to highlight messages that match any keyword in the list. Messages will be highlighted in green.")
        self.populate_keyword_dropdown()
        self.keyword_selector.currentTextChanged.connect(self.update_selected_keyword_list)
        control_layout.addWidget(self.keyword_selector, 2, 1, 1, 2)
        self.create_keyword_button = QPushButton("Create New Keyword List")
        self.create_keyword_button.setToolTip("Create a new keyword list for highlighting relevant messages. Useful for organizing different types of searches or investigations.")
        self.create_keyword_button.clicked.connect(self.create_keyword_list)
        control_layout.addWidget(self.create_keyword_button, 2, 3)
        self.edit_keywords_button = QPushButton("Edit Keywords")
        self.edit_keywords_button.setToolTip("Edit the currently selected keyword list. Add, remove, or modify keywords, and change matching options.")
        self.edit_keywords_button.clicked.connect(self.edit_keywords)
        control_layout.addWidget(self.edit_keywords_button, 2, 4)

        self.selector_label = QLabel("Conversation Selector:")
        self.selector_label.setToolTip("Select a conversation or group chat from the dropdown to view its messages in the table below")
        control_layout.addWidget(self.selector_label, 3, 0)

        self.selector = QComboBox()
        self.selector.addItem("All Conversations")
        self.selector.setToolTip("Select a conversation or group chat to view. Conversations are listed by participant names or group names. Reviewed conversations are marked with [Reviewed].")

        # Install the delegate AFTER the combobox exists
        self.selector.setItemDelegate(RichReviewedDelegate(self.selector))
        self.selector.view().setItemDelegate(RichReviewedDelegate(self.selector))

        # Connect selector directly to execute_search (not schedule_search) for instant cache lookup
        self.selector.currentIndexChanged.connect(self.execute_search)
        control_layout.addWidget(self.selector, 3, 1, 1, 4)
        control_layout.addWidget(self.reviewed_button, 3, 5)


        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        self.search_results_label = QLabel("Found 0 messages")
        main_layout.addWidget(self.search_results_label)

        # Create model and view for virtual scrolling
        self.message_model = MessageTableModel(self)
        self.message_table = QTableView()
        self.message_table.setModel(self.message_model)
        
        # Set custom delegate for media column (column 6) to display thumbnails
        media_delegate = MediaThumbnailDelegate(self, main_window=self)
        self.message_table.setItemDelegateForColumn(6, media_delegate)
        
        # Set bordered cell delegate for all columns to handle custom borders
        bordered_delegate = BorderedCellDelegate(self)
        self.message_table.setItemDelegate(bordered_delegate)
        
        # Configure header
        header = self.message_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        for col in range(11):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
            header.setMinimumSectionSize(50)
            header.setMaximumSectionSize(500)
        self.message_table.setColumnWidth(0, 30)
        self.message_table.setColumnWidth(4, 350)
        self.message_table.setColumnWidth(6, 150)  # Media column - wider for thumbnails
        self.message_table.setColumnWidth(7, 150)  # IP
        self.message_table.setColumnWidth(8, 100)  # Port
        
        # Configure view
        self.message_table.setWordWrap(True)
        self.message_table.setFont(QFont("Courier New", 11))
        self.message_table.setSelectionMode(QTableView.ExtendedSelection)
        self.message_table.setSelectionBehavior(QTableView.SelectItems)
        self.message_table.setEditTriggers(QTableView.NoEditTriggers)
        self.message_table.verticalHeader().setVisible(False)
        self.message_table.doubleClicked.connect(self.handle_double_click)
        self.message_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.message_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add Ctrl+C keyboard shortcut for copying cells
        copy_shortcut = QShortcut(QKeySequence.Copy, self.message_table)
        copy_shortcut.setContext(Qt.WidgetShortcut)
        copy_shortcut.activated.connect(self.copy_selected_cells)
        
        self.message_table.setMinimumWidth(800)
        self.message_table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.message_table.horizontalHeader().customContextMenuRequested.connect(self.show_column_menu)
        main_layout.addWidget(self.message_table)

        self.stats_panel = QGroupBox("Message Statistics")
        self.stats_panel.setVisible(False)
        stats_layout = QVBoxLayout()
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Courier New", 11))
        stats_layout.addWidget(self.stats_text)
        self.stats_panel.setLayout(stats_layout)
        main_layout.addWidget(self.stats_panel)

        toolbar = QToolBar()
        self.view_tagged_button = QPushButton("View Tagged")
        self.view_tagged_button.setToolTip("View all messages that have been tagged across all conversations. Filter by tag type and sort by conversation or timestamp.")
        self.view_tagged_button.clicked.connect(self.view_tagged_messages)
        toolbar.addWidget(self.view_tagged_button)
        self.view_keyword_hits_button = QPushButton("View Keyword Hits")
        self.view_keyword_hits_button.setToolTip("View all messages that match any keyword in the currently selected keyword list. Shows matches across all conversations.")
        self.view_keyword_hits_button.clicked.connect(self.view_keyword_hits)
        toolbar.addWidget(self.view_keyword_hits_button)
        self.manage_tags_button = QPushButton("Manage Tags")
        self.manage_tags_button.setToolTip("Add, edit, or remove custom tag labels. Pre-built tags (CSAM, Evidence, Of Interest) cannot be removed but can be customized.")
        self.manage_tags_button.clicked.connect(self.manage_tags)
        toolbar.addWidget(self.manage_tags_button)
        self.manage_hotkeys_button = QPushButton("Manage Hotkeys")
        self.manage_hotkeys_button.setToolTip("Assign custom keyboard shortcuts to tags for faster tagging. Default hotkeys: Ctrl+1 (CSAM), Ctrl+2 (Evidence), Ctrl+3 (Of Interest).")
        self.manage_hotkeys_button.clicked.connect(self.manage_hotkeys)
        toolbar.addWidget(self.manage_hotkeys_button)
        self.blur_all_button = QPushButton("Blur Media")
        self.blur_all_button.setToolTip("Toggle blur effect for all media thumbnails in the GUI. Useful when reviewing sensitive content. Does not affect exported files.")
        self.blur_all_button.clicked.connect(self.toggle_all_blur)
        toolbar.addWidget(self.blur_all_button)
        self.stats_button = QPushButton("Show Stats")
        self.stats_button.setToolTip("Toggle the statistics panel to view detailed metrics for the selected conversation (message counts, media sent/received) or all conversations.")
        self.stats_button.clicked.connect(self.toggle_stats_panel)
        toolbar.addWidget(self.stats_button)
        self.load_new_button = QPushButton("Load New Data")
        self.load_new_button.setToolTip("Load a new Kik data folder. Select the unzipped folder containing 'content' and 'logs' subfolders, then choose CSV files from 'text-msg-data'.")
        self.load_new_button.clicked.connect(self.load_data)
        toolbar.addWidget(self.load_new_button)
        self.export_button = QPushButton("Export")
        self.export_button.setToolTip("Export messages to HTML or CSV format. Choose export scope, select fields, configure sorting, and set sanitization options for sensitive content.")
        self.export_button.clicked.connect(self.export_messages)
        self.reviewed_button = QPushButton("Mark as Reviewed")
        self.reviewed_button.setToolTip("Mark or unmark the selected conversation as reviewed to track your analysis progress. Reviewed conversations are marked with [Reviewed] in the dropdown.")
        self.reviewed_button.clicked.connect(self.toggle_reviewed_status)
        toolbar.addWidget(self.export_button)
        self.help_button = QPushButton("Help")
        self.help_button.setToolTip("Open the help dialog with detailed instructions, feature descriptions, keyboard shortcuts, and troubleshooting information")
        self.help_button.clicked.connect(self.show_help)
        toolbar.addWidget(self.help_button)
        self.save_progress_button = QPushButton("Save Progress")
        self.save_progress_button.setToolTip("Save your current progress including reviewed conversations and tagged messages to a file. Load saved progress later to resume your analysis.")
        self.save_progress_button.clicked.connect(self.save_progress)
        toolbar.addWidget(self.save_progress_button)
        self.load_progress_button = QPushButton("Load Progress")
        self.load_progress_button.setToolTip("Load previously saved progress from a file")
        self.load_progress_button.clicked.connect(self.load_progress)
        toolbar.addWidget(self.load_progress_button)
        self.notes_button = QPushButton("Notes")
        self.notes_button.setToolTip("View/edit notes for the selected conversation")
        self.notes_button.clicked.connect(self.manage_notes)
        toolbar.addWidget(self.notes_button)
        main_layout.addWidget(toolbar)

        # Apply theme stylesheet
        self.apply_theme()

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.execute_search)
        # Separate timer for date changes with longer debounce
        self.date_timer = QTimer(self)
        self.date_timer.setSingleShot(True)
        self.date_timer.timeout.connect(self.execute_search)
        self.search_worker = None
        self.search_cache = OrderedDict()  # Cache for search results with size limit
        # Multi-level caching (Strategy 3)
        self.date_filtered_cache = OrderedDict()  # Cache for date-filtered results
        # Pre-computed unfiltered state (Strategy 1)
        self.unfiltered_messages = None  # Pre-computed unfiltered messages list
        self.earliest_date = None  # Earliest date in dataset
        self.latest_date = None  # Latest date in dataset
        # Table state tracking for incremental updates (Strategy 2)
        self.table_row_map = {}  # Maps msg_id to row index for incremental updates

        logger.info("UI setup complete.")
    
    def apply_theme(self):
        """Apply the current theme stylesheet to the main window."""
        self.setStyleSheet(self.theme_manager.get_stylesheet())
        # Refresh the UI to apply theme changes (only if data has been loaded)
        if hasattr(self, 'message_table') and hasattr(self, 'search_timer') and hasattr(self, 'conversations') and self.conversations:
            self.schedule_search()  # Refresh table to apply new colors
    
    def refresh_theme(self):
        """Refresh the UI after color changes."""
        # Update main window stylesheet
        self.setStyleSheet(self.theme_manager.get_stylesheet())
        
        # Refresh table view to show new row colors
        if hasattr(self, 'message_table') and hasattr(self, 'message_model'):
            model = self.message_model
            if model and model.rowCount() > 0:
                # Emit dataChanged for all rows to refresh background colors
                top_left = model.index(0, 0)
                bottom_right = model.index(model.rowCount() - 1, model.columnCount() - 1)
                if top_left.isValid() and bottom_right.isValid():
                    model.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole])
                # Force viewport update
                self.message_table.viewport().update()
        
        # Refresh any open dialogs
        for widget in QApplication.allWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                if hasattr(self, 'theme_manager'):
                    widget.setStyleSheet(self.theme_manager.get_dialog_stylesheet())
        
        # Also refresh via schedule_search if available (this will repopulate the table with new colors)
        if hasattr(self, 'schedule_search'):
            self.schedule_search()
        
        logger.info("Theme refreshed after color changes")
    
    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        # Preserve custom colors before switching
        custom_colors = self.theme_manager.get_custom_colors()
        self.dark_mode = not self.dark_mode
        self.theme_manager = ThemeManager(self.dark_mode)
        # Restore custom colors after switching
        self.theme_manager.load_custom_colors(
            custom_colors_light=custom_colors['light'],
            custom_colors_dark=custom_colors['dark']
        )
        self.dark_mode_action.setChecked(self.dark_mode)
        self.apply_theme()
        logger.info(f"Dark mode {'enabled' if self.dark_mode else 'disabled'}")
        self.status_bar.showMessage(f"Dark mode {'enabled' if self.dark_mode else 'disabled'}")
        
    def show_column_menu(self, position):
        menu = QMenu(self)
        for col in range(self.message_table.columnCount()):
            header_text = self.message_table.horizontalHeaderItem(col).text()
            action = menu.addAction(header_text)
            action.setCheckable(True)
            action.setChecked(not self.message_table.isColumnHidden(col))
            action.triggered.connect(lambda checked, c=col: self.message_table.setColumnHidden(c, not checked))
        menu.exec(self.message_table.horizontalHeader().mapToGlobal(position))

    def manage_tags(self):
        dialog = ManageTagsDialog(self.available_tags, self)
        if dialog.exec() == QDialog.Accepted:
            self.available_tags = set(dialog.get_available_tags())
            self.save_config()
            self.schedule_search()  # Refresh to show updated tags

    def show_help(self):
        """Display a help dialog with instructions for using the Kik Conversation Analyzer."""
        logger.info("Displaying help dialog")
        
        # Create a custom dialog instead of QMessageBox to include checkbox
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Help - Kik Conversation Analyzer")
        # Remove question mark help button
        help_dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        help_dialog.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(help_dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Help text area
        help_text_edit = QTextEdit()
        help_text_edit.setReadOnly(True)
        log_file_path = os.path.join(USER_HOME, 'kik_analyzer.log')
        
        # Get current colors for legend (use theme manager to get effective colors including custom)
        tag_csam_color = self.theme_manager.get_color('tag_csam')
        tag_evidence_color = self.theme_manager.get_color('tag_evidence')
        tag_interest_color = self.theme_manager.get_color('tag_interest')
        keyword_hit_color = self.theme_manager.get_color('keyword_hit')
        sender1_color = self.theme_manager.get_color('sender1')
        sender2_color = self.theme_manager.get_color('sender2')
        tag_custom_color = self.theme_manager.get_color('tag_custom')
        
        help_text_edit.setHtml(
            "<h2>Kik Conversation Analyzer - Help</h2>"
            "<p><b>Welcome to the Kik Conversation Analyzer!</b></p>"
            "<p>This tool helps you analyze, organize, and export Kik messenger conversation data. Follow the instructions below to get started.</p>"
            "<h3>Getting Started</h3>"
            "<ul>"
            "<li><b>Load Data</b>: Click the <b>'Load New Data'</b> button to select your unzipped Kik data folder. The folder must contain <b>'content'</b> and <b>'logs'</b> subfolders. When prompted, select CSV files from the <b>'text-msg-data'</b> folder within the content directory.</li>"
            "<li><b>Select Conversation</b>: Use the conversation dropdown menu to select a conversation or group chat to analyze. Messages will appear in the main table below.</li>"
            "</ul>"
            "<h3>Searching and Filtering</h3>"
            "<ul>"
            "<li><b>Search Messages</b>: Enter keywords in the search bar to filter messages by content, sender, receiver, or timestamp. Enable <b>'Exact Word'</b> for whole-word matching (e.g., searching 'hi' will not match 'high'). Enable <b>'Search All'</b> to search across all conversations instead of just the selected one.</li>"
            "<li><b>Date Range Filtering</b>: Use the date pickers to filter messages within a specific date range. Leave dates empty to include all messages.</li>"
            "<li><b>Keyword Highlighting</b>: Select a keyword list from the dropdown to automatically highlight matching messages. Create and manage keyword lists using the <b>'Create Keywords'</b> and <b>'Edit Keywords'</b> buttons.</li>"
            "</ul>"
            "<h3>Tagging Messages</h3>"
            "<ul>"
            "<li><b>Tag Messages</b>: Select a message in the table, then either right-click for the context menu or use keyboard hotkeys to tag or untag messages. Default hotkeys: <b>Ctrl+1</b> for CSAM, <b>Ctrl+2</b> for Evidence, <b>Ctrl+3</b> for Of Interest. Customize hotkeys via <b>'Manage Hotkeys'</b>.</li>"
            "<li><b>Manage Tags</b>: Click <b>'Manage Tags'</b> to add, edit, or remove custom tag labels. Pre-built tags (CSAM, Evidence, Of Interest) cannot be removed but can be customized.</li>"
            "<li><b>View Tagged Messages</b>: Click <b>'View Tagged'</b> to see all tagged messages across all conversations. Filter by tag type and sort by conversation or timestamp.</li>"
            "<li><b>Undo/Redo</b>: Use <b>Ctrl+Z</b> to undo and <b>Ctrl+Y</b> to redo tagging operations (up to 50 actions).</li>"
            "</ul>"
            "<h3>Media Handling</h3>"
            "<ul>"
            "<li><b>View Media</b>: Double-click any cell in the <b>'Media'</b> column to open media files in your default application. Thumbnails are automatically generated for images and videos.</li>"
            "<li><b>Blur Media</b>: Toggle the <b>'Blur Media'</b> button to blur all media thumbnails in the GUI. This is useful when reviewing sensitive content.</li>"
            "</ul>"
            "<h3>Exporting Data</h3>"
            "<ul>"
            "<li><b>Export Messages</b>: Click <b>'Export'</b> to save messages as HTML or CSV files. Choose the export scope (Tagged Messages, Selected Conversation, or All Conversations), select which fields to include, and configure sorting options.</li>"
            "<li><b>Sanitize Export</b>: Use the sanitization options in the export dialog to blur CSAM-tagged media or all media in HTML reports. This helps protect sensitive content when sharing reports.</li>"
            "<li><b>Export Formats</b>: HTML exports include embedded media, file hashes (MD5), and professional styling. CSV exports provide structured data for analysis in spreadsheet applications.</li>"
            "</ul>"
            "<h3>Advanced Features</h3>"
            "<ul>"
            "<li><b>Manage Keywords</b>: Create multiple keyword lists for different investigation purposes. Enable <b>'Whole Word'</b> matching for exact word searches. View all keyword matches using <b>'View Keyword Hits'</b>.</li>"
            "<li><b>Progress Tracking</b>: Select a conversation and click <b>'Mark as Reviewed'</b> to track your analysis progress. Use <b>'Save Progress'</b> to save your work and resume later.</li>"
            "<li><b>Statistics</b>: Toggle <b>'Show Stats'</b> to view detailed statistics for the selected conversation (including message counts and media sent/received tallies) or for all conversations.</li>"
            "<li><b>Notes</b>: Add notes to conversations using <b>'Manage Notes'</b> (if available). Search notes to quickly find conversations with specific annotations.</li>"
            "</ul>"
            f"<h3>Color Legend for Row Backgrounds</h3>"
            "<ul>"
            f"<li><span style='background-color: {tag_csam_color}; color: black; padding: 2px 6px; border-radius: 3px;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>: Tagged as <b>CSAM</b> (highest priority).</li>"
            f"<li><span style='background-color: {tag_evidence_color}; color: black; padding: 2px 6px; border-radius: 3px;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>: Tagged as <b>Evidence</b>.</li>"
            f"<li><span style='background-color: {tag_interest_color}; color: black; padding: 2px 6px; border-radius: 3px;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>: Tagged as <b>Of Interest</b>.</li>"
            f"<li><span style='background-color: {keyword_hit_color}; color: black; padding: 2px 6px; border-radius: 3px;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>: Message matches selected keyword list.</li>"
            f"<li><span style='background-color: {sender1_color}; color: black; padding: 2px 6px; border-radius: 3px;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>: Message from <b>Sender 1</b>.</li>"
            f"<li><span style='background-color: {sender2_color}; color: black; padding: 2px 6px; border-radius: 3px;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>: Message from <b>Sender 2</b>.</li>"
            f"<li><span style='background-color: {tag_custom_color}; color: black; padding: 2px 6px; border-radius: 3px;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>: Message tagged with a <b>Custom Tag</b>.</li>"
            "</ul>"
            "<h3>Support and Troubleshooting</h3>"
            "<p>For errors or other issues:</p>"
            "<ul>"
            f"<li>Check the log file at: <code>{log_file_path}</code> (enable logging in this dialog if needed)</li>"
            "<li>Contact support: <a href='mailto:patrick.koebbe@gmail.com'>patrick.koebbe@gmail.com</a></li>"
            "</ul>"
            "<p><b>Version:</b> 4.2 | <b>GitHub:</b> <a href='https://github.com/Koebbe14/Kik-Parser'>Koebbe14/Kik-Parser</a></p>"
        )
        layout.addWidget(help_text_edit)
        
        # Logging toggle checkbox
        logging_group = QGroupBox()
        logging_layout = QVBoxLayout()
        self.logging_checkbox = QCheckBox("Enable Logging")
        global logging_enabled
        self.logging_checkbox.setChecked(logging_enabled)
        self.logging_checkbox.setToolTip(f"Enable or disable file-based logging. When enabled, application events and errors are logged to: {os.path.join(USER_HOME, 'kik_analyzer.log')}")
        self.logging_checkbox.stateChanged.connect(self.toggle_logging)
        logging_layout.addWidget(self.logging_checkbox)
        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(help_dialog.accept)
        layout.addWidget(buttons)
        
        # Apply theme stylesheet
        if hasattr(self, 'theme_manager'):
            help_dialog.setStyleSheet(self.theme_manager.get_dialog_stylesheet())
        else:
            help_dialog.setStyleSheet("""
                QDialog { background-color: #f4f4f9; }
                QTextEdit { font-size: 14px; background-color: white; }
                QGroupBox { border: 1px solid #d0d0d0; border-radius: 5px; padding: 10px; }
                QCheckBox { font-size: 14px; padding: 5px; }
                QPushButton { padding: 8px; font-size: 14px; min-width: 100px; min-height: 30px; }
                QPushButton:hover { background-color: #e0e0e0; }
            """)
        
        help_dialog.exec()
        self.status_bar.showMessage("Help dialog displayed")
        logger.info("Help dialog closed")
    
    def show_color_settings(self, parent_dialog=None):
        """Open the color settings dialog."""
        dialog = ColorSettingsDialog(self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self.status_bar.showMessage("Color settings applied")
            logger.info("Color settings updated")
        else:
            self.status_bar.showMessage("Color settings cancelled")
    
    def toggle_logging(self, state):
        """Toggle logging on or off based on checkbox state."""
        global logging_enabled
        if state == Qt.Checked:
            enable_logging()
            self.status_bar.showMessage("Logging enabled")
        else:
            disable_logging()
            self.status_bar.showMessage("Logging disabled")
        # Save the logging setting to config
        self.save_config()

    def schedule_search(self):
        """Schedule a search with debounce for text input."""
        self.status_bar.showMessage("Preparing search...")
        # Stop date timer if running to avoid conflicts
        if self.date_timer.isActive():
            self.date_timer.stop()
        self.search_timer.start(SEARCH_DEBOUNCE_MS)  # Debounce delay for text input
    
    def schedule_date_search(self):
        """Schedule a search with longer debounce for date changes."""
        self.status_bar.showMessage("Preparing search...")
        # Stop text search timer if running to avoid conflicts
        if self.search_timer.isActive():
            self.search_timer.stop()
        self.date_timer.start(DATE_DEBOUNCE_MS)  # Longer debounce delay for date changes
    
    def apply_date_filter(self):
        """Apply the date filter when the button is clicked."""
        # Stop any running timers
        if self.search_timer.isActive():
            self.search_timer.stop()
        if self.date_timer.isActive():
            self.date_timer.stop()
        # Execute search immediately with current date filter settings
        # execute_search will check cache first and skip status messages if cache found
        self.execute_search()
    
    def apply_search(self):
        """Apply the search filter when the button is clicked."""
        self.status_bar.showMessage("Applying search filter...")
        # Stop any running timers
        if self.search_timer.isActive():
            self.search_timer.stop()
        if self.date_timer.isActive():
            self.date_timer.stop()
        # Execute search immediately with current search settings
        self.execute_search()
    
    def clear_all_filters(self):
        """Strategy 5: Clear all filters using pre-computed unfiltered state."""
        self.status_bar.showMessage("Clearing all filters...")
        
        # Clear search bar
        self.search_bar.clear()
        
        # Reset checkboxes to unchecked (default state)
        self.search_whole_word.setChecked(False)
        self.search_all.setChecked(False)
        
        # Use pre-computed dates if available
        if hasattr(self, 'earliest_date') and self.earliest_date:
            from_date = QDate(self.earliest_date.year, self.earliest_date.month, self.earliest_date.day)
            self.date_from.setDate(from_date)
        else:
            # Fallback: find dates if not pre-computed
            earliest_date = None
            if self.conversations:
                for conv_id, messages in self.conversations.items():
                    for msg in messages:
                        sent_at = msg.get('sent_at')
                        if sent_at and pd.notna(sent_at):
                            if hasattr(sent_at, 'tz') and sent_at.tz is not None:
                                sent_at = sent_at.tz_localize(None)
                            if earliest_date is None or sent_at < earliest_date:
                                earliest_date = sent_at
            if earliest_date:
                from_date = QDate(earliest_date.year, earliest_date.month, earliest_date.day)
                self.date_from.setDate(from_date)
            else:
                self.date_from.setDate(QDate(2024, 1, 1))
        
        if hasattr(self, 'latest_date') and self.latest_date:
            to_date = QDate(self.latest_date.year, self.latest_date.month, self.latest_date.day)
            self.date_to.setDate(to_date)
        else:
            # Fallback: find dates if not pre-computed
            latest_date = None
            if self.conversations:
                for conv_id, messages in self.conversations.items():
                    for msg in messages:
                        sent_at = msg.get('sent_at')
                        if sent_at and pd.notna(sent_at):
                            if hasattr(sent_at, 'tz') and sent_at.tz is not None:
                                sent_at = sent_at.tz_localize(None)
                            if latest_date is None or sent_at > latest_date:
                                latest_date = sent_at
            if latest_date:
                to_date = QDate(latest_date.year, latest_date.month, latest_date.day)
                self.date_to.setDate(to_date)
            else:
                self.date_to.setDate(QDate.currentDate())
        
        # Stop any running timers
        if self.search_timer.isActive():
            self.search_timer.stop()
        if self.date_timer.isActive():
            self.date_timer.stop()
        
        # Use pre-computed unfiltered cache if available
        if self.unfiltered_messages:
            messages_to_display, message_count = self.unfiltered_messages
            # Update table directly with pre-computed results (instant!)
            self.update_message_table(messages_to_display, message_count, from_cache=True)
            self.status_bar.showMessage(f"All filters cleared - showing {message_count} messages")
            logger.info("Cleared filters using pre-computed unfiltered state")
        else:
            # Fallback to normal search if pre-computed state not available
            self.execute_search()
            self.status_bar.showMessage("All filters cleared")

    def execute_search(self):
        """Execute the search with multi-level caching (Strategy 3)."""
        # Create a unique cache key for final results FIRST (before any status messages)
        cache_key = (
            self.search_bar.text().lower(),
            self.search_whole_word.isChecked(),
            self.search_all.isChecked(),
            self.date_from.date().toString("yyyy-MM-dd"),
            self.date_to.date().toString("yyyy-MM-dd"),
            self.selector.currentText(),
            self.selected_keyword_list
        )
        
        # Check final cache FIRST - if found, return immediately without any processing
        if cache_key in self.search_cache:
            messages_to_display, message_count = self.search_cache[cache_key]
            logger.info(f"Cache HIT - loading from cache. Key: {cache_key}")
            # Pass from_cache=True to skip progress dialog for faster cached updates
            self.update_message_table(messages_to_display, message_count, from_cache=True)
            self.status_bar.showMessage(f"Displayed {message_count} messages (cached)")
            return
        
        # Cache miss - proceed with search
        logger.info(f"Cache MISS - key not found: {cache_key}")
        logger.debug(f"Cache size: {len(self.search_cache)}, keys: {list(self.search_cache.keys())[:3]}...")
        self.status_bar.showMessage("Loading...")
        self.status_bar.showMessage("Loading... (please wait)")
        logger.info("Executing search in background thread...")

        # Strategy 3: Multi-level caching - check date-filtered cache
        date_key = (
            self.date_from.date().toString("yyyy-MM-dd"),
            self.date_to.date().toString("yyyy-MM-dd"),
            self.selector.currentText(),
            self.search_all.isChecked()
        )
        search_text = self.search_bar.text().lower()
        search_whole_word = self.search_whole_word.isChecked()
        
        # If we have date-filtered results, reuse them
        logger.debug(f"Date-filtered cache lookup - key: {date_key}")
        logger.debug(f"Date-filtered cache size: {len(self.date_filtered_cache)}")
        if date_key in self.date_filtered_cache:
            date_filtered_messages = self.date_filtered_cache[date_key]
            
            if search_text:
                # Apply search text filter to date-filtered results
                logger.info("Reusing date-filtered cache, applying search text filter...")
                filtered_messages = self._apply_search_filter_to_list(
                    date_filtered_messages, search_text, search_whole_word
                )
                message_count = len([m for m in filtered_messages if m[0] == 'message'])
                # Cache the final result
                while len(self.search_cache) >= MAX_CACHE_SIZE:
                    self.search_cache.popitem(last=False)
                self.search_cache[cache_key] = (filtered_messages, message_count)
                self.update_message_table(filtered_messages, message_count, from_cache=True)
                self.status_bar.showMessage(f"Displayed {message_count} messages (date-cached + search)")
            else:
                # No search text, use date-filtered results directly
                logger.info("Reusing date-filtered cache (no search text)...")
                message_count = len([m for m in date_filtered_messages if m[0] == 'message'])
                # Cache the final result
                while len(self.search_cache) >= MAX_CACHE_SIZE:
                    self.search_cache.popitem(last=False)
                self.search_cache[cache_key] = (date_filtered_messages, message_count)
                self.update_message_table(date_filtered_messages, message_count, from_cache=True)
                self.status_bar.showMessage(f"Displayed {message_count} messages (date-cached)")
            return

        # Disconnect previous worker if active
        if self.search_worker is not None and self.search_worker.isRunning():
            # Wait a short time for graceful shutdown
            if not self.search_worker.wait(1000):  # Wait up to 1 second
                # Force termination if still running (last resort)
                self.search_worker.terminate()
                self.search_worker.wait()

        # Start new search worker
        self.search_worker = SearchWorker(
            self.conversations,
            self.search_bar.text().lower(),
            self.search_all.isChecked(),
            datetime.datetime.combine(self.date_from.date().toPyDate(), datetime.time.min),
            datetime.datetime.combine(self.date_to.date().toPyDate(), datetime.time.max),
            self.keyword_lists.get(self.selected_keyword_list, []),
            self.keyword_whole_word.get(self.selected_keyword_list, False),
            self.selector.currentText(),
            self.search_whole_word.isChecked()
        )
        self.search_worker.results_ready.connect(self._on_search_results_ready)
        self.search_worker.start()
    
    def _apply_search_filter_to_list(self, messages_list, search_text, search_whole_word):
        """Apply search text filter to a pre-filtered message list."""
        if not search_text:
            return messages_list
        
        filtered = []
        pending_header = None
        current_conv_has_messages = False
        
        for item_type, *args in messages_list:
            if item_type == 'header':
                # If we had messages from previous conversation, the header was already added
                # Store this header for the next conversation
                pending_header = args
                current_conv_has_messages = False
            elif item_type == 'message':
                msg, index, conv_id = args
                fields = [
                    msg['sender'].lower(),
                    msg['receiver'].lower(),
                    msg['message'].lower(),
                    msg['sent_at'].strftime('%Y-%m-%d %H:%M:%S').lower() if pd.notna(msg['sent_at']) else '',
                    msg.get('content_id', '').lower()
                ]
                if search_whole_word:
                    matches = any(re.search(r'\b' + re.escape(search_text) + r'\b', field) for field in fields)
                else:
                    matches = any(search_text in field for field in fields)
                if matches:
                    # Add header for this conversation if we haven't already
                    if not current_conv_has_messages and pending_header:
                        filtered.append(('header', *pending_header))
                        current_conv_has_messages = True
                        pending_header = None
                    filtered.append((item_type, *args))
        
        return filtered
    
    def _on_search_results_ready(self, messages_to_display, message_count):
        """Strategy 3: Handle search results and update date-filtered cache."""
        # Cache date-filtered results for future use
        date_key = (
            self.date_from.date().toString("yyyy-MM-dd"),
            self.date_to.date().toString("yyyy-MM-dd"),
            self.selector.currentText(),
            self.search_all.isChecked()
        )
        search_text = self.search_bar.text().lower()
        
        # If no search text, this is a date-filtered result we can cache
        if not search_text:
            while len(self.date_filtered_cache) >= MAX_CACHE_SIZE:
                self.date_filtered_cache.popitem(last=False)
            self.date_filtered_cache[date_key] = messages_to_display
        
        # Update table with results
        self.update_message_table(messages_to_display, message_count)
        
    def show_context_menu(self, position):
        """Show context menu for table view."""
        index = self.message_table.indexAt(position)
        if not index.isValid():
            return
        
        # If right-clicked on media column, show blur and tag menu
        if index.column() == 6:  # Media column
            # Get media info to identify this thumbnail
            media_info = index.data(Qt.UserRole)
            if media_info and isinstance(media_info, dict):
                content_id = media_info.get('content_id', '')
                if content_id:
                    menu = QMenu(self)
                    # Check if this specific thumbnail is blurred (individually or globally)
                    is_blurred = self.blur_all or content_id in self.blurred_thumbnails
                    action_text = "Unblur This Media" if is_blurred else "Blur This Media"
                    blur_action = menu.addAction(action_text)
                    menu.addSeparator()  # Add separator between blur and tag options
                    tag_action = menu.addAction("Tag Message")
                    action = menu.exec(self.message_table.mapToGlobal(position))
                    
                    if action == blur_action:
                        # Toggle individual blur state for this thumbnail
                        if content_id in self.blurred_thumbnails:
                            self.blurred_thumbnails.discard(content_id)
                        else:
                            self.blurred_thumbnails.add(content_id)
                        # Update just this cell
                        self.message_model.dataChanged.emit(index, index, [])
                        self.message_table.viewport().update()
                    elif action == tag_action:
                        # Tag the message in this row
                        row = index.row()
                        # Get msg_id from the message column (column 4) of the same row
                        msg_index = self.message_model.index(row, 4)
                        if msg_index.isValid():
                            msg_id = self.message_model.data(msg_index, Qt.UserRole)
                            if msg_id:
                                # Get current tags
                                current_tags = set()
                                for conv_id, messages in self.conversations.items():
                                    for msg in messages:
                                        if msg.get('msg_id') == msg_id:
                                            current_tags = msg.get('tags', set()).copy()
                                            break
                                # Open tag dialog
                                dialog = MessageTagsDialog(self.available_tags, current_tags, self)
                                if dialog.exec() == QDialog.Accepted:
                                    new_tags = dialog.get_selected_tags()
                                    self.available_tags.update(new_tags)  # Add any custom to global
                                    # Update tags for this message
                                    for conv_id, messages in self.conversations.items():
                                        for msg in messages:
                                            if msg.get('msg_id') == msg_id:
                                                msg['tags'] = new_tags.copy()
                                                break
                                    # Update the model to refresh display
                                    conv_id_at_row = self.message_model.getConvIdAtRow(row)
                                    if conv_id_at_row:
                                        # Trigger model update for this row
                                        self.message_model.dataChanged.emit(
                                            self.message_model.index(row, 0),
                                            self.message_model.index(row, 10),
                                            []
                                        )
                                    self.save_config()
            return
        
        # For any other column, show tag menu and border options
        selected_indexes = self.message_table.selectedIndexes()
        if not selected_indexes:
            # If no selection, select the cell that was right-clicked
            selected_indexes = [index]
        
        # Collect cell border information for selected cells
        cells_with_borders = []
        cells_without_borders = []
        for idx in selected_indexes:
            if not idx.isValid():
                continue
            row = idx.row()
            col = idx.column()
            # Get msg_id from column 4 (message column) of the same row
            msg_index = self.message_model.index(row, 4)
            if msg_index.isValid():
                msg_id = self.message_model.data(msg_index, Qt.UserRole)
                if msg_id:
                    cell_key = (msg_id, col)
                    if cell_key in self.cell_borders:
                        cells_with_borders.append(cell_key)
                    else:
                        cells_without_borders.append(cell_key)
        
        menu = QMenu(self)
        # Add Copy menu item at the top
        copy_action = menu.addAction("Copy")
        menu.addSeparator()  # Add separator between copy and other options
        edit_tags_action = menu.addAction("Tag Message")
        
        # Add border menu items if applicable
        add_border_action = None
        remove_border_action = None
        if cells_without_borders:
            add_border_action = menu.addAction("Add Border")
        if cells_with_borders:
            remove_border_action = menu.addAction("Remove Border")
        
        action = menu.exec(self.message_table.mapToGlobal(position))
        
        # Handle copy action
        if action == copy_action:
            self.copy_selected_cells()
            return
        
        # Handle border actions
        if action == add_border_action and add_border_action is not None:
            # Check if multiple cells are selected
            if len(selected_indexes) > 1:
                # Multiple cells selected - add a single border around the entire selection
                rows = [idx.row() for idx in selected_indexes if idx.isValid()]
                cols = [idx.column() for idx in selected_indexes if idx.isValid()]
                if rows and cols:
                    min_row = min(rows)
                    max_row = max(rows)
                    min_col = min(cols)
                    max_col = max(cols)
                    # Store the selection region
                    selection_region = (min_row, max_row, min_col, max_col)
                    self.selection_borders.add(selection_region)
            else:
                # Single cell selected - add border to individual cell (original behavior)
                for cell_key in cells_without_borders:
                    self.cell_borders.add(cell_key)
            # Emit dataChanged for affected cells to trigger repaint
            if cells_without_borders or len(selected_indexes) > 1:
                top_left = self.message_model.index(0, 0)
                bottom_right = self.message_model.index(self.message_model.rowCount() - 1, self.message_model.columnCount() - 1)
                self.message_model.dataChanged.emit(top_left, bottom_right, [])
                self.message_table.viewport().update()
                self.save_config()
        elif action == remove_border_action:
            # Check if multiple cells are selected
            if len(selected_indexes) > 1:
                # Multiple cells selected - remove selection region border
                rows = [idx.row() for idx in selected_indexes if idx.isValid()]
                cols = [idx.column() for idx in selected_indexes if idx.isValid()]
                if rows and cols:
                    min_row = min(rows)
                    max_row = max(rows)
                    min_col = min(cols)
                    max_col = max(cols)
                    # Remove the selection region if it exists
                    selection_region = (min_row, max_row, min_col, max_col)
                    self.selection_borders.discard(selection_region)
            else:
                # Single cell selected - remove border from individual cell (original behavior)
                for cell_key in cells_with_borders:
                    self.cell_borders.discard(cell_key)
            # Emit dataChanged for affected cells to trigger repaint
            if cells_with_borders or len(selected_indexes) > 1:
                top_left = self.message_model.index(0, 0)
                bottom_right = self.message_model.index(self.message_model.rowCount() - 1, self.message_model.columnCount() - 1)
                self.message_model.dataChanged.emit(top_left, bottom_right, [])
                self.message_table.viewport().update()
                self.save_config()
        elif action == edit_tags_action:
            # Get current tags from first selected (for multi, we'll apply changes to all)
            selected_rows = sorted(set(idx.row() for idx in selected_indexes))
            first_row = selected_rows[0]
            first_index = self.message_model.index(first_row, 4)
            if not first_index.isValid():
                return
            msg_id = self.message_model.data(first_index, Qt.UserRole)
            if not msg_id:
                return
            current_tags = set()
            for conv_id, messages in self.conversations.items():
                for msg in messages:
                    if msg.get('msg_id') == msg_id:
                        current_tags = msg.get('tags', set()).copy()
                        break
            dialog = MessageTagsDialog(self.available_tags, current_tags, self)
            if dialog.exec() == QDialog.Accepted:
                new_tags = dialog.get_selected_tags()
                self.available_tags.update(new_tags)  # Add any custom to global
                for row in selected_rows:
                    row_index = self.message_model.index(row, 4)
                    if not row_index.isValid():
                        continue
                    msg_id = self.message_model.data(row_index, Qt.UserRole)
                    if not msg_id:
                        continue
                    for conv_id, messages in self.conversations.items():
                        for msg in messages:
                            if msg.get('msg_id') == msg_id:
                                msg['tags'] = new_tags.copy()
                                # Update the model to refresh display
                                conv_id_at_row = self.message_model.getConvIdAtRow(row)
                                if conv_id_at_row:
                                    # Trigger model update for this row
                                    self.message_model.dataChanged.emit(
                                        self.message_model.index(row, 0),
                                        self.message_model.index(row, 10)
                                    )
                                break
                # Refresh the model to show updated tags
                keyword_state = self._get_keyword_state()
                current_messages = self.message_model.messages_data
                self.message_model.setMessages(
                    current_messages,
                    keyword_state,
                    self.compute_row_color,
                    self.get_media_path,
                    self.media_files
                )
                self.save_config()  # Update available_tags

    def copy_selected_cells(self):
        """Copy selected cells to clipboard as tab-separated values."""
        selected_indexes = self.message_table.selectedIndexes()
        if not selected_indexes:
            self.status_bar.showMessage("No cells selected", 2000)
            return
        
        # Organize selected cells by row and column
        # Use a dictionary: {row: {col: value}}
        cells_by_row = {}
        for idx in selected_indexes:
            if not idx.isValid():
                continue
            row = idx.row()
            col = idx.column()
            # Get cell text value
            value = self.message_model.data(idx, Qt.DisplayRole)
            if value is None:
                value = ""
            else:
                value = str(value)
            
            if row not in cells_by_row:
                cells_by_row[row] = {}
            cells_by_row[row][col] = value
        
        if not cells_by_row:
            self.status_bar.showMessage("No valid cells to copy", 2000)
            return
        
        # Build tab-separated text, maintaining row/column structure
        # Get min/max row and column to create a grid
        rows = sorted(cells_by_row.keys())
        cols = sorted(set(col for row_data in cells_by_row.values() for col in row_data.keys()))
        
        lines = []
        for row in rows:
            # Build a row: get values for each column in order, or empty string if not selected
            row_values = []
            for col in cols:
                if col in cells_by_row[row]:
                    row_values.append(cells_by_row[row][col])
                else:
                    row_values.append("")
            lines.append("\t".join(row_values))
        
        # Join rows with newlines
        text = "\n".join(lines)
        
        # Copy to clipboard
        QApplication.clipboard().setText(text)
        
        # Show status message
        cell_count = len(selected_indexes)
        if cell_count == 1:
            self.status_bar.showMessage("Cell copied to clipboard", 2000)
        else:
            self.status_bar.showMessage(f"{cell_count} cells copied to clipboard", 2000)

    def get_row_color(self, row, msg, conv_id):
        return self.compute_row_color(msg, conv_id, row_index=row)

    def view_tagged_messages(self):
        self.status_bar.showMessage("Viewing tagged messages...")
        self.log_message("Viewing tagged messages...")
        tagged_messages = []
        for conv_id, messages in self.conversations.items():
            for msg in messages:
                if msg['tags']:
                    tagged_messages.append((msg, conv_id))
        
        if not tagged_messages:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("No Messages")
            msg.setText("No messages are currently tagged.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.log_message("No tagged messages found.")
            self.status_bar.showMessage("No tagged messages")
            return
        
        dialog = TaggedMessagesDialog(tagged_messages, self)
        dialog.show()
        self.status_bar.showMessage("Tagged messages displayed")

    def update_message_table(self, messages_to_display, message_count, from_cache=False):
        """Update message table using QAbstractTableModel with virtual scrolling.
        
        Args:
            messages_to_display: List of messages to display
            message_count: Number of messages
            from_cache: If True, skip progress dialog for faster cached updates
        """
        # Quick check: If the exact same data is already displayed, skip update entirely
        if self._is_same_data_already_displayed(messages_to_display):
            logger.info("Same data already displayed, skipping table update")
            self.status_bar.showMessage(f"Displayed {message_count} messages (no update needed)")
            return
        
        if not from_cache:
            self.status_bar.showMessage("Updating message table...")
            self.log_message("Updating message table...")
        
        # Show progress for large tables (including cached updates)
        total_items = len(messages_to_display)
        show_progress = total_items > 100
        if show_progress:
            progress = QProgressDialog("Updating table...", None, 0, total_items, self)
            progress.setWindowTitle("Import Progress")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            QApplication.processEvents()
        else:
            progress = None

        # Get keyword state and update model
        keyword_state = self._get_keyword_state()
        
        # Update the model with new data - this is instant with virtual scrolling!
        # The model will only create widgets for visible rows
        self.message_model.setMessages(
            messages_to_display,
            keyword_state,
            self.compute_row_color,
            self.get_media_path,
            self.media_files
        )
        
        # Update row mapping for tracking
        self.table_row_map.clear()
        for row, (item_type, *args) in enumerate(messages_to_display):
            if item_type == 'message':
                msg, index, conv_id = args
                self.table_row_map[msg.get('msg_id', '')] = row
        
        if show_progress and progress:
            progress.setValue(total_items)
            progress.close()
        
        # Resize columns and rows
        if from_cache:
            # Defer resize for cached updates
            QTimer.singleShot(50, lambda: (
                self.message_table.resizeColumnsToContents(),
                self._resize_rows_with_thumbnails()
            ))
        else:
            self.message_table.resizeColumnsToContents()
            self._resize_rows_with_thumbnails()
        
        self.search_results_label.setText(f"Found {message_count} messages")
        
        # Update status message to show completion (clears "Updating message table..." message)
        self.status_bar.showMessage(f"Displayed {message_count} messages")
        
        if logging_enabled:
            logger.debug(f"Displayed {len(messages_to_display)} rows, {message_count} messages")
    
    def _resize_rows_with_thumbnails(self):
        """Set appropriate row heights for rows with thumbnails."""
        # Set row height for all rows that have media thumbnails
        for row in range(self.message_model.rowCount()):
            # Check if this row has media in column 6
            media_index = self.message_model.index(row, 6)
            if media_index.isValid():
                media_info = self.message_model.data(media_index, Qt.UserRole)
                if media_info and isinstance(media_info, dict):
                    content_path = media_info.get('content_path', '')
                    if content_path and os.path.exists(content_path):
                        ext = os.path.splitext(content_path)[1].lower()
                        is_video = ext in ['.mp4', '.webm', '.ogg']
                        is_image = ext in ['.jpg', '.jpeg', '.png', '.gif']
                        if is_video or is_image:
                            # Set row height to accommodate thumbnail + label
                            self.message_table.setRowHeight(row, THUMBNAIL_SIZE[1] + 25)
                            continue
            
            # For non-media rows, use default height or let it auto-size
            # Don't set a height, let the view handle it based on content
    
    def _is_same_data_already_displayed(self, messages_to_display):
        """Check if the exact same messages are already displayed in the table."""
        # If table is empty, data is not displayed
        if self.message_model.rowCount() == 0:
            return False
        
        # Extract message IDs from the new data
        new_msg_ids = set()
        for item_type, *args in messages_to_display:
            if item_type == 'message':
                msg, index, conv_id = args
                msg_id = msg.get('msg_id')
                if msg_id:
                    new_msg_ids.add(msg_id)
        
        # If no messages in new data, not the same
        if not new_msg_ids:
            return False
        
        # Get message IDs currently in model
        current_msg_ids = set()
        for row in range(self.message_model.rowCount()):
            index = self.message_model.index(row, 4)  # Message column
            if index.isValid():
                msg_id = self.message_model.data(index, Qt.UserRole)
                if msg_id:
                    current_msg_ids.add(msg_id)
        
        # If counts don't match, not the same
        if len(current_msg_ids) != len(new_msg_ids):
            return False
        
        # If all message IDs match, it's the same data
        return current_msg_ids == new_msg_ids
    
    def _try_incremental_update(self, messages_to_display, message_count):
        """Strategy 2: Attempt incremental table update instead of full rebuild."""
        # Only attempt incremental update if table already has rows and row map exists
        if not self.table_row_map or self.message_model.rowCount() == 0:
            return False
        
        # Build sets of message IDs for comparison
        current_msg_ids = set(self.table_row_map.keys())
        new_msg_ids = set()
        new_messages_dict = {}  # msg_id -> (msg, index, conv_id)
        
        for item_type, *args in messages_to_display:
            if item_type == 'message':
                msg, index, conv_id = args
                msg_id = msg.get('msg_id')
                if msg_id:
                    new_msg_ids.add(msg_id)
                    new_messages_dict[msg_id] = (msg, index, conv_id)
        
        # Calculate differences
        to_remove = current_msg_ids - new_msg_ids
        to_add = new_msg_ids - current_msg_ids
        to_keep = current_msg_ids & new_msg_ids
        
        # If too many changes, fall back to full rebuild
        total_changes = len(to_remove) + len(to_add)
        total_items = len(current_msg_ids) + len(to_add)
        if total_items == 0:
            return False
        if total_changes > total_items * 0.5:  # If more than 50% changed, rebuild
            return False
        
        # With QAbstractTableModel, incremental updates are handled automatically
        # by the model's virtual scrolling. We just update the model data.
        try:
            keyword_state = self._get_keyword_state()
            self.message_model.setMessages(
                messages_to_display,
                keyword_state,
                self.compute_row_color,
                self.get_media_path,
                self.media_files
            )
            
            # Update row mapping
            self.table_row_map.clear()
            for row, (item_type, *args) in enumerate(messages_to_display):
                if item_type == 'message':
                    msg, index, conv_id = args
                    msg_id = msg.get('msg_id')
                    if msg_id:
                        self.table_row_map[msg_id] = row
            
            self.message_table.resizeColumnsToContents()
            self.search_results_label.setText(f"Found {message_count} messages")
            self.status_bar.showMessage(f"Displayed {message_count} messages (incremental update)")
            
            return True
        except Exception as e:
            logger.error(f"Incremental update failed, falling back to full rebuild: {str(e)}")
            return False
    
    def _create_table_row(self, row, msg, conv_id, bg_color):
        """Strategy 4: Helper method to create a table row (simplified data model layer).
        
        Note: This method is no longer needed with QAbstractTableModel.
        The model's data() method handles row creation automatically.
        Kept for compatibility but not used.
        """
        pass  # Not needed with QAbstractTableModel

    def export_messages(self):
        self.status_bar.showMessage("Exporting messages...")
        self.log_message("Exporting messages...")
        dialog = ExportOptionsDialog(self)
        if dialog.exec() != QDialog.Accepted:
            self.log_message("Export cancelled.")
            self.status_bar.showMessage("Export cancelled")
            return

        selected_options = dialog.get_selected_options()
        selected_fields = dialog.get_selected_fields()
        sort_by = dialog.get_sort_by()
        export_format = dialog.get_export_format()
        blur_csam = dialog.blur_csam_media()
        blur_all = dialog.blur_all_media_export()

        if not selected_options or not selected_fields:
            self.log_message("No options or fields selected.", "ERROR")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("No options or fields selected for export.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Export failed: No options selected")
            return

        file_filter = "HTML Files (*.html)" if export_format == "HTML" else "CSV Files (*.csv)"
        # Create QFileDialog instance for autosizing and centering
        save_dialog = QFileDialog(self)
        save_dialog.setWindowTitle("Save File")
        save_dialog.setFileMode(QFileDialog.AnyFile)
        save_dialog.setAcceptMode(QFileDialog.AcceptSave)
        save_dialog.setNameFilter(file_filter)
        center_and_autosize_dialog(save_dialog, self, width_ratio=0.65, height_ratio=0.7, min_width=700, min_height=550)
        if save_dialog.exec() == QDialog.Accepted:
            output_file = save_dialog.selectedFiles()[0] if save_dialog.selectedFiles() else None
        else:
            output_file = None
        if not output_file:
            self.log_message("Export cancelled.")
            self.status_bar.showMessage("Export cancelled")
            return

        # ------------------ Build messages_to_export ------------------
        messages_to_export = []

        if 'tagged_messages' in selected_options:
            tagged_by_conv = defaultdict(list)
            for conv_id, messages in self.conversations.items():
                for msg in messages:
                    if msg['tags']:
                        tagged_by_conv[conv_id].append(msg)
            for conv_id, messages in tagged_by_conv.items():
                messages_to_export.extend([(msg, conv_id) for msg in messages])

        if 'selected_conversation' in selected_options:
            selection = self.selector.currentText()
            if selection.startswith("Conversation: ") or selection.startswith("Group: "):
                conv_str = selection.replace("Conversation: ", "").replace("Group: ", "").replace(" [Reviewed]", "")
                if selection.startswith("Group: "):
                    conv_id = (conv_str,)
                else:
                    user1, user2 = conv_str.split(" <-> ")
                    conv_id = tuple(sorted([user1, user2]))
                if conv_id in self.conversations:
                    messages_to_export.extend([(msg, conv_id) for msg in self.conversations[conv_id]])

        if 'all_conversations' in selected_options:
            for conv_id, messages in self.conversations.items():
                messages_to_export.extend([(msg, conv_id) for msg in messages])

        if not messages_to_export:
            self.log_message("No messages selected for export.", "ERROR")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warning")
            msg.setText("No messages available to export.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Export failed: No messages")
            return

        if sort_by.startswith("User/Conversation"):
            messages_to_export.sort(key=lambda x: (x[1], x[0]['sent_at']))
        else:
            messages_to_export.sort(key=lambda x: x[0]['sent_at'])

        try:
            # ===================== HTML EXPORT =====================
            if export_format == "HTML":
                output_dir = os.path.dirname(output_file)
                media_dir = os.path.join(output_dir, 'media')
                os.makedirs(media_dir, exist_ok=True)

                copied_media = set()
                file_hashes = {}
                # NEW: mapping content_id -> exported filename (in media/)
                exported_media = {}

                # ---------- Count media files for progress tracking ----------
                media_to_process = []
                for msg, _ in messages_to_export:
                    content_id = msg.get('content_id', '')
                    if content_id and content_id in self.media_files:
                        media_path = self.get_media_path(content_id)
                        if os.path.exists(media_path) and content_id not in copied_media:
                            media_to_process.append((msg, content_id, media_path))
                
                # Create progress dialog for media processing
                total_media = len(media_to_process)
                if total_media > 0:
                    progress = QProgressDialog("Processing media files...", "Cancel", 0, total_media, self)
                    progress.setWindowTitle("Export Progress")
                    progress.setWindowModality(Qt.WindowModal)
                    progress.setMinimumDuration(0)
                    progress.setValue(0)
                    QApplication.processEvents()
                else:
                    progress = None

                # ---------- Copy media & build thumbnails / blur ----------
                processed_count = 0
                for msg, content_id, media_path in media_to_process:
                    # Check if user cancelled
                    if progress and progress.wasCanceled():
                        self.log_message("Media processing cancelled by user", "WARNING")
                        msg_box = QMessageBox(self)
                        msg_box.setIcon(QMessageBox.Warning)
                        msg_box.setWindowTitle("Export Cancelled")
                        msg_box.setText("Media processing was cancelled. The export may be incomplete.")
                        msg_box.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                        msg_box.setStandardButtons(QMessageBox.Ok)
                        msg_box.exec()
                        return
                    
                    # Update progress
                    if progress:
                        processed_count += 1
                        progress.setValue(processed_count)
                        progress.setLabelText(f"Processing media files... ({processed_count}/{total_media})")
                        # Process events every 5 files to keep UI responsive
                        if processed_count % 5 == 0:
                            QApplication.processEvents()
                    
                    if os.path.exists(media_path) and content_id not in copied_media:
                        ext = os.path.splitext(media_path)[1].lower()

                        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.ogg']:
                            thumb_path = media_path if ext in ['.jpg', '.jpeg', '.png', '.gif'] else media_path + '_thumb.jpg'

                            # Create thumbnail for videos if needed
                            if not os.path.exists(thumb_path) and ext in ['.mp4', '.webm', '.ogg']:
                                cap = None
                                try:
                                    cap = cv2.VideoCapture(media_path)
                                    if cap.isOpened():
                                        ret, frame = cap.read()
                                        if ret:
                                            cv2.imwrite(thumb_path, frame)
                                except Exception as e:
                                    self.log_message(f"Failed to generate thumbnail for {media_path}: {str(e)}", "ERROR")
                                    continue
                                finally:
                                    if cap is not None:
                                        cap.release()

                            if os.path.exists(thumb_path):
                                should_blur = blur_all or (blur_csam and 'CSAM' in msg['tags'])

                                if should_blur:
                                    # Generate blurred thumbnail
                                    blurred_thumb_path = os.path.join(output_dir, f"{content_id}_blurred.jpg")
                                    try:
                                        img = cv2.imread(thumb_path)
                                        if img is not None:
                                            blurred_img = cv2.GaussianBlur(img, BLUR_KERNEL_SIZE, BLUR_SIGMA)
                                            cv2.imwrite(blurred_thumb_path, blurred_img)

                                            dest_filename = f"{content_id}_blurred.jpg"
                                            dest_path = os.path.join(media_dir, dest_filename)
                                            shutil.copy2(blurred_thumb_path, dest_path)
                                            file_hashes[dest_filename] = self.compute_file_hash(blurred_thumb_path)
                                            os.remove(blurred_thumb_path)

                                            copied_media.add(content_id)
                                            exported_media[content_id] = dest_filename
                                            self.log_message(f"Created and copied blurred thumbnail for media: {content_id}")
                                        else:
                                            self.log_message(f"Failed to load thumbnail for blurring: {thumb_path}", "ERROR")
                                            continue
                                    except Exception as e:
                                        self.log_message(f"Error creating blurred thumbnail for {content_id}: {str(e)}", "ERROR")
                                        continue
                                else:
                                    # Copy original media
                                    dest_filename = os.path.basename(media_path)
                                    dest_path = os.path.join(media_dir, dest_filename)
                                    shutil.copy2(media_path, dest_path)
                                    file_hashes[dest_filename] = self.compute_file_hash(media_path)
                                    copied_media.add(content_id)
                                    exported_media[content_id] = dest_filename
                                    self.log_message(f"Copied media file: {content_id} to {dest_path}")
                                    if not os.path.exists(dest_path):
                                        self.log_message(f"Failed to verify copied media file at {dest_path}", "ERROR")
                            else:
                                self.log_message(f"No thumbnail available for {content_id}", "ERROR")
                                continue
                        else:
                            # Non-image/video file; we still may want to copy it (no thumbnail)
                            should_blur = blur_all or (blur_csam and 'CSAM' in msg['tags'])
                            if should_blur:
                                self.log_message(f"Skipping non-media file due to blur option: {content_id}")
                                continue
                            else:
                                dest_filename = os.path.basename(media_path)
                                dest_path = os.path.join(media_dir, dest_filename)
                                shutil.copy2(media_path, dest_path)
                                file_hashes[dest_filename] = self.compute_file_hash(media_path)
                                copied_media.add(content_id)
                                exported_media[content_id] = dest_filename
                                self.log_message(f"Copied non-media file: {content_id} to {dest_path}")
                    
                    # Process events after each file to keep UI responsive
                    QApplication.processEvents()

                # Close progress dialog if it was created
                if progress:
                    progress.setValue(total_media)
                    progress.close()
                    QApplication.processEvents()

                # ---------- Copy CSVs and logs ----------
                csv_files = []
                if not hasattr(self, 'csv_files') or not self.csv_files:
                    self.log_message("No CSV files available to export.", "WARNING")
                else:
                    for csv_file in self.csv_files:
                        if os.path.exists(csv_file):
                            src_path = csv_file
                            dest_path = os.path.join(output_dir, os.path.basename(csv_file))
                            try:
                                shutil.copy2(src_path, dest_path)
                                file_hash = self.compute_file_hash(src_path)
                                file_hashes[os.path.basename(csv_file)] = file_hash
                                csv_files.append(os.path.basename(csv_file))
                                self.log_message(f"Copied and hashed CSV file: {os.path.basename(csv_file)} (Hash: {file_hash})")
                            except Exception as e:
                                self.log_message(f"Error copying or hashing CSV file {csv_file}: {str(e)}", "ERROR")
                        else:
                            self.log_message(f"Skipping missing CSV file: {csv_file}", "ERROR")

                log_files = []
                for log_file in os.listdir(self.logs_folder):
                    if log_file.endswith('.txt'):
                        src_path = os.path.join(self.logs_folder, log_file)
                        dest_path = os.path.join(output_dir, log_file)
                        try:
                            shutil.copy2(src_path, dest_path)
                            file_hashes[log_file] = self.compute_file_hash(src_path)
                            log_files.append(log_file)
                            self.log_message(f"Copied log file: {log_file}")
                        except Exception as e:
                            self.log_message(f"Error copying log file {log_file}: {str(e)}", "ERROR")

                # ---------- Stats summary ----------
                stats_summary = ""
                if self.df is not None:
                    total_messages = len(messages_to_export)
                    unique_conversations = len(set(conv_id for _, conv_id in messages_to_export))
                    unique_users = len(set(msg['sender'] for msg, _ in messages_to_export) |
                                       set(msg['receiver'] for msg, _ in messages_to_export))
                    tagged_count = sum(1 for msg, _ in messages_to_export if msg['tags'])
                    keywords, whole_word = self._get_keyword_state()
                    keyword_hits = (
                        sum(
                            1 for msg, _ in messages_to_export
                            if self.is_keyword_match(msg['message'], keywords, whole_word)
                        ) if keywords else 0
                    )
                    total_media = len([msg for msg, _ in messages_to_export if msg.get('content_id', '')])
                    stats_summary = (
                        f"<h3>Export Summary</h3>"
                        f"<p>Total Messages: {total_messages}"
                        f"<br>Unique Conversations: {unique_conversations}"
                        f"<br>Unique Users: {unique_users}"
                        f"<br>Tagged Messages: {tagged_count}"
                        f"<br>Keyword Hits: {keyword_hits}"
                        f"<br>Total Media: {total_media}</p>"
                    )

                # ---------- Write HTML ----------
                # Get colors from theme manager for both light and dark modes
                light_theme = ThemeManager(False)
                light_theme.load_custom_colors(
                    custom_colors_light=self.theme_manager.custom_colors_light,
                    custom_colors_dark={}
                )
                dark_theme = ThemeManager(True)
                dark_theme.load_custom_colors(
                    custom_colors_light={},
                    custom_colors_dark=self.theme_manager.custom_colors_dark
                )
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
                    f.write("<meta charset='UTF-8'>\n<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
                    f.write("<title>Kik Messages Export</title>\n")
                    # Generate CSS with theme colors
                    # Get color values first
                    bg_main_light = light_theme.get_color('bg_main')
                    text_secondary_light = light_theme.get_color('text_secondary')
                    bg_table_light = light_theme.get_color('bg_table')
                    border_light = light_theme.get_color('border')
                    row_alternate_light = light_theme.get_color('row_alternate')
                    bg_table_hover_light = light_theme.get_color('bg_table_hover')
                    tag_csam_light = light_theme.get_color('tag_csam')
                    tag_evidence_light = light_theme.get_color('tag_evidence')
                    tag_interest_light = light_theme.get_color('tag_interest')
                    tag_custom_light = light_theme.get_color('tag_custom')
                    keyword_hit_light = light_theme.get_color('keyword_hit')
                    sender1_light = light_theme.get_color('sender1')
                    sender2_light = light_theme.get_color('sender2')
                    bg_legend_light = light_theme.get_color('bg_legend')
                    
                    bg_main_dark = dark_theme.get_color('bg_main')
                    text_primary_dark = dark_theme.get_color('text_primary')
                    bg_table_dark = dark_theme.get_color('bg_table')
                    row_alternate_dark = dark_theme.get_color('row_alternate')
                    bg_table_hover_dark = dark_theme.get_color('bg_table_hover')
                    tag_csam_dark = dark_theme.get_color('tag_csam')
                    tag_evidence_dark = dark_theme.get_color('tag_evidence')
                    tag_interest_dark = dark_theme.get_color('tag_interest')
                    tag_custom_dark = dark_theme.get_color('tag_custom')
                    keyword_hit_dark = dark_theme.get_color('keyword_hit')
                    sender1_dark = dark_theme.get_color('sender1')
                    sender2_dark = dark_theme.get_color('sender2')
                    bg_legend_dark = dark_theme.get_color('bg_legend')
                    
                    css = f"""<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background-color: {bg_main_light}; transition: background-color 0.3s, color: 0.3s; }}
h2 {{ color: {text_secondary_light}; }}
.controls {{ margin-bottom: 20px; }}
select {{ padding: 8px; font-size: 16px; border-radius: 4px; }}
table {{ border-collapse: collapse; width: 100%; background-color: {bg_table_light}; box-shadow: 0 2px 5px rgba(0,0,0,0.1); table-layout: auto; }}
th, td {{ border: 1px solid {border_light}; padding: 12px; text-align: left; word-wrap: break-word; max-width: 300px; }}
th {{ background-color: #6c757d; color: white; cursor: pointer; position: sticky; top: 0; z-index: 2; }}
th.sort-asc::after {{ content: ' ↑'; }}
th.sort-desc::after {{ content: ' ↓'; }}
tr:nth-child(even) {{ background-color: {row_alternate_light}; }}
tr:hover {{ background-color: {bg_table_hover_light}; }}
tr.tag-csam {{ background-color: {tag_csam_light} !important; color: #fff; }}
tr.tag-evidence {{ background-color: {tag_evidence_light} !important; color: #000; }}
tr.tag-interest {{ background-color: {tag_interest_light} !important; color: #000; }}
tr.tag-custom {{ background-color: {tag_custom_light}; }}
tr.keyword-hit {{ background-color: {keyword_hit_light}; }}
tr.sender1 {{ background-color: {sender1_light}; }}
tr.sender2 {{ background-color: {sender2_light}; }}
tr.hidden {{ display: none; }}
img, video {{ max-width: 100px; height: auto; cursor: pointer; }}
a.media-link {{ text-decoration: none; }}
.media-container {{ display: inline-block; }}
.file-hashes {{ margin-top: 20px; font-size: 14px; }}
#darkModeToggle {{ padding: 8px; background-color: #333; color: #fff; border: none; cursor: pointer; }}
body.dark-mode {{ background-color: {bg_main_dark}; color: {text_primary_dark}; }}
body.dark-mode table {{ background-color: {bg_table_dark}; }}
body.dark-mode th {{ background-color: #808080; }}
body.dark-mode tr:nth-child(even) {{ background-color: {row_alternate_dark}; }}
body.dark-mode tr:hover {{ background-color: {bg_table_hover_dark}; }}
body.dark-mode tr.tag-csam {{ background-color: {tag_csam_dark} !important; }}
body.dark-mode tr.tag-evidence {{ background-color: {tag_evidence_dark} !important; }}
body.dark-mode tr.tag-interest {{ background-color: {tag_interest_dark} !important; }}
body.dark-mode tr.tag-custom {{ background-color: {tag_custom_dark}; }}
body.dark-mode tr.keyword-hit {{ background-color: {keyword_hit_dark}; }}
body.dark-mode tr.sender1 {{ background-color: {sender1_dark}; }}
body.dark-mode tr.sender2 {{ background-color: {sender2_dark}; }}
#searchInput {{ padding: 8px; width: 200px; margin-bottom: 10px; }}
#tagFilter {{ padding: 8px; margin-left: 10px; }}
@media (max-width: 768px) {{ table {{ font-size: 12px; }} th, td {{ padding: 8px; }} img, video {{ max-width: 80px; }} }}
.tooltip {{ position: relative; display: inline-block; }}
.tooltip .tooltiptext {{ visibility: hidden; width: 120px; background-color: black; color: #fff; text-align: center; border-radius: 6px; padding: 5px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -60px; opacity: 0; transition: opacity 0.3s; }}
.tooltip:hover .tooltiptext {{ visibility: visible; opacity: 1; }}
.legend {{ margin: 10px 0; padding: 10px; background-color: {bg_legend_light}; border-radius: 5px; }}
.legend-item {{ padding: 5px 10px; margin: 2px; border-radius: 3px; display: inline-block; font-weight: bold; }}
body.dark-mode .legend {{ background-color: {bg_legend_dark}; }}
</style>
"""
                    f.write(css)
                    f.write("""
<script>
function applyFilters() {
    const convSelect = document.getElementById('convSelect');
    const selectedConv = convSelect.value;
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const tagFilter = document.getElementById('tagFilter').value;
    const rows = document.querySelectorAll('tr[data-conversation]');
    rows.forEach(row => {
        const rowConv = row.getAttribute('data-conversation');
        // For note rows, only show when the specific conversation is selected (not "all")
        if (row.classList.contains('conversation-note')) {
            if (selectedConv === 'all' || rowConv !== selectedConv) {
                row.classList.add('hidden');
            } else {
                row.classList.remove('hidden');
            }
        } else {
            // Regular message rows
            const convMatch = selectedConv === 'all' || rowConv === selectedConv;
            const text = Array.from(row.cells).map(cell => cell.textContent.toLowerCase()).join(' ');
            const searchMatch = searchInput === '' || text.includes(searchInput);
            const tagMatch = tagFilter === '' || row.classList.contains(tagFilter);
            if (convMatch && searchMatch && tagMatch) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        }
    });
}

function toggleAllNotes() {
    const allNotesSection = document.getElementById('allNotesSection');
    const toggleButton = document.getElementById('toggleAllNotesBtn');
    if (allNotesSection.style.display === 'none' || allNotesSection.style.display === '') {
        allNotesSection.style.display = 'block';
        toggleButton.textContent = 'Hide All Notes';
    } else {
        allNotesSection.style.display = 'none';
        toggleButton.textContent = 'View All Notes';
    }
}

function toggleFileHashes() {
    const fileHashesSection = document.getElementById('fileHashesSection');
    const toggleButton = document.getElementById('toggleFileHashesBtn');
    if (fileHashesSection.style.display === 'none' || fileHashesSection.style.display === '') {
        fileHashesSection.style.display = 'block';
        toggleButton.textContent = 'Hide File Hashes';
    } else {
        fileHashesSection.style.display = 'none';
        toggleButton.textContent = 'View File Hashes';
    }
}
function openMedia(src) {
    window.open(src, '_blank');
}
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}
if (localStorage.getItem('darkMode') === 'true') { toggleDarkMode(); }
// Hide all note rows on page load when "all" is selected
window.addEventListener('DOMContentLoaded', function() {
    const noteRows = document.querySelectorAll('tr.conversation-note');
    noteRows.forEach(row => {
        row.classList.add('hidden');
    });
});
function sortTable(colIndex) {
    const table = document.querySelector('table');
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows).filter(row => !row.classList.contains('hidden') && row.getAttribute('data-conversation') !== null);
    const header = table.tHead.rows[0].cells[colIndex];
    const isAsc = header.classList.contains('sort-asc');
    Array.from(table.tHead.rows[0].cells).forEach((th, idx) => {
        if (idx !== colIndex) {
            th.classList.remove('sort-asc', 'sort-desc');
        }
    });
    header.classList.toggle('sort-asc', !isAsc);
    header.classList.toggle('sort-desc', isAsc);
    function getSortValue(cell) {
        let sortVal = cell.getAttribute('data-sort-value');
        if (sortVal !== null) {
            let num = parseFloat(sortVal);
            return isNaN(num) ? sortVal : num;
        }
        let text = cell.textContent.trim();
        let date = Date.parse(text);
        if (!isNaN(date)) {
            return new Date(date);
        }
        let num = parseFloat(text);
        if (!isNaN(num)) {
            return num;
        }
        return text.toLowerCase();
    }
    rows.sort((a, b) => {
        let valA = getSortValue(a.cells[colIndex]);
        let valB = getSortValue(b.cells[colIndex]);
        if (valA instanceof Date && valB instanceof Date) {
            return (valA - valB) * (isAsc ? 1 : -1);
        } else if (typeof valA === 'number' && typeof valB === 'number') {
            return (valA - valB) * (isAsc ? 1 : -1);
        } else {
            return (valA > valB ? 1 : -1) * (isAsc ? 1 : -1);
        }
    });
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    applyFilters();
}
</script>
</head>
""")
                    f.write("<body>\n")
                    f.write("<button id='darkModeToggle' onclick='toggleDarkMode()'>Toggle Dark Mode</button>\n")
                    f.write(stats_summary)
                    f.write("<h2>Kik Messages Export</h2>\n")
                    
                    # Add "View All Notes" section if there are any notes
                    include_notes = 'notes' in selected_fields
                    notes_to_export = {conv_id: note for conv_id, note in self.conversation_notes.items() 
                                      if conv_id in set(conv_id for _, conv_id in messages_to_export) and note}
                    if include_notes and notes_to_export:
                        f.write("<div style='margin: 20px 0;'>")
                        f.write("<button id='toggleAllNotesBtn' onclick='toggleAllNotes()' style='padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; margin-bottom: 10px;'>View All Notes</button>")
                        f.write("</div>")
                        f.write("<div id='allNotesSection' style='display: none; margin: 20px 0;'>")
                        f.write("<h3>All Investigative Notes</h3>")
                        for conv_id, note in sorted(notes_to_export.items(), key=lambda x: x[0][0] if len(x[0]) > 0 else ''):
                            conv_str = conv_id[0] if len(conv_id) == 1 else f"{conv_id[0]} <-> {conv_id[1]}"
                            f.write(f"<div style='")
                            f.write("background: linear-gradient(to right, #d4e6f1 0%, #e8f4f8 100%); ")
                            f.write("border-left: 4px solid #3498db; ")
                            f.write("padding: 12px 15px; ")
                            f.write("margin: 10px 0; ")
                            f.write("font-size: 13px; ")
                            f.write("line-height: 1.6; ")
                            f.write("box-shadow: 0 2px 4px rgba(0,0,0,0.1); ")
                            f.write("border-radius: 4px;'>")
                            f.write(f"<div style='display: flex; align-items: flex-start;'>")
                            f.write(f"<span style='font-size: 16px; margin-right: 8px; color: #2980b9;'>📝</span>")
                            f.write(f"<div style='flex: 1;'>")
                            f.write(f"<div style='font-weight: 600; color: #2c3e50; margin-bottom: 5px; font-size: 14px;'>")
                            f.write(f"<strong>{html.escape(conv_str)}</strong> - Investigative Note:")
                            f.write(f"</div>")
                            f.write(f"<div style='color: #34495e; white-space: pre-wrap;'>")
                            f.write(html.escape(note))
                            f.write(f"</div>")
                            f.write(f"</div>")
                            f.write(f"</div>")
                            f.write("</div>")
                        f.write("</div>")
                    
                    # Color legend using theme colors
                    f.write(f"""
<div class="legend">
<h3>Color Legend</h3>
<span class="legend-item" style="background-color: {light_theme.get_color('tag_csam')}; color: white;">CSAM</span>
<span class="legend-item" style="background-color: {light_theme.get_color('tag_evidence')}; color: black;">Evidence</span>
<span class="legend-item" style="background-color: {light_theme.get_color('tag_interest')}; color: black;">Of Interest</span>
<span class="legend-item" style="background-color: {light_theme.get_color('tag_custom')}; color: black;">Custom Tag</span>
<span class="legend-item" style="background-color: {light_theme.get_color('keyword_hit')}; color: black;">Keyword Hit</span>
<span class="legend-item" style="background-color: {light_theme.get_color('sender1')}; color: black;">Sender 1</span>
<span class="legend-item" style="background-color: {light_theme.get_color('sender2')}; color: black;">Sender 2</span>
</div>
""")
                    f.write("<div class='controls'>\n")
                    f.write("    <label for='convSelect'>Select Conversation: </label>\n")
                    f.write("    <select id='convSelect' onchange='applyFilters()'>\n")
                    f.write("        <option value='all'>All Conversations</option>\n")
                    conv_set = set(conv_id for _, conv_id in messages_to_export)
                    for conv_id in sorted(conv_set, key=lambda x: x[0]):
                        conv_str = conv_id[0] if len(conv_id) == 1 else f"{conv_id[0]} <-> {conv_id[1]}"
                        f.write(f"        <option value='{html.escape(conv_str)}'>{html.escape(conv_str)}</option>\n")
                    f.write("    </select>\n")
                    f.write("    <label for='tagFilter'>Filter by Tag: </label>\n")
                    f.write("    <select id='tagFilter' onchange='applyFilters()'>\n")
                    f.write("        <option value=''>All Tags</option>\n")
                    f.write("        <option value='tag-csam'>CSAM</option>\n")
                    f.write("        <option value='tag-evidence'>Evidence</option>\n")
                    f.write("        <option value='tag-interest'>Of Interest</option>\n")
                    f.write("        <option value='tag-custom'>Custom</option>\n")
                    f.write("        <option value='keyword-hit'>Keyword Hit</option>\n")
                    f.write("    </select>\n")
                    f.write("    <input type='text' id='searchInput' onkeyup='applyFilters()' placeholder='Search table...'>\n")
                    f.write("</div>\n")

                    f.write("<table>\n<tr>\n")
                    headers = {
                        'conversation': 'Conversation',
                        'msg_id': 'Message ID',
                        'sender': 'Sender',
                        'receiver': 'Receiver',
                        'message': 'Message',
                        'timestamp': 'Timestamp',
                        'content_id': 'Media',
                        'ip': 'IP Address',
                        'port': 'Port',
                        'tags': 'Tags',
                        'source': 'Source',
                        'line_number': 'Line Number',
                        'notes': 'Notes',
                    }
                    # Map field names to table column indices
                    field_to_column = {
                        'sender': 2,
                        'receiver': 3,
                        'message': 4,
                        'tags': 5,
                        'content_id': 6,
                        'ip': 7,
                        'port': 8,
                        'source': 9,
                        'line_number': 10,
                        'timestamp': 1,  # Use time column (1) for timestamp field
                        'msg_id': -1,  # Not a table column, so no borders
                        'conversation': -1,  # Not a table column
                        'notes': -1,  # Not a table column
                    }
                    # Get border color from theme
                    border_color = light_theme.get_color('cell_border')
                    for i, field in enumerate(selected_fields):
                        f.write(f"<th onclick='sortTable({i})'>{headers[field]}</th>\n")
                    f.write("</tr>\n")

                    keywords = self.keyword_lists.get(self.selected_keyword_list, [])
                    whole_word = self.keyword_whole_word.get(self.selected_keyword_list, False)

                    # Track current conversation for notes display (only if notes field is selected)
                    # include_notes is already defined earlier for the "View All Notes" section
                    current_conv_id = None
                    for msg, conv_id in messages_to_export:
                        # Show conversation note header when conversation changes (only if notes are selected and note exists)
                        if include_notes and conv_id != current_conv_id:
                            current_conv_id = conv_id
                            # Only show note if this conversation actually has a note
                            if conv_id in self.conversation_notes and self.conversation_notes[conv_id]:
                                note = self.conversation_notes[conv_id]
                                conv_str = conv_id[0] if len(conv_id) == 1 else f"{conv_id[0]} <-> {conv_id[1]}"
                                f.write(f"<tr class='conversation-note' data-conversation='{html.escape(conv_str)}'><td colspan='{len(selected_fields)}' style='")
                                f.write("background: linear-gradient(to right, #d4e6f1 0%, #e8f4f8 100%); ")
                                f.write("border-left: 4px solid #3498db; ")
                                f.write("padding: 12px 15px; ")
                                f.write("margin: 5px 0; ")
                                f.write("font-size: 13px; ")
                                f.write("line-height: 1.6; ")
                                f.write("box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>")
                                f.write(f"<div style='display: flex; align-items: flex-start;'>")
                                f.write(f"<span style='font-size: 16px; margin-right: 8px; color: #2980b9;'>📝</span>")
                                f.write(f"<div style='flex: 1;'>")
                                f.write(f"<div style='font-weight: 600; color: #2c3e50; margin-bottom: 5px; font-size: 14px;'>")
                                f.write(f"Investigative Note:")
                                f.write(f"</div>")
                                f.write(f"<div style='color: #34495e; white-space: pre-wrap;'>")
                                f.write(html.escape(note))
                                f.write(f"</div>")
                                f.write(f"</div>")
                                f.write(f"</div>")
                                f.write("</td></tr>\n")
                        elif not include_notes:
                            current_conv_id = conv_id  # Still track for conversation changes
                        conv_str = conv_id[0] if len(conv_id) == 1 else f"{conv_id[0]} <-> {conv_id[1]}"
                        tag_class = ''
                        if 'CSAM' in msg['tags']:
                            tag_class = 'tag-csam'
                        elif 'Evidence' in msg['tags']:
                            tag_class = 'tag-evidence'
                        elif 'Of Interest' in msg['tags']:
                            tag_class = 'tag-interest'
                        elif msg['tags']:
                            tag_class = 'tag-custom'

                        keyword_class = 'keyword-hit' if any(
                            re.search(r'\b' + re.escape(kw.lower()) + r'\b', msg['message'].lower())
                            if whole_word else kw.lower() in msg['message'].lower()
                            for kw in keywords
                        ) else ''

                        sender_class = ''
                        sender1, sender2 = conv_id if len(conv_id) == 2 else (msg['sender'], None)
                        if msg['sender'] == sender1:
                            sender_class = 'sender1'
                        elif sender2 and msg['sender'] == sender2:
                            sender_class = 'sender2'

                        row_classes = f"{tag_class} {keyword_class} {sender_class}"
                        f.write(f"<tr data-conversation='{html.escape(conv_str)}' class='{row_classes}'>\n")

                        # Get msg_id for border checking
                        msg_id = msg.get('msg_id', '')
                        
                        for i, field in enumerate(selected_fields):
                            if field == 'conversation':
                                value = html.escape(conv_str)
                                sort_val = conv_str.lower()
                                # Check if this cell has a border (conversation is not a table column, so no border)
                                cell_style = ""

                            elif field == 'message':
                                msg_text = msg.get('message', '')
                                # Replace NaN values and "nan" strings with empty string
                                if pd.isna(msg_text):
                                    msg_text = ''
                                else:
                                    msg_text_str = str(msg_text).strip()
                                    if msg_text_str.lower() in ('nan', 'none'):
                                        msg_text = ''
                                    else:
                                        msg_text = msg_text_str
                                value = html.escape(msg_text)
                                sort_val = msg_text.lower()
                                # Check if this cell has a border
                                column_index = field_to_column.get(field, -1)
                                has_border = column_index >= 0 and msg_id and (msg_id, column_index) in self.cell_borders
                                cell_style = f" style='border: 3px solid {border_color} !important;'" if has_border else ""

                            elif field == 'timestamp':
                                value = msg['sent_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(msg['sent_at']) else 'Invalid Timestamp'
                                sort_val = value
                                # Check if this cell has a border
                                column_index = field_to_column.get(field, -1)
                                has_border = column_index >= 0 and msg_id and (msg_id, column_index) in self.cell_borders
                                cell_style = f" style='border: 3px solid {border_color} !important;'" if has_border else ""

                            elif field == 'content_id':
                                content_id = msg.get('content_id', '')
                                # Replace NaN values and "nan" strings with empty string
                                if pd.isna(content_id):
                                    content_id = ''
                                else:
                                    content_id_str = str(content_id).strip()
                                    if content_id_str.lower() in ('nan', 'none'):
                                        content_id = ''
                                    else:
                                        content_id = content_id_str
                                # Check if this cell has a border
                                column_index = field_to_column.get(field, -1)
                                has_border = column_index >= 0 and msg_id and (msg_id, column_index) in self.cell_borders
                                cell_style = f" style='border: 3px solid {border_color} !important;'" if has_border else ""
                                if content_id and content_id in exported_media:
                                    exported_name = exported_media[content_id]
                                    rel_path = f"media/{urllib.parse.quote(exported_name)}"
                                    ext = os.path.splitext(exported_name)[1].lower()

                                    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                                        value = (
                                            f"<a href='{rel_path}' target='_blank' class='media-link'>"
                                            f"<img src='{rel_path}' alt='{html.escape(content_id)}' "
                                            f"title='Click to view full image'></a>"
                                        )
                                    elif ext in ['.mp4', '.webm', '.ogg']:
                                        value = (
                                            f"<a href='{rel_path}' target='_blank' class='media-link' "
                                            f"title='Click to view full video'>"
                                            f"<video><source src='{rel_path}' type='video/{ext[1:]}'>"
                                            f"{html.escape(content_id)}</video></a>"
                                        )
                                    else:
                                        value = f"<a href='{rel_path}' target='_blank'>{html.escape(content_id)}</a>"
                                    sort_val = content_id
                                else:
                                    # No exported media; just show the ID
                                    if content_id:
                                        self.log_message(f"Content ID {content_id} has no exported media entry.", "ERROR")
                                    value = html.escape(content_id)
                                    sort_val = content_id

                            elif field == 'port':
                                raw_val = msg.get('port', '')
                                # Replace NaN values with empty string
                                if pd.isna(raw_val):
                                    raw_val = ''
                                sort_val = str(raw_val)
                                value = html.escape(str(raw_val))
                                # Check if this cell has a border
                                column_index = field_to_column.get(field, -1)
                                has_border = column_index >= 0 and msg_id and (msg_id, column_index) in self.cell_borders
                                cell_style = f" style='border: 3px solid {border_color} !important;'" if has_border else ""

                            elif field == 'tags':
                                tags_set = msg['tags']
                                pri = max([self.tag_priorities.get(t, (0, '#e0ffe0'))[0] for t in tags_set] or [0])
                                tags_str = ', '.join(sorted(tags_set))
                                value = (
                                    f"<span class='tooltip'>{html.escape(tags_str)}"
                                    f"<span class='tooltiptext'>Tags: {html.escape(tags_str)}</span></span>"
                                    if tags_str else ''
                                )
                                sort_val = pri
                                # Check if this cell has a border
                                column_index = field_to_column.get(field, -1)
                                has_border = column_index >= 0 and msg_id and (msg_id, column_index) in self.cell_borders
                                cell_style = f" style='border: 3px solid {border_color} !important;'" if has_border else ""
                                f.write(f"<td data-sort-value=\"{sort_val}\"{cell_style}>{value}</td>\n")
                                continue

                            elif field == 'notes':
                                # Notes are shown as a separate row above messages, so this cell is empty
                                value = ''
                                sort_val = ''
                                # Notes is not a table column, so no border
                                cell_style = ""
                                f.write(f"<td data-sort-value=\"{sort_val}\"{cell_style}>{value}</td>\n")
                                continue

                            else:
                                # Generic field: includes 'msg_id', 'sender', 'receiver', 'ip', 'source', 'line_number', etc.
                                raw_val = msg.get(field, '')
                                # Replace NaN values and "nan" strings with empty string
                                if pd.isna(raw_val):
                                    raw_val = ''
                                else:
                                    raw_val_str = str(raw_val).strip()
                                    if raw_val_str.lower() in ('nan', 'none'):
                                        raw_val = ''
                                    else:
                                        raw_val = raw_val_str
                                if isinstance(raw_val, (int, float)):
                                    sort_val = raw_val
                                else:
                                    sort_val = str(raw_val).lower()
                                value = html.escape(str(raw_val))
                                # Check if this cell has a border
                                column_index = field_to_column.get(field, -1)
                                has_border = column_index >= 0 and msg_id and (msg_id, column_index) in self.cell_borders
                                cell_style = f" style='border: 3px solid {border_color} !important;'" if has_border else ""

                            f.write(
                                f"<td data-sort-value=\"{html.escape(str(sort_val))}\" "
                                f"title='{html.escape(str(raw_val)) if field in ['sender', 'receiver', 'message'] else ''}'{cell_style}>"
                                f"{value}</td>\n"
                            )

                        f.write("</tr>\n")

                    f.write("</table>\n")
                    
                    # File Hashes section with toggle button
                    if file_hashes:
                        f.write("<div style='margin: 30px 0;'>")
                        f.write("<button id='toggleFileHashesBtn' onclick='toggleFileHashes()' style='padding: 10px 20px; background-color: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; margin-bottom: 10px;'>View File Hashes</button>")
                        f.write("</div>")
                        f.write("<div id='fileHashesSection' style='display: none; margin: 20px 0;'>")
                        f.write("<h3 style='color: #2c3e50; margin-bottom: 15px;'>File Hashes (MD5)</h3>")
                        f.write("<div style='background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px;'>")
                        f.write("<table style='width: 100%; border-collapse: collapse; background-color: white;'>")
                        f.write("<thead><tr style='background-color: #27ae60; color: white;'>")
                        f.write("<th style='padding: 10px; text-align: left; border: 1px solid #dee2e6;'>Filename</th>")
                        f.write("<th style='padding: 10px; text-align: left; border: 1px solid #dee2e6;'>MD5 Hash</th>")
                        f.write("</tr></thead><tbody>")
                        for filename, file_hash in sorted(file_hashes.items()):
                            f.write("<tr style='border-bottom: 1px solid #dee2e6;'>")
                            f.write(f"<td style='padding: 10px; border: 1px solid #dee2e6; font-weight: 500;'>{html.escape(filename)}</td>")
                            f.write(f"<td style='padding: 10px; border: 1px solid #dee2e6; font-family: monospace; font-size: 12px; word-break: break-all;'>{html.escape(file_hash)}</td>")
                            f.write("</tr>")
                        f.write("</tbody></table>")
                        f.write("</div>")
                        f.write("</div>")
                    
                    f.write("</body>\n</html>")

            # ===================== CSV EXPORT =====================
            else:
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    headers_row = [opt for opt in selected_fields]
                    writer.writerow(headers_row)

                    # Track current conversation for notes in CSV
                    current_conv_id = None
                    for msg, conv_id in messages_to_export:
                        row = []
                        conv_str = conv_id[0] if len(conv_id) == 1 else f"{conv_id[0]} <-> {conv_id[1]}"
                        for field in headers_row:
                            if field == 'conversation':
                                value = conv_str
                            elif field == 'timestamp':
                                value = msg['sent_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(msg['sent_at']) else 'Invalid Timestamp'
                            elif field == 'message':
                                msg_text = msg.get('message', '')
                                # Replace NaN values and "nan" strings with empty string
                                if pd.isna(msg_text):
                                    value = ''
                                else:
                                    msg_text_str = str(msg_text).strip()
                                    value = '' if msg_text_str.lower() in ('nan', 'none') else msg_text_str
                            elif field == 'port':
                                port_val = msg.get('port', '')
                                # Replace NaN values and "nan" strings with empty string
                                if pd.isna(port_val):
                                    value = ''
                                else:
                                    port_str = str(port_val).strip()
                                    value = '' if port_str.lower() in ('nan', 'none') else port_str
                            elif field == 'content_id':
                                content_id = msg.get('content_id', '')
                                # Replace NaN values and "nan" strings with empty string
                                if pd.isna(content_id):
                                    value = ''
                                else:
                                    content_id_str = str(content_id).strip()
                                    value = '' if content_id_str.lower() in ('nan', 'none') else content_id_str
                            elif field == 'tags':
                                value = ', '.join(sorted(msg['tags']))
                            elif field == 'notes':
                                # Include note for this conversation if it exists
                                if conv_id != current_conv_id:
                                    current_conv_id = conv_id
                                value = self.conversation_notes.get(conv_id, '')
                            else:
                                raw_val = msg.get(field, '')
                                # Replace NaN values and "nan" strings with empty string
                                if pd.isna(raw_val):
                                    value = ''
                                else:
                                    val_str = str(raw_val).strip()
                                    value = '' if val_str.lower() in ('nan', 'none') else val_str
                            row.append(value)
                        writer.writerow(row)

            self.log_message(f"Exported {len(messages_to_export)} messages to {output_file}")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText(f"Exported {len(messages_to_export)} messages to {output_file}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Export completed")

        except Exception as e:
            self.log_message(f"Error exporting messages: {str(e)}", "ERROR")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Error exporting messages: {str(e)}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Export failed")
            
    def populate_keyword_dropdown(self):
        self.keyword_selector.clear()
        for list_name in sorted(self.keyword_lists.keys()):
            self.keyword_selector.addItem(list_name)
        self.keyword_selector.setCurrentText(self.selected_keyword_list)

    def update_selected_keyword_list(self, text):
        self.selected_keyword_list = text
        self.save_config()
        self.schedule_search()
        
    def _parse_version(self, v: str):
        # strip common 'v' prefix and split into numeric parts for comparison
        v = v.strip().lstrip('vV')
        parts = []
        for token in v.replace('-', '.').split('.'):
            if token.isdigit():
                parts.append(int(token))
            else:
                # Non-numeric tokens -> keep as-is for a stable tuple compare
                parts.append(token)
        return tuple(parts)
        
    def check_for_updates(self):
    # Disable the button while checking
        self.update_button.setEnabled(False)
        self.status_bar.showMessage("Checking for updates...")

        self._update_worker = UpdateCheckWorker()
        self._update_worker.result.connect(self._on_update_check_result)
        self._update_worker.start()

    def auto_check_for_updates(self):
        """Automatically check for updates on startup. Only shows message if update is available."""
        self.status_bar.showMessage("Checking for updates...")

        self._auto_update_worker = UpdateCheckWorker()
        self._auto_update_worker.result.connect(self._on_auto_update_check_result)
        self._auto_update_worker.start()

    def _on_update_check_result(self, error, data):
        # Re-enable the button
        self.update_button.setEnabled(True)

        if error:
            logger.error(f"Update check failed: {error}")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Update Check")
            msg.setText(f"Could not check for updates:\n{error}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Update check failed")
            return

        try:
            latest_tag = str(data.get("tag_name", "")).strip()
            latest_name = str(data.get("name", latest_tag)).strip() or latest_tag
            latest_url  = str(data.get("html_url", GITHUB_RELEASES_PAGE)).strip() or GITHUB_RELEASES_PAGE

            cur_v = self._parse_version(APP_VERSION)
            lat_v = self._parse_version(latest_tag) if latest_tag else cur_v

            if lat_v > cur_v:
                # Newer release available
                msg = QMessageBox(self)
                msg.setWindowTitle("Update Available")
                # Remove question mark help button
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setTextFormat(Qt.RichText)
                msg.setText(
                    f"<b>A new version is available.</b><br><br>"
                    f"Current version: <code>{APP_VERSION}</code><br>"
                    f"Latest release: <code>{html.escape(latest_name)}</code>"
                )
                open_btn = msg.addButton("Open Releases Page", QMessageBox.AcceptRole)
                msg.addButton(QMessageBox.Close)
                # Center and autosize dialog
                center_and_autosize_dialog(msg, self, width_ratio=0.45, height_ratio=0.35, min_width=500, min_height=250)
                msg.exec()
                if msg.clickedButton() == open_btn:
                    webbrowser.open(latest_url or GITHUB_RELEASES_PAGE)
                self.status_bar.showMessage("Update available")
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Up to Date")
                msg.setText(f"You are running the latest version ({APP_VERSION}).")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                self.status_bar.showMessage("You are up to date")
        except Exception as e:
            logger.error(f"Error parsing update data: {e}")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Update Check")
            msg.setText("Unexpected response from GitHub.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Update check failed")

    def _on_auto_update_check_result(self, error, data):
        """Handle automatic update check results. Only shows message if update is available."""
        # Clear the status message
        self.status_bar.showMessage("")

        if error:
            # Silently fail for automatic checks - don't show error message
            logger.error(f"Automatic update check failed: {error}")
            return

        try:
            latest_tag = str(data.get("tag_name", "")).strip()
            latest_name = str(data.get("name", latest_tag)).strip() or latest_tag
            latest_url  = str(data.get("html_url", GITHUB_RELEASES_PAGE)).strip() or GITHUB_RELEASES_PAGE

            cur_v = self._parse_version(APP_VERSION)
            lat_v = self._parse_version(latest_tag) if latest_tag else cur_v

            if lat_v > cur_v:
                # Newer release available - show message
                msg = QMessageBox(self)
                msg.setWindowTitle("Update Available")
                # Remove question mark help button
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setTextFormat(Qt.RichText)
                msg.setText(
                    f"<b>A new version is available.</b><br><br>"
                    f"Current version: <code>{APP_VERSION}</code><br>"
                    f"Latest release: <code>{html.escape(latest_name)}</code>"
                )
                open_btn = msg.addButton("Open Releases Page", QMessageBox.AcceptRole)
                msg.addButton(QMessageBox.Close)
                # Center and autosize dialog
                center_and_autosize_dialog(msg, self, width_ratio=0.45, height_ratio=0.35, min_width=500, min_height=250)
                msg.exec()
                if msg.clickedButton() == open_btn:
                    webbrowser.open(latest_url or GITHUB_RELEASES_PAGE)
                self.status_bar.showMessage("Update available")
            # If up to date, silently do nothing - no message needed
        except Exception as e:
            # Silently fail for automatic checks - don't show error message
            logger.error(f"Error parsing automatic update check data: {e}")



    def create_keyword_list(self):
        """Create a new keyword list."""
        dialog = KeywordEditorDialog(self.keyword_lists, None, is_new=True, parent=self)
        if dialog.exec() == QDialog.Accepted:
            list_name = dialog.get_list_name()
            keywords = dialog.get_keywords()
            whole_word = dialog.get_whole_word()
            if list_name and keywords:
                self.save_keyword_list(list_name, keywords, whole_word)
                # Refresh keyword selector after creating new list
                self.keyword_selector.clear()
                for name in sorted(self.keyword_lists.keys()):
                    self.keyword_selector.addItem(name)
                # Select the newly created list
                idx = self.keyword_selector.findText(list_name)
                if idx >= 0:
                    self.keyword_selector.setCurrentIndex(idx)
                logger.info(f"Refreshed keyword selector after creating '{list_name}'")
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Warning")
                msg.setText("List name or keywords cannot be empty.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()

    def edit_keywords(self):
        selected_list = self.keyword_selector.currentText()
        if selected_list:
            dialog = KeywordEditorDialog(self.keyword_lists, selected_list, is_new=False, parent=self)
            if dialog.exec() == QDialog.Accepted:
                # Check if list was deleted
                if hasattr(dialog, 'deleted_list') and dialog.deleted_list:
                    self.delete_keyword_list(dialog.deleted_list)
                else:
                    # Normal edit - save changes
                    keywords = dialog.get_keywords()
                    whole_word = dialog.get_whole_word()
                    self.save_keyword_list(selected_list, keywords, whole_word)
                    # Refresh keyword selector after editing list
                    self.keyword_selector.clear()
                    for list_name in sorted(self.keyword_lists.keys()):
                        self.keyword_selector.addItem(list_name)
                    self.keyword_selector.setCurrentIndex(self.keyword_selector.findText(selected_list))  # Reselect the edited list
                    logger.info(f"Refreshed keyword selector after editing '{selected_list}'")

    def log_message(self, message, level="INFO"):
        if level == "ERROR":
            logger.error(message)
        else:
            logger.info(message)

    def load_data(self):
        try:
            self.status_bar.showMessage("Loading data...")
            self.log_message("Prompting user to select Kik data folder...")
            
            # --- START MODIFICATION: REPLACE QMessageBox WITH QDialog ---
            
            # 1. Create a custom QDialog (which is fully controllable)
            folder_msg = QDialog(self)
            folder_msg.setWindowTitle("Import Kik Data")
            folder_msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            folder_msg.setWindowModality(Qt.ApplicationModal)

            # 2. Setup the internal layout
            main_layout = QVBoxLayout(folder_msg)
            
            # 3. Create the main text QLabel using the original content with larger font sizes
            text_label = QLabel(
                "<html><head><style>body { font-size: 26px; } h3 { font-size: 31px; } p, li { font-size: 26px; }</style></head><body>"
                "<h3><u>Import Kik Data Folder</u></h3>"
                "<br>"
                "<p><b>Please select the unzipped Kik data folder.</b></p>"
                "<br>"
                "<p>The selected folder must contain the following subfolders:</p>"
                "<ul>"
                "<li><b>content</b>: Contains media files and a <b>'text-msg-data'</b> subfolder with CSV files containing message data.</li>"
                "<li><b>logs</b>: Contains log files (e.g., <code>chat_platform_sent.txt</code>).</li>"
                "</ul>"
                "<br>"
                "<p><b>Important:</b> Ensure the Kik data folder is fully unzipped before proceeding. The application will prompt you to select CSV files from the 'text-msg-data' folder after you select the main folder.</p>"
                "</body></html>"
            )
            text_label.setWordWrap(True)
            text_label.setTextFormat(Qt.RichText)
            text_label.setContentsMargins(30, 30, 30, 30) # Add generous padding
            # Set explicit font size for the label
            label_font = QFont()
            label_font.setPointSize(24)
            text_label.setFont(label_font)
            main_layout.addWidget(text_label)
            
            # 4. Create the button box for OK/Cancel
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(folder_msg.accept)
            button_box.rejected.connect(folder_msg.reject)
            # Set explicit font size for buttons to ensure they're readable
            button_font = QFont()
            button_font.setPointSize(22)
            for button in button_box.buttons():
                button.setFont(button_font)
                button.setMinimumSize(176, 55)
            main_layout.addWidget(button_box)
            
            # --- END MODIFICATION 1 ---
            
            # --- Dynamic scaling and styling (from V3.18) ---
            screen = self.screen() or QApplication.primaryScreen()

            # Apply stylesheet to the QDialog and its children (from V3.18)
            # Override theme stylesheet with larger fonts for better readability on laptop displays
            # Use !important to ensure our styles override theme_manager styles
            folder_msg.setStyleSheet("""
                QDialog { background-color: #f4f4f9; }
                QLabel { 
                    font-size: 26px !important; 
                    font-weight: normal;
                }
                QPushButton {
                    font-size: 22px !important;
                    padding: 18px 31px !important;
                    min-width: 176px !important;
                    min-height: 55px !important;
                }
                QDialogButtonBox QPushButton {
                    font-size: 22px !important;
                    padding: 18px 31px !important;
                    min-width: 176px !important;
                    min-height: 55px !important;
                }
                QPushButton:hover { background-color: #e0e0e0; }
                QDialogButtonBox QPushButton:hover { background-color: #e0e0e0; }
            """)
            # --- End Dynamic scaling and styling ---

            # --- Forced Resizing and Centering (Now reliable with QDialog) ---
            
            # Remove all the obsolete resizing/label searching from the old QMessageBox attempts.
            # Calculate screen geometry as before
            screen_geo = screen.availableGeometry()
            
            # Resizable dialog with larger size for better readability on laptop displays
            dialog_width = 1200
            dialog_height = 900
            folder_msg.setMinimumSize(dialog_width, dialog_height)
            folder_msg.resize(dialog_width, dialog_height)
            
            # Center the dialog horizontally and vertically on the correct screen
            center_x = screen_geo.x() + (screen_geo.width() - dialog_width) // 2
            center_y = screen_geo.y() + (screen_geo.height() - dialog_height) // 2
            
            # Set geometry and move to center
            folder_msg.setGeometry(center_x, center_y, dialog_width, dialog_height)
            folder_msg.move(center_x, center_y)

            
            # --- End Forced Resizing and Centering ---
            
            # Execute the dialog, checking for QDialog.Accepted (formerly QMessageBox.Ok)
            if folder_msg.exec() != QDialog.Accepted:
                self.log_message("Folder selection cancelled.", "INFO")
                self.status_bar.showMessage("Folder selection cancelled")
                return


            # Create a QFileDialog instance for folder selection with autosizing and centering
            folder_dialog = QFileDialog(self)
            folder_dialog.setWindowTitle("Select Kik Data Folder - Must contain 'content' and 'logs' subfolders")
            folder_dialog.setFileMode(QFileDialog.Directory)
            folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
            folder_dialog.setDirectory(os.getcwd())
            
            # Center the dialog horizontally and vertically on the correct screen
            center_x = screen_geo.x() + (screen_geo.width() - dialog_width) // 2
            center_y = screen_geo.y() + (screen_geo.height() - dialog_height) // 2
            
            # Set geometry and move to center
            folder_msg.setGeometry(center_x, center_y, dialog_width, dialog_height)
            folder_msg.move(center_x, center_y)

            
            # --- End Forced Resizing and Centering ---
            
            if folder_dialog.exec() == QDialog.Accepted:
                folder = folder_dialog.selectedFiles()[0] if folder_dialog.selectedFiles() else None
            else:
                folder = None
            if not folder:
                self.log_message("No folder selected.", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("No folder selected. Please select the unzipped Kik data folder containing 'content' and 'logs' subfolders.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            self.content_folder = None
            self.logs_folder = None
            text_msg_dir = None

            # Locate content and logs
            for root, dirs, _ in os.walk(folder):
                if 'content' in dirs and not self.content_folder:
                    self.content_folder = os.path.join(root, 'content')
                    logger.info(f"Found content folder: {self.content_folder}")
                if 'logs' in dirs and not self.logs_folder:
                    self.logs_folder = os.path.join(root, 'logs')
                    logger.info(f"Found logs folder: {self.logs_folder}")
                if self.content_folder and self.logs_folder:
                    break

            # Locate text-msg-data under content
            if self.content_folder:
                for root, dirs, _ in os.walk(self.content_folder):
                    if 'text-msg-data' in dirs and not text_msg_dir:
                        text_msg_dir = os.path.join(root, 'text-msg-data')
                        logger.info(f"Found text-msg-data folder: {text_msg_dir}")
                        break

            if not self.content_folder or not self.logs_folder or not text_msg_dir:
                missing = []
                if not self.content_folder:
                    missing.append("'content'")
                if not self.logs_folder:
                    missing.append("'logs'")
                if not text_msg_dir:
                    missing.append("'content/text-msg-data'")
                self.log_message(f"Invalid folder structure: missing {', '.join(missing)}.", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"The selected folder must contain {', '.join(missing)} subfolders.\n\nPlease unzip the Kik data and select the correct folder.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            # Permission checks
            if (not os.access(self.content_folder, os.R_OK) or
                    not os.access(self.logs_folder, os.R_OK) or
                    not os.access(text_msg_dir, os.R_OK)):
                self.log_message("Permission denied for selected folder or subfolders.", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("Permission denied for the selected folder or its subfolders.\n\nPlease ensure you have read permissions for the folder and try again.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            # Build media_files from content
            self.media_files = {}
            for root, _, files in os.walk(self.content_folder):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.ogg')):
                        content_id = os.path.splitext(file)[0]
                        full_path = os.path.join(root, file)
                        self.media_files[content_id] = full_path
                        self.log_message(f"Found media file: {content_id} -> {full_path}")
            self.log_message(f"Found {len(self.media_files)} media files in content folder")

            # Collect CSV files from text-msg-data
            csv_files = []
            for root, _, files in os.walk(text_msg_dir):
                for file in files:
                    if file.lower().endswith('.csv'):
                        csv_files.append(os.path.join(root, file))
            self.log_message(f"Found {len(csv_files)} CSV files in text-msg-data: {csv_files}")

            # Let user choose which CSVs to load
            csv_dialog = CSVFileDialog(text_msg_dir, self)
            if csv_dialog.exec() != QDialog.Accepted:
                self.log_message("CSV file selection cancelled.", "INFO")
                self.status_bar.showMessage("CSV file selection cancelled")
                return self.load_data()

            csv_files = csv_dialog.get_selected_files()
            self.csv_files = csv_files
            if not csv_files:
                self.log_message("No CSV files selected.", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("No CSV files selected.\n\nPlease select one or more CSV files from the 'text-msg-data' folder.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            # ---- Load CSVs into dfs ----
            dfs = []
            for csv_file in csv_files:
                try:
                    self.log_message(f"Loading CSV: {csv_file}")
                    df = pd.read_csv(csv_file, low_memory=False)
                    if df.empty:
                        self.log_message(f"CSV file {csv_file} is empty, skipping.", "ERROR")
                        continue

                    # Preserve original line numbers before any processing
                    # pandas index represents row position in DataFrame (0-indexed)
                    # CSV line 1 = header, CSV line 2 = DataFrame index 0
                    # So: DataFrame index n = CSV line n+2
                    # Formula: index 0 = line 2, index 1 = line 3, index n = line n+2
                    df['_original_line_number'] = df.index + 2  # +2: index 0 = CSV line 2 (1 for header, 1 for 0-index offset)

                    self.log_message(f"CSV {csv_file} loaded, rows: {len(df)}")
                    self.log_message(f"CSV columns: {list(df.columns)}")

                    # Port column debug
                    if 'port' in df.columns:
                        self.log_message(f"Port column found in {csv_file}, sample values: {df['port'].head().tolist()}")
                        self.log_message(
                            f"Port column null count: {df['port'].isna().sum()}, "
                            f"non-null count: {df['port'].notna().sum()}"
                        )
                    else:
                        self.log_message(f"No port column in {csv_file}", "WARNING")

                    column_map = {col.lower(): col for col in df.columns}
                    required_columns = ['msg_id', 'sender_jid', 'receiver_jid', 'msg', 'sent_at']
                    # Columns that are truly required (cannot be empty) - msg can be empty for media messages
                    truly_required_columns = ['msg_id', 'sender_jid', 'receiver_jid', 'sent_at']

                    # Normalize required columns
                    for req_col in required_columns:
                        if req_col == 'sent_at':
                            if 'sent_at' in column_map:
                                df.rename(columns={column_map['sent_at']: 'sent_at'}, inplace=True)
                            elif 'timestamp' in column_map:
                                df.rename(columns={column_map['timestamp']: 'sent_at'}, inplace=True)
                            else:
                                self.log_message(f"No 'sent_at' or 'timestamp' column found in {csv_file}", "ERROR")
                                continue
                        else:
                            if req_col not in column_map:
                                self.log_message(f"Missing required column {req_col} in {csv_file}", "ERROR")
                                continue

                    # Convert optional columns to strings FIRST before dropna to preserve rows with empty msg but valid content_id
                    for col in ['msg', 'content_id', 'ip', 'group_jid', 'port']:
                        if col in df.columns:
                            df[col] = df[col].astype(str).fillna('')
                            # Enhanced handling for content_id
                            if col == 'content_id':
                                df[col] = df[col].str.strip()  # Remove whitespace
                                df[col] = df[col].replace('nan', '')  # Normalize 'nan' strings to empty
                        else:
                            df[col] = ''

                    self.log_message(f"Converting sent_at to datetime for {csv_file}...")
                    df['sent_at'] = pd.to_datetime(df['sent_at'], errors='coerce')
                    if df['sent_at'].dt.tz is not None:
                        self.log_message(f"sent_at column in {csv_file} is already tz-aware. Converting to UTC...")
                        df['sent_at'] = df['sent_at'].dt.tz_convert('UTC')
                    else:
                        self.log_message(f"sent_at column in {csv_file} is tz-naive. Localizing to UTC...")
                        df['sent_at'] = df['sent_at'].dt.tz_localize('UTC')

                    invalid_indices = df[df['sent_at'].isna()].index
                    if not invalid_indices.empty:
                        self.log_message(f"Found {len(invalid_indices)} invalid timestamps in {csv_file}.")

                    self.log_message(f"Cleaning CSV data for {csv_file}...")
                    pre_clean_rows = len(df)
                    # Only drop rows where TRULY required columns are missing (not msg, since it can be empty for media)
                    df = df.dropna(subset=truly_required_columns)
                    self.log_message(
                        f"After cleaning {csv_file}, rows: {len(df)} "
                        f"(dropped {pre_clean_rows - len(df)} rows)"
                    )

                    # Log rows with content_id after cleaning
                    if 'content_id' in df.columns:
                        rows_with_content_id = df[df['content_id'].astype(str).str.strip() != '']
                        if not rows_with_content_id.empty:
                            self.log_message(f"CSV {os.path.basename(csv_file)}: Found {len(rows_with_content_id)} rows with content_id (sample: {rows_with_content_id['content_id'].iloc[0] if len(rows_with_content_id) > 0 else 'N/A'})")
                        else:
                            self.log_message(f"CSV {os.path.basename(csv_file)}: No rows with content_id found after cleaning")

                    # --- ADD SOURCE + LINE NUMBER FOR CSV ROWS ---
                    rel_path = os.path.relpath(csv_file, folder).replace('\\', '/')
                    df['source'] = rel_path

                    # Use preserved original line numbers (set before cleaning)
                    if '_original_line_number' in df.columns:
                        df['line_number'] = df['_original_line_number']
                        df = df.drop(columns=['_original_line_number'])
                    elif 'line_number' not in df.columns:
                        # Fallback: if original line numbers weren't preserved, use sequential
                        df['line_number'] = range(1, len(df) + 1)
                    # --- END ADD ---

                    dfs.append(df)
                    self.log_message(f"Successfully processed {csv_file} with {len(df)} rows.")

                except pd.errors.EmptyDataError:
                    self.log_message(f"CSV file {csv_file} is empty or invalid.", "ERROR")
                    continue
                except Exception as e:
                    self.log_message(f"Error loading CSV {csv_file}: {str(e)}", "ERROR")
                    continue

            if not dfs:
                self.log_message("No valid CSV files loaded.", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("No valid CSV files loaded.\n\nPlease select valid CSV files from the 'text-msg-data' folder.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            # Combine CSV dfs (self.df is still useful elsewhere)
            try:
                self.df = pd.concat(dfs, ignore_index=True)
                # Fill all NaN values with empty strings to prevent "nan" from displaying
                self.df = self.df.fillna('')
                self.log_message(f"Combined {len(dfs)} CSV files, total rows: {len(self.df)}")
            except Exception as e:
                self.log_message(f"Error combining CSV files: {str(e)}", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Error combining CSV files: {str(e)}.\n\nPlease select valid CSV files.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            # ---- Log file definitions ----
            log_file_structures = {
                'chat_platform_sent.txt': {
                    'headers': ['Timestamp', 'User JID', 'Related User JID', 'App Name', 'ContentID', 'User IP', 'DateTime'],
                    'csv_headers': ['msg_id', 'sender_jid', 'receiver_jid', 'msg', 'sent_at',
                                    'content_id', 'ip', 'group_jid', 'line_number']
                },
                'group_send_msg_platform.txt': {
                    'headers': ['Timestamp', 'User JID', 'Group JID', 'Related User JID', 'App Name', 'Content ID', 'User IP', 'DateTime'],
                    'csv_headers': ['msg_id', 'sender_jid', 'receiver_jid', 'msg', 'sent_at',
                                    'content_id', 'ip', 'group_jid', 'line_number']
                },
                'chat_platform_sent_received.txt': {
                    'headers': ['Timestamp', 'User JID', 'Related User JID', 'App Name', 'ContentID', 'User IP', 'DateTime'],
                    'csv_headers': ['msg_id', 'sender_jid', 'receiver_jid', 'msg', 'sent_at',
                                    'content_id', 'ip', 'group_jid', 'line_number']
                },
                'group_receive_msg_platform.txt': {
                    'headers': ['Timestamp', 'Group JID', 'Related User JID', 'Group JID Copy', 'App Name', 'Content ID', 'User IP', 'DateTime'],
                    'csv_headers': ['msg_id', 'sender_jid', 'receiver_jid', 'msg', 'sent_at',
                                    'content_id', 'ip', 'group_jid', 'line_number']
                }
            }

            # ---- Process logs into log_dfs ----
            log_dfs = []
            temp_csv_dir = os.path.join(self.logs_folder, 'temp_csv')
            os.makedirs(temp_csv_dir, exist_ok=True)
            self.log_message(f"Created temporary CSV directory: {temp_csv_dir}")

            log_files_found = []
            for root, _, files in os.walk(self.logs_folder):
                for file in files:
                    if file in log_file_structures:
                        log_files_found.append(os.path.join(root, file))
            self.log_message(f"Found {len(log_files_found)} log files: {log_files_found}")

            for log_path in log_files_found:
                log_file = os.path.basename(log_path)
                structure = log_file_structures.get(log_file)
                if not structure:
                    self.log_message(f"Log file {log_file} not recognized, skipping.")
                    continue

                try:
                    self.log_message(f"Reading {log_file}...")
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = [line.strip() for line in f.readlines() if line.strip()]

                    if not lines:
                        self.log_message(
                            f"Log file {log_file} is empty or contains only whitespace. Skipping processing."
                        )
                        continue

                    self.log_message(f"First 5 lines of {log_file}: {''.join(lines[:5])}")

                    csv_filename = os.path.splitext(log_file)[0] + '.csv'
                    csv_path = os.path.join(temp_csv_dir, csv_filename)

                    csv_rows = []
                    for line_num, line in enumerate(lines, start=1):
                        fields = line.split('\t')
                        expected_columns = len(structure['headers'])
                        if len(fields) != expected_columns:
                            self.log_message(
                                f"Warning: {log_file} line has {len(fields)} columns, "
                                f"expected {expected_columns}: {line}",
                                "ERROR"
                            )
                            continue

                        if log_file in ['chat_platform_sent.txt', 'chat_platform_sent_received.txt']:
                            msg_id = fields[4]
                            sender_jid = fields[1]
                            receiver_jid = fields[2]
                            app_name = fields[3]
                            content_id = fields[4]
                            msg = f"{app_name} [{content_id}]"
                            sent_at = fields[6]
                            ip = fields[5]
                            group_jid = ''
                        elif log_file == 'group_send_msg_platform.txt':
                            msg_id = fields[5]
                            sender_jid = fields[1]
                            receiver_jid = fields[3]
                            app_name = fields[4]
                            content_id = fields[5]
                            msg = f"{app_name} [{content_id}]"
                            sent_at = fields[7]
                            ip = fields[6]
                            group_jid = fields[2]
                        elif log_file == 'group_receive_msg_platform.txt':
                            msg_id = fields[5]
                            sender_jid = fields[1]
                            receiver_jid = fields[2]
                            app_name = fields[4]
                            content_id = fields[5]
                            msg = f"{app_name} [{content_id}]"
                            sent_at = fields[7]
                            ip = fields[6]
                            group_jid = fields[1]
                        else:
                            continue

                        if not msg_id or not sender_jid or not receiver_jid:
                            self.log_message(f"Skipping invalid row in {log_file}: {fields}", "ERROR")
                            continue

                        csv_rows.append([
                            msg_id,
                            sender_jid,
                            receiver_jid,
                            msg,
                            sent_at,
                            content_id,
                            ip,
                            group_jid,
                            line_num
                        ])

                    if not csv_rows:
                        self.log_message(
                            f"No valid data in {log_file} after processing. Skipping CSV creation."
                        )
                        continue

                    self.log_message(f"Writing converted CSV: {csv_path}")
                    with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(structure['csv_headers'])
                        writer.writerows(csv_rows)

                    self.log_message(f"Loading converted CSV: {csv_path}")
                    df = pd.read_csv(csv_path, encoding='utf-8')
                    self.log_message(
                        f"CSV {csv_filename} loaded, rows: {len(df)}, columns: {list(df.columns)}"
                    )

                    df['sent_at'] = pd.to_datetime(
                        df['sent_at'], format='%Y-%m-%d %H:%M:%S', errors='coerce'
                    )
                    if df['sent_at'].dt.tz is not None:
                        self.log_message(f"sent_at in {csv_filename} is already tz-aware. Converting to UTC...")
                        df['sent_at'] = df['sent_at'].dt.tz_convert('UTC')
                    else:
                        self.log_message(f"sent_at in {csv_filename} is tz-naive. Localizing to UTC...")
                        df['sent_at'] = df['sent_at'].dt.tz_localize('UTC')

                    invalid_timestamps = df[df['sent_at'].isna()]
                    if not invalid_timestamps.empty:
                        self.log_message(
                            f"Found {len(invalid_timestamps)} invalid timestamps in {csv_filename}."
                        )

                    for col in ['msg', 'content_id', 'ip', 'group_jid', 'port']:
                        if col in df.columns:
                            df[col] = df[col].astype(str).fillna('')
                        else:
                            df[col] = ''

                    df = df[df['msg'].notna() & (df['msg'] != '')]
                    if df.empty:
                        self.log_message(
                            f"No valid messages in {csv_filename} after filtering. Skipping DataFrame."
                        )
                        continue

                    # --- ADD SOURCE + LINE NUMBER FOR LOG ROWS ---
                    rel_path = os.path.relpath(log_path, folder).replace('\\', '/')
                    df['source'] = rel_path

                    if 'line_number' not in df.columns:
                        df['line_number'] = range(1, len(df) + 1)
                    # --- END ADD ---

                    log_dfs.append(df)
                    self.log_message(f"Successfully processed {csv_filename} with {len(df)} rows.")

                except Exception as e:
                    self.log_message(f"Error processing {log_file}: {str(e)}", "ERROR")
                    try:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            first_lines = f.readlines()[:5]
                            self.log_message(
                                f"First 5 lines of {log_file}: {''.join(first_lines)}",
                                "ERROR"
                            )
                    except Exception as e2:
                        self.log_message(
                            f"Could not read {log_file} for debugging: {str(e2)}",
                            "ERROR"
                        )
                    continue

            self.log_message("Combining CSV and log data...")
            all_dfs = dfs + log_dfs
            if not log_dfs:
                self.log_message("No valid log data loaded; using only CSV data.")
            if not all_dfs:
                self.log_message("No valid data loaded.", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("No valid CSV or log files loaded.\n\nPlease ensure the folder structure and files are correct.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            # >>> UPDATED: include source and line_number <<<
            required_columns = [
                'msg_id',
                'sender_jid',
                'receiver_jid',
                'msg',
                'sent_at',
                'content_id',
                'ip',
                'group_jid',
                'port',
                'source',
                'line_number',
            ]

            for df in all_dfs:
                # Make sure all required columns exist and have sensible defaults
                for col in required_columns:
                    if col not in df.columns:
                        if col == 'line_number':
                            df[col] = 0
                        else:
                            df[col] = ''

                df['sent_at'] = pd.to_datetime(df['sent_at'], errors='coerce')
                if df['sent_at'].dt.tz is not None:
                    df['sent_at'] = df['sent_at'].dt.tz_convert('UTC')
                else:
                    df['sent_at'] = df['sent_at'].dt.tz_localize('UTC')

                for col in ['msg', 'content_id', 'ip', 'group_jid', 'port', 'source']:
                    if col in df.columns:
                        df[col] = df[col].astype(str).fillna('')
                        # Enhanced handling for content_id - preserve all non-empty values
                        if col == 'content_id':
                            # Store original count before normalization
                            original_non_empty = len(df[df[col].astype(str).str.strip() != ''])
                            df[col] = df[col].str.strip()  # Remove whitespace
                            df[col] = df[col].replace('nan', '')  # Normalize 'nan' strings to empty
                            # Verify we didn't lose any content_id values
                            after_non_empty = len(df[df[col].astype(str).str.strip() != ''])
                            if original_non_empty != after_non_empty:
                                self.log_message(f"WARNING: Lost {original_non_empty - after_non_empty} content_id values during normalization in {df['source'].iloc[0] if 'source' in df.columns and len(df) > 0 else 'unknown'}", "ERROR")
                    else:
                        df[col] = ''

            try:
                combined_df = pd.concat(
                    [df[required_columns] for df in all_dfs if not df.empty],
                    ignore_index=True
                )
                # Fill all NaN values with empty strings to prevent "nan" from displaying
                combined_df = combined_df.fillna('')
                
                # NEW: Intelligent deduplication based on sender, receiver, date/time, IP, and port
                # Multiple records can have the same content_id and not be duplicates
                # Only merge if sender_jid, receiver_jid, sent_at, ip, and port all match
                self.log_message("Checking for duplicate messages from CSV and log files...")
                
                # Log content_id statistics before deduplication
                csv_with_content_id = combined_df[combined_df['source'].str.contains(r'text-msg-data|\.csv', case=False, na=False) & (combined_df['content_id'] != '')]
                log_with_content_id = combined_df[combined_df['source'].str.contains('logs/', case=False, na=False) & (combined_df['content_id'] != '')]
                self.log_message(f"Before deduplication: {len(csv_with_content_id)} CSV rows with content_id, {len(log_with_content_id)} log rows with content_id")
                
                # Mark source type for prioritization (CSV sources take priority for content_id)
                # Be more explicit about CSV detection to ensure we catch all CSV sources
                def identify_source_type(source_str):
                    source_lower = str(source_str).lower()
                    if 'text-msg-data' in source_lower or source_lower.endswith('.csv') or '/text-msg-data/' in source_lower:
                        return 'csv'
                    return 'log'
                
                combined_df['_source_type'] = combined_df['source'].apply(identify_source_type)
                
                # Log source type distribution
                csv_count = len(combined_df[combined_df['_source_type'] == 'csv'])
                log_count = len(combined_df[combined_df['_source_type'] == 'log'])
                csv_with_content_id_count = len(combined_df[(combined_df['_source_type'] == 'csv') & (combined_df['content_id'].astype(str).str.strip() != '')])
                self.log_message(f"Source type distribution: {csv_count} CSV rows ({csv_with_content_id_count} with content_id), {log_count} log rows")
                
                # Create a function to merge duplicate rows
                def merge_duplicate_rows(group):
                    # Prefer non-empty content_id from CSV, then from logs
                    csv_rows = group[group['_source_type'] == 'csv']
                    log_rows = group[group['_source_type'] == 'log']
                    
                    # Get non-empty content_ids from CSV (strip whitespace to ensure proper matching)
                    csv_content_ids = csv_rows['content_id'] if not csv_rows.empty else pd.Series(dtype=object)
                    log_content_ids = log_rows['content_id'] if not log_rows.empty else pd.Series(dtype=object)
                    
                    # Convert to string and strip to handle any edge cases
                    csv_content_ids_str = csv_content_ids.astype(str).str.strip()
                    log_content_ids_str = log_content_ids.astype(str).str.strip()
                    
                    # Get non-empty content_ids
                    csv_non_empty = csv_content_ids_str[csv_content_ids_str != ''].tolist()
                    log_non_empty = log_content_ids_str[log_content_ids_str != ''].tolist()
                    
                    # Prefer CSV content_id if available, otherwise use log content_id
                    merged_content_id = csv_non_empty[0] if csv_non_empty else (log_non_empty[0] if log_non_empty else '')
                    
                    # Log when merging preserves CSV content_id
                    if csv_non_empty and merged_content_id == csv_non_empty[0]:
                        self.log_message(f"Merging duplicate: preserving CSV content_id '{merged_content_id}'")
                    elif log_non_empty and merged_content_id == log_non_empty[0]:
                        self.log_message(f"Merging duplicate: using log content_id '{merged_content_id}' (no CSV content_id)")
                    elif not csv_non_empty and not log_non_empty:
                        self.log_message(f"Merging duplicate: no content_id in either source")
                    
                    # For other fields, prefer CSV row if available, otherwise use first log row
                    if not csv_rows.empty:
                        result = csv_rows.iloc[0].copy()
                    else:
                        result = log_rows.iloc[0].copy() if not log_rows.empty else group.iloc[0].copy()
                    
                    # Set merged content_id - CRITICAL: Always preserve CSV content_id if it exists
                    if csv_non_empty:
                        result['content_id'] = csv_non_empty[0]
                        self.log_message(f"Merge result: Set content_id to CSV value '{csv_non_empty[0]}'")
                    elif log_non_empty:
                        result['content_id'] = log_non_empty[0]
                    else:
                        result['content_id'] = ''
                    
                    # Merge source information to show both sources if different
                    sources = group['source'].unique()
                    if len(sources) > 1:
                        # Collect source and line number pairs, preserving order
                        source_line_pairs = []
                        for _, row in group.iterrows():
                            source_val = str(row.get('source', '')).strip()
                            line_num = str(row.get('line_number', '')).strip()
                            if line_num and line_num.lower() not in ('nan', 'none', ''):
                                source_line_pairs.append((os.path.basename(source_val), line_num))
                            else:
                                source_line_pairs.append((os.path.basename(source_val), ''))
                        
                        # Remove duplicate sources while preserving order and collecting line numbers
                        seen_sources = {}
                        ordered_sources = []
                        ordered_line_numbers = []
                        
                        for source_name, line_num in source_line_pairs:
                            if source_name not in seen_sources:
                                seen_sources[source_name] = []
                                ordered_sources.append(source_name)
                            if line_num:
                                seen_sources[source_name].append(line_num)
                        
                        # Build source string (without line numbers)
                        result['source'] = '; '.join(ordered_sources)
                        
                        # Build line number string matching source order
                        for source_name in ordered_sources:
                            line_nums = seen_sources[source_name]
                            if line_nums:
                                # Remove duplicates and keep first occurrence
                                unique_line_nums = []
                                seen_line_nums = set()
                                for ln in line_nums:
                                    if ln not in seen_line_nums:
                                        unique_line_nums.append(ln)
                                        seen_line_nums.add(ln)
                                ordered_line_numbers.extend(unique_line_nums)
                        
                        if ordered_line_numbers:
                            result['line_number'] = '; '.join(ordered_line_numbers)
                        else:
                            result['line_number'] = ''
                    else:
                        # Single source, just use its line number
                        result['source'] = os.path.basename(str(group.iloc[0].get('source', '')).strip())
                        result['line_number'] = str(group.iloc[0].get('line_number', '')).strip()
                    
                    # Merge msg_id if available (prefer CSV msg_id)
                    if 'msg_id' in group.columns:
                        csv_msg_ids = csv_rows['msg_id']
                        csv_msg_ids_non_empty = csv_msg_ids[csv_msg_ids != ''].tolist()
                        if csv_msg_ids_non_empty:
                            result['msg_id'] = csv_msg_ids_non_empty[0]
                        else:
                            log_msg_ids = group[group['_source_type'] == 'log']['msg_id']
                            log_msg_ids_non_empty = log_msg_ids[log_msg_ids != ''].tolist()
                            result['msg_id'] = log_msg_ids_non_empty[0] if log_msg_ids_non_empty else ''
                    
                    # Convert Series to dict to ensure proper handling
                    if isinstance(result, pd.Series):
                        return result.to_dict()
                    return result
                
                # Group by sender_jid, receiver_jid, sent_at, ip, port to find duplicates
                # Only deduplicate if we have both CSV and log data
                csv_count = len(combined_df[combined_df['_source_type'] == 'csv'])
                log_count = len(combined_df[combined_df['_source_type'] == 'log'])
                
                if csv_count > 0 and log_count > 0:
                    # Normalize values for deduplication key to handle differences
                    # Normalize sender_jid and receiver_jid (strip whitespace, handle 'nan')
                    normalized_sender = combined_df['sender_jid'].astype(str).str.strip().replace('nan', '')
                    normalized_receiver = combined_df['receiver_jid'].astype(str).str.strip().replace('nan', '')
                    
                    # Normalize timestamps to seconds precision (round to nearest second to handle microsecond differences)
                    # Also ensure timezone is consistent (convert to UTC and format)
                    def normalize_timestamp(ts):
                        if pd.isna(ts):
                            return ''
                        try:
                            # Ensure it's a datetime
                            if isinstance(ts, pd.Timestamp):
                                # Convert to UTC if timezone-aware, otherwise assume UTC
                                if ts.tz is not None:
                                    ts_utc = ts.tz_convert('UTC')
                                else:
                                    ts_utc = ts.tz_localize('UTC')
                                # Format to seconds precision (no microseconds)
                                return ts_utc.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                return str(ts)
                        except Exception:
                            return str(ts)
                    
                    normalized_sent_at = combined_df['sent_at'].apply(normalize_timestamp)
                    
                    # Normalize IP (strip whitespace, handle 'nan')
                    normalized_ip = combined_df['ip'].astype(str).str.strip().replace('nan', '')
                    
                    # Normalize content_id for deduplication key
                    # Empty/nan content_id normalized to 'NO_CONTENT_ID' so rows without media can still match
                    normalized_content_id = combined_df['content_id'].astype(str).str.strip().replace('nan', '')
                    normalized_content_id = normalized_content_id.replace('', 'NO_CONTENT_ID')
                    
                    # Create deduplication key based on: sender, receiver, date/time, IP, content_id
                    # Port is NOT included in the key since it may differ between sources
                    # content_id IS included to prevent merging different media messages with same metadata
                    combined_df['_dup_key'] = (
                        normalized_sender + '|' +
                        normalized_receiver + '|' +
                        normalized_sent_at + '|' +
                        normalized_ip + '|' +
                        normalized_content_id
                    )
                    
                    # Log sample of deduplication keys for debugging
                    sample_keys = combined_df['_dup_key'].head(10).tolist()
                    self.log_message(f"Sample deduplication keys (first 10): {sample_keys[:3]}")
                    
                    grouped = combined_df.groupby('_dup_key', as_index=False)
                    merged_rows = []
                    duplicates_found = 0
                    
                    for key, group in grouped:
                        if len(group) > 1:
                            # Multiple rows with same key - merge them
                            duplicates_found += len(group) - 1  # Count how many duplicates we're removing
                            
                            # Log details about the merge
                            csv_rows_in_group = group[group['_source_type'] == 'csv']
                            log_rows_in_group = group[group['_source_type'] == 'log']
                            csv_with_content_id = csv_rows_in_group[csv_rows_in_group['content_id'].astype(str).str.strip() != '']
                            if not csv_with_content_id.empty:
                                self.log_message(f"Merging {len(group)} rows with key '{key[:50]}...': CSV has content_id '{csv_with_content_id.iloc[0]['content_id']}'")
                            
                            merged_row = merge_duplicate_rows(group)
                            # Convert Series to dict to ensure proper DataFrame construction
                            if isinstance(merged_row, pd.Series):
                                merged_rows.append(merged_row.to_dict())
                            else:
                                merged_rows.append(merged_row)
                        else:
                            # Single row - keep as is (no duplicate to merge with)
                            row = group.iloc[0]
                            # Log single CSV rows with content_id for debugging
                            if group.iloc[0]['_source_type'] == 'csv':
                                row_content_id = str(group.iloc[0].get('content_id', '')).strip()
                                if row_content_id and row_content_id != '':
                                    self.log_message(f"Keeping single CSV row with content_id '{row_content_id}' (no duplicate found)")
                                elif row_content_id == '':
                                    self.log_message(f"Keeping single CSV row with empty content_id (no duplicate found)")
                            # Ensure content_id is preserved as string
                            if isinstance(row, pd.Series):
                                row_dict = row.to_dict()
                                # Explicitly preserve content_id
                                if 'content_id' in row_dict:
                                    row_dict['content_id'] = str(row_dict['content_id']).strip()
                                merged_rows.append(row_dict)
                            else:
                                # If it's already a dict, ensure content_id is preserved
                                if isinstance(row, dict) and 'content_id' in row:
                                    row['content_id'] = str(row['content_id']).strip()
                                merged_rows.append(row)
                    
                    # Reconstruct DataFrame ensuring all required columns are present
                    if merged_rows:
                        combined_df = pd.DataFrame(merged_rows)
                        # Ensure all required columns exist
                        for col in required_columns:
                            if col not in combined_df.columns:
                                combined_df[col] = ''
                        # Ensure content_id is properly formatted as string
                        if 'content_id' in combined_df.columns:
                            combined_df['content_id'] = combined_df['content_id'].astype(str).str.strip()
                            combined_df['content_id'] = combined_df['content_id'].replace('nan', '')
                    else:
                        combined_df = pd.DataFrame(columns=required_columns)
                    
                    # Log content_id statistics after deduplication
                    csv_with_content_id_after = combined_df[combined_df['source'].str.contains(r'text-msg-data|\.csv', case=False, na=False) & (combined_df['content_id'].astype(str).str.strip() != '')]
                    log_with_content_id_after = combined_df[combined_df['source'].str.contains('logs/', case=False, na=False) & (combined_df['content_id'].astype(str).str.strip() != '')]
                    self.log_message(
                        f"After merging duplicates: {len(combined_df)} rows "
                        f"(removed {duplicates_found} duplicate entries)"
                    )
                    self.log_message(f"After deduplication: {len(csv_with_content_id_after)} CSV rows with content_id, {len(log_with_content_id_after)} log rows with content_id")
                    
                    # Log specific content_id values from CSV for debugging
                    if not csv_with_content_id_after.empty:
                        sample_content_ids = csv_with_content_id_after['content_id'].head(5).tolist()
                        self.log_message(f"Sample CSV content_id values after deduplication: {sample_content_ids}")
                else:
                    self.log_message("Only one source type found, skipping deduplication")
                
                # Remove temporary columns
                if '_source_type' in combined_df.columns:
                    combined_df = combined_df.drop(columns=['_source_type'])
                if '_dup_key' in combined_df.columns:
                    combined_df = combined_df.drop(columns=['_dup_key'])
                
                self.log_message(
                    f"Combined dataframe rows: {len(combined_df)}, "
                    f"columns: {list(combined_df.columns)}"
                )
                if not combined_df.empty:
                    self.log_message(
                        f"Sample combined data (first row): {combined_df.iloc[0].to_dict()}"
                    )
            except Exception as e:
                self.log_message(f"Error combining DataFrames: {str(e)}", "ERROR")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Error combining data: {str(e)}.\n\nPlease ensure all files are valid and try again.")
                msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return self.load_data()

            # >>> THIS WAS MISSING – actually build conversations/UI <<<
            self.populate_conversations(combined_df)
            self.log_message("Data loaded successfully!")
            self.status_bar.showMessage("Data loaded successfully")
            self.showNormal()

            # Invalidate any stale search results from pre-load searches and refresh
            self.search_cache.clear()
            self.date_filtered_cache.clear()
            self.unfiltered_messages = None
            self.table_row_map.clear()
            self.earliest_date = None
            self.latest_date = None
            self.schedule_search()

        except Exception as e:
            self.log_message(f"Unexpected error in load_data: {str(e)}", "ERROR")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Unexpected error: {str(e)}.\n\nPlease try again or check the log file for details.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return self.load_data()


    def populate_conversations(self, df):
        self.log_message("Grouping conversations...")
        self.conversations = {}
        self.media_counts = {}
        self.df = df

        # Create progress dialog
        total_rows = len(df)
        progress = QProgressDialog("Processing messages...", "Cancel", 0, total_rows, self)
        progress.setWindowTitle("Import Progress")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # Show immediately
        progress.setValue(0)
        QApplication.processEvents()  # Process events to show dialog

        row_count = 0
        for row in df.itertuples():
            row_count += 1
            if row_count % 100 == 0:  # Update progress every 100 rows
                progress.setValue(row_count)
                progress.setLabelText(f"Processing messages... ({row_count}/{total_rows})")
                QApplication.processEvents()  # Keep UI responsive
            
            if progress.wasCanceled():
                self.log_message("Conversation population cancelled by user")
                return
            
            sender = getattr(row, 'sender_jid', '')
            receiver = getattr(row, 'receiver_jid', '')
            
            # Skip invalid rows with missing sender or receiver
            if pd.isna(sender) or pd.isna(receiver) or not sender or not receiver:
                continue
            
            conv_id = tuple(sorted([sender, receiver]))
            
            if conv_id not in self.conversations:
                self.conversations[conv_id] = []
                self.media_counts[conv_id] = 0
            
            content_id_val = getattr(row, 'content_id', '') or ''
            ip_val = getattr(row, 'ip', '') or ''
            port_val = getattr(row, 'port', '') or ''
            source_val = getattr(row, 'source', 'Unknown') or 'Unknown'
            line_num_val = getattr(row, 'line_number', 0)
            # Handle line_number - it may be a combined string like "10; 6" after merging duplicates
            if pd.isna(line_num_val):
                line_number = 0
            else:
                line_num_str = str(line_num_val).strip()
                # If it contains ';', it's a combined value - just use the first one for display purposes
                # or keep as string for the message dict
                if ';' in line_num_str:
                    # For combined line numbers, extract first value for numeric operations if needed
                    first_line_num = line_num_str.split(';')[0].strip()
                    try:
                        line_number = int(first_line_num) if first_line_num else 0
                    except (ValueError, TypeError):
                        line_number = 0
                else:
                    try:
                        line_number = int(line_num_str) if line_num_str else 0
                    except (ValueError, TypeError):
                        line_number = 0
            
            # Replace NaN values with empty strings for all message fields
            msg_id_val = getattr(row, 'msg_id', '')
            msg_text = getattr(row, 'msg', '')
            if pd.isna(msg_id_val):
                msg_id_val = ''
            if pd.isna(msg_text):
                msg_text = ''
            if pd.isna(content_id_val):
                content_id_val = ''
            if pd.isna(ip_val):
                ip_val = ''
            if pd.isna(port_val):
                port_val = ''
            if pd.isna(source_val):
                source_val = 'Unknown'
            
            message = {
                'msg_id': msg_id_val,
                'sender': sender,
                'receiver': receiver,
                'message': msg_text,
                'sent_at': getattr(row, 'sent_at', None),
                'tags': set(),
                'content_id': content_id_val,
                'ip': ip_val,
                'port': port_val,
                'source': source_val,
                'line_number': str(line_num_val).strip() if pd.notna(line_num_val) else '0'  # Keep original value (may be combined string like "10; 6")
            }
            # Removed excessive logging - only log every 1000th message for performance
            # self.log_message(f"Message port value for msg_id {message['msg_id']}: {message['port']}")
            self.conversations[conv_id].append(message)
            
            if content_id_val and content_id_val in self.media_files and os.path.exists(self.media_files[content_id_val]):
                self.media_counts[conv_id] += 1
        
        progress.setLabelText("Sorting conversations...")
        progress.setValue(total_rows)
        QApplication.processEvents()
        
        for conv_id in self.conversations:
            self.conversations[conv_id].sort(key=lambda x: x['sent_at'])
        
        progress.setLabelText("Populating conversation list...")
        QApplication.processEvents()
        
        self.log_message(f"Found {len(self.conversations)} conversations.")
        
        self.selector.clear()
        self.selector.addItem("All Conversations")
        for conv_id in sorted(self.conversations.keys(), key=lambda x: x[0]):
            display_text = f"Conversation: {conv_id[0]} <-> {conv_id[1]}"
            if conv_id in self.reviewed_conversations:
                display_text += " [Reviewed]"
            self.selector.addItem(display_text)
        
        progress.setValue(total_rows)
        progress.close()
        self.log_message("Dropdown populated.")
        
        # Strategy 1: Pre-compute unfiltered state for instant display
        # This also sets the date filters to match the pre-computed dates
        self._precompute_unfiltered_state()

    def _precompute_unfiltered_state(self):
        """Strategy 1: Pre-compute the unfiltered state for instant display."""
        self.log_message("Pre-computing unfiltered state...")
        earliest_date = None
        latest_date = None
        
        # Find date range from all conversations
        for conv_id, messages in self.conversations.items():
            for msg in messages:
                sent_at = msg.get('sent_at')
                if sent_at and pd.notna(sent_at):
                    # Handle timezone-aware timestamps
                    if hasattr(sent_at, 'tz') and sent_at.tz is not None:
                        sent_at = sent_at.tz_localize(None)
                    
                    if earliest_date is None or sent_at < earliest_date:
                        earliest_date = sent_at
                    if latest_date is None or sent_at > latest_date:
                        latest_date = sent_at
        
        # Store date range for quick access
        self.earliest_date = earliest_date
        self.latest_date = latest_date
        
        # Build unfiltered messages list (all conversations, no filters)
        messages_to_display = []
        message_count = 0
        for conv_id in sorted(self.conversations.keys(), key=lambda x: x[0]):
            conv_str = f"Conversation: {conv_id[0]} <-> {conv_id[1]}" if len(conv_id) == 2 else f"Group: {conv_id[0]}"
            messages_to_display.append(('header', conv_str))
            for index, msg in enumerate(self.conversations[conv_id]):
                messages_to_display.append(('message', msg, index, conv_id))
                message_count += 1
        
        # Cache with special key for unfiltered state
        earliest_str = earliest_date.strftime('%Y-%m-%d') if earliest_date else '2024-01-01'
        latest_str = latest_date.strftime('%Y-%m-%d') if latest_date else QDate.currentDate().toString("yyyy-MM-dd")
        
        unfiltered_key = (
            '',  # No search text
            False,  # search_whole_word unchecked
            True,  # search_all checked
            earliest_str,
            latest_str,
            'All Conversations',
            self.selected_keyword_list
        )
        
        # Store pre-computed unfiltered state
        self.unfiltered_messages = (messages_to_display, message_count)
        self.search_cache[unfiltered_key] = (messages_to_display, message_count)
        
        self.log_message(f"Pre-computed unfiltered state: {message_count} messages, date range: {earliest_str} to {latest_str}")
        
        # IMPORTANT: Set date filters to match pre-computed dates so cache keys will match
        # This ensures that when switching back to "All Conversations", the cache will be found
        if earliest_date:
            from_date = QDate(earliest_date.year, earliest_date.month, earliest_date.day)
            self.date_from.setDate(from_date)
            logger.info(f"Set date_from to pre-computed earliest date: {earliest_str}")
        if latest_date:
            to_date = QDate(latest_date.year, latest_date.month, latest_date.day)
            self.date_to.setDate(to_date)
            logger.info(f"Set date_to to pre-computed latest date: {latest_str}")

    def handle_double_click(self, index):
        """Handle double-click on table view."""
        if not index.isValid() or index.column() != 6:
            return
        
        msg = self.message_model.getMessageAtRow(index.row())
        if msg:
            content_id = msg.get('content_id', '')
            media_path = self.get_media_path(content_id)
            if media_path and os.path.exists(media_path):
                self.log_message(f"Opening media file: {media_path}")
                self.open_media_file(media_path)
            else:
                self.log_message(f"No media file found for Content ID: {content_id}", "ERROR")
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("Info")
                msg_box.setText(f"No media file found for Content ID: {content_id}")
                msg_box.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()
                self.status_bar.showMessage(f"No media file for {content_id}")

    def view_keyword_hits(self):
        self.status_bar.showMessage("Viewing keyword hits...")
        self.log_message("Viewing keyword hits...")
        keyword_hits = []
        keywords, whole_word = self._get_keyword_state()
        if keywords:
            for conv_id, messages in self.conversations.items():
                for msg in messages:
                    if self.is_keyword_match(msg['message'], keywords, whole_word):
                        keyword_hits.append((msg, conv_id))
        
        if not keyword_hits:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("No Hits")
            msg.setText("No messages match the selected keyword list.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.log_message("No keyword hits found.")
            self.status_bar.showMessage("No keyword hits")
            return
        
        dialog = KeywordHitsDialog(keyword_hits, self)
        dialog.show()
        self.status_bar.showMessage("Keyword hits displayed")

    def toggle_stats_panel(self):
        self.stats_visible = not self.stats_visible
        self.stats_panel.setVisible(self.stats_visible)
        self.stats_button.setText("Hide Stats" if self.stats_visible else "Show Stats")
        if self.stats_visible:
            self.update_stats_panel()
        self.status_bar.showMessage("Stats panel toggled")

    def update_stats_panel(self):
        self.status_bar.showMessage("Updating stats...")
        self.log_message("Updating stats...")
        stats_text = ""
        selection = self.selector.currentText()
        if self.df is not None and selection == "All Conversations":
            total_messages = len(self.df)
            unique_conversations = len(self.conversations)
            unique_users = len(set(self.df['sender_jid'].unique()) | set(self.df['receiver_jid'].unique()))
            tagged_count = sum(1 for messages in self.conversations.values() for msg in messages if msg['tags'])
            keywords, whole_word = self._get_keyword_state()
            keyword_hits = (
                sum(
                    1
                    for messages in self.conversations.values()
                    for msg in messages
                    if self.is_keyword_match(msg['message'], keywords, whole_word)
                ) if keywords else 0
            )
            total_media = sum(self.media_counts.values())
            stats_text = f"Total Messages: {total_messages}\nUnique Conversations: {unique_conversations}\nUnique Users: {unique_users}\nTagged Messages: {tagged_count}\nKeyword Hits: {keyword_hits}\nTotal Media: {total_media}"
        elif selection.startswith("Conversation: ") or selection.startswith("Group: "):
            conv_str = selection.replace("Conversation: ", "").replace("Group: ", "").replace(" [Reviewed]", "")
            conv_id = (conv_str,) if selection.startswith("Group: ") else tuple(sorted(conv_str.split(" <-> ")))
            if conv_id in self.conversations:
                messages = self.conversations[conv_id]
                total_messages = len(messages)
                senders = set(msg['sender'] for msg in messages)
                receivers = set(msg['receiver'] for msg in messages)
                unique_users = len(senders | receivers)
                tagged_count = sum(1 for msg in messages if msg['tags'])
                keywords, whole_word = self._get_keyword_state()
                keyword_hits = (
                    sum(
                        1
                        for msg in messages
                        if self.is_keyword_match(msg['message'], keywords, whole_word)
                    ) if keywords else 0
                )
                media_total = self.media_counts.get(conv_id, 0)
                if len(conv_id) == 2:
                    sender1, sender2 = conv_id
                    media_from_sender1 = sum(1 for msg in messages if msg['sender'] == sender1 and msg.get('content_id', ''))
                    media_from_sender2 = sum(1 for msg in messages if msg['sender'] == sender2 and msg.get('content_id', ''))
                    media_tally = f"{media_total} total ({media_from_sender1} from {sender1}, {media_from_sender2} from {sender2})"
                else:
                    media_tally = f"{media_total} total"
                stats_text = f"Messages: {total_messages}\nUnique Users: {unique_users}\nTagged Messages: {tagged_count}\nKeyword Hits: {keyword_hits}\nMedia Sent/Received: {media_tally}"
            else:
                stats_text = "No data for selected conversation"
        else:
            stats_text = "Select a conversation to view stats"
        self.stats_text.setPlainText(stats_text)
        self.status_bar.showMessage("Stats updated")

    def toggle_reviewed_status(self):
        selection = self.selector.currentText()
        if selection.startswith("Conversation: ") or selection.startswith("Group: "):
            conv_str = selection.replace("Conversation: ", "").replace("Group: ", "").replace(" [Reviewed]", "")
            conv_id = (conv_str,) if selection.startswith("Group: ") else tuple(sorted(conv_str.split(" <-> ")))
            old_reviewed = conv_id in self.reviewed_conversations
            
            # Record action for undo
            action = {
                'type': 'reviewed_status',
                'conv_id': conv_id,
                'old_state': old_reviewed,
                'new_state': not old_reviewed
            }
            self._record_action(action)
            
            if conv_id in self.reviewed_conversations:
                self.reviewed_conversations.remove(conv_id)
                new_text = selection.replace(" [Reviewed]", "")
            else:
                self.reviewed_conversations.add(conv_id)
                new_text = f"{selection} [Reviewed]"
            index = self.selector.currentIndex()
            self.selector.setItemText(index, new_text)
            
            if not old_reviewed and conv_id in self.reviewed_conversations:
                current_index = self.selector.currentIndex()
                if current_index < self.selector.count() - 1:
                    self.selector.setCurrentIndex(current_index + 1)
            
    def create_shortcuts(self):
        if hasattr(self, '_shortcuts'):
            for shortcut in self._shortcuts:
                shortcut.setEnabled(False)
                logger.info(f"Disabled existing shortcut: {shortcut.key().toString()}")
        self._shortcuts = []
        logger.info(f"Creating shortcuts with hotkeys: {self.hotkeys}")
        for key, keystr in self.hotkeys.items():
            if keystr:
                try:
                    shortcut = QShortcut(QKeySequence(keystr), self, context=Qt.ApplicationShortcut)
                    if key == 'Reviewed':
                        shortcut.activated.connect(self.toggle_reviewed_status)
                    else:
                        shortcut.activated.connect(lambda t=key: self.apply_tag_to_selected(t))
                    self._shortcuts.append(shortcut)
                    logger.info(f"Created shortcut for {key}: {keystr} (QKeySequence: {shortcut.key().toString()})")
                except Exception as e:
                    logger.error(f"Failed to create shortcut for {key}: {keystr}, error: {str(e)}")
        
        # Add undo/redo shortcuts
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self, context=Qt.ApplicationShortcut)
        undo_shortcut.activated.connect(self.undo_action)
        self._shortcuts.append(undo_shortcut)
        
        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self, context=Qt.ApplicationShortcut)
        redo_shortcut.activated.connect(self.redo_action)
        self._shortcuts.append(redo_shortcut)
                    
    def apply_tag_to_selected(self, tag):
        selected_rows = sorted(set(index.row() for index in self.message_table.selectedIndexes()))
        if not selected_rows:
            return
        
        # Record action for undo - collect all changes
        tag_changes = []
        for row in selected_rows:
            row_item = self.message_table.item(row, 4)
            if not row_item:
                continue
            msg_id = row_item.data(Qt.UserRole)
            if not msg_id:
                continue
            for conv_id, messages in self.conversations.items():
                for msg in messages:
                    if msg.get('msg_id') == msg_id:
                        old_tags = msg.get('tags', set()).copy()
                        current_tags = msg.get('tags', set())
                        if tag in current_tags:
                            current_tags.remove(tag)
                        else:
                            current_tags.add(tag)
                        msg['tags'] = current_tags
                        new_tags = current_tags.copy()
                        tag_changes.append({
                            'msg_id': msg_id,
                            'old_tags': old_tags,
                            'new_tags': new_tags
                        })
                        tags_item = self.message_table.item(row, 5)
                        if tags_item:
                            tags_item.setText(', '.join(sorted(msg['tags'])))
                        bg_color = self.compute_row_color(msg, conv_id, row_index=row)
                        for col in range(11):
                            cell_item = self.message_table.item(row, col)
                            if cell_item:
                                cell_item.setBackground(QBrush(QColor(bg_color)))
                        break
        
        # Record action for undo
        if tag_changes:
            action = {
                'type': 'tag_change',
                'tag': tag,
                'changes': tag_changes
            }
            self._record_action(action)
        
        self.status_bar.showMessage(f"Toggled tag '{tag}' on {len(selected_rows)} message(s)")

    def manage_hotkeys(self):
        dialog = ManageHotkeysDialog(self.available_tags, self.hotkeys, self)
        if dialog.exec() == QDialog.Accepted:
            self.hotkeys = dialog.get_hotkeys()
            self.create_shortcuts()
            self.save_config()
    
    def _record_action(self, action):
        """Record an action for undo/redo."""
        self.undo_stack.append(action)
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
        # Limit undo history size
        if len(self.undo_stack) > self.max_undo_history:
            self.undo_stack.pop(0)
    
    def undo_action(self):
        """Undo the last action."""
        if not self.undo_stack:
            self.status_bar.showMessage("Nothing to undo")
            return
        
        action = self.undo_stack.pop()
        self.redo_stack.append(action)
        
        if action['type'] == 'reviewed_status':
            conv_id = action['conv_id']
            # Reverse the action
            if action['new_state']:  # Was set to reviewed, now un-review
                if conv_id in self.reviewed_conversations:
                    self.reviewed_conversations.remove(conv_id)
            else:  # Was un-reviewed, now review
                self.reviewed_conversations.add(conv_id)
            
            # Update UI
            for i in range(self.selector.count()):
                item_text = self.selector.itemText(i)
                if item_text.startswith("Conversation: ") or item_text.startswith("Group: "):
                    conv_str = item_text.replace("Conversation: ", "").replace("Group: ", "").replace(" [Reviewed]", "")
                    check_conv_id = (conv_str,) if item_text.startswith("Group: ") else tuple(sorted(conv_str.split(" <-> ")))
                    if check_conv_id == conv_id:
                        if conv_id in self.reviewed_conversations and " [Reviewed]" not in item_text:
                            self.selector.setItemText(i, f"{item_text} [Reviewed]")
                        elif conv_id not in self.reviewed_conversations and " [Reviewed]" in item_text:
                            self.selector.setItemText(i, item_text.replace(" [Reviewed]", ""))
                        break
            
            self.status_bar.showMessage("Undo: Reviewed status")
        
        elif action['type'] == 'tag_change':
            # Reverse tag changes
            for change in action['changes']:
                msg_id = change['msg_id']
                old_tags = change['old_tags']
                # Find message and restore old tags
                for conv_id, messages in self.conversations.items():
                    for msg in messages:
                        if msg['msg_id'] == msg_id:
                            msg['tags'] = old_tags.copy()
                            # Update model to refresh display
                            keyword_state = self._get_keyword_state()
                            current_messages = self.message_model.messages_data
                            self.message_model.setMessages(
                                current_messages,
                                keyword_state,
                                self.compute_row_color,
                                self.get_media_path,
                                self.media_files
                            )
                            break
            
            self.status_bar.showMessage(f"Undo: Tag '{action['tag']}' change")
        
        # Refresh view
        self.schedule_search()
    
    def redo_action(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            self.status_bar.showMessage("Nothing to redo")
            return
        
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        
        if action['type'] == 'reviewed_status':
            conv_id = action['conv_id']
            # Apply the action
            if action['new_state']:  # Set to reviewed
                self.reviewed_conversations.add(conv_id)
            else:  # Un-review
                if conv_id in self.reviewed_conversations:
                    self.reviewed_conversations.remove(conv_id)
            
            # Update UI
            for i in range(self.selector.count()):
                item_text = self.selector.itemText(i)
                if item_text.startswith("Conversation: ") or item_text.startswith("Group: "):
                    conv_str = item_text.replace("Conversation: ", "").replace("Group: ", "").replace(" [Reviewed]", "")
                    check_conv_id = (conv_str,) if item_text.startswith("Group: ") else tuple(sorted(conv_str.split(" <-> ")))
                    if check_conv_id == conv_id:
                        if conv_id in self.reviewed_conversations and " [Reviewed]" not in item_text:
                            self.selector.setItemText(i, f"{item_text} [Reviewed]")
                        elif conv_id not in self.reviewed_conversations and " [Reviewed]" in item_text:
                            self.selector.setItemText(i, item_text.replace(" [Reviewed]", ""))
                        break
            
            self.status_bar.showMessage("Redo: Reviewed status")
        
        elif action['type'] == 'tag_change':
            # Apply tag changes
            for change in action['changes']:
                msg_id = change['msg_id']
                new_tags = change['new_tags']
                # Find message and apply new tags
                for conv_id, messages in self.conversations.items():
                    for msg in messages:
                        if msg['msg_id'] == msg_id:
                            msg['tags'] = new_tags.copy()
                            # Update model to refresh display
                            keyword_state = self._get_keyword_state()
                            current_messages = self.message_model.messages_data
                            self.message_model.setMessages(
                                current_messages,
                                keyword_state,
                                self.compute_row_color,
                                self.get_media_path,
                                self.media_files
                            )
                            break
            
            self.status_bar.showMessage(f"Redo: Tag '{action['tag']}' change")
        
        # Refresh view
        self.schedule_search()
    
    def manage_notes(self):
        """Open dialog to view/edit notes for the selected conversation."""
        selection = self.selector.currentText()
        if not selection.startswith("Conversation: ") and not selection.startswith("Group: "):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("No Selection")
            msg.setText("Please select a conversation first.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        
        conv_str = selection.replace("Conversation: ", "").replace("Group: ", "").replace(" [Reviewed]", "")
        conv_id = (conv_str,) if selection.startswith("Group: ") else tuple(sorted(conv_str.split(" <-> ")))
        
        # Get current note
        current_note = self.conversation_notes.get(conv_id, "")
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Conversation Notes")
        # Remove question mark help button
        dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        
        # Conversation info
        info_label = QLabel(f"<b>Conversation:</b> {conv_str}")
        layout.addWidget(info_label)
        
        # Notes text area
        notes_label = QLabel("Notes:")
        layout.addWidget(notes_label)
        notes_text = QTextEdit()
        notes_text.setPlainText(current_note)
        notes_text.setPlaceholderText("Enter notes about this conversation...")
        layout.addWidget(notes_text)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Resizable dialog (from V3.18 style, but made resizable)
        dialog.setMinimumSize(600, 400)
        dialog.resize(600, 400)
        
        if dialog.exec() == QDialog.Accepted:
            new_note = notes_text.toPlainText()
            if new_note.strip():
                self.conversation_notes[conv_id] = new_note
            elif conv_id in self.conversation_notes:
                # Remove note if empty
                del self.conversation_notes[conv_id]
            self.status_bar.showMessage("Note saved")
    
    def search_notes(self, search_term):
        """Search for conversations containing the search term in notes."""
        if not search_term:
            return []
        
        search_term_lower = search_term.lower()
        matching_conversations = []
        for conv_id, note in self.conversation_notes.items():
            if search_term_lower in note.lower():
                matching_conversations.append(conv_id)
        return matching_conversations

    def save_progress(self):
        """Save reviewed conversations and tagged messages to a JSON file."""
        if not self.conversations:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("No Data")
            msg.setText("No conversations loaded. Please load data first.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        
        # Get save file path (default to user's home directory)
        default_filename = os.path.join(USER_HOME, f"KikParser_progress_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        # Create QFileDialog instance for autosizing and centering
        save_dialog = QFileDialog(self)
        save_dialog.setWindowTitle("Save Progress")
        save_dialog.setFileMode(QFileDialog.AnyFile)
        save_dialog.setAcceptMode(QFileDialog.AcceptSave)
        save_dialog.setNameFilter("JSON Files (*.json);;All Files (*)")
        save_dialog.selectFile(default_filename)
        center_and_autosize_dialog(save_dialog, self, width_ratio=0.65, height_ratio=0.7, min_width=700, min_height=550)
        if save_dialog.exec() == QDialog.Accepted:
            file_path = save_dialog.selectedFiles()[0] if save_dialog.selectedFiles() else None
        else:
            file_path = None
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Collect all tagged messages
            tagged_messages = {}
            for conv_id, messages in self.conversations.items():
                for msg in messages:
                    if msg['tags']:
                        tagged_messages[msg['msg_id']] = list(msg['tags'])
            
            # Convert reviewed conversations from set of tuples to list of lists for JSON
            reviewed_conversations = [list(conv_id) for conv_id in self.reviewed_conversations]
            
            # Convert conversation notes from dict of tuples to dict of lists for JSON
            conversation_notes = {str(list(conv_id)): note for conv_id, note in self.conversation_notes.items()}
            
            # Convert cell_borders from set of tuples to list of lists for JSON
            cell_borders = [list(border) for border in self.cell_borders]
            
            # Create progress data structure
            progress_data = {
                'version': APP_VERSION,
                'saved_at': datetime.datetime.now().isoformat(),
                'reviewed_conversations': reviewed_conversations,
                'tagged_messages': tagged_messages,
                'conversation_notes': conversation_notes,
                'cell_borders': cell_borders,
                'total_reviewed': len(self.reviewed_conversations),
                'total_tagged': len(tagged_messages),
                'total_notes': len(self.conversation_notes),
                'total_borders': len(self.cell_borders)
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=4)
            
            self.status_bar.showMessage(
                f"Progress saved: {len(self.reviewed_conversations)} reviewed conversations, "
                f"{len(tagged_messages)} tagged messages, {len(self.conversation_notes)} notes, "
                f"{len(self.cell_borders)} cell borders"
            )
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Progress Saved")
            msg.setText(f"Progress saved successfully!\n\nReviewed conversations: {len(self.reviewed_conversations)}\nTagged messages: {len(tagged_messages)}\nNotes: {len(self.conversation_notes)}\nCell borders: {len(self.cell_borders)}\n\nFile: {os.path.basename(file_path)}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            logger.info(f"Progress saved to {file_path}")
        except Exception as e:
            error_msg = f"Error saving progress: {str(e)}"
            logger.error(error_msg)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Save Error")
            msg.setText(error_msg)
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Error saving progress")

    def load_progress(self):
        """Load previously saved progress from a JSON file."""
        if not self.conversations:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("No Data")
            msg.setText("No conversations loaded. Please load data first.")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        
        # Get load file path (default to user's home directory)
        # Create QFileDialog instance for autosizing and centering
        open_dialog = QFileDialog(self)
        open_dialog.setWindowTitle("Load Progress")
        open_dialog.setFileMode(QFileDialog.ExistingFile)
        open_dialog.setNameFilter("JSON Files (*.json);;All Files (*)")
        open_dialog.setDirectory(USER_HOME)
        center_and_autosize_dialog(open_dialog, self, width_ratio=0.65, height_ratio=0.7, min_width=700, min_height=550)
        if open_dialog.exec() == QDialog.Accepted:
            file_path = open_dialog.selectedFiles()[0] if open_dialog.selectedFiles() else None
        else:
            file_path = None
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Create progress dialog
            progress = QProgressDialog("Loading progress...", None, 0, 100, self)
            progress.setWindowTitle("Import Progress")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            QApplication.processEvents()
            
            # Load progress data
            progress.setLabelText("Reading progress file...")
            progress.setValue(10)
            QApplication.processEvents()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            # Validate structure
            if 'reviewed_conversations' not in progress_data or 'tagged_messages' not in progress_data:
                raise ValueError("Invalid progress file format")
            
            # Convert reviewed conversations from list of lists back to set of tuples
            progress.setLabelText("Processing reviewed conversations...")
            progress.setValue(30)
            QApplication.processEvents()
            
            reviewed_conversations = set(tuple(conv_id) for conv_id in progress_data['reviewed_conversations'])
            
            # Load tagged messages
            tagged_messages = progress_data['tagged_messages']
            
            # Load conversation notes
            conversation_notes = {}
            if 'conversation_notes' in progress_data:
                import ast
                for conv_id_list_str, note in progress_data['conversation_notes'].items():
                    try:
                        # Validate input before using ast.literal_eval
                        if not isinstance(conv_id_list_str, str) or not conv_id_list_str.strip():
                            continue
                        # Convert list representation back to tuple (same format as reviewed_conversations)
                        conv_id_list = ast.literal_eval(conv_id_list_str)
                        # Validate the result is a list
                        if not isinstance(conv_id_list, list):
                            continue
                        conv_id = tuple(conv_id_list)
                        # Validate note is a string
                        if isinstance(note, str):
                            conversation_notes[conv_id] = note
                    except (ValueError, SyntaxError, TypeError) as e:
                        logger.warning(f"Failed to parse conversation note key '{conv_id_list_str}': {e}")
                        continue
            
            # Load cell borders
            cell_borders = set()
            if 'cell_borders' in progress_data:
                cell_borders_list = progress_data['cell_borders']
                # Convert list of lists to set of tuples
                cell_borders = {tuple(border) for border in cell_borders_list if isinstance(border, list) and len(border) == 2}
            
            # Apply reviewed status
            progress.setLabelText("Applying reviewed status...")
            progress.setValue(40)
            QApplication.processEvents()
            
            loaded_reviewed = 0
            for conv_id in reviewed_conversations:
                if conv_id in self.conversations:
                    self.reviewed_conversations.add(conv_id)
                    loaded_reviewed += 1
            
            # Apply conversation notes
            progress.setLabelText("Loading notes...")
            progress.setValue(45)
            QApplication.processEvents()
            
            loaded_notes = 0
            for conv_id, note in conversation_notes.items():
                if conv_id in self.conversations:
                    self.conversation_notes[conv_id] = note
                    loaded_notes += 1
            
            # Apply cell borders
            progress.setLabelText("Loading cell borders...")
            progress.setValue(47)
            QApplication.processEvents()
            
            self.cell_borders = cell_borders
            loaded_borders = len(cell_borders)
            
            # OPTIMIZATION: Create a msg_id lookup dictionary for O(1) access instead of O(n*m)
            progress.setLabelText("Building message index...")
            progress.setValue(50)
            QApplication.processEvents()
            
            msg_id_to_message = {}
            for conv_id, messages in self.conversations.items():
                for msg in messages:
                    msg_id_to_message[msg['msg_id']] = msg
            
            # Apply tags to messages using the lookup dictionary
            progress.setLabelText("Applying tags to messages...")
            progress.setValue(60)
            QApplication.processEvents()
            
            total_tagged = len(tagged_messages)
            loaded_tags = 0
            for idx, (msg_id, tags_list) in enumerate(tagged_messages.items()):
                if msg_id in msg_id_to_message:
                    msg_id_to_message[msg_id]['tags'] = set(tags_list)
                    loaded_tags += 1
                
                # Update progress every 100 messages
                if (idx + 1) % 100 == 0 or (idx + 1) == total_tagged:
                    progress_value = 60 + int(30 * (idx + 1) / total_tagged) if total_tagged > 0 else 90
                    progress.setValue(progress_value)
                    progress.setLabelText(f"Applying tags... ({loaded_tags}/{total_tagged})")
                    QApplication.processEvents()
            
            # Update conversation selector to show reviewed status
            progress.setLabelText("Updating conversation list...")
            progress.setValue(90)
            QApplication.processEvents()
            
            for i in range(self.selector.count()):
                item_text = self.selector.itemText(i)
                if item_text.startswith("Conversation: "):
                    conv_str = item_text.replace("Conversation: ", "").replace(" [Reviewed]", "")
                    conv_id = tuple(sorted(conv_str.split(" <-> ")))
                    if conv_id in self.reviewed_conversations and " [Reviewed]" not in item_text:
                        self.selector.setItemText(i, f"{item_text} [Reviewed]")
            
            progress.setLabelText("Refreshing display...")
            progress.setValue(95)
            QApplication.processEvents()
            
            # Refresh the current view to show updated tags and borders
            self.schedule_search()
            
            # Trigger table refresh to show cell borders
            if hasattr(self, 'message_model') and self.message_model:
                top_left = self.message_model.index(0, 0)
                bottom_right = self.message_model.index(self.message_model.rowCount() - 1, self.message_model.columnCount() - 1)
                self.message_model.dataChanged.emit(top_left, bottom_right, [])
                if hasattr(self, 'message_table'):
                    self.message_table.viewport().update()
            
            progress.setValue(100)
            progress.close()
            
            self.status_bar.showMessage(
                f"Progress loaded: {loaded_reviewed} reviewed conversations, "
                f"{loaded_tags} tagged messages, {loaded_notes} notes, {loaded_borders} cell borders"
            )
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Progress Loaded")
            msg.setText(f"Progress loaded successfully!\n\nReviewed conversations restored: {loaded_reviewed}\nTagged messages restored: {loaded_tags}\nNotes restored: {loaded_notes}\nCell borders restored: {loaded_borders}\n\nFile: {os.path.basename(file_path)}")
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            logger.info(f"Progress loaded from {file_path}: {loaded_reviewed} reviewed, {loaded_tags} tagged, {loaded_notes} notes, {loaded_borders} borders")
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON file: {str(e)}"
            logger.error(error_msg)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Load Error")
            msg.setText(error_msg)
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Error loading progress: Invalid file format")
        except Exception as e:
            error_msg = f"Error loading progress: {str(e)}"
            logger.error(error_msg)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Load Error")
            msg.setText(error_msg)
            msg.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.status_bar.showMessage("Error loading progress")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = KikAnalyzerGUI()
    window.show()
    sys.exit(app.exec())