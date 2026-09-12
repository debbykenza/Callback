<script>
	import { onMount, onDestroy, tick } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import { getSession, sendAnswer, endSession, listPersonas, API_BASE } from '$lib/api.js';
	import { personaColor, personaInitial, personaHairStyle } from '$lib/personas.js';
	import { VoiceInterview, wsUrlFor } from '$lib/voice.js';
	import PersonaFace from '$lib/components/PersonaFace.svelte';

	$: id = $page.params.id;

	/** @type {any} */
	let session = null;
	/** @type {{id: string, name: string, tag: string}[]} */
	let personas = [];
	let draft = '';
	let sending = false;
	let ending = false;
	/** @type {string | null} */
	let error = null;
	/** @type {HTMLDivElement} */
	let scrollEl;

	// --- Plein ecran ---
	/** @type {HTMLDivElement} */
	let containerEl;
	let isFullscreen = false;

	function onFullscreenChange() {
		const doc = /** @type {any} */ (document);
		const fsEl = document.fullscreenElement || doc.webkitFullscreenElement;
		isFullscreen = fsEl === containerEl;
	}

	async function toggleFullscreen() {
		try {
			if (!isFullscreen) {
				const el = /** @type {any} */ (containerEl);
				if (el.requestFullscreen) await el.requestFullscreen();
				else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
			} else {
				const doc = /** @type {any} */ (document);
				if (document.exitFullscreen) await document.exitFullscreen();
				else if (doc.webkitExitFullscreen) doc.webkitExitFullscreen();
			}
		} catch {
			error = "Le plein ecran n'est pas disponible sur ce navigateur.";
		}
	}

	// --- Mode vocal (V2, Gemini Live) ---
	let voiceMode = false;
	/** @type {'connecting' | 'ready' | 'error'} */
	let voiceStatus = 'connecting';
	/** @type {VoiceInterview | null} */
	let voice = null;

	const voiceStatusLabel = {
		connecting: 'Connexion en cours...',
		ready: "A l'ecoute — parle normalement",
		error: 'Erreur'
	};

	/** @type {HTMLVideoElement} */
	let selfVideoEl;
	let cameraReady = false;
	let cameraNote = '';
	let assistantLevel = 0;
	let selfLevel = 0;
	/** @type {number | null} */
	let levelLoopId = null;

	function levelLoop() {
		if (!voice) return;
		// Lissage leger (moyenne mobile) pour eviter que la bouche/le halo ne
		// tremblotent trop entre deux mesures brutes du niveau audio.
		assistantLevel = assistantLevel * 0.55 + voice.getOutputLevel() * 0.45;
		selfLevel = selfLevel * 0.55 + voice.getInputLevel() * 0.45;
		levelLoopId = requestAnimationFrame(levelLoop);
	}

	function stopLevelLoop() {
		if (levelLoopId !== null) cancelAnimationFrame(levelLoopId);
		levelLoopId = null;
		assistantLevel = 0;
		selfLevel = 0;
	}

	$: personaMeta = personas.find((p) => p.id === session?.persona);
	$: isOver = session?.status !== 'active';

	async function scrollToBottom() {
		await tick();
		if (scrollEl) scrollEl.scrollTop = scrollEl.scrollHeight;
	}

	onMount(async () => {
		document.addEventListener('fullscreenchange', onFullscreenChange);
		document.addEventListener('webkitfullscreenchange', onFullscreenChange);
		try {
			[session, personas] = await Promise.all([getSession(id), listPersonas()]);
			await scrollToBottom();
		} catch (e) {
			error = e.message;
		}
	});

	async function send() {
		if (!draft.trim() || sending || isOver) return;
		sending = true;
		error = null;
		const content = draft;
		draft = '';
		try {
			session = await sendAnswer(id, content);
			await scrollToBottom();
		} catch (e) {
			error = e.message;
			draft = content;
		} finally {
			sending = false;
		}
	}

	async function finish() {
		ending = true;
		try {
			if (voiceMode) await stopVoice();
			if (isFullscreen) await toggleFullscreen();
			await endSession(id);
			goto(`/summary/${id}`);
		} catch (e) {
			error = e.message;
			ending = false;
		}
	}

	/** @param {KeyboardEvent} e */
	function onKeydown(e) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			send();
		}
	}

	async function startVoice() {
		if (isOver || voiceMode) return;
		error = null;
		cameraReady = false;
		cameraNote = '';
		voiceMode = true;
		voiceStatus = 'connecting';
		voice = new VoiceInterview(
			wsUrlFor(API_BASE, id),
			{
				onStatus: (state) => {
					if (state === 'ready') voiceStatus = 'ready';
				},
				onTranscript: (t) => {
					session = { ...session, messages: [...session.messages, { role: t.role, content: t.text }] };
					scrollToBottom();
				},
				onError: (message) => {
					error = message;
					voiceStatus = 'error';
				},
				onClose: () => {
					voiceMode = false;
					stopLevelLoop();
				},
				onVideoUnavailable: () => {
					cameraNote = "Camera non disponible — l'entretien continue en audio seul.";
				}
			},
			{ video: true }
		);
		try {
			await voice.start();
			await tick();
			if (selfVideoEl) selfVideoEl.srcObject = voice.mediaStream;
			cameraReady = voice.videoAvailable;
			levelLoopId = requestAnimationFrame(levelLoop);
		} catch (e) {
			error = e.message ?? "Impossible d'acceder au micro.";
			voiceStatus = 'error';
			voiceMode = false;
			voice = null;
		}
	}

	async function stopVoice() {
		stopLevelLoop();
		if (selfVideoEl) selfVideoEl.srcObject = null;
		voice?.stop();
		voice = null;
		voiceMode = false;
		cameraReady = false;
		try {
			session = await getSession(id);
			await scrollToBottom();
		} catch (e) {
			error = e.message;
		}
	}

	onDestroy(() => {
		// onDestroy s'execute aussi cote serveur (SSR) contrairement a onMount —
		// `document` n'existe pas dans cet environnement, d'ou la garde `browser`.
		if (browser) {
			document.removeEventListener('fullscreenchange', onFullscreenChange);
			document.removeEventListener('webkitfullscreenchange', onFullscreenChange);
			if (document.fullscreenElement === containerEl) document.exitFullscreen?.().catch(() => {});
		}
		stopLevelLoop();
		voice?.stop();
	});
