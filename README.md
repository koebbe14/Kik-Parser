Kik Analyzer V1.5 - User Guide

Introduction

Kik Analyzer V1.4-1 is a graphical user interface (GUI) application designed to analyze Kik messaging data exported from Kik's servers. It allows users to load Kik chat data, view conversations, search and filter messages, tag messages for review (e.g., for evidence or CSAM), highlight keyword hits, blur sensitive media, generate statistics, and export data to HTML or CSV formats. This tool is designed to parse and help analyze responsive records received by Kik pursuant to legal process.

The application is a standalone executable file (.exe) for Windows. It processes CSV files from Kik's "text-msg-data" folder and log files from the "logs" folder, while also indexing media files from the "content" folder.

Key Features:

•	Load and parse Kik data folders (specifically these files: chat_platform_sent.txt, chat_platform_sent_received.txt, group_receive_msg_platform.txt, group_send_msg_plaform.txt, text-msg-data .CSV)
•	Search and filter messages by text, date, and keywords.
•	Tag messages with customizable labels and hotkeys.
•	Blur media thumbnails globally or selectively.
•	View tagged messages and keyword hits in dedicated dialogs.
•	Mark conversations as "Reviewed."
•	Display conversation statistics.
•	Export filtered/tagged data with optional sanitization (blurring).
•	Manage tags, hotkeys, and keyword lists.
This guide provides step-by-step instructions for using all features.
System Requirements
•	Operating System: Windows
•	Hardware: At least 4GB RAM (for large datasets); disk space for Kik data folders (which can be gigabytes).
•	Kik Data Export: You must have an unzipped Kik data folder from Kik (containing "content" and "logs" subfolders). Obtain this via legal means (e.g., search warrant or user export).

Installation and Running the Program

1.	Download the executable file KikAnalyzerV1.4.exe: 
  o	Place the file in a folder (the program will generate additional files that will be created in this same folder)

2.	Run the Application: 
  o	Double click to Run the executable 

Loading Kik Data

Upon first launch (or clicking "Load New Data" button), the app prompts you to load data.

1.	Select Kik Data Folder: 
  o	A message box appears: "Import Kik Data Folder."
  o	A file dialog opens: Choose the root Kik data folder containing the unzipped Kik folder containing "content" (with media files and "text-msg-data"   subfolder) and "logs" (with .txt log files).
  o	Click "OK" to proceed or "Cancel" to exit.
  o	If the folder is invalid (missing subfolders), an error pops up—retry.

2.	Select CSV Files: 
  o	A "Select Kik Message CSV Files" dialog opens.
  o	It points to the "text-msg-data" folder inside "content."
  o	Click "Browse..." to select one or more .CSV files (e.g., chat messages).
  o	Selected files appear in the text area.
  o	Click "OK" to load.
  o	If no files are selected or invalid, an error appears—retry.
  3.	Data Processing: 
  o	The app indexes media files (images/videos) from "content."
  o	CSVs and logs (e.g., chat_platform_sent.txt) for messages will be parsed.
  o	Messages are grouped into conversations (1:1 or groups) and sent/received media is included in the parsed conversations
  o	The Status bar shows "Data loaded successfully”, and All Conversations messages will appear in the GUI
  o	Users can use the dropdown option to select particular conversations

Reloading Data: Click "Load New Data" button anytime to restart the process.
Main Interface Overview

The GUI has:

