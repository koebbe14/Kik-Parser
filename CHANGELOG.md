# Changelog - KikAnalyzer V4.2

## Session Changes Summary

### Data Processing & Deduplication

#### Added support for text-msg-data.csv files containing a "content_id" column
- **Issue**: Prior versions of the program will built around text-msg-data.csv files not containing a "content_id" column.  Instead, the content_id was obtained from various log .txt files.  Recieved media has been identifed in these new versions of the text-msg-data.csv files but not listed in the associated log files
- **Fix**: Added support to find, analyze, and parse the text-msg-data.csv file for "content_IDs"
- **Result**: Media files are now properly displayed if the records come from either the log files or the .csv files.  If the same content_id is found in mulitple records and has the same sender/user/time/date/ip, then the data is aggragated and compiled as one entry


### User Interface Improvements

#### Dialog Window Sizing for Laptop Displays
- **Issue**: Initial dialog windows ("Import Kik Data" and "Select Kik Message CSV Files") were too small with hard-to-read text on laptop displays.
- **Fixes**:
  - **Import Kik Data Dialog**:
    - Window size increased from 700x600 to 1200x900 pixels.
    - Label font size increased to 24pt (QFont) and 26px (HTML).
    - Heading font size increased to 31px (HTML).
    - Button font size increased to 22pt with larger padding (18px 31px).
    - Button minimum size increased to 176x55 pixels.
  
  - **Select Kik Message CSV Files Dialog**:
    - Window size increased from 900x650 to 1200x900 pixels.
    - Minimum size increased from 880x660 to 1100x800 pixels.
    - All font sizes increased proportionally (labels: 24pt, buttons: 22pt, text edit: 22px).
    - Button sizes and padding increased to match Import dialog.

#### Automatic Update Checking
- **Feature**: Added automatic update checking on application startup.
- **Behavior**:
  - Checks for updates automatically 1 second after the main GUI is displayed.
  - Only shows a message if an update is available (same message as manual check).
  - Silently fails if no update is available or if there's an error (no message shown).
  - Manual "Check for updates" button still works as before, showing all messages including "up to date" status.

### Border Feature Enhancements

#### Selection Region Borders
- **Issue**: When multiple cells were selected, "Add Border" placed individual borders around each cell instead of one border around the entire selection.
- **Fix**: 
  - Modified border logic to detect multiple cell selections.
  - When multiple cells are selected, calculates the bounding rectangle and draws a single border around the entire selection region.
  - Single cell selections still work as before (individual cell borders).
  - Selection region borders are stored separately and persist in configuration.

#### Increased Border Thickness
- **Enhancement**: Increased border line thickness from 3px to 5px for better visibility.
- **Applies to**: Both individual cell borders and selection region borders.

### Technical Details

#### Data Structures
- Added `selection_borders` set to store selection region borders as `(min_row, max_row, min_col, max_col)` tuples.
- Enhanced deduplication key to include `content_id` for more accurate duplicate detection.

#### Configuration Persistence
- Selection borders are now saved and loaded with the application configuration.
- Line number preservation ensures accurate CSV line number tracking.

---

## Files Modified
- `KikAnalyzerV4.1.py` - Main application file with all improvements

## Testing Recommendations
1. Test deduplication with media files that exist in both CSV and log files.
2. Verify line numbers match actual CSV line numbers.
3. Test border feature with both single and multiple cell selections.
4. Verify dialog readability on laptop displays.
5. Test automatic update checking on startup.