</script>

<div
	bind:this={containerEl}
	class="mx-auto flex flex-col bg-[#f5f9f8] px-4 py-6 sm:px-6"
	class:h-screen={isFullscreen}
	class:h-[calc(100vh-73px)]={!isFullscreen}
	class:max-w-3xl={!isFullscreen}
	class:max-w-5xl={isFullscreen}
>
	{#if error}
		<div class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
	{/if}

	{#if session}
		<div class="mb-4 flex items-center justify-between rounded-2xl border border-[#dde9e7] bg-white px-5 py-3.5">
			<div class="flex items-center gap-3">
				<div
					class="flex h-9 w-9 items-center justify-center rounded-full font-display text-sm font-semibold text-white"
					style="background:{personaColor(session.persona)}"
				>
					{personaInitial(personaMeta?.name ?? session.persona)}
				</div>
				<div>
					<div class="text-sm font-semibold text-teal-900">{personaMeta?.name ?? session.persona}</div>
					<div class="text-xs text-[#6d8783]">{personaMeta?.tag ?? ''}</div>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<button
					type="button"
					on:click={toggleFullscreen}
					class="flex h-[38px] w-[38px] shrink-0 items-center justify-center rounded-lg bg-[#e6f4f2] text-teal-900"
					aria-label={isFullscreen ? "Quitter le plein ecran" : "Passer en plein ecran"}
					title={isFullscreen ? "Quitter le plein ecran" : "Passer en plein ecran"}
				>
					{#if isFullscreen}
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
							<path d="M9 3v3a2 2 0 0 1-2 2H4M21 8h-3a2 2 0 0 1-2-2V3M3 16h3a2 2 0 0 1 2 2v3M16 21v-3a2 2 0 0 1 2-2h3" />
						</svg>
					{:else}
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
							<path d="M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M8 21H5a2 2 0 0 1-2-2v-3M16 21h3a2 2 0 0 0 2-2v-3" />
						</svg>
					{/if}
				</button>
				<button
					type="button"
					on:click={voiceMode ? stopVoice : startVoice}
					disabled={isOver || ending}
					class="flex items-center gap-1.5 rounded-lg px-4 py-2 text-[13.5px] font-semibold disabled:opacity-50"
					class:bg-teal-900={voiceMode}
					class:text-white={voiceMode}
					class:bg-[#e6f4f2]={!voiceMode}
					class:text-teal-900={!voiceMode}
				>
					{voiceMode ? '⏹ Raccrocher' : '🎙️ Mode vocal'}
				</button>
				<button
					type="button"
					on:click={finish}
					disabled={ending}
					class="rounded-lg bg-[#fee2c7] px-4 py-2 text-[13.5px] font-semibold text-[#8a4415] disabled:opacity-50"
				>
					{ending ? 'Generation de la fiche...' : "Terminer l'entretien"}
				</button>
			</div>
		</div>

		{#if voiceMode}
			<div class="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
				<!-- Tuile persona : visage anime (bouche + clignements + reaction quand tu parles) -->
				<div class="relative flex flex-col items-center justify-center gap-3 overflow-hidden rounded-2xl border border-teal-100 bg-teal-50 px-5 py-8">
					<div class="relative flex h-32 w-32 items-center justify-center">
						<span
							class="absolute inset-0 rounded-full bg-teal-400 transition-transform duration-100 ease-out"
							style="transform: scale({1 + assistantLevel * 0.35}); opacity: {voiceStatus === 'ready' ? 0.25 : 0}"
						></span>
						<div class="relative h-28 w-28">
							<PersonaFace
								color={personaColor(session.persona)}
								hairStyle={personaHairStyle(session.persona)}
								mouthLevel={assistantLevel}
								listening={selfLevel}
								active={voiceStatus === 'ready'}
							/>
						</div>
					</div>
					<div class="text-center">
						<div class="text-sm font-semibold text-teal-900">{personaMeta?.name ?? session.persona}</div>
						<div class="text-xs text-[#6d8783]">{voiceStatusLabel[voiceStatus]}</div>
					</div>
				</div>

				<!-- Tuile "toi" : ta propre camera, comme un retour video de toi-meme -->
				<div
					class="relative flex aspect-[4/3] items-center justify-center overflow-hidden rounded-2xl border-2 bg-[#0b1f1c] sm:aspect-auto"
					style="border-color: {cameraReady ? `rgba(13,148,136,${0.25 + selfLevel * 0.6})` : '#dde9e7'}"
				>
					<!-- svelte-ignore a11y-media-has-caption -->
					<video
						bind:this={selfVideoEl}
						autoplay
						playsinline
						muted
						class="h-full w-full object-cover"
						style="transform: scaleX(-1); visibility: {cameraReady ? 'visible' : 'hidden'}"
					></video>
					{#if !cameraReady}
						<div class="absolute inset-0 flex items-center justify-center px-4 text-center text-xs text-white/70">
							{cameraNote || 'Connexion a la camera...'}
						</div>
					{/if}
					<div class="absolute bottom-2 left-2 rounded-md bg-black/40 px-2 py-1 text-[11px] font-medium text-white">Toi</div>
				</div>
			</div>
		{/if}

		<div bind:this={scrollEl} class="flex-1 space-y-4 overflow-y-auto rounded-2xl border border-[#dde9e7] bg-white p-5">
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
					<div
						class="max-w-[80%] rounded-2xl px-4 py-2.5 text-[13.5px] leading-relaxed"
						class:bg-[#f0fdfa]={message.role === 'assistant'}
						class:bg-teal-900={message.role === 'user'}
						class:text-white={message.role === 'user'}
						class:text-[#12201e]={message.role === 'assistant'}
					>
						{message.content}
					</div>
				</div>
			{/each}

			{#if isOver}
				<div class="rounded-xl border border-teal-100 bg-teal-50 px-4 py-3 text-center text-[13.5px] text-teal-900">
					L'entretien est termine — clique sur « Terminer l'entretien » pour voir ta fiche recapitulative.
				</div>
			{/if}
		</div>

		<div class="mt-4 flex items-end gap-3">
			<textarea
				bind:value={draft}
				on:keydown={onKeydown}
				disabled={sending || isOver || voiceMode}
				rows="2"
				placeholder={voiceMode
					? "Mode vocal actif — parle a l'oral, ou clique sur « Raccrocher » pour repasser a l'ecrit"
					: isOver
						? 'Entretien termine'
						: 'Ecris ta reponse... (Entree pour envoyer, Maj+Entree pour un saut de ligne)'}
				class="flex-1 resize-none rounded-xl border border-[#e2ede9] bg-white p-3 text-sm focus:border-teal-600 focus:outline-none disabled:bg-[#f5f9f8]"
			></textarea>
			<button
				type="button"
				on:click={send}
				disabled={sending || isOver || voiceMode || !draft.trim()}
				class="flex h-[46px] shrink-0 items-center gap-2 rounded-xl bg-teal-900 px-5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
			>
				Envoyer
			</button>
		</div>
	{:else if !error}
		<div class="flex flex-1 items-center justify-center text-sm text-[#6d8783]">Chargement de l'entretien...</div>
	{/if}
</div>
