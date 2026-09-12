// Test de bout en bout (optionnel) : simule le parcours complet dans un vrai
// navigateur avec Playwright. Sert a verifier que le backend (port 8000) et le
// frontend (port 5173) fonctionnent bien ensemble.
//
// Pour l'utiliser :
//   npm install --no-save playwright && npx playwright install chromium
//   (backend lance sur :8000, frontend lance sur :5173)
//   node e2e/test_flow.mjs

import { chromium } from 'playwright';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CV_PATH = path.join(ROOT, 'sample_data', 'cv_exemple.pdf');

const OFFER_TEXT = `Developpeur Fullstack en alternance
Niji Nantes

Nous recherchons un(e) alternant(e) developpeur/developpeuse fullstack. Stack : React, FastAPI, PostgreSQL. Profil junior bienvenu.`;

const DETAILED_ANSWER =
	"Sur mon projet LifeCard, j'ai migre l'adapter Vercel et resolu une incompatibilite SQLite en environnement serverless, ce qui a stabilise le deploiement pour plusieurs releases suivantes.";

async function main() {
	const browser = await chromium.launch();
	const page = await browser.newPage();
	page.on('pageerror', (err) => console.log('PAGE ERROR:', err.message));

	console.log('1) Ouverture de la page de configuration...');
	await page.goto('http://127.0.0.1:5173/');
	await page.waitForSelector('text=Prepare ton prochain entretien');
	await page.waitForLoadState('networkidle');
	await page.waitForTimeout(300); // laisse l'hydratation SvelteKit se terminer

	console.log('2) Upload du CV...');
	await page.setInputFiles('input[type="file"]', CV_PATH);
	await page.waitForSelector('text=cv_exemple.pdf');

	console.log("3) Collage de l'offre...");
	await page.fill('textarea', OFFER_TEXT);

	console.log("4) Selection d'une persona...");
	await page.click('text=Marc');

	console.log("5) Clic sur Commencer l'entretien...");
	await page.click('button:has-text("Commencer l\'entretien")');
	await page.waitForURL(/\/interview\//, { timeout: 15000 });
	console.log('   -> redirige vers', page.url());
	await page.waitForSelector('text=Marc', { timeout: 10000 });

	console.log("6) Reponse a la question d'ouverture...");
	await page.fill('textarea', "Je suis etudiante en cycle ingenieur informatique a l'UTBM, apres un diplome de developpement logiciel.");
	await page.click('button:has-text("Envoyer")');
	await page.waitForTimeout(800);

	console.log('7) Reponse volontairement vague (doit declencher une relance)...');
	await page.fill('textarea', "Oui j'ai deja fait ca.");
	await page.click('button:has-text("Envoyer")');
	await page.waitForTimeout(800);

	const bodyText = await page.innerText('body');
	if (!bodyText.includes('exemple') && !bodyText.includes('concret')) {
		throw new Error('Relance attendue introuvable dans le texte de la page');
	}
	console.log('   -> relance detectee dans le transcript');

	console.log("8) Reponses detaillees jusqu'a la fin du questionnaire...");
	for (let i = 0; i < 6; i++) {
		const overBanner = await page.locator('text=entretien est termine').count();
		if (overBanner > 0) break;
		await page.fill('textarea', DETAILED_ANSWER);
		await page.click('button:has-text("Envoyer")');
		await page.waitForTimeout(800);
	}

	console.log("9) Clic sur Terminer l'entretien...");
	await page.click('button:has-text("Terminer l\'entretien")');
	await page.waitForURL(/\/summary\//, { timeout: 15000 });
	console.log('   -> redirige vers', page.url());

	await page.waitForSelector('text=Fiche recapitulative');
	await page.waitForSelector('text=Points forts');
	console.log('10) Fiche recapitulative affichee avec Points forts.');

	console.log("11) Bascule vers l'onglet Transcript complet...");
	await page.click('button:has-text("Transcript complet")');
	await page.waitForSelector('text=Bonjour');

	console.log("12) Retour a l'historique...");
	await page.click("text=Retour a l'historique");
	await page.waitForURL(/\/history/, { timeout: 15000 });
	await page.waitForSelector('text=Niji Nantes');
	console.log('   -> historique affiche avec la session Niji Nantes.');

	console.log('13) Clic sur Retenter...');
	await page.click('button:has-text("Retenter")');
	await page.waitForURL(/\/interview\//, { timeout: 15000 });
	console.log('   -> nouvelle session interview lancee:', page.url());

	await browser.close();
	console.log('\nE2E TEST OK — parcours complet valide dans un vrai navigateur.');
}

main().catch((err) => {
	console.error('E2E TEST FAILED:', err);
	process.exit(1);
});
