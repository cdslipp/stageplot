<script lang="ts">
	import { onMount } from 'svelte';
	import { toggleMode } from 'mode-watcher';
	import { MusicianCombobox, ItemCommandPalette, StagePatch, ImportExport } from '$lib';
	import Selecto from 'selecto';
	import itemsData from '$lib/items.json';
	import Inspector from '$lib/components/Inspector.svelte';
	import { Debounced, onClickOutside, PressedKeys, StateHistory } from 'runed';
	import StageDeck from '$lib/components/StageDeck.svelte';
	import { STAGE_SIZES } from '$lib/utils/scale';
	import { ContextMenu } from 'bits-ui';
	import db from '$lib/db';

	// Use reactive copy of db.data
let stagePlot = $state(structuredClone(db.data));

// Persist reactive state to lowdb
function write() {
    db.data = $state.snapshot(stagePlot);
    return db.write();
}

// --- Undo / Redo with StateHistory ---
const history = new StateHistory(
    () => $state.snapshot(stagePlot.items), // getter produces a plain snapshot of items array
    (itemsSnapshot) => {
        // setter restores items and persists
        // Replace the items array contents so that reactivity is retained
        stagePlot.items.splice(0, stagePlot.items.length, ...itemsSnapshot);
        write();
    }
);

	// Canvas state
	let canvasEl = $state(null); // To get canvas bounding box
	let canvasWidth = $state(stagePlot.canvas.width); // Default width
	let canvasHeight = $state(stagePlot.canvas.height); // Default height (1100x850 aspect ratio)
	let stagePlotContainer = $state(null); // Reference to the main stage plot container

	// Track pressed keys (Alt/Option for duplication)
	const keys = new PressedKeys();
	const isAltPressed = $derived(keys.has('Alt'));

	// --- Keyboard shortcuts using runed PressedKeys ---
	function nudgeSelected(dx: number, dy: number) {
		if (!selectedItems.length) return;
		selectedItems.forEach((el) => {
			const id = parseInt(el.dataset?.id || '0');
			const item = stagePlot.items.find((i) => i.id === id);
			if (!item) return;

			// Constrain within canvas bounds
			const newX = Math.max(0, Math.min(canvasWidth - item.position.width, item.position.x + dx));
			const newY = Math.max(0, Math.min(canvasHeight - item.position.height, item.position.y + dy));
			item.position.x = newX;
			item.position.y = newY;
		});
		write();
	}

	function deleteSelected() {
		if (!selectedItems.length) return;
		const selectedIds = selectedItems.map(el => parseInt(el.dataset?.id || '0'));
		stagePlot.items = stagePlot.items.filter(item => !selectedIds.includes(item.id));
		clearSelections();
		write();
	}

	// Stage Builder Modal state
	let showStageModal = $state(false);
	let modalDeckSize = $state<'4x4' | '4x8'>('4x4');
	let modalDecksWide = $state(3);
	let modalDecksDeep = $state(2);

	function openStageModal() {
		showStageModal = true;
	}

	function buildStage() {
		// Remove any existing stageDecks
		stagePlot.items = stagePlot.items.filter((i) => i.type !== 'stageDeck');

		const deckInfo = STAGE_SIZES[modalDeckSize];
		const totalWidth = deckInfo.width * modalDecksWide;
		const totalHeight = deckInfo.height * modalDecksDeep;
		const startX = Math.round((canvasWidth - totalWidth) / 2);
		const startY = Math.round((canvasHeight - totalHeight) / 2);

		for (let r = 0; r < modalDecksDeep; r++) {
			for (let c = 0; c < modalDecksWide; c++) {
				stagePlot.items.push({
					id: Date.now() + r * modalDecksWide + c,
					type: 'stageDeck',
					size: modalDeckSize,
					position: {
						width: deckInfo.width,
						height: deckInfo.height,
						x: startX + c * deckInfo.width,
						y: startY + r * deckInfo.height,
					},
					name: 'Stage Deck',
					channel: '',
					musician: ''
				});
			}
		}

		showStageModal = false;
		write();
	}

	function deleteStage() {
		stagePlot.items = stagePlot.items.filter((i) => i.type !== 'stageDeck');
		write();
	}

// Helper: prevent deletion when typing in input/textarea
	function handleDeleteHotkey() {
		const active = document.activeElement as HTMLElement | null;
		if (active) {
			const tag = active.tagName;
			if (tag === 'INPUT' || tag === 'TEXTAREA' || active.isContentEditable) {
				return; // Don't delete items when editing a text field
			}
		}
		deleteSelected();
	}