•	Top Controls (Group Box): 
  o	Search bar: Text input for filtering messages, sender, receiver.
  o	"Exact Word Match" checkbox: For whole-word searching. (e.g., "cat" won't match "category").
  o	"Search All Conversations" checkbox: Search across all conversations vs. only the selected.
  o	Date filters: "From" and "To" date pickers.
  o	"Keyword List:" dropdown: Select a list for highlighting.
  o	"Create New Keyword List" and "Edit Keywords" buttons.
  o	"Conversation:" dropdown: Select to view.
•	Search Results Label: "Found X messages."
•	Message Table: Columns: Date, Time, Sender, Receiver, Message, Tags, Media. 
  o	Media column shows thumbnails (click to open full media).
  o	Right-click messages to tag or use Hotkeys (multiple messages can be selected and simultaneously tagged)
•	Stats Panel: Hidden by default; shows message counts, users, etc.
•	Toolbar (Bottom Buttons): 
  o	"View Tagged": Open tagged messages dialog.
  o	"View Keyword Hits": Open keyword matches dialog.
  o	"Mark as Reviewed": Toggles “[Reviewed]” on selected conversation in dropdown menu
  o	"Manage Tags": Edit available tags.
  o	"Manage Hotkeys": Assign shortcuts to tags.
  o	"Blur Media": Toggle thumbnail blur.
  o	"Show Stats": Toggle stats panel.
  o	"Load New Data": Reload data.
  o	"Export": Export options dialog.
  o	"Help": Show instructions

Navigation Tips:
  •	Use mouse/keyboard to select rows (multi-select with Ctrl/Shift).
  •	Double-click media thumbnails to open full file.
  •	Hover for tooltips on most elements.

Searching and Filtering Messages
1.	Basic Search: 
  o	Enter text in "Search:" bar (e.g., "hello").
  o	Matches sender, receiver, message
  o	Results update in table after a short delay.
2.	Exact Word Match: 
  o	Check "Exact Word Match" for whole-word search (e.g., "hi" won't match "high").
3.	Search All Conversations: 
  o	Check to search across all; uncheck for selected conversation only.
4.	Date Filtering: 
  o	Set "From:" and "To:" dates via calendar popups.
  o	Filters messages within the range.
5.	Keyword Highlighting: 
  o	Select a list from "Keyword List:" dropdown
  o	Matches are highlighted in green
  o	Whole-word matching per list (set when creating/editing).

Results Display:
•	Table shows filtered messages, grouped by conversation headers if "All."
•	Keyword hits in green; tags in colors (red=CSAM, orange=Evidence, yellow=Of Interest).

Managing Keyword Lists

Keyword lists highlight messages for specific terms (e.g., CSAM keywords).

1.	Select List: 
  o	Use dropdown to choose (loads from "keywords" folder as .txt files).
2.	Create New List: 
  o	Click "Create New Keyword List."
  o	Dialog: Enter "List Name," keywords (one per line in text area).
  o	Check "Exact Word Matching" for whole words.
  o	Click "OK" to save as .txt in "keywords" folder.
3.	Edit Existing List: 
  o	Select list, click "Edit Keywords."
  o	Edit name (disabled for existing), keywords, whole-word checkbox.
  o	Save updates the .txt file.

Tips: Lists persist across sessions. Default is empty "default.txt."

Viewing and Managing Conversations

1.	Select Conversation: 
  o	Dropdown: Choose "All" or specific (sorted alphabetically).
  o	Table updates with messages, sorted by timestamp.
2.	Mark as Reviewed: 
  o	Select conversation, click "Mark as Reviewed."
  o	Adds "[Reviewed]" to dropdown label; toggles off/on.
3.	Stats Panel: 
  o	Click "Show Stats" to display.
  o	Shows totals: messages, users, tagged, keyword hits, media (with sender breakdown for 1:1).

Tagging Messages

Tags flag messages (e.g., "CSAM," "Evidence").
1.	Prebuilt Tags: CSAM (red), Evidence (orange), Of Interest (yellow).
2.	Tag a Message: 
  o	Select row(s) in table.
  o	Right-click message column: "Tag Message" menu.
  o	Dialog: Check tags to apply (multi-select).
  o	Tags appear in "Tags" column; row color updates.
3.	Hotkeys: 
  o	Default: Ctrl+1=CSAM, Ctrl+2=Evidence, Ctrl+3=Of Interest.
o	Select rows, press hotkey to toggle tag.
4.	Manage Tags: 
  o	Click "Manage Tags" button.
  o	Dialog: List of tags; Add/Edit/Delete.
  o	Save updates available tags.
5.	Manage Hotkeys: 
  o	Click "Manage Hotkeys."
  o	Dialog: Assign key sequences (e.g., Ctrl+4) to tags.
  o	Save and shortcuts activate.

View Tagged:
•	Click "View Tagged" button.
•	Dialog: Table of tagged messages (sortable by time/conversation).
•	Columns: Date, Time, Sender, Receiver, Message, Tags, Media.
•	Copy selected to clipboard.

Blurring Media

Protects sensitive thumbnails.
1.	Toggle Global Blur: 
  o	Click "Blur Media" to blur all thumbnail media.  Click again to unblur all thumbnail media
  o	The “Blur Media” button works independently of locally blurring an individual thumbnail via the right click > blur feature
2.	Local Blur (right click): 
  o	Right-click thumbnail: "Blur Media" / "Unblur Media" for that item only.  This stays persistent regardless of the state of the “Blur Media” toggle button
3.	Export Blurring: Covered in Export section (CSAM-only or all).

Note: Blur affects thumbnail previews in the GUI, not originals or full size images once clicked

Viewing Keyword Hits
•	Click "View Keyword Hits."
•	Dialog: Table of matches appears
•	Similar to tagged dialog: Copy, right-click to tag (or use hotkeys)

Exporting Data

Exports filtered/tagged data with options.
1.	Open Export Dialog: 
  o	Click "Export."
  o	Dialog: Scope (Tagged, Selected Conversation, All), Sanitize (Blur CSAM-only or All), Format (HTML/CSV), Sort By (User/Conversation or Timestamp), Fields to Include.
2.	Options: 
  o	Scope: Check one (e.g., "Tagged Messages").
  o	Sanitize: Blur medial in export
  o	Format: HTML (styled table with links) or CSV.
  o	Sort: By conversation or time.
  o	Fields: Select all or specific (e.g., exclude IP).
  o	Click "OK," choose save location.
3.	HTML Export Details: 
  o	Includes summary stats, dark mode toggle, search/filter
  o	Media: Embedded thumbnails (blurred if selected); links to full (blurred/original).
  o	Hashes (MD5) of all files (media, CSVs, logs).
  o	Copied media/logs/CSVs to subfolder.
4.	CSV Export: 
  o	Simple table with selected fields.

Tips: Large exports may take time.

Help and Additional Features
•	Help Button: Click for instructions
•	Logging: All actions/errors in kik_analyzer.log.
•	Config: Saves tags, hotkeys, selected keyword in config.json.

Best Practices and Tips
•	Performance: For large datasets (>10k messages), searches may lag—use filters and BE PATIENT
•	Security: Handle sensitive data carefully; blur CSAM.
•	Errors: Check log if having issues

