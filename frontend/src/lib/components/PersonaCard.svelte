<script>
	import { personaColor, personaInitial } from '$lib/personas.js';

	/** @type {{id: string, name: string, tag: string}} */
	export let persona;
	/** @type {boolean} */
	export let selected = false;
	/** @type {(id: string) => void} */
	export let onSelect;
</script>

<button
	type="button"
	on:click={() => onSelect(persona.id)}
	class="flex items-center gap-3 rounded-xl border-[1.5px] bg-white p-3.5 text-left transition-colors"
	style="border-color: {selected ? '#0d9488' : '#dde9e7'}"
>
	<div
		class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full font-display text-sm font-semibold text-white"
		style="background:{personaColor(persona.id)}"
	>
		{personaInitial(persona.name)}
	</div>
	<div class="min-w-0 flex-1">
		<div class="text-sm font-semibold text-teal-900">{persona.name}</div>
		<div class="mt-0.5 text-xs text-[#6d8783]">{persona.tag}</div>
	</div>
	{#if selected}
		<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0d9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shrink-0">
			<circle cx="12" cy="12" r="9" /><path d="m8.5 12.5 2.5 2.5 4.5-5" />
		</svg>
	{/if}
</button>