// Register key combos (auto cleans up on component destroy)
	keys.onKeys(['ArrowUp'], () => nudgeSelected(0, -1));
	keys.onKeys(['ArrowDown'], () => nudgeSelected(0, 1));
	keys.onKeys(['ArrowLeft'], () => nudgeSelected(-1, 0));
	keys.onKeys(['ArrowRight'], () => nudgeSelected(1, 0));
	keys.onKeys(['Delete'], handleDeleteHotkey);
	keys.onKeys(['Backspace'], handleDeleteHotkey);

	// --- Item Management State ---
	let selectedItems = $state<any[]>([]);
	let editingItem = $state(null); // Declare editingItem

	// For adding new items
	let isAddingItem = $state(false);

	// UI toggles
	let showZones = $state(true);
	// Stage builder mode
	let isBuildingStage = $state(false);

	// --- Stage Zones (2 rows x 3 columns): DSR DSC DSL / USR USC USL ---
	// From stage perspective (left/right switched from audience perspective)
	const ZONE_LABELS = ['DSL', 'DSC', 'DSR', 'USL', 'USC', 'USR']; // left-to-right within row
	function getZones(canvasWidth, canvasHeight) {
		const colWidth = canvasWidth / 3;
		const rowHeight = canvasHeight / 2;
		return [
			{ key: 'DSR', x: 0, y: rowHeight, w: colWidth, h: rowHeight }, // Switched from DSL to DSR
			{ key: 'DSC', x: colWidth, y: rowHeight, w: colWidth, h: rowHeight },
			{ key: 'DSL', x: colWidth * 2, y: rowHeight, w: colWidth, h: rowHeight }, // Switched from DSR to DSL
			{ key: 'USR', x: 0, y: 0, w: colWidth, h: rowHeight }, // Switched from USL to USR
			{ key: 'USC', x: colWidth, y: 0, w: colWidth, h: rowHeight },
			{ key: 'USL', x: colWidth * 2, y: 0, w: colWidth, h: rowHeight } // Switched from USR to USL
		];
	}

	function rectIntersectionArea(ax, ay, aw, ah, bx, by, bw, bh) {
		const xOverlap = Math.max(0, Math.min(ax + aw, bx + bw) - Math.max(ax, bx));
		const yOverlap = Math.max(0, Math.min(ay + ah, by + bh) - Math.max(ay, by));
		return xOverlap * yOverlap;
	}

	function getItemZone(item) {
		const zones = getZones(canvasWidth, canvasHeight);
		let maxArea = 0;
		let chosen = zones[0].key; // fallback first option if perfect split or no overlap
		for (const z of zones) {
			const area = rectIntersectionArea(
				item.position.x,
				item.position.y,
				item.position.width,
				item.position.height,
				z.x,
				z.y,
				z.w,
				z.h
			);
			if (area > maxArea) {
				maxArea = area;
				chosen = z.key;
			}
		}
		return chosen;
	}

	// Calculate position relative to downstage center edge (0,0)
	// X: 0 at downstage center edge, negative stage left, positive stage right
	// Y: 0 at downstage edge, positive upstage (no negative values)
	function getItemPosition(item) {
		if (!canvasWidth || !canvasHeight) return { x: 0, y: 0 };

		// X position relative to downstage center edge
		const relativeX = item.position.x + item.position.width / 2 - canvasWidth / 2;

		// Y position relative to downstage edge (no negative values)
		const relativeY = canvasHeight - (item.position.y + item.position.height / 2);

		return {
			x: Math.round(relativeX),
			y: Math.round(relativeY)
		};
	}

	// Update item position based on relative coordinates from downstage center edge
	function updateItemPosition(itemId, relativeX, relativeY) {
		const item = stagePlot.items.find((i) => i.id === itemId);
		if (item && canvasWidth && canvasHeight) {
			// Convert relative coordinates back to absolute canvas coordinates
			const absoluteX = relativeX + canvasWidth / 2 - item.position.width / 2;
			const absoluteY = canvasHeight - relativeY - item.position.height / 2;

			// Update item's position with boundary checks
			item.position.x = Math.max(0, Math.min(absoluteX, canvasWidth - item.position.width));
			item.position.y = Math.max(0, Math.min(absoluteY, canvasHeight - item.position.height));
			write();
		}
	}


	// Reactive effect to update zones when items move or canvas size changes
	$effect(() => {
		// This effect will run whenever items array, canvasWidth, or canvasHeight change
		if (stagePlot.items.length > 0 && canvasWidth > 0 && canvasHeight > 0) {
			// Force reactivity by accessing properties that might change
			stagePlot.items.forEach((item) => {
				// Just access the properties to make them reactive
				item.position.x;
				item.position.y;
				item.position.width;
				item.position.height;
			});
		}
	});

	let placingItem = $state(null); // The object being placed
	let showHelp = $state(false);

	// For musicians
	let newMusician = $state({ name: '', instrument: '' });

	let selecto; // Store reference to selecto instance
	let justSelected = false; // Flag to ignore the click immediately following a Selecto selection

	// Function to clear all selections - moved outside onMount so it's accessible globally
	function clearSelections() {
		if (selecto && selectedItems.length > 0) {
			// Remove visual indicators
			selectedItems.forEach((el) => {
				el.classList.remove('!ring-2', '!ring-blue-500');
			});
			// Clear the selection
			selectedItems = [];
			selecto.setSelectedTargets([]);
		}
	}

	onMount(() => {
		selecto = new Selecto({
			container: canvasEl,
			selectableTargets: ['.selectable-item'],
			selectByClick: true,
			selectFromInside: false, // Don't start selection from inside items
			toggleContinueSelect: 'shift',
			// Prevent selection when dragging starts on an item
			dragCondition: (e) => {
				// Check if the drag starts on a selectable item or its children
				const target = e.inputEvent.target;
				const item = target.closest('.selectable-item');
				// Only allow Selecto drag if not starting on an item
				return !item;
			}
		});

		selecto.on('select', (e) => {
							// Update selectedItems array with the DOM elements
				selectedItems = e.selected;
				// Prevent the immediate canvas click from clearing this fresh selection
				if (e.selected.length) justSelected = true;
				// Apply visual selected class
				e.added.forEach((el) => {
					el.classList.add('!ring-2', '!ring-blue-500');
				});
				e.removed.forEach((el) => {
					el.classList.remove('!ring-2', '!ring-blue-500');
				});
		});

		// Observe canvas size changes
		if (canvasEl) {
			const resizeObserver = new ResizeObserver((entries) => {
				for (let entry of entries) {
					const { width, height } = entry.contentRect;
					canvasWidth = width;
					canvasHeight = height;
					stagePlot.canvas.width = width;
					stagePlot.canvas.height = height;
					write();
				}
			});

			resizeObserver.observe(canvasEl);

			// Set initial size
			const rect = canvasEl.getBoundingClientRect();
			canvasWidth = rect.width || 1100; // Default to 1100 if 0
			canvasHeight = rect.height || 850; // Default to 850 if 0

			return () => {
				resizeObserver.disconnect();
			};
		}

		// Setup click outside handler to deselect items
		// Using canvasEl directly for more specific targeting
		onClickOutside(
			() => canvasEl,
			(event) => {
				// Check if the click is outside critical UI elements
				const target = event.target as HTMLElement;
				const isInInspector = target.closest('.inspector-panel');
				const isInCommandPalette = target.closest('[data-command-palette]');
				const isInItem = target.closest('.selectable-item');
				const isInCanvas = target === canvasEl || canvasEl?.contains(target);

				// Only clear selections if clicking on empty canvas area or completely outside
									// onClickOutside only triggers when the click is OUTSIDE canvasEl
					// We still want to preserve selection when interacting with the inspector or command palette
					if (!isInInspector && !isInCommandPalette) {
						clearSelections();
					}
			}
		);
	});

	// --- Functions for Adding Items ---
	function openAddMenu() {
		isAddingItem = true;
	}

	// Unified logic to prepare an item for placement on the canvas
	async function preparePlacingItem(item, channel = null) {
		// Get the natural dimensions of the image
		const img = new Image();
		img.src = item.image;
		await new Promise((resolve) => {
			img.onload = resolve;
			img.onerror = () => resolve(); // Continue even if image fails
		});

		// Create a representation of the item to be placed.
					placingItem = {
				type: item.type ?? item.item_type ?? 'input',
			itemData: item, // full item data
			width: img.naturalWidth || 80,
			height: img.naturalHeight || 60,
			x: -1000,
			y: -1000,
			channel // may be null if coming from command palette
		};
	}

	async function handleItemSelect(item) {
		isAddingItem = false;
		await preparePlacingItem(item);
	}

	function handleCanvasMouseMove(event) {
		if (placingItem) {
			const rect = canvasEl.getBoundingClientRect();
			// Position the preview item under the cursor
			placingItem.x = event.clientX - rect.left - placingItem.width / 2;
			placingItem.y = event.clientY - rect.top - placingItem.height / 2;
		}
	}

		function handleCanvasClick(event) {
				// Ignore this click if it immediately follows a Selecto selection drag
				if (justSelected) {
					justSelected = false;
					return;
				}
				if (placingItem) {
			const rect = canvasEl.getBoundingClientRect();
			const x = event.clientX - rect.left - placingItem.width / 2;
			const y = event.clientY - rect.top - placingItem.height / 2;

			// Add the new item to the main items array
			const newItem = {
				id: Date.now(),
				type: placingItem.type,
				itemData: placingItem.itemData, // Store the full item data from command palette
				currentVariant: 'default', // Track which variant is showing
				position: {
					width: placingItem.width, // Natural image width
					height: placingItem.height, // Natural image height
					x: Math.max(0, Math.min(x, canvasWidth - placingItem.width)),
					y: Math.max(0, Math.min(y, canvasHeight - placingItem.height)),
				},
				name: placingItem.itemData?.name || '',
				channel: '',
				musician: ''
			};

			            {
				// Determine appropriate channel
				let ch = placingItem.channel;
				if (ch == null && placingItem.type === 'input') {
					ch = getNextAvailableChannel();
				}
				newItem.channel = ch != null ? String(ch) : '';
			}
            stagePlot.items.push(newItem);

            // If this item is a drum kit with default inputs, create input items automatically
            const defaultInputs = placingItem.itemData?.default_inputs;
            if (defaultInputs && Array.isArray(defaultInputs)) {
                defaultInputs.forEach((inputDef, idx) => {
                    stagePlot.items.push({
                        id: Date.now() + idx + 1,
                        type: 'input',
                        itemData: {
                            ...inputDef,
                            item_type: 'input',
                            name: inputDef.name,
                            category: 'Input',
                            path: '',
                        },
                        name: inputDef.name,
                        channel: String(inputDef.ch || ''),
                        musician: inputDef.source || '',
                        currentVariant: 'default',
                        position: { width: 0, height: 0, x: 0, y: 0 }
                    });
                });
            }

			placingItem = null; // Done placing
			write();
		} else {
			// If not placing an item, check if we clicked on empty canvas to deselect
			const clickedItem = event.target.closest('.selectable-item');
			if (!clickedItem) {
				clearSelections();
			}
		}
	}

	function cancelPlacing(event) {
		if (event.key === 'Escape') {
			placingItem = null;
		}
	}

	function handleGlobalKeydown(event) {
		// Open command palette with Cmd/Ctrl + K
		if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
			event.preventDefault();
			openAddMenu();
		}
		// Undo / Redo shortcuts
		if ((event.metaKey || event.ctrlKey) && event.key === 'z' && !event.shiftKey) {
			event.preventDefault();
			history.undo();
			return;
		}
		if ((event.metaKey || event.ctrlKey) && ((event.key === 'z' && event.shiftKey) || event.key === 'y')) {
			event.preventDefault();
			history.redo();
			return;
		}

		// Handle escape for canceling placement and clearing selections
		if (event.key === 'Escape') {
			placingItem = null;
			clearSelections();
		}
	}

	function deleteItem(id) {
		const index = stagePlot.items.findIndex((item) => item.id === id);
		if (index !== -1) {
			stagePlot.items.splice(index, 1);
			write();
		}
	}

	/**
	 * Duplicate an existing item (used by context menu and Alt-drag)
	 */
	function duplicateItem(sourceItem, overrides = {}) {
		if (!sourceItem) return;
		// Create a shallow copy; spread unwraps proxy getters into plain values
		const baseCopy = { ...sourceItem };
		const newItem = {
			...baseCopy,
			...overrides,
			id: Date.now()
		};
		// If position not overridden, offset slightly so it’s visible
		if (overrides.x === undefined) {
			newItem.position.x = Math.min(sourceItem.position.x + 20, canvasWidth - sourceItem.position.width);
		}
		if (overrides.y === undefined) {
			newItem.position.y = Math.min(sourceItem.position.y + 20, canvasHeight - sourceItem.position.height);
		}
		stagePlot.items.push(newItem);
		write();
	}

	// --- Functions for Editing Items ---
	function openItemEditor(item, event) {
		// Prevent dragging when clicking to edit
		event.stopPropagation();

							// Find the DOM element for this item
					const itemEl = document.querySelector(`[data-id="${item.id}"]`);
					if (itemEl) {
						// Deselect anything that was previously selected
						if (selectedItems.length) {
							selectedItems.forEach((el) => el.classList.remove('!ring-2', '!ring-blue-500'));
						}

						// Select only this item
						selectedItems = [itemEl];

						// Keep Selecto's internal state in sync so box-drag works next time
						selecto?.setSelectedTargets([itemEl]);

						// Apply visual selected class
						itemEl.classList.add('!ring-2', '!ring-blue-500');
					}
	}

	// --- Musician Management ---
	function addMusician() {
		if (newMusician.name.trim() !== '') {
			stagePlot.musicians.push({
				id: Date.now(),
				name: newMusician.name.trim(),
				instrument: newMusician.instrument.trim()
			});
			newMusician.name = '';
			newMusician.instrument = '';
			write();
		}
	}

	function deleteMusician(id) {
		const index = stagePlot.musicians.findIndex((m) => m.id === id);
		if (index !== -1) {
			stagePlot.musicians.splice(index, 1);
			write();
		}
	}

	// --- Functions for Dragging Existing Items (using HTML5 DnD API) ---

	function handleDragStart(event, item) {
		// Hide the item being placed preview
		if (placingItem) placingItem = null;

		// Set data to transfer
		event.dataTransfer.setData(
			'application/json',
			JSON.stringify({
				id: item.id,
				offsetX: event.offsetX, // a property of the mouse event
				offsetY: event.offsetY
			})
		);
		event.dataTransfer.effectAllowed = 'move';

		// Optional: reduce opacity of the original item
		event.currentTarget.style.opacity = '0.5';
	}

	function handleDragOver(event) {
		event.preventDefault(); // Necessary to allow drop
	}

	function handleDrop(event) {
		event.preventDefault();
		const data = JSON.parse(event.dataTransfer.getData('application/json'));

		const item = stagePlot.items.find((i) => i.id === data.id);

		if (item) {
			const rect = canvasEl.getBoundingClientRect();

			// Calculate new position based on drop location and initial offset
			const x = event.clientX - rect.left - data.offsetX;
			const y = event.clientY - rect.top - data.offsetY;

			// If Alt/Option is pressed, duplicate instead of move
			const targetX = Math.max(0, Math.min(x, canvasWidth - item.position.width));
			const targetY = Math.max(0, Math.min(y, canvasHeight - item.position.height));

			// Alt-drag duplication disabled; always move item
			item.position.x = targetX;
			item.position.y = targetY;
			write();
		}
	}

	function handleDragEnd(event) {
		// Restore opacity
		event.currentTarget.style.opacity = '1';
	}

	// --- Functions for Rotating Items ---
	function getItemVariants(item) {
		// Get variants from the item's stored data
		if (!item.itemData) return null;

		// The itemData from command palette has direct variants property
		if (item.itemData.variants) {
			return item.itemData.variants;
		}

		// Fallback to looking in the original JSON
		const jsonItem = itemsData.find((i) => i.name === item.itemData.name);
		return jsonItem?.variants || null;
	}

	function getVariantKeys(item) {
		const variants = getItemVariants(item);
		if (!variants) return ['default'];
		return Object.keys(variants);
	}

	function rotateItemLeft(item) {
		const variants = getItemVariants(item);
		if (!variants) return;

		const variantKeys = Object.keys(variants);
		const currentIndex = variantKeys.indexOf(item.currentVariant || 'default');
		const newIndex = (currentIndex - 1 + variantKeys.length) % variantKeys.length;
		item.currentVariant = variantKeys[newIndex];

		// Update the image source
		const newImagePath = variants[item.currentVariant];

		// Load new image to get dimensions
		const img = new Image();
		img.src = buildImagePath(item, newImagePath);
		img.onload = () => {
			item.position.width = img.naturalWidth;
			item.position.height = img.naturalHeight;
			write();
		};

		// Update in main state
		updateItemProperty(item.id, 'currentVariant', item.currentVariant);
	}

	function rotateItemRight(item) {
		const variants = getItemVariants(item);
		if (!variants) return;

		const variantKeys = Object.keys(variants);
		const currentIndex = variantKeys.indexOf(item.currentVariant || 'default');
		const newIndex = (currentIndex + 1) % variantKeys.length;
		item.currentVariant = variantKeys[newIndex];

		// Update the image source
		const newImagePath = variants[item.currentVariant];

		// Load new image to get dimensions
		const img = new Image();
		img.src = buildImagePath(item, newImagePath);
		img.onload = () => {
			item.position.width = img.naturalWidth;
			item.position.height = img.naturalHeight;
			write();
		};

		// Update in main state
		updateItemProperty(item.id, 'currentVariant', item.currentVariant);
	}

	function getCurrentImageSrc(item) {
		const variants = getItemVariants(item);
		if (!variants) return item.itemData?.image || '/img/egt/FenderAmp.png';

		const variant = item.currentVariant || 'default';
		const imagePath = variants[variant] || variants.default || Object.values(variants)[0];

		return buildImagePath(item, imagePath);
	}

	function buildImagePath(item, imagePath) {
		// If item has a path property, it's from final_assets structure
		if (item.itemData?.path) {
			// For final_assets items, build path from the item's directory path
			return `/final_assets/${item.itemData.path}/${imagePath}`;
		}
		
		// For old structure items, check if path already starts with /
		return imagePath.startsWith('/') ? imagePath : '/' + imagePath;
	}

	// --- Functions for Stage Patch ---
	function handlePatchItemUpdate(itemId: number, property: string, value: string) {
		const item = stagePlot.items.find((i) => i.id === itemId);
		if (item) {
			item[property] = value;
			write();
		}
	}

	function updateItemProperty(itemId: number, property: string, value: string) {
		const item = stagePlot.items.find((i) => i.id === itemId);
		if (item) {
			item[property] = value;
			write();
		}
	}

	function handlePatchReorder(fromIndex: number, toIndex: number) {
		// TODO: implement drag-reorder for patch list if desired
		console.log(`Reorder patch from ${fromIndex} to ${toIndex}`);
	}

	function getNextAvailableChannel() {
		const used = new Set(stagePlot.items.filter(i => i.channel).map(i => parseInt(i.channel)));
		let ch = 1;
		while (used.has(ch)) ch++;
		return ch;
	}

	// Add/Replace an input from StagePatch combobox
	function handlePatchAddItem(item: any, channel: number) {
		// Remove any existing staged item on that channel; we'll replace after placement
		stagePlot.items = stagePlot.items.filter(i => i.channel !== String(channel));

        // Use the same interactive placement flow used by the Command-palette
        // but preset the desired channel so it is auto-assigned after click.
        preparePlacingItem(item, channel);
	}

	function handlePatchRemoveItem(channel: number) {
		stagePlot.items = stagePlot.items.filter(i => i.channel !== String(channel));
		write();
	}
