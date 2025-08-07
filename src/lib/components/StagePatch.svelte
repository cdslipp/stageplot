<script lang="ts">
	import { Combobox, Tabs } from 'bits-ui';
	import { loadFinalAssets, filterItems, type ProcessedItem } from '$lib/utils/finalAssetsLoader';
	import { onMount } from 'svelte';

	type Item = {
		id: number;
		name: string;
		channel: string;
		musician: string;
		itemData: any;
		category?: string;
	};

	type Props = {
		items: Item[];
		onUpdateItem?: (itemId: number, property: string, value: string) => void;
		onReorderPatch?: (fromIndex: number, toIndex: number) => void;
		onSelectItem?: (item: Item, event: MouseEvent) => void;
		onAddItem?: (item: ProcessedItem, channel: number) => void;
		onRemoveItem?: (channel: number) => void;
	};

	let { items, onUpdateItem, onReorderPatch, onSelectItem, onAddItem, onRemoveItem }: Props = $props();

	// Channel mode options
	type ChannelMode = 8 | 16 | 24 | 32 | 48;
	const CHANNEL_OPTIONS: ChannelMode[] = [8, 16, 24, 32, 48];
	
	// Separate channel modes for inputs and outputs
	let inputChannelMode = $state<ChannelMode>(48);
	let outputChannelMode = $state<ChannelMode>(16);
	const NUM_COLUMNS = 4;
	
	// Dynamic calculations for inputs
	const TOTAL_INPUT_CHANNELS = $derived(inputChannelMode);
	const INPUT_ROWS_PER_COLUMN = $derived(Math.ceil(inputChannelMode / NUM_COLUMNS));
	
	// Dynamic calculations for outputs
	const TOTAL_OUTPUT_CHANNELS = $derived(outputChannelMode);
	const OUTPUT_ROWS_PER_COLUMN = $derived(Math.ceil(outputChannelMode / NUM_COLUMNS));

	// State for loaded items
	let allAvailableItems: ProcessedItem[] = $state([]);
	let loading = $state(true);
	
	// Track selected items per channel for inputs and outputs separately
	// Selected items per channel are now derived from the canonical `items` prop.
// This ensures perfect, reactive linkage with the canvas.
// Map channel → full canvas item (stagePlot item) for quick lookup
const canvasItemByChannel = $derived.by(() => {
	const map: Record<number, Item | null> = {};
	items.forEach((it) => {
		if (it.channel) {
			map[parseInt(it.channel as string)] = it as Item;
		}
	});
	return map;
});

// Map channel → ProcessedItem metadata (for combobox selection)
const selectedInputItemsByChannel = $derived.by(() => {
	const map: Record<number, ProcessedItem | null> = {};
	items.forEach((it) => {
		if (it.channel) {
			const ch = parseInt(it.channel as string);
			if (it.itemData) {
            // Merge live name (may have been edited) into the stored metadata so combobox shows latest
            map[ch] = { ...(it.itemData as ProcessedItem), name: it.name } as ProcessedItem;
        } else {
            // Fallback to basic object when itemData missing
            map[ch] = { id: String(it.id), name: it.name, category: it.category ?? 'Input', image: '', type: 'input', keywords: [] } as unknown as ProcessedItem;
        }
		}
	});
	return map;
});

