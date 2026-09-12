<script>
	import { goto } from '$app/navigation';
	import { loginUser } from '$lib/api.js';
	import { auth } from '$lib/auth.js';

	let email = '';
	let password = '';
	let submitting = false;
	/** @type {string | null} */
	let error = null;

	async function onSubmit() {
		if (submitting) return;
		submitting = true;
		error = null;
		try {
			const data = await loginUser(email, password);
			auth.setSession(data.access_token, data.user);
			goto('/');
		} catch (e) {
			error = e.message ?? "Une erreur s'est produite.";
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Se connecter — Callback</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[#f7fbfa] px-6 py-12">
	<div class="w-full max-w-sm">
		<a href="/landing" class="mb-8 flex items-center justify-center gap-2">
			<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0d9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M4 4v5h5" /><path d="M5.5 9a7 7 0 1 1 1.4 7.5" />
			</svg>
			<span class="font-display text-lg font-bold tracking-tight text-teal-900">Callback</span>
		</a>

		<div class="rounded-2xl border border-[#dde9e7] bg-white p-7 shadow-sm">
			<h1 class="font-display text-xl font-bold text-teal-900">Content de te revoir</h1>
			<p class="mt-1 text-[13.5px] text-[#6d8783]">Connecte-toi pour retrouver tes entretiens.</p>

			{#if error}
				<div class="mt-4 rounded-xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-[13px] text-red-800">
					{error}
				</div>
			{/if}

			<form class="mt-5 flex flex-col gap-3.5" on:submit|preventDefault={onSubmit}>
				<label class="flex flex-col gap-1.5 text-[13px] font-medium text-teal-900">
					Email
					<input
						type="email"
						autocomplete="email"
						required
						bind:value={email}
						placeholder="toi@exemple.com"
						class="rounded-xl border border-[#e2ede9] bg-[#fafefe] px-3.5 py-2.5 text-sm text-ink placeholder:text-[#93a5a2] focus:border-teal-600 focus:outline-none"
					/>
				</label>
				<label class="flex flex-col gap-1.5 text-[13px] font-medium text-teal-900">
					Mot de passe
					<input
						type="password"
						autocomplete="current-password"
						required
						minlength="8"
						bind:value={password}
						placeholder="••••••••"
						class="rounded-xl border border-[#e2ede9] bg-[#fafefe] px-3.5 py-2.5 text-sm text-ink placeholder:text-[#93a5a2] focus:border-teal-600 focus:outline-none"
					/>
				</label>

				<button
					type="submit"
					disabled={submitting}
					class="mt-1.5 flex items-center justify-center gap-2 rounded-xl bg-teal-900 px-6 py-3 text-[14.5px] font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
				>
					{submitting ? 'Connexion...' : 'Se connecter'}
				</button>
			</form>
		</div>

		<p class="mt-5 text-center text-[13.5px] text-[#6d8783]">
			Pas encore de compte ?
			<a href="/signup" class="font-semibold text-teal-700">Creer un compte</a>
		</p>
	</div>
</div>
