<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { ModeWatcher } from "mode-watcher";

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<ModeWatcher />
<div class="min-h-screen bg-bg-secondary text-text-primary">
  <div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-[1600px]">
    {@render children?.()}
  </div>
</div>