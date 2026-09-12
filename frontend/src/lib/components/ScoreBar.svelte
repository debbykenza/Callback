<script>
	/** @type {string} */
	export let label;
	/** @type {number} */
	export let value;
</script>

<div>
	<div class="mb-1.5 flex justify-between text-[13px] text-[#3f5c57]">
		<span>{label}</span>
		<span class="font-semibold text-teal-900">{value}/100</span>
	</div>
	<div class="h-[7px] rounded-full bg-[#e6f1ef]">
		<div class="h-full rounded-full bg-teal-600" style="width:{value}%"></div>
	</div>
</div>
