# Scale System

## Overview

The Stage Plot Creator uses a real-world scale system based on actual equipment dimensions to ensure accurate stage layout planning.

## Scale Reference

### Reference Item: Fender Deluxe Reverb
- **Physical Width**: 24.5 inches
- **Image Width**: 57 pixels (FenderAmp.png)
- **Scale Factor**: 2.327 pixels per inch

### Scale Calculation
```
57 pixels = 24.5 inches
1 pixel = 24.5 ÷ 57 = 0.4298 inches
1 inch = 57 ÷ 24.5 = 2.327 pixels
```

## Scale Utilities

### Basic Conversions
```typescript
import { inchesToPixels, feetToPixels, pixelsToInches, pixelsToFeet } from '$lib/utils/scale';

// Convert real-world measurements to pixels
const width = inchesToPixels(24.5); // 57 pixels
const stageWidth = feetToPixels(4); // 112 pixels (4 feet)

// Convert pixels back to real-world measurements  
const realWidth = pixelsToInches(57); // 24.5 inches
const stageFeet = pixelsToFeet(112); // 4 feet
```

### Formatting Dimensions
```typescript
import { formatDimensions } from '$lib/utils/scale';

const formatted = formatDimensions(112, 112); // "4' × 4'"
const formatted2 = formatDimensions(57, 36); // "2'0.5" × 1'3.5""
```

## Standard Stage Sizes

### Pre-defined Stage Decks
```typescript
import { STAGE_SIZES } from '$lib/utils/scale';

// Available sizes:
STAGE_SIZES['4x4'] // 112 × 112 pixels (4' × 4')
STAGE_SIZES['4x8'] // 112 × 224 pixels (4' × 8') 
STAGE_SIZES['8x8'] // 224 × 224 pixels (8' × 8')
```

### Custom Dimensions
```typescript
// For custom items, calculate dimensions based on real measurements
const customAmp = {
  width: inchesToPixels(22), // 22" wide amp
  height: inchesToPixels(18), // 18" deep amp
  name: "Custom Amp"
};
```

## SVG Stage Elements

### Stage Deck Component
```svelte
<script>
  import { StageDeck } from '$lib';
</script>

<StageDeck 
  size="4x4"
  x={100} 
  y={200}
  bind:selected
/>
```

### Properties
- **size**: '4x4' | '4x8' | '8x8'
- **x, y**: Position in pixels
- **selected**: Selection state
- **id**: Unique identifier

## Real-World Examples

### Common Equipment Scales
```typescript
// Based on actual equipment dimensions
const equipment = {
  fenderDeluxeReverb: { width: 57, height: 36 }, // 24.5" × 15.5"
  marshallStack: { width: 70, height: 105 },     // 30" × 45"
  drumKit: { width: 140, height: 93 },           // 60" × 40"
  keyboard88: { width: 135, height: 35 },        // 58" × 15"
};
```

### Stage Planning
```typescript
// Plan a 20' × 16' stage
const stageWidth = feetToPixels(20);  // 465 pixels
const stageHeight = feetToPixels(16); // 372 pixels

// Add 4×4 stage decks
const deckSize = STAGE_SIZES['4x4']; // 112 × 112 pixels each
const decksWide = Math.floor(stageWidth / deckSize.width); // 4 decks
const decksDeep = Math.floor(stageHeight / deckSize.height); // 3 decks
```

## Validation

### Scale Verification
```typescript
import { validateScale } from '$lib/utils/scale';

const validation = validateScale();
if (validation.isValid) {
  console.log('Scale system is accurate');
} else {
  console.warn('Scale validation failed:', validation.details);
}
```

## Design Principles

### 1. Real-World Accuracy
- All items scaled to actual equipment dimensions
- Musicians can trust measurements for venue planning
- Accurate spacing calculations for cable runs, power, etc.

### 2. Consistent Reference
- Single reference item (Fender Deluxe Reverb) for all scaling
- Prevents drift and inconsistency across different items
- Easy to verify and validate

### 3. Professional Standards
- Uses industry-standard equipment as references
- Measurements match technical specifications
- Compatible with venue planning requirements

### 4. Extensible System
- Easy to add new items with accurate dimensions
- Scale utilities handle all conversions automatically
- SVG system allows for precise vector graphics

## Future Enhancements

### Metric Support
```typescript
// Future: Add metric conversions
const cmToPixels = (cm: number) => inchesToPixels(cm / 2.54);
const metersToPixels = (m: number) => cmToPixels(m * 100);
```

### Scale Validation Tools
- Visual overlay showing real-world grid
- Measurement tools for verification
- Export with dimension annotations

### Dynamic Scaling
- Zoom levels while maintaining accuracy
- Different scales for different view modes
- Automatic scale adjustment for print sizes

## Technical Implementation

### Pixel Perfect Scaling
- All conversions rounded to nearest pixel
- Maintains visual clarity at standard zoom levels
- Prevents sub-pixel rendering issues

### Performance Considerations
- Pre-calculated common dimensions
- Cached conversion results
- Efficient SVG rendering for stage elements

### Cross-Platform Consistency
- Same scale on all devices and browsers
- Independent of screen DPI/resolution
- Consistent export results

This scale system ensures that stage plots created in the app accurately represent real-world stage layouts, making them useful for actual production planning and equipment placement.