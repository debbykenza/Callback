<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { getSession, getSummary, listHistory, listPersonas, retrySession } from '$lib/api.js';
	import { personaColor, personaInitial } from '$lib/personas.js';
	import ScoreBar from '$lib/components/ScoreBar.svelte';

	$: id = $page.params.id;

	/** @type {any} */
	let session = null;
	/** @type {any} */
	let summary = null;
	/** @type {any} */
	let historyItem = null;
	/** @type {{id: string, name: string, tag: string}[]} */
	let personas = [];
	/** @type {string | null} */
	let error = null;
	let tab = 'resume';
	let retrying = false;

	$: personaMeta = personas.find((p) => p.id === session?.persona);

	onMount(async () => {
		try {
			const [s, sum, history, p] = await Promise.all([getSession(id), getSummary(id), listHistory(), listPersonas()]);
			session = s;
			summary = sum;
			historyItem = history.find((h) => h.id === id) ?? null;
			personas = p;
		} catch (e) {
			error = e.message;
		}
	});

	async function retry() {
		retrying = true;
		try {
			const newSession = await retrySession(id);
			goto(`/interview/${newSession.id}`);
		} catch (e) {
			error = e.message;
			retrying = false;
		}
	}
</script>

<div class="mx-auto max-w-3xl px-6 py-10">
	{#if error}
		<div class="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
	{/if}

	{#if session && summary}
		<div class="mb-5 flex items-start gap-3.5">
			<a href="/history" class="mt-1 text-[#5b7d78]" aria-label="Retour a l'historique">
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
					<path d="M19 12H5M11 6l-6 6 6 6" />
				</svg>
			</a>
			<div>
				<h1 class="font-display text-2xl font-bold text-teal-900">Fiche recapitulative</h1>
				<div class="mt-1 text-[13.5px] text-[#6d8783]">
					{historyItem?.job_title ?? ''} · avec {personaMeta?.name ?? session.persona}
				</div>
			</div>
		</div>

		<div class="mb-6 flex gap-1 border-b border-[#dde9e7]">
			<button
				type="button"
				on:click={() => (tab = 'resume')}
				class="mr-6 border-b-2 px-1 py-3 text-sm font-semibold"
				style="border-color:{tab === 'resume' ? '#0d9488' : 'transparent'}; color:{tab === 'resume' ? '#0b3d3a' : '#6d8783'}"
			>
				Resume
			</button>
			<button
				type="button"
				on:click={() => (tab = 'transcript')}
				class="border-b-2 px-1 py-3 text-sm font-semibold"
				style="border-color:{tab === 'transcript' ? '#0d9488' : 'transparent'}; color:{tab === 'transcript' ? '#0b3d3a' : '#6d8783'}"
			>
				Transcript complet
			</button>
		</div>

		{#if tab === 'resume'}
			<div class="mb-5 rounded-2xl border border-[#dde9e7] bg-white p-6 text-sm leading-relaxed text-[#334f4b]">
				{summary.overall_comment}
			</div>

			<div class="mb-6 grid gap-5 md:grid-cols-2">
				<div class="rounded-2xl border border-[#dde9e7] bg-white p-5">
					<div class="mb-3.5 flex items-center gap-2">
						<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0d9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<circle cx="12" cy="12" r="9" /><path d="m8.5 12.5 2.5 2.5 4.5-5" />
						</svg>
						<span class="text-sm font-semibold text-teal-900">Points forts</span>
					</div>
					<div class="flex flex-col gap-3">
						{#each summary.strengths as s}
							<div class="text-[13.5px] leading-relaxed text-[#334f4b]">{s}</div>
						{/each}
					</div>
				</div>

				<div class="rounded-2xl border border-[#dde9e7] bg-white p-5">
					<div class="mb-3.5 flex items-center gap-2">
						<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#c2661f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M12 9v4" /><path d="M12 17h.01" /><path d="M10.3 3.9 1.9 18a2 2 0 0 0 1.7 3h16.8a2 2 0 0 0 1.7-3L14.7 3.9a2 2 0 0 0-3.4 0Z" />
						</svg>
						<span class="text-sm font-semibold text-[#8a4415]">A travailler</span>
					</div>
					<div class="flex flex-col gap-3">
						{#each summary.improvements as s}
							<div class="text-[13.5px] leading-relaxed text-[#334f4b]">{s}</div>
						{/each}
					</div>
				</div>
			</div>

			<div class="mb-7 rounded-2xl border border-[#dde9e7] bg-white p-6">
				<div class="mb-4 text-sm font-semibold text-teal-900">Evaluation par critere</div>
				<div class="flex flex-col gap-4">
					{#each summary.criteria as c}
						<ScoreBar label={c.label} value={c.value} />
					{/each}
				</div>
			</div>
		{:else}
			<div class="mb-7 flex flex-col gap-4 rounded-2xl border border-[#dde9e7] bg-white p-6">
				{#each session.messages as message}
					<div class="flex gap-2.5" class:flex-row-reverse={message.role === 'user'}>
						<div
							class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[11px] font-bold"
							style={message.role === 'assistant'
								? `background:${personaColor(session.persona)}; color:white`
								: 'background:#ccfbf1; color:#0b3d3a'}
						>
							{message.role === 'assistant' ? personaInitial(personaMeta?.name ?? session.persona) : 'K'}
						</div>
						<div class="max-w-[85%] text-[13.5px] leading-relaxed text-[#334f4b]">{message.content}</div>
					</div>
				{/each}
			</div>
		{/if}

		<div class="flex items-center justify-end gap-3 pt-1.5">
			<a
				href="/history"
				class="rounded-xl border border-[#cfe0dc] bg-white px-6 py-3 text-sm font-semibold text-[#3f5c57]"
			>
				Retour a l'historique
			</a>
			<button
				type="button"
				on:click={retry}
				disabled={retrying}
				class="flex items-center gap-2 rounded-xl bg-teal-900 px-6 py-3 text-sm font-semibold text-white disabled:opacity-50"
			>
				<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
					<path d="M4 4v5h5" /><path d="M20 20v-5h-5" /><path d="M5.5 9a7 7 0 0 1 12-3.5L20 8" /><path d="M18.5 15a7 7 0 0 1-12 3.5L4 16" />
				</svg>
				{retrying ? 'Preparation...' : "Retenter l'entretien"}
			</button>
		</div>
	{:else if !error}
		<div class="py-20 text-center text-sm text-[#6d8783]">Chargement de la fiche...</div>
	{/if}
</div>