</script>

<svelte:window onkeydown={handleGlobalKeydown} />

<div class="flex h-[100dvh] flex-col gap-6 py-6 overflow-y-hidden">
	<!-- Title + Actions - spans full width -->
	<div class="mb-4 flex items-center justify-between gap-4">
		<input
			bind:value={stagePlot.plot_name}
			oninput={() => write()}
			class="w-full border-b-2 border-dashed border-border-secondary bg-transparent px-2 py-1 text-4xl font-bold text-text-primary transition-all placeholder:font-normal placeholder:text-text-tertiary hover:border-border-primary focus:border-solid focus:border-blue-500 focus:outline-none"
			placeholder="Band Name"
		/>
		<div class="flex shrink-0 items-center gap-2">
			<div class="hidden text-sm text-text-secondary sm:block">
				Last Modified: {new Date(stagePlot.revision_date).toLocaleDateString()}
			</div>
			<ImportExport
				bind:stagePlot
				on:importComplete={() => {
					// Clear selections and reset UI state after import
					clearSelections();
					placingItem = null;
					editingItem = null;
				}}
			/>
			<button
				onclick={() => (showHelp = !showHelp)}
				class="flex h-9 w-9 items-center justify-center rounded-full text-text-secondary transition hover:bg-surface-hover hover:text-text-primary"
				title="Help"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-5 w-5"
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<path
						fill-rule="evenodd"
						d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>
			<button
				onclick={toggleMode}
				class="rounded-lg border border-border-primary px-3 py-2 text-sm text-text-primary hover:bg-surface-hover"
				title="Toggle dark mode"
			>
				Toggle Theme
			</button>
			<button
				onclick={() => (showZones = !showZones)}
				class="rounded-lg border border-border-primary px-3 py-2 text-sm text-text-primary hover:bg-surface-hover"
				title="Show/Hide zone guidelines"
			>
				{showZones ? 'Hide Zones' : 'Show Zones'}
			</button>


			<button
				onclick={openAddMenu}
				class="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white transition hover:bg-blue-700"
				title="Add Item (⌘K)"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-4 w-4"
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<path
						fill-rule="evenodd"
						d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
						clip-rule="evenodd"
					/>
				</svg>
				Add Item
				<span class="rounded bg-blue-500 px-1.5 py-0.5 text-xs text-blue-100">⌘K</span>
			</button>
		</div>
	</div>

	<!-- Main content area with canvas and sidebar -->
	<div class="flex flex-col gap-6 lg:flex-row lg:items-start">
		<!-- Main Content -->
		<div class="flex-1" bind:this={stagePlotContainer}>
			{#if showHelp}
				<div class="mb-4 rounded-xl border border-border-primary bg-surface p-4 shadow-sm">
					<h3 class="mb-2 font-semibold text-text-primary">How to use</h3>
					<ul class="space-y-1 text-sm text-text-secondary">
						<li>• Click Add Item to add an item</li>
						<li>• Click on canvas to place the item</li>
						<li>• Drag items to reposition them</li>
						<li>• Click × to delete an item</li>
						<li>• Click on an item to edit its properties</li>
						<li>• Press 'Escape' to cancel placing</li>
					</ul>
				</div>
			{/if}

			<!-- Canvas Card -->
			<div class="border border-border-primary bg-surface p-4 shadow-sm">
				<div
					bind:this={canvasEl}
					class="items-container relative mx-auto w-full bg-white dark:bg-gray-800"
					style="aspect-ratio: 11/8.5; max-width: 1100px; cursor: {placingItem ? 'copy' : 'default'}"
					onmousemove={handleCanvasMouseMove}
					onclick={handleCanvasClick}
					ondragover={handleDragOver}
					ondrop={handleDrop}
				>
					<div
						class="bg-grid-pattern pointer-events-none absolute inset-0 bg-[length:20px_20px] opacity-20 dark:opacity-10"
					></div>

					<!-- Zone guidelines -->
					{#if showZones}
						{#key canvasWidth + ':' + canvasHeight}
							{#each getZones(canvasWidth, canvasHeight) as z}
								<div
									class="pointer-events-none absolute"
									style="left:{z.x}px; top:{z.y}px; width:{z.w}px; height:{z.h}px; border: 1px dashed rgba(0,0,0,0.08);"
								></div>
							{/each}
							{#each getZones(canvasWidth, canvasHeight) as z}
								<div
									class="absolute text-[10px] tracking-wide uppercase"
									style="left:{z.x + z.w / 2 - 12}px; top:{z.y +
										4}px; color: rgba(0,0,0,0.25); mix-blend-mode: multiply;"
								>
									{z.key}
								</div>
							{/each}
						{/key}
					{/if}

					{#each stagePlot.items as item (item.id)}
					<ContextMenu.Root>
						<ContextMenu.Trigger>
						<div
							class="group selectable-item absolute transition-all cursor-move {editingItem?.id === item.id ? 'ring-2 ring-blue-500' : ''}"
							class:selected={selectedItems.includes(item)}
							data-id={item.id}
							style="left: {item.position.x}px; top: {item.position.y}px; width: {item.position.width}px; height: {item.position.height}px;"
							draggable="true"
							ondragstart={(e) => handleDragStart(e, item)}
							ondragend={handleDragEnd}
							onclick={(e) => openItemEditor(item, e)}
						>
							{#if item.type === 'stageDeck'}
										<StageDeck size={item.size} x={0} y={0} class="w-full h-full" />
									{:else}
										<img src={getCurrentImageSrc(item)} alt={item.itemData?.name || item.name || 'Stage Item'} style="width: {item.position.width}px; height: {item.position.height}px;" />
									{/if}

							<!-- Rotate buttons - only show when selected, positioned below item -->
							{#if selectedItems.some((el) => el.dataset?.id === String(item.id))}
								{#if getVariantKeys(item).length > 1}
									<div
										class="absolute -bottom-8 left-1/2 z-20 flex -translate-x-1/2 transform gap-1"
									>

										<button
											onclick={(e) => {
												e.stopPropagation();
												rotateItemRight(item);
											}}
											class="flex h-6 w-6 items-center justify-center rounded-full bg-blue-500 text-sm text-white shadow-md transition-colors hover:bg-blue-600"
											title="Rotate Right"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												class="h-4 w-4"
												viewBox="0 0 20 20"
												fill="currentColor"
											>
												<path
													fill-rule="evenodd"
													d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
													clip-rule="evenodd"
												/>
											</svg>
										</button>
									</div>
								{/if}
							{/if}

							<button
								onclick={(e) => {
									e.stopPropagation();
									deleteItem(item.id);
								}}
								class="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100"
							>
								&times;
							</button>
						</div>
					</ContextMenu.Trigger>
					<ContextMenu.Portal>
						<ContextMenu.Content class="z-50 w-[200px] rounded-xl border border-gray-300 bg-white px-1 py-1.5 shadow-lg dark:border-gray-600 dark:bg-gray-800">
							<ContextMenu.Item onSelect={(e) => openItemEditor(item, e)} class="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
								Edit
							</ContextMenu.Item>
							<ContextMenu.Item onSelect={() => duplicateItem(item)} class="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
								Duplicate
							</ContextMenu.Item>
							<ContextMenu.Separator class="bg-muted -mx-1 my-1 block h-px" />
							<ContextMenu.Item onSelect={() => deleteItem(item.id)} class="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-red-50 dark:hover:bg-red-600/30">
								Delete
							</ContextMenu.Item>
						</ContextMenu.Content>
					</ContextMenu.Portal>
					</ContextMenu.Root>
					{/each}

					{#if placingItem}
						<div
							class="pointer-events-none absolute opacity-60"
							style="left: {placingItem.x}px; top: {placingItem.y}px; width: {placingItem.width}px; height: {placingItem.height}px;"
						>
							<img
								src={placingItem.itemData?.image || '/img/egt/FenderAmp.png'}
								alt={placingItem.itemData?.name || 'Item Preview'}
								style="width: {placingItem.width}px; height: {placingItem.height}px;"
							/>
						</div>
					{/if}
				</div>
			</div>

			<div class="mt-2 flex justify-between text-xs text-text-tertiary">
				<div class="flex items-center gap-3">Items: {stagePlot.items.length} | Musicians: {stagePlot.musicians.length}
					{#if isAltPressed}
						<span class="text-blue-600 font-semibold animate-bounce">(Duplicate)</span>
					{/if}
				</div>
				<div>
					{#if placingItem}Click on canvas to place item. Press 'Escape' to cancel.{/if}
				</div>
			</div>

			<!-- Stage Patch Component -->
			<div class="mt-6">
				<StagePatch
						items={stagePlot.items}
						onUpdateItem={handlePatchItemUpdate}
						onReorderPatch={handlePatchReorder}
						onSelectItem={openItemEditor}
						onAddItem={handlePatchAddItem}
						onRemoveItem={handlePatchRemoveItem}
					/>
			</div>
		</div>
		<!-- Right Sidebar (Inspector and Musicians) -->
		<div class="flex w-full flex-col gap-6 lg:w-80">
			<!-- Inspector Panel -->
			<div
				class="inspector-panel h-fit rounded-xl border border-border-primary bg-surface p-4 shadow-sm"
			>
				<Inspector
						onOpenStageModal={openStageModal}
						bind:selectedItems
						bind:items={stagePlot.items}
						bind:musicians={stagePlot.musicians}
						bind:title={stagePlot.plot_name}
						bind:lastModified={stagePlot.revision_date}
					onUpdateItem={updateItemProperty}
					onAddMusician={(name, instrument) => {
							newMusician.name = name;
							newMusician.instrument = instrument;
							addMusician();
						}}
						{getItemZone}
						{getItemPosition}
						{updateItemPosition}
				/>
			</div>

			<!-- Musicians Panel -->
			<div class="h-fit rounded-xl border border-border-primary bg-surface p-4 shadow-sm">
				<h2 class="mb-4 text-xl font-semibold text-text-primary">Musicians</h2>

				<!-- Add Musician Form -->
				<div class="mb-5 border-b border-border-primary pb-4">
					<div class="space-y-3">
						<input
							type="text"
							bind:value={newMusician.name}
							class="w-full rounded-lg border border-border-primary bg-surface px-3 py-2 text-sm text-text-primary focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
							placeholder="Musician name"
						/>
						<button
							onclick={addMusician}
							class="w-full rounded-lg bg-green-600 px-3 py-2 text-sm text-white transition hover:bg-green-700"
						>
							Add Musician
						</button>
					</div>
				</div>

				<!-- Musicians List -->
				<div class="space-y-2 pr-1">
					{#if stagePlot.musicians.length === 0}
						<p class="py-4 text-center text-sm text-text-secondary">No musicians added yet</p>
					{:else}
						{#each stagePlot.musicians as musician (musician.id)}
							<div class="flex items-center justify-between rounded-lg bg-muted p-2">
								<div class="min-w-0">
									<div class="truncate text-sm font-medium text-text-primary">{musician.name}</div>
								</div>
								<button
									onclick={() => deleteMusician(musician.id)}
									class="text-red-500 hover:text-red-700"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 20 20"
										fill="currentColor"
									>
										<path
											fill-rule="evenodd"
											d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
											clip-rule="evenodd"
										/>
									</svg>
								</button>
							</div>
						{/each}
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

{#if showStageModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center">
		<div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onclick={() => (showStageModal = false)}></div>
		<div class="relative w-[min(400px,90vw)] rounded-xl bg-surface p-6 shadow-lg">
			<h2 class="mb-4 text-lg font-semibold">Build Stage</h2>

			<div class="space-y-4">
				<label class="block text-sm">Deck size
					<select bind:value={modalDeckSize} class="mt-1 w-full rounded border p-2">
						<option value="4x4">4′ × 4′</option>
						<option value="4x8">4′ × 8′</option>
					</select>
				</label>
				<label class="block text-sm">Width (number of decks)
					<input type="number" min="1" bind:value={modalDecksWide} class="mt-1 w-full rounded border p-2" />
				</label>
				<label class="block text-sm">Depth (number of decks)
					<input type="number" min="1" bind:value={modalDecksDeep} class="mt-1 w-full rounded border p-2" />
				</label>
			</div>

			<div class="mt-6 flex justify-end gap-2">
				<button class="px-3 py-2" onclick={() => (showStageModal = false)}>Cancel</button>
				<button class="rounded bg-blue-600 px-3 py-2 text-white" onclick={buildStage}>Build</button>
			</div>
		</div>
	</div>
{/if}

<!-- Footer -->
<footer class="mt-4 rounded-xl border border-border-primary bg-surface p-4 shadow-sm">
	<div class="flex flex-col items-center justify-between gap-3 text-sm sm:flex-row">
		<div class="text-text-secondary">
			Stage Plot Creator — plan your stage layout and input list.
		</div>
		<div class="flex items-center gap-4 text-text-tertiary">
			<a href="javascript:void(0)" class="hover:text-text-primary" aria-label="Twitter / X">X</a>
			<a href="javascript:void(0)" class="hover:text-text-primary" aria-label="GitHub">GitHub</a>
			<a href="javascript:void(0)" class="hover:text-text-primary" aria-label="Instagram"
				>Instagram</a
			>
		</div>
		<div>
			<a
				href="javascript:void(0)"
				class="inline-flex items-center rounded-lg border border-blue-600 px-3 py-1.5 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30"
				>Donate</a
			>
		</div>
	</div>
</footer>

<!-- Command Palette for Adding Items -->
<div data-command-palette>
	<ItemCommandPalette
		bind:open={isAddingItem}
		onselect={handleItemSelect}
		onclose={() => (isAddingItem = false)}
	/>
</div>

<style>
	/* Visual feedback when dragging */
	.selectable-item:active {
		opacity: 0.8;
	}

	/* Hover state for items - subtle opacity change */
	.selectable-item:hover {
		opacity: 0.95;
	}
</style>