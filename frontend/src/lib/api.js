import { PUBLIC_API_URL } from '$env/static/public';
import { getToken } from './auth.js';

const BASE = PUBLIC_API_URL;

export const API_BASE = BASE;

/** @param {Response} res */
async function unwrap(res) {
	if (!res.ok) {
		let detail = res.statusText;
		try {
			const body = await res.json();
			detail = body.detail ?? detail;
		} catch {
			// pas de corps JSON, on garde le statusText
		}
		const err = new Error(detail);
		// @ts-ignore
		err.status = res.status;
		throw err;
	}
	return res.json();
}

/** @param {Record<string, string>} [extra] */
function authHeaders(extra = {}) {
	const token = getToken();
	return token ? { ...extra, Authorization: `Bearer ${token}` } : extra;
}

// --- Auth ---

export async function registerUser(email, password, name = '') {
	return unwrap(
		await fetch(`${BASE}/api/auth/register`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, password, name })
		})
	);
}

export async function loginUser(email, password) {
	return unwrap(
		await fetch(`${BASE}/api/auth/login`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, password })
		})
	);
}

// --- Reste de l'API (protege par un token une fois connecte) ---

export async function listPersonas() {
	return unwrap(await fetch(`${BASE}/api/personas`));
}

export async function uploadCv(file) {
	const form = new FormData();
	form.append('file', file);
	return unwrap(await fetch(`${BASE}/api/cv`, { method: 'POST', headers: authHeaders(), body: form }));
}

export async function createOffer(rawText) {
	return unwrap(
		await fetch(`${BASE}/api/offers`, {
			method: 'POST',
			headers: authHeaders({ 'Content-Type': 'application/json' }),
			body: JSON.stringify({ raw_text: rawText })
		})
	);
}

export async function createSession(cvId, jobOfferId, persona) {
	return unwrap(
		await fetch(`${BASE}/api/sessions`, {
			method: 'POST',
			headers: authHeaders({ 'Content-Type': 'application/json' }),
			body: JSON.stringify({ cv_id: cvId, job_offer_id: jobOfferId, persona })
		})
	);
}

export async function getSession(id) {
	return unwrap(await fetch(`${BASE}/api/sessions/${id}`, { headers: authHeaders() }));
}

export async function sendAnswer(id, content) {
	return unwrap(
		await fetch(`${BASE}/api/sessions/${id}/messages`, {
			method: 'POST',
			headers: authHeaders({ 'Content-Type': 'application/json' }),
			body: JSON.stringify({ content })
		})
	);
}

export async function endSession(id) {
	return unwrap(await fetch(`${BASE}/api/sessions/${id}/end`, { method: 'POST', headers: authHeaders() }));
}

export async function getSummary(id) {
	return unwrap(await fetch(`${BASE}/api/sessions/${id}/summary`, { headers: authHeaders() }));
}

export async function listHistory() {
	return unwrap(await fetch(`${BASE}/api/history`, { headers: authHeaders() }));
}

export async function retrySession(id) {
	return unwrap(await fetch(`${BASE}/api/sessions/${id}/retry`, { method: 'POST', headers: authHeaders() }));
}
