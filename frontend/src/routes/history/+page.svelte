<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listHistory, retrySession } from '$lib/api.js';
	import { personaColor, personaInitial } from '$lib/personas.js';
	import ScoreBadge from '$lib/components/ScoreBadge.svelte';

	/** @type {any[]} */
	let sessions = [];
	/** @type {string | null} */
	let selectedId = null;
	/** @type {string | null} */
	let error = null;
	let retrying = false;

	$: selected = sessions.find((s) => s.id === selectedId) ?? sessions[0] ?? null;

	const dateFormatter = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });

	onMount(async () => {
		try {
			sessions = await listHistory();
			if (sessions.length) selectedId = sessions[0].id;
		} catch (e) {
			error = e.message;
		}
	});

	async function retry() {
		if (!selected) return;
		retrying = true;
		try {
			const session = await retrySession(selected.id);
			goto(`/interview/${session.id}`);
		} catch (e) {
			error = e.message;
			retrying = false;
		}
	}
</script>

<div class="mx-auto max-w-6xl px-6 py-10 sm:px-10">
	<div class="mb-6">
		<h1 class="font-display text-2xl font-bold text-teal-900">Historique des entretiens</h1>
		<p class="mt-1 text-sm text-[#6d8783]">
			{sessions.length} entretien{sessions.length > 1 ? 's' : ''} simule{sessions.length > 1 ? 's' : ''} — clique sur l'un d'eux pour revoir sa fiche.
		</p>
	</div>

	{#if error}
		<div class="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
	{/if}

	{#if sessions.length === 0 && !error}
		<div class="rounded-2xl border border-dashed border-[#b7d4cf] bg-white px-6 py-12 text-center text-sm text-[#6d8783]">
			Aucun entretien pour l'instant. <a href="/" class="font-semibold text-teal-600">Lance ton premier entretien</a>.
		</div>
	{:else}
		<div class="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
			<div class="flex flex-col gap-2.5">
				{#each sessions as s (s.id)}
					<button
						type="button"
						on:click={() => (selectedId = s.id)}
						class="flex items-center gap-3 rounded-xl border-[1.5px] bg-white p-3.5 text-left"
						style="border-color:{selected?.id === s.id ? '#0d9488' : '#dde9e7'}"
					>
						<div
							class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full font-display text-[13px] font-semibold text-white"
							style="background:{personaColor(s.persona)}"
						>
							{personaInitial(s.persona)}
						</div>
						<div class="min-w-0 flex-1">
							<div class="truncate text-sm font-semibold text-teal-900">{s.job_title}</div>
							<div class="mt-0.5 text-[12.5px] text-[#6d8783]">
								{s.company} · {dateFormatter.format(new Date(s.started_at))}
							</div>
						</div>
						<ScoreBadge score={s.score} />
					</button>
				{/each}
			</div>

			{#if selected}
				<div class="sticky top-5 h-fit rounded-2xl border border-[#dde9e7] bg-white p-6">
					<div class="mb-1 flex items-center justify-between">
						<div class="font-display text-[17px] font-bold text-teal-900">{selected.job_title}</div>
						<ScoreBadge score={selected.score} />
					</div>
					<div class="mb-4 text-[13px] text-[#6d8783]">
						{selected.company} · {dateFormatter.format(new Date(selected.started_at))}
					</div>

					<div class="mb-4 flex items-center gap-1.5 text-[12.5px] text-[#5b7d78]">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
							<path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" /><path d="M14 3v5h5" />
						</svg>
						{selected.cv_filename}
					</div>

					{#if selected.status === 'ended'}
						<p class="mb-5 text-[13px] text-[#5b7d78]">
							Fiche recapitulative disponible — consulte le detail complet pour les points forts et les axes de progression.
						</p>
					{:else}
						<p class="mb-5 text-[13px] text-[#5b7d78]">
							Cet entretien n'a pas ete termine — pas de fiche recapitulative pour l'instant.
						</p>
					{/if}

					<div class="flex gap-2.5">
						{#if selected.status === 'ended'}
							<a
								href="/summary/{selected.id}"
								class="flex-1 rounded-xl border border-[#cfe0dc] bg-white py-2.5 text-center text-[13.5px] font-semibold text-[#3f5c57]"
							>
								Fiche complete
							</a>
						{/if}
						<button
							type="button"
							on:click={retry}
							disabled={retrying}
							class="flex-1 rounded-xl bg-teal-900 py-2.5 text-[13.5px] font-semibold text-white disabled:opacity-50"
						>
							{retrying ? 'Preparation...' : 'Retenter'}
						</button>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
