# Bits UI Command Integration

This document explains how the Stage Plot Creator integrates with Bits UI's Command component to provide a powerful command palette for adding stage items.

## Overview

The `ItemCommandPalette` component leverages Bits UI's Command component to create a searchable, keyboard-navigable interface for selecting and adding stage equipment to the canvas. This replaces the previous simple modal dialog with a much more powerful and user-friendly interface.

## Key Features

### 🔍 Search & Filter
- **Real-time Search**: Type to instantly filter through 50+ stage equipment items
- **Keyword Matching**: Items are searchable by name, type, category, and custom keywords
- **Smart Scoring**: Uses Bits UI's built-in scoring algorithm for relevance-based results

### ⌨️ Keyboard Navigation
- **Command Palette Style**: Open with `Cmd/Ctrl + K` (universal command palette shortcut)
- **Arrow Keys**: Navigate up/down through items
- **Enter**: Select an item
- **Escape**: Close the palette
- **VIM Bindings**: Ctrl+N/J/P/K for navigation (enabled by default)

### 🎨 Visual Design
- **Item Previews**: Each item shows its actual stage equipment image
- **Category Organization**: Items grouped by Microphones, Amplifiers, Keyboards, etc.
- **Theme Support**: Fully supports light/dark mode with proper theming
- **Responsive**: Works on all screen sizes with optimized layouts

## Component Architecture

### ItemCommandPalette.svelte

The main command palette component that wraps Bits UI's Command component:

```svelte
<Command.Root>
  <Command.Input />        <!-- Search input -->
  <Command.List>          <!-- Scrollable list container -->
    <Command.Viewport>    <!-- Handles dynamic sizing -->
      <Command.Empty />   <!-- "No results" state -->
      <Command.Group>     <!-- Category groups -->
        <Command.GroupHeading />
        <Command.GroupItems>
          <Command.Item />  <!-- Individual items -->
        </Command.GroupItems>
      </Command.Group>
    </Command.Viewport>
  </Command.List>
</Command.Root>
```

### Data Structure

Each stage item is defined with the following structure:

```typescript
type Item = {
  id: string;           // Unique identifier
  name: string;         // Display name
  type: string;         // Item type (mic, amp, keyboard, etc.)
  category: string;     // Group category
  image: string;        // Path to preview image
  keywords: string[];   // Search keywords
  description?: string; // Optional description
};
```

## Integration Points

### 1. Main Page Integration

The command palette is integrated into the main stage plot interface:

```svelte
<!-- Add Item button with keyboard shortcut indicator -->
<button onclick={openAddMenu} title="Add Item (⌘K)">
  Add Item
  <span class="shortcut">⌘K</span>
</button>

<!-- Command palette component -->
<ItemCommandPalette 
  bind:open={isAddingItem} 
  on:select={handleItemSelect}
/>
```

### 2. Item Selection Flow

1. User opens command palette (button click or `Cmd/Ctrl + K`)
2. User searches/browses for desired item
3. User selects item (click or Enter)
4. System creates placing preview that follows mouse
5. User clicks on canvas to place item
6. Item is added to the stage with proper data

### 3. Dynamic Item Rendering

Items on the canvas now render dynamically based on their data:

```svelte
<img 
  src={item.itemData?.image || "/img/egt/FenderAmp.png"} 
  alt={item.itemData?.name || "Stage Item"} 
  class="h-full w-full object-contain"
>
```

## Available Items

The command palette includes 50+ categorized stage equipment items:

### Microphones
- Center Vocal Mic, Boom Mics, Instrument Mics
- Overhead Mics, Wireless Mics, Headset Mics

### Amplifiers  
- Fender Amps, Marshall Heads/Cabinets, Vox Amps
- Bass Amps, Ampeg Rigs

### Keyboards
- Keyboard Stands, Hammond B3, Rhodes Piano
- Nord Stage, Double Keyboard Setups

### Drums
- Complete Drum Kits, Individual Drums
- Cymbals, Electronic Drums

### Monitors
- Floor Wedges, In-Ear Monitors
- Personal Monitor Systems

### Instruments
- Electric/Acoustic Guitars, Bass Guitars
- Guitar Stands and Accessories

### DJ Equipment
- Complete DJ Setups, CDJ Players, DJ Mixers

### Percussion
- Bongos, Djembes, Marimbas

### Accessories & Devices
- Music Stands, Equipment Racks, Flight Cases
- Laptops, Audio Mixers

## Customization

### Adding New Items

To add new stage equipment items:

1. Add the item to the `items` array in `ItemCommandPalette.svelte`
2. Ensure the image exists in the appropriate `/static/img/` subdirectory
3. Include relevant keywords for searchability
4. Choose the appropriate category

Example:
```javascript
{
  id: "new-synthesizer",
  name: "Moog Synthesizer", 
  type: "keyboard",
  category: "Keyboards",
  image: "/img/keyboard/moog-synth.png",
  keywords: ["moog", "synthesizer", "analog", "bass", "lead"],
  description: "Analog synthesizer with classic Moog sound"
}
```

### Customizing Search Behavior

The component uses Bits UI's default search scoring, but you can customize it:

```svelte
<Command.Root
  filter={customFilterFunction}
  shouldFilter={true}
  loop={true}
>
```

### Styling Customization

The component uses the project's design system tokens:
- `bg-surface`, `border-border-primary` for theming
- `text-text-primary`, `text-text-secondary` for typography  
- `hover:bg-muted`, `data-[selected]:bg-muted` for states

## Performance Considerations

- **Lazy Loading**: Item images use `loading="lazy"` for performance
- **Efficient Filtering**: Bits UI handles search performance internally
- **Optimized Rendering**: Only visible items are rendered in the viewport
- **Keyboard Shortcuts**: Global shortcuts don't interfere with text inputs

## Accessibility

The Bits UI Command component provides built-in accessibility features:
- **Screen Reader Support**: Proper ARIA attributes and roles
- **Keyboard Navigation**: Full keyboard accessibility
- **Focus Management**: Automatic focus handling
- **Semantic Markup**: Proper heading hierarchy and list structure

## Future Enhancements

Potential improvements for the command palette:
- **Recent Items**: Show recently used items at the top
- **Favorites**: Allow users to star frequently used items  
- **Categories**: Add filtering by category
- **Grid View**: Optional grid layout for visual browsing
- **Custom Items**: Allow users to add custom equipment
- **Import/Export**: Share item libraries between users

## Bits UI Dependencies

This integration requires:
- `bits-ui` v2.9.1 or higher
- Svelte 5 with runes syntax
- Modern browser with CSS custom properties support

The Command component is fully typed and provides excellent TypeScript support out of the box.