<script lang="ts">
	import { Combobox } from "bits-ui";
	
	interface Props {
		musicians: Array<{ id: number; name: string; instrument: string }>;
		value?: string;
		onValueChange?: (value: string) => void;
		onAddMusician?: (name: string, instrument: string) => void;
	}
	
	let { musicians, value = "", onValueChange, onAddMusician }: Props = $props();
	
	let searchValue = $state("");
	let open = $state(false);
	
	// Filter musicians based on search
	const filteredMusicians = $derived(
		searchValue === ""
			? musicians
			: musicians.filter((musician) =>
					musician.name.toLowerCase().includes(searchValue.toLowerCase())
				)
	);
	
	// Check if search value matches any existing musician
	const exactMatch = $derived(
		musicians.find(m => m.name.toLowerCase() === searchValue.toLowerCase())
	);
	
	// Show "Add new musician" option when no exact match and search has value
	const showAddOption = $derived(
		searchValue.trim() !== "" && !exactMatch
	);
	
	function handleValueChange(newValue: string) {
		onValueChange?.(newValue);
	}
	
	function handleOpenChange(newOpen: boolean) {
		open = newOpen;
		if (!newOpen) {
			searchValue = "";
		}
	}
	
	function handleAddNew() {
		if (searchValue.trim() && onAddMusician) {
			// For now, we'll add with empty instrument - could be enhanced to ask for instrument
			onAddMusician(searchValue.trim(), "");
			onValueChange?.(searchValue.trim());
			searchValue = "";
			open = false;
		}
	}
	
	function handleInput(e: Event & { currentTarget: HTMLInputElement }) {
		searchValue = e.currentTarget.value;
	}
</script>

<Combobox.Root
	type="single"
	bind:value
	bind:open
	onValueChange={handleValueChange}
	onOpenChange={handleOpenChange}
>
	<div class="relative">
		<Combobox.Input
			oninput={handleInput}
			class="w-full px-2 py-1.5 text-sm border border-border-primary rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-surface text-text-primary"
			placeholder="Select or add musician"
		/>
		<Combobox.Trigger class="absolute right-2 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary">
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</Combobox.Trigger>
	</div>
	
	<Combobox.Portal>
		<Combobox.Content
			class="z-50 max-h-60 w-[var(--bits-combobox-anchor-width)] min-w-[var(--bits-combobox-anchor-width)] overflow-hidden rounded-lg border border-border-primary bg-surface shadow-lg"
			sideOffset={4}
		>
			<Combobox.Viewport class="p-1">
				{#each filteredMusicians as musician (musician.id)}
					<Combobox.Item
						class="relative flex cursor-pointer select-none items-center rounded-md px-2 py-1.5 text-sm outline-none data-[highlighted]:bg-muted text-text-primary hover:bg-muted"
						value={musician.name}
						label={musician.name}
					>
						{#snippet children({ selected })}
							<div class="flex-1">
								<div class="font-medium">{musician.name}</div>
								{#if musician.instrument}
									<div class="text-xs text-text-secondary">{musician.instrument}</div>
								{/if}
							</div>
							{#if selected}
								<svg class="ml-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
								</svg>
							{/if}
						{/snippet}
					</Combobox.Item>
				{/each}
				
				{#if showAddOption}
					<div class="border-t border-border-primary mt-1 pt-1">
						<button
							onclick={handleAddNew}
							class="relative flex w-full cursor-pointer select-none items-center rounded-md px-2 py-1.5 text-sm outline-none hover:bg-muted text-text-primary"
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Add "{searchValue}"
						</button>
					</div>
				{/if}
				
				{#if filteredMusicians.length === 0 && !showAddOption}
					<div class="px-2 py-1.5 text-sm text-text-secondary">
						No musicians found
					</div>
				{/if}
			</Combobox.Viewport>
		</Combobox.Content>
	</Combobox.Portal>
</Combobox.Root>