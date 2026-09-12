<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listPersonas, uploadCv, createOffer, createSession } from '$lib/api.js';
	import PersonaCard from '$lib/components/PersonaCard.svelte';

	/** @type {{id: string, name: string, tag: string}[]} */
	let personas = [];
	let selectedPersona = '';
	let offerText = '';
	/** @type {File | null} */
	let cvFile = null;
	let submitting = false;
	/** @type {string | null} */
	let error = null;

	onMount(async () => {
		try {
			personas = await listPersonas();
			if (personas.length) selectedPersona = personas[0].id;
		} catch (e) {
			error = "Impossible de contacter l'API (" + e.message + "). Verifie que le backend tourne.";
		}
	});

	/** @param {Event} e */
	function onFileChange(e) {
		const target = /** @type {HTMLInputElement} */ (e.target);
		cvFile = target.files?.[0] ?? null;
	}

	$: canSubmit = !!cvFile && offerText.trim().length > 20 && !!selectedPersona && !submitting;

	async function start() {
		if (!canSubmit || !cvFile) return;
		submitting = true;
		error = null;
		try {
			const cv = await uploadCv(cvFile);
			const offer = await createOffer(offerText);
			const session = await createSession(cv.id, offer.id, selectedPersona);
			goto(`/interview/${session.id}`);
		} catch (e) {
			error = e.message ?? "Une erreur s'est produite.";
			submitting = false;
		}
	}
</script>

<div class="mx-auto max-w-5xl px-6 py-10 sm:px-10">
	<div class="mb-8">
		<h1 class="font-display text-3xl font-bold tracking-tight text-teal-900">
			Prepare ton prochain entretien
		</h1>
		<p class="mt-2 text-[15px] text-[#55716d]">
			Colle l'offre, ajoute ton CV, choisis ton recruteur virtuel — l'entretien s'adapte a toi.
		</p>
	</div>

	{#if error}
		<div class="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
			{error}
		</div>
	{/if}

	<div class="mb-8 grid gap-6 md:grid-cols-2">
		<div class="flex flex-col gap-3 rounded-2xl border border-[#dde9e7] bg-white p-5">
			<div class="flex items-center gap-2">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0d9488" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
					<rect x="4" y="3" width="16" height="18" rx="1" /><path d="M9 8h1M14 8h1M9 12h1M14 12h1M9 16h1M14 16h1" />
				</svg>
				<span class="text-sm font-semibold text-teal-900">L'offre d'emploi</span>
			</div>
			<textarea
				bind:value={offerText}
				placeholder="Colle ici le contenu de l'offre : intitule, entreprise, stack demandee, missions..."
				class="min-h-[190px] w-full resize-y rounded-xl border border-[#e2ede9] bg-[#fafefe] p-3.5 text-sm leading-relaxed text-ink placeholder:text-[#93a5a2] focus:border-teal-600 focus:outline-none"
			></textarea>
		</div>

		<div class="flex flex-col gap-3 rounded-2xl border border-[#dde9e7] bg-white p-5">
			<div class="flex items-center gap-2">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0d9488" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
					<path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" /><path d="M14 3v5h5" />
				</svg>
				<span class="text-sm font-semibold text-teal-900">Ton CV</span>
			</div>

			{#if cvFile}
				<div class="flex flex-1 flex-col items-center justify-center gap-3.5 px-3.5 py-7">
					<div class="flex w-full max-w-xs items-center gap-2.5 rounded-xl border border-teal-100 bg-teal-50 px-3.5 py-2.5">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="shrink-0">
							<path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" /><path d="M14 3v5h5" />
						</svg>
						<span class="flex-1 truncate text-[13px] font-medium text-teal-900">{cvFile.name}</span>
						<button type="button" class="shrink-0 text-[#5b7d78]" on:click={() => (cvFile = null)} aria-label="Retirer le CV">
							<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M6 6l12 12M18 6 6 18" />
							</svg>
						</button>
					</div>
					<span class="text-[12.5px] text-[#6d8783]">CV pret a etre utilise pendant l'entretien</span>
				</div>
			{:else}
				<label class="flex flex-1 cursor-pointer flex-col items-center justify-center gap-2.5 rounded-xl border-[1.5px] border-dashed border-[#b7d4cf] bg-[#fafefe] px-3.5 py-7">
					<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#5b8a83" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
						<path d="M7 18a4.6 4.4 0 0 1-1.6-8.9 5.5 5.5 0 0 1 10.6-2.5A4.5 4.5 0 0 1 18 15.5" /><path d="M12 12v7" /><path d="m9 15 3-3 3 3" />
					</svg>
					<span class="text-[13.5px] font-medium text-[#3f5c57]">Glisse ton CV ici ou clique pour parcourir</span>
					<span class="text-xs text-[#8aa39f]">PDF — 5 Mo max</span>
					<input type="file" accept="application/pdf" class="hidden" on:change={onFileChange} />
				</label>
			{/if}
		</div>
	</div>

	<div class="mb-7">
		<div class="mb-1 text-sm font-semibold text-teal-900">Choisis ton recruteur virtuel</div>
		<p class="mb-3.5 text-[13px] text-[#6d8783]">La voix et le style d'entretien changent selon la persona choisie.</p>
		<div class="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
			{#each personas as persona (persona.id)}
				<PersonaCard {persona} selected={selectedPersona === persona.id} onSelect={(id) => (selectedPersona = id)} />
			{/each}
		</div>
	</div>

	<div class="flex items-center justify-between border-t border-[#e2ede9] pt-3">
		<div class="flex items-center gap-2 text-[13px] text-[#6d8783]">
			<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" />
			</svg>
			Durée estimee : 15–20 minutes
		</div>
		<button
			type="button"
			disabled={!canSubmit}
			on:click={start}
			class="flex items-center gap-2 rounded-xl bg-teal-900 px-6 py-3 text-[14.5px] font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
		>
			{submitting ? 'Preparation en cours...' : "Commencer l'entretien"}
			{#if !submitting}
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M5 12h14M13 6l6 6-6 6" />
				</svg>
			{/if}
		</button>
	</div>
</div>
