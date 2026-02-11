# Changelog - KikAnalyzer V4.2 → V4.3

## Version 4.3 - New Tag and Enhanced Blur Options

## Summary
This update adds the "Child Notable/Age Difficult" tag and enhanced blur options. The new tag provides better categorization for age-related content, while the new blur options offer more granular control over media sanitization in exports.

### New Features

#### 1. New Default Tag: "Child Notable/Age Difficult"
- Added "Child Notable/Age Difficult" as a new default/prebuilt tag
- Tag is automatically available in all tag selection dialogs
- Tag cannot be removed (protected as a default tag)
- Tag appears in tag management interfaces with protection from deletion
- Tag is automatically included in `available_tags` even when loading from older config files

#### 2. Enhanced Export Blur Options
- **New Option**: "Blur Child Notable/Age Difficult-tagged" checkbox in export dialog
  - Allows selective blurring of media tagged with "Child Notable/Age Difficult"
  - Works independently of other blur options
  
- **New Option**: "Blur Media That's Currently Blurred" checkbox in export dialog
  - Blurs media that has been manually blurred in the GUI using the blur button
  - Respects individual media blur states tracked by the application
  - Useful for maintaining blur state consistency between GUI and exports

### Changes to Existing Features

#### Tag System
- Updated `prebuilt_tags` list to include: `["Evidence", "CSAM", "Child Notable/Age Difficult", "Of Interest"]`
- Added "Child Notable/Age Difficult" to `tag_priorities` with priority 2.5 (between CSAM and Evidence)
- Tag priority order: CSAM (2) → Child Notable/Age Difficult (2.5) → Evidence (3) → Of Interest (1)
- Updated `get_tag_color()` method to recognize and apply color to the new tag

#### Theme and Color Management
- Added `tag_child_notable` color to ThemeManager for both light and dark themes
  - Light theme: `#ffa500` (Orange)
  - Dark theme: `#ffa500` (Orange)
- Added `tag_child_notable` to color customization options
- Updated color label mapping to include "Child Notable/Age Difficult Tag"

#### Export Functionality
- Enhanced blur logic in `export_messages()` to support multiple blur conditions:
  - Blur all media (existing)
  - Blur CSAM-tagged media (existing)
  - Blur Child Notable/Age Difficult-tagged media (new)
  - Blur currently blurred media (new)
- Blur conditions are evaluated with OR logic - any matching condition will blur the media
- Updated both image/video blur logic and non-media file handling

#### HTML Export
- Added "Child Notable/Age Difficult" to HTML export color legend
- Added CSS styling for `tr.tag-child-notable` class in both light and dark modes
- Updated tag filter dropdown in HTML export to include "Child Notable/Age Difficult"
- Updated tag class assignment logic to recognize the new tag in priority order
- Tag appears in exported HTML with proper color coding and filtering support

#### Help Documentation
- Updated help dialog to include "Child Notable/Age Difficult" in color legend
- Updated help text to mention the new tag in pre-built tags list
- Updated export sanitization help text to describe new blur options
- Updated tooltips to reference the new tag where applicable

#### Configuration Management
- Enhanced `load_config()` to ensure all prebuilt tags are always included in `available_tags`
- Prevents missing tags when loading from older config files
- Maintains backward compatibility while adding new default tags

#### Tag Management Dialog
- Added protection for "Child Notable/Age Difficult" tag in `ManageTagsDialog`
- Prevents deletion of the new default tag
- Shows appropriate warning message when attempting to delete protected tags



#### Export Options Dialog
- Reorganized blur options for better clarity:
  - "Blur CSAM-tagged" (renamed from "Blur Only Media Tagged as CSAM")
  - "Blur Child Notable/Age Difficult-tagged" (new)
  - "Blur All" (renamed from "Blur All Media")
  - "Blur Media That's Currently Blurred" (new)
- Added tooltips for new blur options explaining their functionality



### Backward Compatibility
- ✅ Fully backward compatible with existing config files
- ✅ Existing tags and settings are preserved
- ✅ Older exports remain functional
- ✅ New tag automatically added to existing installations

### Migration Notes
- No manual migration required
- Application will automatically include new tag on next startup
- Existing tagged messages continue to work as before
- New blur options are opt-in (disabled by default)

### Bug Fixes
- Fixed issue where prebuilt tags might not appear if config file was created before tag was added
- Ensured all default tags are always available regardless of config file state

---



