# Changelog

## Recent Updates

### Color Customization System
- **Added**: Comprehensive color settings feature allowing users to customize all application colors
  - New "Color Settings" option in View menu
  - Separate tabs for Light Mode and Dark Mode color customization
  - Color picker dialog with preview swatches showing current colors
  - All color changes are persistent and saved to `KikParser_config.json`
  - "Reset to Default" option to restore original color scheme
  - Color previews update in real-time as colors are changed

- **Added**: Custom color support in ThemeManager
  - Extended ThemeManager to support user-defined color overrides
  - Custom colors take precedence over default theme colors
  - Custom colors are preserved when switching between light and dark modes
  - All UI components respect custom color settings

- **Enhanced**: HTML Export color integration
  - HTML exports now use current theme colors (including custom colors)
  - Color legend in HTML reports reflects custom color settings
  - Dynamic CSS generation based on active theme and custom colors
  - Both light and dark mode colors are embedded in HTML for theme switching

- **Changed**: Default color scheme updated
  - New professional color palette for light mode
  - Improved contrast and readability
  - Updated tag colors to use Bootstrap-inspired professional colors
  - HTML table header color changed from green to medium gray (#6c757d)

- **Improved**: Color legend in Help dialog
  - Color legend now displays actual custom colors when applied
  - Removed descriptive text names, showing only color swatches
  - Legend dynamically updates to reflect current color settings

### Custom Cell Borders Feature
- **Added**: Custom cell border functionality allowing users to highlight individual cells
  - Right-click context menu with "Add Border" and "Remove Border" options
  - Borders are customizable via Color Settings dialog (default: bold red)
  - Borders persist across sessions and are saved in configuration
  - Borders appear in HTML exports with the same styling
  - Supports selecting individual cells or multiple cells (Ctrl+Click)

### Cell Selection Improvements
- **Changed**: Table selection behavior from row-only to cell-level selection
  - Users can now select individual cells or multiple cells
  - Supports Ctrl+Click for multiple cell selection
  - Shift+Click for range selection
  - Entire rows can still be selected by selecting all cells in the row

### Copy Functionality
- **Added**: Copy selected cells to clipboard
  - Right-click context menu "Copy" option
  - Ctrl+C keyboard shortcut support
  - Copies cells as tab-separated values (TSV) for easy pasting into Excel/Notepad
  - Maintains row/column structure when copying multiple cells

### Save Progress Enhancement
- **Added**: Cell borders are now saved and restored with the "Save Progress" feature
  - Cell borders are included in `KikParser_progress.json` files
  - Borders are automatically restored when loading saved progress
  - Table refreshes to display restored borders

### Bug Fixes
- **Fixed**: Data loading issue when config file exists on second run
  - Prevented `schedule_search()` from being called before data is loaded
  - Added check to ensure conversations exist before triggering search

- **Fixed**: HTML export border mapping for Message ID field
  - Message ID cells no longer incorrectly inherit borders from Message column
  - Message ID field correctly mapped to -1 (not a table column)

- **Fixed**: Label truncation in Export Options Dialog
  - Added CSS styling to prevent QGroupBox title truncation
  - "Export Scope (Select One)", "Sanitize Export", and "Fields to Include" labels now fully visible
  - Improved spacing and layout to prevent checkbox overlap with titles

### Color Settings Dialog
- **Added**: Comprehensive color settings dialog with organized categories
  - Background Colors: Main, Widget, Alternate, Dialog, Table, Hover, Group Box, Legend
  - Text Colors: Primary, Secondary
  - Border Colors: Border, Cell Border
  - Button Colors: Hover, Background
  - Tag Colors: CSAM, Evidence, Of Interest, Custom
  - Keyword Colors: Keyword Hit
  - Sender Colors: Sender 1, Sender 2
  - Row Colors: Default Row, Alternate Row
  - Scrollable interface with grouped color options
  - Monospace font for hex color codes
  - Improved layout to prevent label truncation

### Technical Improvements
- **Added**: `BorderedCellDelegate` class for rendering custom cell borders
- **Added**: `copy_selected_cells()` method for clipboard functionality
- **Added**: `ColorSettingsDialog` class for comprehensive color customization
- **Enhanced**: `ThemeManager` class with custom color support and persistence
- **Enhanced**: Progress save/load to include cell borders data
- **Improved**: Table refresh mechanisms for border display updates
- **Improved**: Dynamic stylesheet generation for all UI components
- **Improved**: Configuration persistence for custom colors and cell borders

