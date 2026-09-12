// Couleurs d'avatar par persona (les noms/tags viennent du backend, /api/personas).
export const PERSONA_COLORS = {
	claire: '#0d9488',
	marc: '#0f766e',
	lea: '#115e59',
	hugo: '#134e4a'
};

export function personaColor(id) {
	return PERSONA_COLORS[id] ?? '#0d9488';
}

export function personaInitial(name) {
	return (name || '?').charAt(0).toUpperCase();
}

// Silhouette de "cheveux" du visage anime (PersonaFace.svelte) par persona —
// purement decoratif, sert juste a distinguer les personas visuellement.
export const PERSONA_HAIR = {
	claire: 'bob',
	marc: 'short',
	lea: 'part',
	hugo: 'spiky'
};

export function personaHairStyle(id) {
	return PERSONA_HAIR[id] ?? 'short';
}
