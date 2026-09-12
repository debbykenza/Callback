<script>
	import '../app.css';
	import { browser } from '$app/environment';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/auth.js';

	$: pathname = $page.url.pathname;
	$: onHistory = pathname.startsWith('/history');
	$: isPublicRoute =
		pathname.startsWith('/landing') || pathname.startsWith('/login') || pathname.startsWith('/signup');

	$: user = $auth.user;
	$: initial = (user?.name?.trim()?.[0] || user?.email?.[0] || '?').toUpperCase();

	// Garde d'authentification cote client : pas de token -> retour au login sur les pages de
	// l'appli ; deja connecte -> on ne reste pas sur /login ou /signup.
	$: if (browser) {
		if (!$auth.token && !isPublicRoute) {
			goto('/login');
		} else if ($auth.token && (pathname === '/login' || pathname === '/signup')) {
			goto('/');
		}
	}

	function logout() {
		auth.clear();
		goto('/login');
	}
</script>

<div class="flex min-h-screen flex-col">
	{#if !isPublicRoute}
		<div class="flex items-center justify-between border-b border-[#dde9e7] bg-white px-6 py-4 sm:px-10">
			<a href="/" class="flex items-center gap-2.5">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0d9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M4 4v5h5" /><path d="M5.5 9a7 7 0 1 1 1.4 7.5" />
				</svg>
				<span class="font-display text-xl font-bold tracking-tight text-teal-900">Callback</span>
			</a>
			<div class="hidden gap-1.5 sm:flex">
				<a
					href="/"
					class="rounded-lg px-4 py-2 text-sm font-semibold"
					class:bg-teal-600={!onHistory}
					class:text-white={!onHistory}
					class:text-[#45605c]={onHistory}
				>
					Nouvel entretien
				</a>
				<a
					href="/history"
					class="rounded-lg px-4 py-2 text-sm font-semibold"
					class:bg-teal-600={onHistory}
					class:text-white={onHistory}
					class:text-[#45605c]={!onHistory}
				>
					Historique
				</a>
			</div>
			<div class="flex items-center gap-3">
				<div
					class="flex h-9 w-9 items-center justify-center rounded-full bg-teal-100 text-sm font-semibold text-teal-900"
					title={user?.email ?? ''}
				>
					{initial}
				</div>
				<button
					type="button"
					on:click={logout}
					class="text-[13px] font-medium text-[#6d8783] hover:text-teal-900"
				>
					Se deconnecter
				</button>
			</div>
		</div>
	{/if}

	<main class="flex-1">
		<slot />
	</main>
</div>
