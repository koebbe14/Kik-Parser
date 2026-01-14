# Kik Analyzer V4.1

[![Version](https://img.shields.io/badge/version-4.1-blue.svg)](https://github.com/Koebbe14/Kik-Parser/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

> A professional forensic analysis tool for parsing, searching, and analyzing Kik messaging data exported from Kik's servers pursuant to legal process.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Guide](#user-guide)
  - [Loading Data](#loading-data)
  - [Search and Filter](#search-and-filter)
  - [Tagging Messages](#tagging-messages)
  - [Keyword Management](#keyword-management)
  - [Media Handling](#media-handling)
  - [Export Options](#export-options)
  - [Advanced Features](#advanced-features)
- [Technical Details](#technical-details)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## Overview

**Kik Analyzer V4.1** is a comprehensive graphical user interface (GUI) application designed for forensic analysis of Kik messaging data. The tool processes responsive records received from Kik pursuant to legal process, enabling investigators and analysts to efficiently parse, search, filter, tag, and export conversation data for evidentiary purposes.

The application processes multiple data formats from Kik exports:
- CSV message files from the `text-msg-data` folder
- Log files from the `logs` folder (including `chat_platform_sent.txt`, `chat_platform_sent_received.txt`, `group_receive_msg_platform.txt`, `group_send_msg_plaform.txt`)
- Media files (images and videos) from the `content` folder

---

## Features

### Core Functionality

- **Multi-Format Data Parsing**: Automatically parses CSV files, log files, and indexes media files from Kik data exports
- **Conversation Management**: Groups messages into individual and group conversations with intuitive navigation
- **Advanced Search & Filter**: 
  - Full-text search across messages, senders, and receivers
  - Exact word matching option
  - Date range filtering
  - Search across all conversations or filter by selected conversation
- **Keyword Highlighting**: Create and manage keyword lists for automatic message highlighting (useful for CSAM detection, evidence identification, etc.)
- **Message Tagging System**: 
  - Pre-built tags: CSAM, Evidence, Of Interest
  - Custom tag creation and management
  - Keyboard hotkeys for rapid tagging (default: Ctrl+1, Ctrl+2, Ctrl+3)
  - Multi-select tagging support
- **Media Management**:
  - Thumbnail previews in message table
  - Global and per-item media blurring for sensitive content protection
  - Full-size media viewer
  - Media file indexing and linking
- **Export Capabilities**:
  - HTML export with interactive features (dark mode, search, filtering)
  - CSV export with customizable field selection
  - Optional media sanitization (blurring) in exports
  - MD5 hash generation for all files
  - Complete data package with copied media, logs, and CSV files
- **Statistics Dashboard**: Comprehensive statistics panel showing message counts, user breakdowns, tagged messages, keyword hits, and media statistics
- **Review Tracking**: Mark conversations as reviewed to track analysis progress

### Advanced Features

- **Undo/Redo System**: 50-action history for tagging and review operations
- **Conversation Notes**: Add notes to conversations for case documentation
- **Theme Support**: Light and dark mode with customizable color schemes
- **Update Checking**: Automatic version checking via GitHub API
- **Configurable Settings**: Persistent configuration for tags, hotkeys, keyword lists, and preferences
- **Cell Border Highlighting**: Visual emphasis for specific messages or cells
- **Comprehensive Logging**: Optional detailed logging to `kik_analyzer.log` for troubleshooting

---

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 7 or later (64-bit recommended)
- **RAM**: 4 GB minimum (8 GB recommended for large datasets)
- **Storage**: Sufficient disk space for Kik data folders (can range from hundreds of MB to several GB)
- **Display**: 1280x720 resolution minimum (1920x1080 recommended)

### Data Requirements

- **Kik Data Export**: Unzipped Kik data folder obtained through legal means (search warrant, etc.)
- **Required Folder Structure**:
  ```
  Kik Data Folder/
  ├── content/
  │   ├── text-msg-data/
  │   │   └── *.csv (message files)
  │   └── [media files]
  └── logs/
      └── *.txt (log files)
  ```

---

## Installation

### Download

1. Navigate to the [Releases](https://github.com/Koebbe14/Kik-Parser/releases) page
2. Download the latest `KikAnalyzerV4.1.exe` file
3. Place the executable in your desired installation directory

> **Note**: The application will create configuration files, keyword lists, and logs in the directory:  C:\Users\\[Username]

### First Run

1. Double-click `KikAnalyzerV4.1.exe` to launch the application
2. The application will prompt you to load Kik data on first launch
3. Configuration files (`config.json`) will be created automatically

---

## Quick Start

1. **Launch Application**: Double-click `KikAnalyzerV4.1.exe`
2. **Load Data**: Click "Load New Data" and select your unzipped Kik data folder
3. **Select CSV Files**: Choose one or more CSV files from the `text-msg-data` folder
4. **Select Conversation**: Use the dropdown to choose a conversation to analyze
5. **Search & Filter**: Use the search bar and date filters to find specific messages
6. **Tag Messages**: Right-click messages or use hotkeys (Ctrl+1, Ctrl+2, Ctrl+3) to tag
7. **Export Results**: Click "Export" to save filtered/tagged data in HTML or CSV format

---

## User Guide

### Loading Data

#### Initial Data Load

1. Click the **"Load New Data"** button in the toolbar
2. In the file dialog, navigate to and select the root Kik data folder containing:
   - `content` subfolder (with `text-msg-data` and media files)
   - `logs` subfolder (with `.txt` log files)
3. Click **"OK"** to proceed
4. In the CSV selection dialog, browse and select one or more CSV files from the `text-msg-data` folder
5. Click **"OK"** to begin processing

#### Data Processing

During data loading, the application will:
- Index all media files (images/videos) from the `content` folder
- Parse CSV files for message data
- Parse log files for additional message metadata
- Group messages into conversations (1:1 chats and group chats)
- Associate sent/received media with conversations
- Display "Data loaded successfully" in the status bar

#### Reloading Data

Click **"Load New Data"** at any time to restart the data loading process or load another case. This will clear existing data and load fresh data.

---

### Search and Filter

#### Basic Text Search

1. Enter search terms in the **"Search:"** text field
2. The search automatically filters messages matching:
   - Message content
   - Sender name
   - Receiver name
3. Results update automatically after a brief delay (debounced for performance)

#### Exact Word Matching

- Check the **"Exact Word Match"** checkbox to enable whole-word searching
- Example: Searching "cat" will not match "category" or "scatter"

#### Search Scope

- **Unchecked**: Searches only within the selected conversation
- **Checked ("Search All Conversations")**: Searches across all conversations

#### Date Range Filtering

1. Click the **"From:"** date picker to set the start date
2. Click the **"To:"** date picker to set the end date
3. Leave dates empty to include all messages
4. Messages are filtered to show only those within the specified date range

#### Search Results

- The label above the message table displays: **"Found X messages"**
- Messages are displayed in a sortable table with columns: Date, Time, Sender, Receiver, Message, Tags, Media
- Keyword hits are highlighted in green
- Tagged messages display colored tags in the Tags column

---

### Tagging Messages

#### Pre-built Tags

The application includes three pre-built tags with default colors:
- **CSAM** (Red) - For child sexual abuse material
- **Evidence** (Orange) - For evidentiary messages
- **Of Interest** (Yellow) - For messages requiring further review

#### Tagging via Context Menu

1. Select one or more message rows (use Ctrl+Click or Shift+Click for multiple selection)
2. Right-click on the selected message(s)
3. Choose **"Tag Message"** from the context menu
4. In the dialog, check the tags you want to apply
5. Click **"OK"** to apply tags

#### Tagging via Hotkeys

Default hotkeys:
- **Ctrl+1**: Toggle CSAM tag
- **Ctrl+2**: Toggle Evidence tag
- **Ctrl+3**: Toggle Of Interest tag

To use:
1. Select one or more message rows
2. Press the appropriate hotkey combination
3. Tags are toggled on/off for selected messages

#### Managing Tags

1. Click the **"Manage Tags"** button in the toolbar
2. In the dialog:
   - **Add**: Create new custom tags
   - **Edit**: Modify existing tag names and colors
   - **Delete**: Remove tags (pre-built tags cannot be deleted)
3. Click **"Save"** to apply changes

#### Managing Hotkeys

1. Click the **"Manage Hotkeys"** button in the toolbar
2. Assign key sequences (e.g., Ctrl+4, Ctrl+5) to tags
3. Click **"Save"** to activate shortcuts

---

### Keyword Management

#### Creating Keyword Lists

1. Click **"Create New Keyword List"** button
2. Enter a list name in the dialog
3. Add keywords (one per line) in the text area
4. Check **"Exact Word Matching"** if you want whole-word matching for all keywords in the list
5. Click **"OK"** to save (saved in the KikParser_config.json)

#### Editing Keyword Lists

1. Select a keyword list from the **"Keyword List:"** dropdown
2. Click **"Edit Keywords"** button
3. Modify the list name (for new lists), keywords, or matching options
4. Click **"OK"** to save changes

#### Using Keyword Lists

1. Select a keyword list from the **"Keyword List:"** dropdown
2. Messages containing matching keywords are automatically highlighted in specified color
3. Matching behavior (exact word or partial) is determined by the list's settings

#### Viewing Keyword Hits

1. Click the **"View Keyword Hits"** button in the toolbar
2. A dedicated dialog displays all messages containing keyword matches
3. You can tag, or copy messages from this dialog

---

### Media Handling

#### Viewing Media

- **Thumbnails**: Media files are displayed as thumbnails in the "Media" column of the message table
- **Full Size**: Double-click a thumbnail to open the full-size image/video in your default viewer

#### Blurring Media

**Global Blur Toggle:**
- Click the **"Blur Media"** button to blur all media thumbnails globally
- Click again to unblur all thumbnails
- This affects only thumbnail previews, not original files

**Per-Item Blur:**
- Right-click on a specific media thumbnail
- Select **"Blur Media"** or **"Unblur Media"** from the context menu
- Per-item blur settings persist independently of the global blur toggle

**Export Blurring:**
- When exporting, you can choose to blur:
  - CSAM-tagged media only
  - All media
- Blurred media in exports protects sensitive content while maintaining file integrity

---

### Export Options

#### Opening Export Dialog

1. Click the **"Export"** button in the toolbar
2. The export options dialog appears with multiple configuration options

#### Export Scope

Select what to export:
- **Tagged Messages**: Export only messages that have been tagged
- **Selected Conversation**: Export messages from the currently selected conversation
- **All Conversations**: Export all messages from all conversations

#### Sanitization Options

- **Blur CSAM Only**: Blur media in messages tagged as CSAM
- **Blur All Media**: Blur all media in the export
- **No Blurring**: Export media without blurring

#### Export Format

**HTML Export:**
- Interactive HTML file with:
  - Summary statistics
  - Dark mode toggle
  - Built-in search and filtering
  - Embedded media thumbnails (blurred if selected)
  - Links to full-size media files
  - MD5 hash table for all files (media, CSVs, logs)
  - Complete data package: exported HTML, media files, logs, and CSV files in organized subfolders

**CSV Export:**
- Simple CSV table with selected fields
- Suitable for import into spreadsheet applications or databases

#### Field Selection

Choose which fields to include in the export:
- Date/Time
- Sender/Receiver
- Message content
- Tags
- Media references
- IP addresses
- Port numbers
- Content IDs
- Conversation names
- Notes

#### Sorting Options

- **By Conversation/User**: Group messages by conversation
- **By Timestamp**: Sort chronologically

#### Export Process

1. Configure all export options
2. Click **"OK"**
3. Choose the save location and filename
4. Wait for processing (large exports may take several minutes)
5. A success message displays when export is complete

---

### Advanced Features

#### Statistics Panel

1. Click **"Show Stats"** button to toggle the statistics panel
2. View comprehensive statistics:
   - Total message count
   - Number of unique users
   - Tagged message counts
   - Keyword hit counts
   - Media file counts
   - Sender breakdown (for 1:1 conversations)

#### Conversation Management

**Mark as Reviewed:**
- Select a conversation from the dropdown
- Click **"Mark as Reviewed"** button
- The conversation label updates with "[Reviewed]" prefix
- Toggle on/off to track review status

**Conversation Notes:**
- Add notes to conversations for case documentation
- Notes are included in exports when the "notes" field is selected
- Access notes through the conversation context menu

#### Undo/Redo

- **Undo**: Press Ctrl+Z to undo the last tagging or review action (up to 50 actions)
- **Redo**: Press Ctrl+Y to redo an undone action
- Useful for correcting accidental tag applications

#### Theme Customization

- The application supports light and dark themes
- Access color settings through the via the View button
- Color settings are saved in configuration

#### Update Checking

- Click the **"Check for Updates"** button to check for newer versions
- The application connects to GitHub to check for updates
- If an update is available, you'll be directed to the releases page

---

## Technical Details

### File Formats Supported

- **CSV Files**: Comma-separated values from Kik's `text-msg-data` folder
- **Log Files**: Plain text log files from Kik's `logs` folder:
  - `chat_platform_sent.txt`
  - `chat_platform_sent_received.txt`
  - `group_receive_msg_platform.txt`
  - `group_send_msg_plaform.txt`
- **Media Files**: Images and videos indexed from the `content` folder

### Configuration Files

- **KikParser_config.json**: Stores application settings, tags, hotkeys, and preferences
- **kik_analyzer.log**: Optional logging file (disabled by default)

### Data Processing

- Messages are parsed and grouped by conversation ID
- Timestamps are normalized and sorted chronologically
- Media files are indexed by content ID and linked to messages
- Large datasets are processed with progress indicators

### Performance Considerations

- **Search Debouncing**: 600ms delay for text search, 1000ms for date filters
- **Caching**: Thumbnail cache (200 items) for improved performance
- **Threading**: Background processing for data loading and searching
- **Memory Management**: Efficient handling of large datasets

### Security Features

- Media blurring for sensitive content protection
- MD5 hash generation for file integrity verification
- Optional logging for audit trails
- Secure handling of sensitive data

---

## Best Practices

### Performance Optimization

- **Large Datasets**: For datasets with >10,000 messages:
  - Use conversation filters to narrow scope
  - Apply date range filters before searching
  - Be patient during initial data loading
  - Consider exporting subsets rather than entire datasets

### Data Security

- **Sensitive Content**: Always blur CSAM and other sensitive media before sharing exports
- **File Integrity**: Use MD5 hashes provided in HTML exports to verify file integrity
- **Secure Storage**: Store Kik data folders and exports in secure, encrypted locations
- **Access Control**: Limit access to the application and data files to authorized personnel only

### Workflow Recommendations

1. **Initial Review**: Load data and review conversation list
2. **Keyword Screening**: Create and apply keyword lists for initial screening
3. **Systematic Tagging**: Use consistent tagging methodology (e.g., CSAM, Evidence, Of Interest)
4. **Review Tracking**: Mark conversations as reviewed as you complete analysis
5. **Documentation**: Add conversation notes for important findings
6. **Export Strategy**: Export tagged messages and keyword hits for further analysis
7. **Verification**: Review exported data and verify MD5 hashes

### Tagging Best Practices

- Use consistent tag names and meanings across cases
- Document tag definitions in case notes
- Use hotkeys for frequently applied tags
- Review tagged messages periodically using "View Tagged" dialog

---

## Troubleshooting

### Common Issues

**"Data loaded successfully" but no messages appear:**
- Verify CSV files contain valid message data
- Check that date filters are not excluding all messages
- Ensure conversation dropdown is set to "All" or a valid conversation

**Search not working:**
- Clear search field and try again
- Uncheck "Exact Word Match" if partial matches are expected
- Verify you're searching in the correct conversation scope

**Media thumbnails not displaying:**
- Verify media files exist in the `content` folder
- Check file paths in the original Kik data structure
- Ensure media files are not corrupted

**Export taking too long:**
- Large exports (10,000+ messages) may take 10+ minutes
- Consider exporting smaller subsets
- Ensure sufficient disk space for export files

**Application crashes or freezes:**
- Check `kik_analyzer.log` for error messages
- Verify Kik data folder structure is correct
- Ensure sufficient RAM (4GB minimum, 8GB recommended)
- Try reloading data

### Logging

To enable detailed logging for troubleshooting:
- Logging is disabled by default
- If enabled, logs are written to `kik_analyzer.log` in the user's home directory
- Logs include timestamps, log levels, and detailed error messages

### Getting Help

1. Check the **"Help"** button in the application for built-in instructions
2. Review this README for detailed feature documentation
3. Check the log file (`kik_analyzer.log`) for error details
4. Verify your Kik data folder structure matches requirements

---

## Support

### Version Information

- **Current Version**: 4.1
- **Release Notes**: Includes delete keyword list feature and various improvements

### Updates

- Check for updates via the application's update checker
- Visit the [Releases](https://github.com/Koebbe14/Kik-Parser/releases) page for latest version
- Updates are released on GitHub

### Legal Notice

This tool is designed for use with Kik data obtained through legal process (search warrants, etc.). Users are responsible for ensuring they have proper legal authority to access and analyze the data. The tool is provided "as-is" without warranty.

### License

Proprietary software. All rights reserved.

---

## Acknowledgments

Kik Analyzer V4.1 is developed for forensic analysis purposes. The tool processes data exported from Kik's servers pursuant to legal process and is intended for use by law enforcement, legal professionals, and authorized investigators.

---

## License

Permission is hereby granted to law-enforcement agencies, digital-forensic analysts, and authorized investigative personnel ("Authorized Users") to use and copy this software for the purpose of criminal investigations, evidence review, training, or internal operational use.

The following conditions apply:

1. **Redistribution:** This software may not be sold, published, or redistributed to the general public. Redistribution outside an authorized agency requires written permission from the developer.

2. **No Warranty:** This software is provided "AS IS," without warranty of any kind, express or implied, including but not limited to the warranties of accuracy, completeness, performance, non-infringement, or fitness for a particular purpose. The developer shall not be liable for any claim, damages, or other liability arising from the use of this software, including the handling of digital evidence.

3. **Evidence Integrity:** Users are responsible for maintaining forensic integrity and chain of custody when handling evidence. This software does not alter source evidence files and is intended only for analysis and review.

4. **Modifications:** Agencies and investigators may modify the software for internal purposes. Modified versions may not be publicly distributed without permission from the developer.

5. **Logging & Privacy:** Users are responsible for controlling log files and output generated during use of the software to prevent unauthorized disclosure of sensitive or personally identifiable information.

6. **Compliance:** Users agree to comply with all applicable laws, departmental policies, and legal requirements when using the software.

By using this software, the user acknowledges that they have read, understood, and agreed to the above terms.

---

## About the Developer

Patrick Koebbe is an Internet Crimes Against Children (ICAC) Investigator with expertise in digital forensics tools. This software was developed to streamline Kik data analysis in real-world investigations.

For support, feature requests, or collaborations, contact: koebbe14@gmail.com.


**Last Updated**: 2026  
**Version**: 4.1  
**Platform**: Windows
