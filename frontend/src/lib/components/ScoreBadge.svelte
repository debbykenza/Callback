<script>
	/** @type {number | null | undefined} */
	export let score = null;

	$: tone =
		score == null
			? { bg: '#e6f1ef', fg: '#5b7d78' }
			: score >= 75
				? { bg: '#ccfbf1', fg: '#0b3d3a' }
				: score >= 65
					? { bg: '#fef3c7', fg: '#7a5b06' }
					: { bg: '#fee2e2', fg: '#8a1f1f' };
</script>

<span
	class="inline-flex shrink-0 items-center rounded-lg px-2.5 py-1 text-xs font-bold"
	style="background:{tone.bg}; color:{tone.fg}"
>
	{score == null ? '—' : score}
</span>
