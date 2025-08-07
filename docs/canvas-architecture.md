# Canvas Architecture

## Problem Statement

Variable canvas sizes would cause major positioning issues when importing/exporting stage plots. If User A creates a plot on a 1100×850 canvas and User B imports it on a different canvas size, all item positions would be incorrect.

## Solution: Standardized Canvas + Stage Architecture

### Canvas (The "Paper")
- **Format**: Letter size (8.5" × 11")
- **Orientation**: Landscape 
- **Dimensions**: 1056×816 pixels @ 96 DPI
- **Purpose**: Consistent "paper" size for all stage plots

### Stage (The Performance Area)
- **Position**: 50px offset from canvas edges
- **Dimensions**: 956×666 pixels (after margins)
- **Purpose**: Actual area where items are placed

### Margins
- **Top**: 50px (space for title)
- **Left/Right**: 50px each (general margins)
- **Bottom**: 100px (space for legends, input lists)

## Benefits

### 1. Positioning Consistency
```typescript
// Export on any device
item.x = 200; // Position within stage area

// Import on any device  
item.x = 200; // Same position within stage area
```

### 2. Professional Layout
```
┌─────────────── Canvas (1056×816) ──────────────┐
│  Title: "Rock Band Stage Plot"        [50px]  │
│ ┌────────── Stage Area (956×666) ─────────┐ │ │
│ │                                         │ │ │
│ │  🎸     🥁      🎤      🎸              │ │ │
│ │  Guitar Drums   Vocal   Bass            │ │ │
│ │                                         │ │ │
│ │                                         │ │ │
│ └─────────────────────────────────────────┘ │ │
│  Input List: 1. Guitar, 2. Bass, 3. Vocal... │
│  Date: 2024-01-15    Version: 1.0.0   [100px] │
└─────────────────────────────────────────────────┘
```

### 3. Future Extensibility
- Easy to add A4 support (210×297mm)
- Tabloid size (11×17") for large productions
- Different orientations (portrait for tall stages)

## Implementation

### Standard Configuration
```typescript
import { getStandardConfig } from '$lib/utils/canvas';

const config = getStandardConfig();
// {
//   canvas: { format: 'letter', orientation: 'landscape', width: 1056, height: 816, dpi: 96 },
//   stage: { x: 50, y: 50, width: 956, height: 666, margins: {...} }
// }
```

### Coordinate Conversion
```typescript
import { stageToCanvas, canvasToStage } from '$lib/utils/canvas';

// Convert between coordinate systems
const canvasPos = stageToCanvas(stageX, stageY, stageArea);
const stagePos = canvasToStage(canvasX, canvasY, stageArea);
```

### Export Format
```json
{
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
    "margins": { "top": 50, "right": 50, "bottom": 100, "left": 50 }
  },
  "items": [
    {
      "position": {
        "x": 200,     // Position within stage area
        "y": 150,     // Position within stage area
        "width": 80,
        "height": 120
      }
    }
  ]
}
```

## Migration Strategy

### Phase 1: Enforce Standard (Current)
- All new exports use letter-landscape format
- Imports force standard canvas size
- Legacy variable-size exports still work (converted)

### Phase 2: Multiple Formats (Future)
```typescript
type PaperFormat = 'letter' | 'a4' | 'tabloid';
type Orientation = 'landscape' | 'portrait';

const config = getCanvasConfig('a4', 'portrait');
```

### Phase 3: Smart Scaling (Future)
- Auto-detect optimal paper size based on content
- Scale items proportionally between formats
- Maintain aspect ratios and relationships

## Design Principles

1. **Consistency First**: Same layout on every device
2. **Professional Output**: Print-ready from day one  
3. **Future-Proof**: Extensible to new formats
4. **User-Friendly**: Transparent to end users
5. **Standards-Based**: Follow industry paper sizes

## Technical Details

### DPI Calculation
```typescript
// Letter: 8.5" × 11"
// @ 96 DPI (standard web resolution)
width = 8.5 * 96 = 816px (portrait)
height = 11 * 96 = 1056px (portrait)

// Landscape orientation swaps dimensions
width = 1056px
height = 816px
```

### Margin Rationale
- **50px standard margins**: ~0.52" at 96 DPI (professional printing standard)
- **100px bottom margin**: Extra space for input lists and metadata
- **Total usable area**: 90.4% of canvas (956×666 of 1056×816)

### Browser Compatibility
- Uses standard web measurements (pixels @ 96 DPI)
- Compatible with all modern browsers
- CSS print media queries for actual printing
- Responsive design maintains proportions

This architecture solves the fundamental positioning problem while setting up a professional, extensible foundation for the future.