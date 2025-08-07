<script lang="ts">
    import { Command } from 'bits-ui';
    import { loadFinalAssets, filterItems, type ProcessedItem } from '$lib/utils/finalAssetsLoader';

    type Item = ProcessedItem;

    type Props = {
        open?: boolean;
        onselect?: (item: Item) => void;
        onclose?: () => void;
    };

    let { open = $bindable(false), onselect, onclose }: Props = $props();

    let allItems = $state<Item[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);

    // Load items when the component is initialized
    $effect(() => {
        async function load() {
            try {
                loading = true;
                error = null;
                const loadedItems = await loadFinalAssets();
                allItems = loadedItems;
            } catch (err) {
                console.error('Error loading final assets:', err);
                error = err instanceof Error ? err.message : 'Failed to load items';
            } finally {
                loading = false;
            }
        }
        load();
    });

    const items = $derived(filterItems(allItems, {
        includeInputs: true,
        includeAccessories: true,
        includeSymbols: false,
    }));

    const groupedItems = $derived.by(() => {
        const groups = items.reduce(
            (acc, item) => {
                if (!acc[item.category]) {
                    acc[item.category] = [];
                }
                acc[item.category].push(item);
                return acc;
            },
            {} as Record<string, Item[]>
        );

        return Object.entries(groups).map(([category, items]) => ({
            name: category,
            items
        }));
    });

    function customFilter(value: string, search: string, keywords?: string[]): number {
        if (!search.trim()) return 1;
        const searchLower = search.toLowerCase();
        const valueLower = value.toLowerCase();
        if (valueLower.includes(searchLower)) return 1;
        if (keywords) {
            for (const keyword of keywords) {
                if (keyword.toLowerCase().includes(searchLower)) return 1;
            }
        }
        return 0;
    }

    function handleSelect(item: Item) {
        onselect?.(item);
        open = false;
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            open = false;
            onclose?.();
        }
    }

    function handleBackdropClick() {
        open = false;
        onclose?.();
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
    <div class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" role="button" aria-label="Close dialog" onclick={handleBackdropClick}></div>
        <div class="relative mx-4 max-h-[80vh] w-[min(800px,95vw)]">
            <Command.Root
                class="flex flex-col overflow-hidden rounded-xl border border-border-primary bg-surface shadow-2xl"
                shouldFilter={true}
                filter={customFilter}
                loop={true}
                columns={6}
            >
                <div class="border-b border-border-primary px-4 py-3">
                    <Command.Input
                        class="w-full bg-transparent text-lg outline-none placeholder:text-text-secondary"
                        placeholder="Search for stage items..."
                        autofocus
                    />
                </div>

                <Command.List class="flex-1 overflow-hidden">
                    <Command.Viewport class="max-h-[60vh] overflow-y-auto p-2">
                        {#if loading}
                            <div class="py-8 text-center text-text-secondary">
                                <div class="flex flex-col items-center gap-2">
                                    <div class="animate-spin h-6 w-6 border-2 border-text-secondary border-t-transparent rounded-full"></div>
                                    <div>Loading items...</div>
                                </div>
                            </div>
                        {:else if error}
                            <div class="py-8 text-center text-text-secondary">
                                <div class="flex flex-col items-center gap-2">
                                    <div class="text-red-500">⚠</div>
                                    <div>Error loading items: {error}</div>
                                    <button 
                                        class="text-xs text-blue-500 hover:underline" 
                                        onclick={() => window.location.reload()}
                                    >
                                        Retry
                                    </button>
                                </div>
                            </div>
                        {:else}
                            <Command.Empty class="py-8 text-center text-text-secondary">
                                No items found. Try a different search term.
                            </Command.Empty>

                            {#each groupedItems as group (group.name)}
                                <Command.Group>
                                    <Command.GroupHeading
                                        class="px-2 py-2 text-xs font-semibold tracking-wider text-text-secondary uppercase"
                                    >
                                        {group.name}
                                    </Command.GroupHeading>
                                    <Command.GroupItems class="grid grid-cols-6 gap-2 px-2">
                                        {#each group.items as item (item.id)}
                                            <Command.Item
                                                value={`${item.name} ${item.id} ${item.keywords.join(' ')}`}
                                                class="flex aspect-square cursor-pointer flex-col items-center gap-2 rounded-lg px-2 py-3 transition-colors hover:bg-muted data-[selected]:bg-muted"
                                                onSelect={() => handleSelect(item)}
                                            >
                                                <div
                                                    class="flex flex-shrink-0 items-center justify-center"
                                                    style="min-height: 32px; min-width: 32px;"
                                                >
                                                    <img
                                                        src={item.image}
                                                        alt={item.name}
                                                        style="max-width: 60px; max-height: 40px;"
                                                        loading="lazy"
                                                        onerror={() => {}}
                                                    />
                                                </div>
                                                <div class="min-w-0 flex-1 text-center">
                                                    <div class="truncate text-xs font-medium text-text-primary">
                                                        {item.name}
                                                    </div>
                                                    {#if item.type === 'input'}
                                                        <div class="text-xs text-green-600 font-semibold">INPUT</div>
                                                    {/if}
                                                </div>
                                            </Command.Item>
                                        {/each}
                                    </Command.GroupItems>
                                </Command.Group>
                            {/each}
                        {/if}
                    </Command.Viewport>
                </Command.List>

                <div class="border-t border-border-primary bg-muted/30 px-4 py-2">
                    <div class="flex items-center justify-between text-xs text-text-secondary">
                        <div class="flex items-center gap-4">
                            <span>↑↓ Navigate</span>
                            <span>↵ Select</span>
                            <span>ESC Close</span>
                        </div>
                        <div>{items.length} items available</div>
                    </div>
                </div>
            </Command.Root>
        </div>
    </div>
{/if}