<script>
	import { onMount, onDestroy } from 'svelte';

	/** Couleur de fond de la tete (voir personas.js). */
	export let color = '#0d9488';
	/** 'bob' | 'short' | 'part' | 'spiky' — voir personaHairStyle() dans personas.js. */
	export let hairStyle = 'bob';
	/** Niveau audio de la voix de l'IA (0-1) : fait bouger la bouche en temps reel. */
	export let mouthLevel = 0;
	/** Niveau du micro de l'utilisateur (0-1) : declenche une petite reaction "a l'ecoute". */
	export let listening = 0;
	/** Anime le clignement des yeux + le leger balancement idle quand true (connexion active). */
	export let active = false;

	let blinking = false;
	/** @type {ReturnType<typeof setTimeout>} */
	let blinkTimer;

	function scheduleBlink() {
		const delay = 2200 + Math.random() * 2800;
		blinkTimer = setTimeout(() => {
			blinking = true;
			setTimeout(() => {
				blinking = false;
				scheduleBlink();
			}, 130);
		}, delay);
	}

	onMount(() => scheduleBlink());
	onDestroy(() => clearTimeout(blinkTimer));

	$: clampedMouth = Math.max(0, Math.min(1, mouthLevel));
	$: mouthRy = 1.6 + clampedMouth * 11;
	$: mouthRx = 10 - clampedMouth * 2.2;
	$: isListening = listening > 0.1;
</script>

<svg viewBox="0 0 100 100" class="h-full w-full" class:idle-bob={active}>
	<g class:tilt={isListening}>
		<circle cx="50" cy="48" r="34" fill={color} />

		{#if hairStyle === 'bob'}
			<path d="M 16 46 A 34 34 0 0 1 84 46 L 84 29 A 34 34 0 0 0 16 29 Z" fill="#0b3d3a" opacity="0.88" />
		{:else if hairStyle === 'short'}
			<path d="M 18 33 A 32 32 0 0 1 82 33 L 82 23 A 32 32 0 0 0 18 23 Z" fill="#0b3d3a" opacity="0.88" />
		{:else if hairStyle === 'part'}
			<path d="M 18 33 A 32 32 0 0 1 82 33 L 82 23 A 32 32 0 0 0 18 23 Z" fill="#0b3d3a" opacity="0.88" />
			<line x1="50" y1="14" x2="50" y2="29" stroke={color} stroke-width="2.6" />
		{:else if hairStyle === 'spiky'}
			<path
				d="M 17 33 L 25 15 L 33 30 L 41 13 L 50 29 L 59 13 L 67 30 L 75 15 L 83 33 A 34 34 0 0 0 17 33 Z"
				fill="#0b3d3a"
				opacity="0.88"
			/>
		{/if}

		<path d="M 30 33 Q 36 29 42 32" stroke="#0b3d3a" stroke-width="2.4" fill="none" stroke-linecap="round" />
		<path d="M 58 32 Q 64 29 70 33" stroke="#0b3d3a" stroke-width="2.4" fill="none" stroke-linecap="round" />

		<g class:blink={blinking}>
			<ellipse cx="38" cy="43" rx="6.5" ry="7" fill="white" />
			<circle cx="38" cy="43" r="3" fill="#12201e" />
		</g>
		<g class:blink={blinking}>
			<ellipse cx="62" cy="43" rx="6.5" ry="7" fill="white" />
			<circle cx="62" cy="43" r="3" fill="#12201e" />
		</g>

		<ellipse cx="50" cy="63" rx={mouthRx} ry={mouthRy} fill="#12201e" />
	</g>
</svg>

<style>
	svg {
		display: block;
	}
	g.blink {
		transform-box: fill-box;
		transform-origin: center;
		transform: scaleY(0.08);
		transition: transform 90ms ease-in-out;
	}
	g.tilt {
		transform-box: fill-box;
		transform-origin: 50% 85%;
		transform: rotate(-3deg);
		transition: transform 220ms ease-out;
	}
	ellipse {
		transition:
			rx 70ms ease-out,
			ry 70ms ease-out;
	}
	svg.idle-bob {
		animation: bob 3.2s ease-in-out infinite;
	}
	@keyframes bob {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-2px);
		}
	}
</style>
