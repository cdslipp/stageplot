# Import/Export System

The Stage Plot Creator includes a robust import/export system that allows users to save their work and share stage plots with others.

## Overview

The import/export system uses a standardized JSON format based on the InputList 1.0.0 specification, adapted specifically for stage plots with positioning data.

**Key Design Decision**: All stage plots use a standardized **letter-size landscape** canvas (8.5" × 11") to ensure consistent positioning across different devices and exports. This prevents positioning issues that would occur with variable canvas sizes.

## Features

### Export Functionality
- **One-click export**: Downloads current stage plot as a JSON file
- **Automatic naming**: Files are named `{plot-name}-{date}.json`
- **Complete state preservation**: Saves all items, positions, musicians, and settings
- **Metadata tracking**: Includes export timestamp and version info

### Import Functionality
- **File validation**: Checks for valid JSON and stage plot format
- **State restoration**: Loads all items with exact positioning
- **UI reset**: Clears selections and resets interface state
- **Error handling**: User-friendly error messages for invalid files

## JSON Schema

The export format follows the Stage Plot 1.0.0 schema located at `/specs/stage-plot-1.0.0.json`.

### Key Structure
```json
{
  "version": "1.0.0",
  "type": "stage_plot",
  "plot_name": "Band Name",
  "revision_date": "2024-01-15",
  "canvas": {
    "format": "letter",
    "orientation": "landscape",
    "width": 1056,
    "height": 816,
    "dpi": 96
  },
  "stage": {
    "x": 50,
    "y": 50,
    "width": 956,
    "height": 666,
    "margins": {
      "top": 50,
      "right": 50,
      "bottom": 100,
      "left": 50
    }
  },
  "items": [
    {
      "id": 123456789,
      "name": "Lead Guitar",
      "type": "egt",
      "position": {
        "x": 200,
        "y": 300,
        "width": 80,
        "height": 120,
        "zone": "DSL",
        "relativeX": -350,
        "relativeY": 425
      },
      "channel": "1",
      "musician": "John Doe",
      "itemData": { /* original catalog data */ }
    }
  ],
  "musicians": [
    {
      "id": 1,
      "name": "John Doe",
      "instrument": "Guitar"
    }
  ]
}
```

## Position System

The system uses a dual positioning approach:

### Absolute Positioning
- `x`, `y`: Stage coordinates (pixels from stage area origin)
- `width`, `height`: Item dimensions in pixels

### Canvas vs Stage Architecture
- **Canvas**: The "paper" or viewport (standardized letter size, 8.5" × 11" landscape = 1056×816px @ 96 DPI)
- **Stage**: The performance area within the canvas (with 50px margins, leaving 956×666px for items)
- **Margins**: Space reserved for titles, legends, input lists, and metadata

This separation allows for:
- Consistent positioning across all exports/imports
- Professional printable layouts
- Future support for different paper sizes (A4, tabloid)
- Space for additional UI elements outside the stage area

### Relative Positioning
- `relativeX`: Distance from downstage center edge (negative = stage left, positive = stage right)
- `relativeY`: Distance from downstage edge (always positive, upstage direction)
- `zone`: Stage zone classification (DSL, DSC, DSR, USL, USC, USR)

## Usage

### Exporting a Stage Plot
1. Click the "File" button in the top-right header
2. Select "Export Plot"
3. File downloads automatically with format: `{plot-name}-{YYYY-MM-DD}.json`

### Importing a Stage Plot
1. Click the "File" button in the top-right header
2. Select "Import Plot"
3. Choose a previously exported JSON file
4. Plot loads with all items and settings restored

### Viewing File Format
- Click "File" → "File Format" to view the JSON schema specification

## Technical Implementation

### Export Process
1. Collect current application state (items, musicians, canvas settings)
2. Calculate relative positions using stage coordinate system
3. Serialize to JSON format with validation
4. Generate filename with timestamp
5. Trigger browser download

### Import Process
1. File selection via hidden input element
2. JSON parsing and format validation
3. Schema compliance checking
4. State restoration in correct order:
   - Canvas dimensions
   - Plot metadata
   - Musicians list
   - Items with positioning
5. UI state reset (clear selections, stop placement mode)

### Error Handling
- Invalid file format detection
- Missing required fields validation
- Graceful degradation for partial data
- User feedback via alerts and console logging

## File Compatibility

### Supported Formats
- `.json` files only
- Stage Plot schema v1.0.0
- UTF-8 encoding

### Version Compatibility
- Forward compatible design for future schema versions
- Version field allows for migration strategies
- Extensible metadata section for new features

## Security Considerations

- Client-side only processing (no server upload)
- No executable code in JSON files
- File size limits via browser constraints
- Input sanitization for all imported data

## Future Enhancements

- Batch export/import for multiple plots
- Direct sharing via URLs
- Integration with cloud storage services
- Version history and change tracking
- Collaborative editing features

## Troubleshooting

### Common Issues

**Import fails with "Invalid format"**
- Ensure file is a valid JSON
- Check that `type` field equals "stage_plot"
- Verify required fields are present

**Items appear in wrong positions**
- Canvas dimensions may differ between export/import
- Check that relative positioning is preserved
- Verify zone calculations are correct

**Missing musicians or metadata**
- Older export formats may lack some fields
- Check export version compatibility
- Re-export from current version if needed

## API Reference

### Component Props
```typescript
type ImportExportProps = {
  title: string;
  lastModified: string;
  items: Item[];
  musicians: Musician[];
  canvasWidth: number;
  canvasHeight: number;
  getItemZone: (item: Item) => string;
  getItemPosition: (item: Item) => { x: number; y: number };
  onImportComplete?: () => void;
};
```

### Export Data Format
See `/specs/stage-plot-1.0.0.json` for complete schema definition.