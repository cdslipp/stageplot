# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stage Plot Creator is a SvelteKit 2 web application for creating visual stage layout diagrams and input lists. Musicians and event organizers use it to plan stage setups with drag-and-drop equipment placement.

## Tech Stack

- **Framework**: SvelteKit 2.22.0 with Svelte 5 (using new runes syntax: `$state`, `$props`)
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS 4.0 (alpha) with @tailwindcss/vite plugin
- **UI Components**: Bits UI 2.9.1 (headless component primitives)
- **Dark Mode**: mode-watcher 1.1.0 for theme management
- **Build Tool**: Vite 7.0.4
- **Testing**: Vitest 3.2.3 (unit) and Playwright 1.49.1 (e2e)

## Essential Commands

```bash
# Development
npm run dev           # Start development server at localhost:5173
npm run dev -- --open # Start dev server and open browser

# Building & Preview
npm run build         # Build for production
npm run preview       # Preview production build at localhost:4173

# Code Quality
npm run lint          # Check formatting with Prettier and ESLint
npm run format        # Auto-format code with Prettier
npm run check         # Type checking with svelte-check

# Testing
npm run test          # Run all tests (unit + e2e)
npm run test:unit     # Run unit tests with Vitest (watch mode)
npm run test:unit -- --run  # Run unit tests once
npm run test:e2e      # Run e2e tests with Playwright
```

## Architecture

### Application Structure
- **Main Canvas**: 1100x850px drag-and-drop area in `src/routes/+page.svelte`
- **State Management**: Uses Svelte 5's reactive `$state` runes
- **Dark Mode**: Implemented with mode-watcher and CSS custom properties
- **Item System**: Draggable stage equipment items with editable properties (name, channel, musician)
- **Musician Management**: Advanced combobox for selecting/adding musicians with search and autocomplete

### Key Files
- `src/routes/+page.svelte`: Main application component with all core functionality
- `src/routes/+layout.svelte`: Layout with ModeWatcher for dark mode management
- `src/app.css`: Global Tailwind CSS imports with custom CSS properties for theming
- `src/lib/components/MusicianCombobox.svelte`: Advanced combobox component for musician selection
- `static/img/`: Extensive library of stage equipment images organized by category

### Testing Strategy
- **Unit Tests**: `*.svelte.spec.ts` files run in browser environment using Vitest
- **E2E Tests**: Located in `e2e/` directory, run with Playwright
- Tests are split into client (browser) and server (node) environments

### Image Assets
The `static/img/` directory contains 500+ categorized equipment images:
- `agt/`: Acoustic guitars
- `artist/`: Musician icons
- `drum/`: Drum kit components
- `egt/`: Electric guitars and amps
- `mic/`: Microphones
- `monitor/`: Stage monitors
- Additional categories for keyboards, DJ equipment, pedals, etc.

## Development Notes

### Svelte 5 Runes
This project uses Svelte 5's new runes syntax:
```javascript
let items = $state([]);  // Reactive state
let { item } = $props(); // Component props
```

### Tailwind CSS 4 & Theming
Using Tailwind CSS 4 alpha with the Vite plugin configuration. Dark mode is implemented using:
- CSS custom properties defined in `app.css` 
- `@custom-variant dark` for Tailwind v4 dark mode support
- `mode-watcher` library for seamless theme switching
- Custom color tokens (e.g., `bg-surface`, `text-text-primary`) for consistent theming

### UI Components
- **Bits UI**: Headless component primitives for accessibility and flexibility
- **MusicianCombobox**: Custom searchable combobox with autocomplete and "add new" functionality
- **Grid System**: Custom CSS grid pattern for canvas background

### Current Implementation Status
- ✅ Basic drag-and-drop functionality is complete
- ✅ Item management (add, edit, delete) is functional
- ✅ Dark/light mode toggle with proper theming
- ✅ Advanced musician selection with search and autocomplete
- ⚠️ Currently only "amp" type items are visually supported
- ⚠️ No backend/API integration yet - purely client-side

### File Conventions
- Component tests: `ComponentName.svelte.spec.ts`
- Use TypeScript for all new code
- Follow existing Prettier/ESLint configuration
- Components go in `src/lib/components/` and export via `src/lib/index.ts`
- Images go in appropriate `static/img/` subdirectories
- Use CSS custom properties for theming (defined in `src/app.css`)

## Component Architecture

### MusicianCombobox Component
Located at `src/lib/components/MusicianCombobox.svelte`, this component provides:
- Searchable dropdown with existing musicians
- Autocomplete filtering by musician name
- "Add new musician" functionality for non-existing entries
- Proper dark/light mode theming
- Keyboard navigation and accessibility via Bits UI

Usage:
```svelte
<MusicianCombobox
  {musicians}
  value={selectedMusician}
  onValueChange={(newValue) => selectedMusician = newValue}
  onAddMusician={(name, instrument) => addNewMusician(name, instrument)}
/>
```

## Development Best Practices

### Adding New Components
1. Create component in `src/lib/components/`
2. Export from `src/lib/index.ts`
3. Use CSS custom properties for theming
4. Follow existing TypeScript patterns
5. Test in both light and dark modes

### Styling Guidelines
- Use semantic color tokens (`text-text-primary`, `bg-surface`, etc.)
- Apply responsive design with Tailwind breakpoints
- Maintain accessibility standards with proper ARIA attributes
- Test keyboard navigation for interactive components