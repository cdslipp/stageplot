<script lang="ts">
	import { STAGE_SIZES, formatDimensions } from '$lib/utils/scale';

	type StageDeckSize = '4x4' | '4x8' | '8x8';
	
	let {
		size = $bindable<StageDeckSize>('4x4'),
		x = $bindable<number>(0),
		y = $bindable<number>(0),
		selected = $bindable<boolean>(false),
		id = $bindable<string>(''),
		class: className = ''
	} = $props();

	const stageSize = $derived(STAGE_SIZES[size]);
	const dimensions = $derived(formatDimensions(stageSize.width, stageSize.height));
</script>

<!-- Stage deck as SVG -->
<svg
	class="stage-deck {className} {selected ? 'selected' : ''}"
	width={stageSize.width}
	height={stageSize.height}
	style="position: absolute; left: {x}px; top: {y}px;"
	data-id={id}
	role="img"
	aria-label="Stage deck {dimensions}"
>
	<!-- Main deck surface -->
	<rect
		x="0"
		y="0"
		width={stageSize.width}
		height={stageSize.height}
		fill="#D4AF37"
		stroke="#B8860B"
		stroke-width="2"
		rx="4"
		ry="4"
	/>
	
	<!-- Wood grain lines for texture -->
	{#each Array(Math.floor(stageSize.height / 8)) as _, i}
		<line
			x1="4"
			y1={8 + i * 8}
			x2={stageSize.width - 4}
			y2={8 + i * 8}
			stroke="#B8860B"
			stroke-width="0.5"
			opacity="0.3"
		/>
	{/each}
	
	<!-- Corner reinforcements -->
	{#each [
		[4, 4],
		[stageSize.width - 12, 4],
		[4, stageSize.height - 12],
		[stageSize.width - 12, stageSize.height - 12]
	] as [cornerX, cornerY]}
		<rect
			x={cornerX}
			y={cornerY}
			width="8"
			height="8"
			fill="#8B7355"
			rx="1"
		/>
	{/each}
	
	<!-- Size label (only show if deck is large enough) -->
	{#if stageSize.width > 60 && stageSize.height > 40}
		<text
			x={stageSize.width / 2}
			y={stageSize.height / 2 - 4}
			text-anchor="middle"
			font-family="Arial, sans-serif"
			font-size="10"
			font-weight="bold"
			fill="#8B4513"
			opacity="0.7"
		>
			STAGE
		</text>
		<text
			x={stageSize.width / 2}
			y={stageSize.height / 2 + 8}
			text-anchor="middle"
			font-family="Arial, sans-serif"
			font-size="8"
			fill="#8B4513"
			opacity="0.6"
		>
			{size.replace('x', ' × ')}
		</text>
	{/if}
</svg>

<style>
	.stage-deck {
		cursor: move;
		transition: opacity 0.2s ease;
	}
	
	.stage-deck:hover {
		opacity: 0.9;
	}
	
	.stage-deck.selected {
		filter: drop-shadow(0 0 4px #2563eb);
	}
	
	.stage-deck:hover rect:first-child {
		fill: #DAA520;
	}
</style>