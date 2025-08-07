# Stage Plot Creator Documentation

Welcome to the Stage Plot Creator documentation! This tool helps musicians and sound engineers create visual stage layouts with precise item positioning and input list management.

## Documentation Index

### Core Features
- **[Import/Export System](./import-export.md)** - Save and share stage plots using standardized JSON format
- **[Canvas Architecture](./canvas-architecture.md)** - Standardized canvas and stage layout system
- **[Scale System](./scale-system.md)** - Real-world measurements and SVG stage elements
- **[Bits UI Integration](./bits-ui-integration.md)** - Component library integration for consistent UI

### Development & Strategy
- **[Custom Items Strategy](./custom-items-strategy.md)** - Future roadmap for user-generated content and business model

## Quick Start

1. **Create a Stage Plot**
   - Enter your band name in the title field
   - Click "Add Item" or press `⌘K` to open the item palette
   - Select items and click on the canvas to place them
   - Drag items to reposition them

2. **Manage Items**
   - Click items to select them
   - Use the Inspector panel to edit properties
   - Right-click for context menu options (duplicate, delete)
   - Assign musicians and channels

3. **Save Your Work**
   - Click "File" → "Export Plot" to download a JSON file
   - Use "Import Plot" to load previously saved plots
   - Files are named automatically with date stamps

## Key Concepts

### Stage Coordinate System
The app uses a professional stage coordinate system:
- **Downstage**: Front of stage (closest to audience)
- **Upstage**: Back of stage (away from audience)  
- **Stage Left/Right**: From performer's perspective
- **Zones**: 6-zone grid system (DSL, DSC, DSR, USL, USC, USR)

### Item Types
Items on the stage plot are broadly categorized to help organize and filter them:
- **Musical Instruments**: Guitars, basses, keyboards, drums, etc.
- **Audio Gear**: Amplifiers, monitors, microphones, DI boxes, etc.
- **Staging Elements**: Risers, screens, lighting fixtures, etc.

Each item will have a `category` field (e.g., 'guitars', 'amps', 'drums') for more granular grouping.

### File Format
Stage plots are saved as JSON files following the Stage Plot 1.0.0 specification, which includes:
- Item positions (absolute and relative coordinates)
- Musician assignments
- Canvas dimensions
- Metadata and revision tracking

## Features

### Current Features
- ✅ Drag-and-drop item placement
- ✅ Multi-select with Selecto
- ✅ Zone-based positioning
- ✅ Musician management
- ✅ Import/export functionality
- ✅ Item variants and customization
- ✅ Context menus and keyboard shortcuts
- ✅ Responsive design

### Planned Features
- 🔄 Custom item support
- 🔄 Input list generation
- 🔄 PDF export
- 🔄 Collaboration features
- 🔄 Template library
- 🔄 Cloud storage integration

## Technical Architecture

### Built With
- **Svelte 5** - Modern reactive framework with runes
- **SvelteKit** - Full-stack framework
- **Bits UI** - Accessible component library
- **Tailwind CSS** - Utility-first styling
- **TypeScript** - Type safety
- **Selecto** - Multi-selection library

### Key Components
- `+page.svelte` - Main stage plot canvas and state management
- `ImportExport.svelte` - File operations
- `Inspector.svelte` - Item property editor
- `ItemCommandPalette.svelte` - Item selection interface
- `StagePatch.svelte` - Input list management

## Contributing

### Development Setup
```bash
cd stage-plot-creator
npm install
npm run dev
```

### Code Standards
- Use Svelte 5 runes (`$state`, `$derived`, `$bindable`)
- Follow TypeScript best practices
- Use semantic HTML and ARIA labels
- Maintain responsive design principles

### File Organization
```
src/
├── lib/
│   ├── components/     # Reusable Svelte components
│   ├── assets/         # Static assets
│   └── index.ts        # Component exports
├── routes/             # SvelteKit pages
└── app.html           # HTML template
```

## Support

For issues, feature requests, or questions:
- Check the [troubleshooting section](./import-export.md#troubleshooting) in import/export docs
- Review the [custom items strategy](./custom-items-strategy.md) for future features
- File issues on the project repository

## License

This project is part of the InputList ecosystem for professional audio workflows.