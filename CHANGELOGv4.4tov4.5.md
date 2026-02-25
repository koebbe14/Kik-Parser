# Changelog

## V4.5

### New Records Format Support

- **Dual-format data loading**: The application now auto-detects and supports both the **legacy** format (`content/text-msg-data/` per-conversation CSV files + `.txt` log files) and the **new** Kik records format (`content/data-text.csv` and `content/data-media.csv` + `.csv` log files). Format detection is automatic based on the presence of `data-text.csv` or `data-media.csv` in the content folder.
- **New-format content parsing**: Reads `data-text.csv` and `data-media.csv` directly from the content folder
- **New-format log file support**: Parses CSV-based log files (`chat_platform_sent.csv`, `group_send_msg_platform.csv`, `chat_platform_sent_received.csv`, `group_receive.csv`, `group_receive_msg_platform.csv`) alongside legacy `.txt` log files. 
- **Media files from `medias/` folder**: For the new format, media files are resolved from a `medias/` folder (under content or root) using the `filename` and `content_id` columns in `data-media.csv`.
- **Updated import dialog**: The "Import Kik Data" dialog now explains both formats and no longer requires manual CSV file selection for the new format.

### File Menu and Button Relocation

- **New File menu**: Added a `File` menu to the menu bar containing `Manage Tags`, `Manage Hotkeys`, `Load New Data`, `Check for updates`, and `Help`.
- **Toolbar cleanup**: Removed the following buttons from the bottom toolbar to reduce clutter (moved to File menu): `Manage Tags`, `Manage Hotkeys`, `Load New Data`, `Help`.
- **"Check for updates" relocated**: Moved from a permanent status bar widget to the File menu.

### Group Legend

- **Group Legend button**: New toolbar button opens a dialog displaying group legend data loaded from a `group-legend-[username].csv` file found alongside the content/logs folders.
- **Group Legend dialog**: Shows a table with GID, Name, Code, Public, Deleted, Last Join, Last Activity, plus computed Send Count and Receive Count from loaded message data.
- **Export Group Legend**: The dialog includes an option to export the group legend table to CSV.

### Table Selection and Row Highlighting

- **Row highlighting on cell click**: Clicking any cell in the main message table now highlights the entire row with a soft background color for easier readability. The specifically selected cell(s) are shown with a darker highlight to distinguish them from the row highlight.
- **Theme-aware highlight colors**: Added `row_highlight` and `cell_highlight` colors to both light and dark themes, customizable via the Color Settings dialog.
- **Right-click copy options**: The context menu now offers **"Copy Selected Cells"** (copies only selected cells as tab-separated values) and **"Copy Selected Rows"** (copies all columns for every row containing a selection).
- **Multi-select support**: Ctrl+click to add individual cells to the selection; Shift+click for range selection. Row highlighting extends to all rows that contain any selected cell.

### Border Improvements

- **Fixed multi-cell border detection**: The right-click context menu now correctly detects existing selection-region borders when determining whether to show "Add Border" or "Remove Border." Previously, only individual cell borders were checked.
- **Fixed "Remove Border" for multi-cell regions**: "Remove Border" now appears in the context menu when right-clicking cells within an existing multi-cell border region. Removal works by finding and discarding all overlapping selection-region borders rather than requiring an exact selection match.