// Keep combobox search boxes in sync with canvas
$effect(() => {
	// Depend on names so we update when they change, not just on length
	items.map(i => i.name).join('|');
	for (const ch of inputChannelNumbers) {
		const proc = selectedInputItemsByChannel[ch] as ProcessedItem | null;
		inputSearchValues[ch] = proc ? proc.name : '';
	}
});
	let selectedOutputItemsByChannel = $state<Record<number, ProcessedItem | null>>({});
	
	// Search values for each combobox (separate for inputs and outputs)
	let inputSearchValues = $state<Record<number, string>>({});
	let outputSearchValues = $state<Record<number, string>>({});
	
	// Create channel lists based on current modes
	const inputChannelNumbers = $derived.by(() => {
		return Array.from({ length: TOTAL_INPUT_CHANNELS }, (_, i) => i + 1);
	});
	
	const outputChannelNumbers = $derived.by(() => {
		return Array.from({ length: TOTAL_OUTPUT_CHANNELS }, (_, i) => i + 1);
	});

	// Load items on component mount
	onMount(async () => {
		try {
			loading = true;
			
			// Load all items from final_assets structure
			const loadedItems = await loadFinalAssets();
			
			// Filter items - for now, include inputs and accessories, exclude symbols/numerals
			allAvailableItems = filterItems(loadedItems, {
				includeInputs: true,
				includeAccessories: true,
				includeSymbols: false,
			});
			
			console.log('Loaded items for comboboxes:', allAvailableItems.length);
			
		} catch (err) {
			console.error('Error loading final assets:', err);
		} finally {
			loading = false;
		}
	});

	// Filter items for a specific combobox based on search
	function getFilteredItems(searchValue: string) {
		if (!searchValue) return allAvailableItems;
		
		const searchLower = searchValue.toLowerCase();
		return allAvailableItems.filter(item => 
			item.name.toLowerCase().includes(searchLower) ||
			item.keywords.some(kw => kw.toLowerCase().includes(searchLower))
		);
	}

	// Handle input item selection
	function handleInputItemSelect(channel: number, item: ProcessedItem | null) {
		if (item) {
			// Add or overwrite canvas for this channel
			onAddItem?.(item, channel);
		} else {
			// Clear channel on canvas
			onRemoveItem?.(channel);
		}
	}

	// Handle output item selection (placeholder - no action for now)
	function handleOutputItemSelect(channel: number, item: ProcessedItem | null) {
		selectedOutputItemsByChannel[channel] = item;
		// TODO: Add output handling logic later
	}



	// Split input channels into columns
	const inputColumns = $derived.by(() => {
		return Array.from({ length: NUM_COLUMNS }, (_, col) =>
			inputChannelNumbers.slice(col * INPUT_ROWS_PER_COLUMN, (col + 1) * INPUT_ROWS_PER_COLUMN)
		);
	});

	// Split output channels into columns
	const outputColumns = $derived.by(() => {
		return Array.from({ length: NUM_COLUMNS }, (_, col) =>
			outputChannelNumbers.slice(col * OUTPUT_ROWS_PER_COLUMN, (col + 1) * OUTPUT_ROWS_PER_COLUMN)
		);
	});
</script>

