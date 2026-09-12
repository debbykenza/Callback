import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const STORAGE_KEY = 'callback_auth';

/** @typedef {{ id: string, email: string, name: string }} AuthUser */
/** @typedef {{ token: string | null, user: AuthUser | null }} AuthState */

/** @returns {AuthState} */
function readStored() {
	if (!browser) return { token: null, user: null };
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (!raw) return { token: null, user: null };
		const parsed = JSON.parse(raw);
		return { token: parsed.token ?? null, user: parsed.user ?? null };
	} catch {
		return { token: null, user: null };
	}
}

function createAuthStore() {
	const { subscribe, set } = writable(readStored());

	/** @param {AuthState} value */
	function persist(value) {
		if (browser) {
			if (value.token) {
				localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
			} else {
				localStorage.removeItem(STORAGE_KEY);
			}
		}
		set(value);
	}

	return {
		subscribe,
		/**
		 * @param {string} token
		 * @param {AuthUser} user
		 */
		setSession(token, user) {
			persist({ token, user });
		},
		clear() {
			persist({ token: null, user: null });
		}
	};
}

export const auth = createAuthStore();

/** Lecture synchrone du token, pour les appels API (hors composants Svelte). */
export function getToken() {
	return readStored().token;
}