<div class="border border-border-primary bg-surface rounded-xl shadow-sm overflow-hidden">
	<Tabs.Root value="inputs" class="w-full">
		<!-- Tab Headers -->
		<div class="border-b border-border-primary bg-muted/30 px-4 pt-4">
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-xl font-semibold text-text-primary">Patch List</h2>
				<div class="text-sm text-text-secondary">
					{TOTAL_INPUT_CHANNELS} inputs • {TOTAL_OUTPUT_CHANNELS} outputs
				</div>
			</div>
			
			<Tabs.List class="flex gap-1">
				<Tabs.Trigger 
					value="inputs" 
					class="px-4 py-2 text-sm font-medium rounded-t-lg transition-colors data-[state=active]:bg-surface data-[state=active]:text-text-primary data-[state=inactive]:text-text-secondary hover:text-text-primary"
				>
					Inputs
				</Tabs.Trigger>
				<Tabs.Trigger 
					value="outputs" 
					class="px-4 py-2 text-sm font-medium rounded-t-lg transition-colors data-[state=active]:bg-surface data-[state=active]:text-text-primary data-[state=inactive]:text-text-secondary hover:text-text-primary"
				>
					Outputs
				</Tabs.Trigger>
				<Tabs.Trigger 
					value="settings" 
					class="px-4 py-2 text-sm font-medium rounded-t-lg transition-colors data-[state=active]:bg-surface data-[state=active]:text-text-primary data-[state=inactive]:text-text-secondary hover:text-text-primary"
				>
					Settings
				</Tabs.Trigger>
			</Tabs.List>
		</div>
		
		<!-- Tab Contents -->
		<div class="p-4">
			<!-- Inputs Tab -->
			<Tabs.Content value="inputs" class="mt-0">
				{#if loading}
					<div class="py-8 text-center text-text-secondary">
						<div class="flex flex-col items-center gap-2">
							<div class="animate-spin h-6 w-6 border-2 border-text-secondary border-t-transparent rounded-full"></div>
							<div>Loading items...</div>
						</div>
					</div>
				{:else}
					<!-- Excel-like 4-column grid -->
					<div class="grid grid-cols-4 gap-0 border border-border-primary">
			{#each inputColumns as col, colIndex}
				<div class="border-r border-border-primary last:border-r-0">
					{#each col as channelNum}
						<div class="border-b border-border-primary last:border-b-0 h-10 flex items-center">
							<!-- Channel number cell -->
							<div class="w-10 h-full flex items-center justify-center border-r border-border-primary text-xs font-semibold cursor-pointer transition-colors {selectedInputItemsByChannel[channelNum] ? 'bg-blue-600 text-white' : 'bg-muted/50 text-text-secondary'}" onclick={() => { const itm = canvasItemByChannel[channelNum]; itm && onSelectItem?.(itm, new MouseEvent('click')); }}>
								{channelNum}
							</div>
							
							<!-- Combobox cell -->
							<div class="flex-1 px-1">
								<Combobox.Root
                                       value={selectedInputItemsByChannel[channelNum]?.id ?? undefined}
                                       type="single"
                                       name="input-{channelNum}"
                                       inputValue={selectedInputItemsByChannel[channelNum]?.name ?? ''}
                                       onValueChange={(value) => {
                                           const selected = allAvailableItems.find(item => item.id === value);
                                           handleInputItemSelect(channelNum, selected || null);
                                       }}
                                   >
									<div class="relative">
										<Combobox.Input
                                            class="w-full h-8 px-2 text-xs bg-transparent border-0 outline-none placeholder:text-text-secondary/50 focus:ring-1 focus:ring-foreground/20 rounded"
                                            placeholder="Select item..."
                                            oninput={(e) => {
                                                inputSearchValues[channelNum] = (e.currentTarget as HTMLInputElement).value;
                                            }}
                                        />
										<Combobox.Trigger class="absolute right-1 top-1/2 -translate-y-1/2 w-4 h-4 opacity-50 hover:opacity-100">
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-full h-full">
												<path d="M6 9l6 6 6-6"/>
											</svg>
										</Combobox.Trigger>
									</div>
									
									<Combobox.Portal>
										<Combobox.Content
											class="z-50 max-h-60 w-[var(--bits-combobox-anchor-width)] min-w-[200px] overflow-hidden rounded-md border border-border-primary bg-surface shadow-lg"
											sideOffset={4}
										>
											<Combobox.Viewport class="p-1">
												{#each getFilteredItems(inputSearchValues[channelNum] || '') as item (item.id)}
													<Combobox.Item
														value={item.id}
														label={item.name}
														class="relative flex cursor-pointer select-none items-center rounded px-2 py-1.5 text-xs outline-none data-[highlighted]:bg-muted"
													>
														{#snippet children({ selected })}
															<span class="truncate">{item.name}</span>
															{#if selected}
																<svg class="ml-auto h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
																	<path d="M20 6L9 17l-5-5"/>
																</svg>
															{/if}
														{/snippet}
													</Combobox.Item>
												{:else}
													<div class="px-2 py-1.5 text-xs text-text-secondary">
														No items found
													</div>
												{/each}
											</Combobox.Viewport>
										</Combobox.Content>
									</Combobox.Portal>
								</Combobox.Root>
							</div>
						</div>
					{/each}
				</div>
			{/each}
					</div>
				{/if}
			</Tabs.Content>
			
			<!-- Outputs Tab -->
			<Tabs.Content value="outputs" class="mt-0">
				{#if loading}
					<div class="py-8 text-center text-text-secondary">
						<div class="flex flex-col items-center gap-2">
							<div class="animate-spin h-6 w-6 border-2 border-text-secondary border-t-transparent rounded-full"></div>
							<div>Loading items...</div>
						</div>
					</div>
				{:else}
					<!-- Excel-like 4-column grid for outputs -->
					<div class="grid grid-cols-4 gap-0 border border-border-primary">
			{#each outputColumns as col}
				<div class="border-r border-border-primary last:border-r-0">
					{#each col as channelNum}
						<div class="border-b border-border-primary last:border-b-0 h-10 flex items-center">
							<!-- Channel number cell -->
							<div class="w-10 h-full flex items-center justify-center border-r border-border-primary text-xs font-semibold cursor-pointer transition-colors {selectedInputItemsByChannel[channelNum] ? 'bg-blue-600 text-white' : 'bg-muted/50 text-text-secondary'}" onclick={() => { const itm = canvasItemByChannel[channelNum]; itm && onSelectItem?.(itm, new MouseEvent('click')); }}>
								{channelNum}
							</div>
							
							<!-- Combobox cell -->
							<div class="flex-1 px-1">
								<Combobox.Root
                                   value={selectedOutputItemsByChannel[channelNum]?.id ?? undefined}
                                   type="single"
                                   name="output-{channelNum}"
                                                                      inputValue={selectedOutputItemsByChannel[channelNum]?.name ?? ''}
                                   onValueChange={(value) => {
                                       const selected = allAvailableItems.find(item => item.id === value);
                                       handleOutputItemSelect(channelNum, selected || null);
                                   }}
								>
									<div class="relative">
										<Combobox.Input
                                            class="w-full h-8 px-2 text-xs bg-transparent border-0 outline-none placeholder:text-text-secondary/50 focus:ring-1 focus:ring-foreground/20 rounded"
                                            placeholder="Select item..."
                                            oninput={(e) => {
                                                outputSearchValues[channelNum] = (e.currentTarget as HTMLInputElement).value;
                                            }}
                                        />
										<Combobox.Trigger class="absolute right-1 top-1/2 -translate-y-1/2 w-4 h-4 opacity-50 hover:opacity-100">
											<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-full h-full">
												<path d="M6 9l6 6 6-6"/>
											</svg>
										</Combobox.Trigger>
									</div>
									
									<Combobox.Portal>
										<Combobox.Content
											class="z-50 max-h-60 w-[var(--bits-combobox-anchor-width)] min-w-[200px] overflow-hidden rounded-md border border-border-primary bg-surface shadow-lg"
											sideOffset={4}
										>
											<Combobox.Viewport class="p-1">
												{#each getFilteredItems(outputSearchValues[channelNum] || '') as item (item.id)}
													<Combobox.Item
														value={item.id}
														label={item.name}
														class="relative flex cursor-pointer select-none items-center rounded px-2 py-1.5 text-xs outline-none data-[highlighted]:bg-muted"
													>
														{#snippet children({ selected })}
															<span class="truncate">{item.name}</span>
															{#if selected}
																<svg class="ml-auto h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
																	<path d="M20 6L9 17l-5-5"/>
																</svg>
															{/if}
														{/snippet}
													</Combobox.Item>
												{:else}
													<div class="px-2 py-1.5 text-xs text-text-secondary">
														No items found
													</div>
												{/each}
											</Combobox.Viewport>
										</Combobox.Content>
									</Combobox.Portal>
								</Combobox.Root>
							</div>
						</div>
					{/each}
				</div>
			{/each}
					</div>
				{/if}
			</Tabs.Content>
			
			<!-- Settings Tab -->
			<Tabs.Content value="settings" class="mt-0">
				<div class="space-y-8">
					<!-- Input Channel Configuration -->
					<div>
						<h3 class="text-sm font-medium text-text-primary mb-3">Input Channels</h3>
						<div class="flex flex-wrap gap-2">
							{#each CHANNEL_OPTIONS as option}
								<button
									onclick={() => inputChannelMode = option}
									class="px-3 py-2 rounded-lg border text-sm transition-colors {inputChannelMode === option ? 'bg-blue-500 text-white border-blue-500' : 'border-border-primary text-text-secondary hover:border-border-primary hover:text-text-primary'}"
								>
									{option}
								</button>
							{/each}
						</div>
						<p class="text-xs text-text-secondary mt-2">
							{Math.ceil(inputChannelMode / NUM_COLUMNS)} rows × {NUM_COLUMNS} columns = {inputChannelMode} channels
						</p>
					</div>

					<!-- Output Channel Configuration -->
					<div>
						<h3 class="text-sm font-medium text-text-primary mb-3">Output Channels</h3>
						<div class="flex flex-wrap gap-2">
							{#each CHANNEL_OPTIONS as option}
								<button
									onclick={() => outputChannelMode = option}
									class="px-3 py-2 rounded-lg border text-sm transition-colors {outputChannelMode === option ? 'bg-blue-500 text-white border-blue-500' : 'border-border-primary text-text-secondary hover:border-border-primary hover:text-text-primary'}"
								>
									{option}
								</button>
							{/each}
						</div>
						<p class="text-xs text-text-secondary mt-2">
							{Math.ceil(outputChannelMode / NUM_COLUMNS)} rows × {NUM_COLUMNS} columns = {outputChannelMode} channels
						</p>
					</div>
				</div>
			</Tabs.Content>
		</div>
	</Tabs.Root>
</div>