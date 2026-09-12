<svelte:head>
	<link
		rel="stylesheet"
		href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"
	/>
</svelte:head>

<div class="landing">
	<!-- NAV -->
	<div
		style="display: flex; align-items: center; justify-content: space-between; max-width: 1180px; margin: 0 auto; padding: 28px 32px; gap: 24px; border-bottom: 1px solid var(--line);"
	>
		<div style="display: flex; align-items: center; gap: 10px;">
			<span class="mono" style="color: var(--teal); font-size: 17px;">&gt;_</span>
			<span style="font-size: 19px; font-weight: 700;">Callback</span>
		</div>
		<div style="display: flex; align-items: center; gap: 24px;">
			<a href="#features" class="mono" style="font-size: 13px; color: var(--ink-soft);">Fonctionnalités</a>
			<a href="#comment-ca-marche" class="mono" style="font-size: 13px; color: var(--ink-soft);">Comment ça marche</a>
			<!-- TODO: remplacer par tes vraies routes une fois le systeme de compte en place -->
			<a href="/login" class="mono" style="font-size: 13px; color: var(--ink);">Se connecter</a>
			<a
				href="/signup"
				class="mono"
				style="font-size: 13px; font-weight: 600; color: var(--bg); background: var(--teal); border-radius: 6px; padding: 9px 16px;"
				>Créer un compte</a
			>
		</div>
	</div>

	<!-- HERO -->
	<div class="hero-photo">
		<img class="hero-bg" src="/profil6.png" alt="" />
		<div class="hero-overlay"></div>

		<div class="hero-top">
			<span
				class="mono"
				style="display: inline-flex; align-items: center; gap: 9px; font-size: 12.5px; font-weight: 600; color: var(--teal); background: rgba(16,28,25,0.7); border: 1px solid var(--line); border-radius: 999px; padding: 8px 16px 8px 12px; margin-bottom: 22px; backdrop-filter: blur(4px);"
			>
				<span
					style="width: 7px; height: 7px; border-radius: 50%; background: var(--teal); animation: cb-pulse-dot 1.8s ease-in-out infinite;"
				></span>
				Coach d'entretien IA &middot; gratuit
			</span>
			<p style="font-style: italic; font-size: 21px; color: var(--teal); line-height: 1.4; margin-bottom: 16px;">
				L'entretien blanc qui connaît vraiment ton CV.
			</p>
			<p style="font-size: 16.5px; color: #d3e2de; max-width: 460px; line-height: 1.65; margin-bottom: 26px;">
				Dépose ton CV et l'offre à laquelle tu postules, choisis une persona de recruteur, et entraîne-toi à voix
				haute ou à l'écrit. Callback pose des questions adaptées à ton parcours réel, relance quand tu restes
				vague, et te laisse une fiche récap à la fin.
			</p>
			<div style="display: flex; gap: 14px; flex-wrap: wrap; align-items: center;">
				<a
					href="/signup"
					style="display: flex; align-items: center; gap: 9px; background: var(--amber); color: #241505; font-weight: 700; font-size: 15px; padding: 14px 24px; border-radius: 8px;"
				>
					Créer un compte gratuit
				</a>
				<a
					href="/login"
					class="mono"
					style="display: flex; align-items: center; gap: 9px; color: #fff; font-weight: 500; font-size: 14px; padding: 14px 22px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.35);"
				>
					Se connecter
				</a>
			</div>
			<p class="mono" style="font-size: 12.5px; color: #a9beb9; margin-top: 14px;">
				Gratuit &middot; aucune carte bancaire requise
			</p>
		</div>

		<h1 class="hero-giant">Callback</h1>
	</div>

	<!-- PROBLEM -->
	<div style="max-width: 1180px; margin: 0 auto; padding: 20px 32px 100px;">
		<div style="max-width: 620px; margin-bottom: 44px;">
			<span class="mono" style="font-size: 13px; color: var(--teal);">01</span>
			<h2 style="font-size: 34px; margin: 14px 0;">Le problème avec les simulateurs classiques</h2>
			<p style="font-size: 15px; color: var(--ink-soft); line-height: 1.6;">
				La plupart des outils d'entraînement posent une liste de questions génériques. Un vrai recruteur, lui, a lu ton
				CV avant de te recevoir.
			</p>
		</div>
		<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 10px; overflow: hidden;">
			<div style="display: flex; align-items: center; gap: 8px; padding: 12px 16px; border-bottom: 1px solid var(--line);">
				<span style="width: 10px; height: 10px; border-radius: 50%; background: var(--red);"></span>
				<span style="width: 10px; height: 10px; border-radius: 50%; background: var(--amber);"></span>
				<span style="width: 10px; height: 10px; border-radius: 50%; background: var(--teal-dim);"></span>
				<span class="mono" style="font-size: 12px; color: var(--ink-soft); margin-left: 8px;">diff.log</span>
			</div>
			<div class="mono" style="padding: 26px 24px; font-size: 14px; line-height: 2;">
				<p style="color: var(--red);">- Les mêmes questions pour tout le monde</p>
				<p style="color: var(--red);">- Ignore le contenu réel du CV et de l'offre</p>
				<p style="color: var(--red);">- Aucune relance si la réponse reste vague</p>
				<p style="color: var(--teal); margin-top: 8px;">+ Une question par compétence exigée par l'offre</p>
				<p style="color: var(--teal);">+ Question ancrée dans un extrait concret de ton CV</p>
				<p style="color: var(--teal);">+ Relance automatique si c'est trop vague</p>
			</div>
		</div>
	</div>

	<!-- FEATURES -->
	<div id="features" style="max-width: 1180px; margin: 0 auto; padding: 20px 32px 110px;">
		<span class="mono" style="font-size: 13px; color: var(--teal);">02</span>
		<h2 style="font-size: 34px; margin: 14px 0 44px;">Ce que ça fait</h2>
		<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px;">
			<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 12px; padding: 28px;">
				<span class="mono" style="font-size: 12px; color: var(--teal);">01</span>
				<h3 style="font-size: 17px; margin: 12px 0 10px;">Questions adaptées à ton CV</h3>
				<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
					Chaque compétence requise par l'offre est comparée à ton CV pour poser une question sur du concret plutôt
					qu'une généralité.
				</p>
			</div>

			<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 12px; padding: 28px;">
				<span class="mono" style="font-size: 12px; color: var(--teal);">02</span>
				<h3 style="font-size: 17px; margin: 12px 0 10px;">Relance si tu restes vague</h3>
				<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
					L'IA évalue si ta réponse est assez précise. Si c'est flou, une relance te demande un exemple concret avant
					de passer à la compétence suivante.
				</p>
			</div>

			<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 12px; padding: 28px;">
				<span class="mono" style="font-size: 12px; color: var(--teal);">03</span>
				<h3 style="font-size: 17px; margin: 12px 0 10px;">Mode vocal, façon visio</h3>
				<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
					Un échange voix-à-voix en temps réel, un visage animé qui réagit à la conversation, et ta caméra en retour
					vidéo local &mdash; jamais envoyée ni enregistrée.
				</p>
			</div>

			<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 12px; padding: 28px;">
				<span class="mono" style="font-size: 12px; color: var(--teal);">04</span>
				<h3 style="font-size: 17px; margin: 12px 0 10px;">Fiche récap + historique</h3>
				<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
					À la fin : points forts, points à travailler, notes par critère. Chaque entretien est sauvegardé, avec
					possibilité de retenter avec le même CV et la même offre.
				</p>
			</div>
		</div>
	</div>

	<!-- COMMENT CA MARCHE -->
	<div id="comment-ca-marche" style="max-width: 1180px; margin: 0 auto; padding: 20px 32px 110px;">
		<span class="mono" style="font-size: 13px; color: var(--teal);">03</span>
		<h2 style="font-size: 34px; margin: 14px 0 36px;">Comment ça marche</h2>

		<div class="roadmap">
			<div class="roadmap-line"></div>
			<div class="roadmap-grid">
				<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 16px;">
					<div class="roadmap-node"><span class="mono" style="color: var(--teal); font-weight: 700; font-size: 14px;">01</span></div>
					<h3 style="font-size: 18px;">Dépose ton CV et l'offre</h3>
					<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
						Un CV, l'offre à laquelle tu postules&nbsp;: Callback prépare un entretien qui correspond vraiment à ton profil.
					</p>
				</div>

				<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 16px;">
					<div class="roadmap-node"><span class="mono" style="color: var(--teal); font-weight: 700; font-size: 14px;">02</span></div>
					<h3 style="font-size: 18px;">Choisis ta persona et ton mode</h3>
					<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
						À l'écrit ou à l'oral, façon visio avec ta caméra en retour local, parmi plusieurs personas de recruteur.
					</p>
				</div>

				<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 16px;">
					<div class="roadmap-node"><span class="mono" style="color: var(--teal); font-weight: 700; font-size: 14px;">03</span></div>
					<h3 style="font-size: 18px;">Passe l'entretien, reçois ta fiche</h3>
					<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
						Des questions sur tes compétences réelles, une relance si tu restes vague, et une fiche de débrief à la fin.
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- GRATUIT / CONFIDENTIALITE -->
	<div style="max-width: 1180px; margin: 0 auto; padding: 20px 32px 90px;">
		<span class="mono" style="font-size: 13px; color: var(--teal);">04</span>
		<h2 style="font-size: 34px; margin: 14px 0 36px;">Quelques avantages</h2>
		<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px;">
			<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 10px; padding: 22px;">
				<h3 style="font-size: 15px; margin-bottom: 10px;">100&nbsp;% gratuit</h3>
				<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
					Aucune carte bancaire, aucun abonnement, aucune limite cachée.
				</p>
			</div>
			<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 10px; padding: 22px;">
				<h3 style="font-size: 15px; margin-bottom: 10px;">Ta caméra reste chez toi</h3>
				<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
					Elle sert uniquement à ton propre retour vidéo local, jamais envoyée ni enregistrée.
				</p>
			</div>
			<div style="background: var(--bg-raised); border: 1px solid var(--line); border-radius: 10px; padding: 22px;">
				<h3 style="font-size: 15px; margin-bottom: 10px;">Tes entretiens restent privés</h3>
				<p style="font-size: 14px; color: var(--ink-soft); line-height: 1.6;">
					CV, réponses et fiches ne sont visibles que par toi, depuis ton compte.
				</p>
			</div>
		</div>
	</div>

	<!-- CLOSING CTA -->
	<div style="max-width: 1180px; margin: 0 auto; padding: 40px 32px 70px; border-top: 1px solid var(--line); text-align: center;">
		<h2 style="font-size: 36px; margin-bottom: 16px;">Prêt à t'entraîner&nbsp;?</h2>
		<p style="font-size: 15px; color: var(--ink-soft); max-width: 460px; margin: 0 auto 30px; line-height: 1.6;">
			Crée ton compte et passe ton premier entretien en quelques minutes. C'est gratuit.
		</p>
		<div style="display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; margin-bottom: 14px;">
			<a
				href="/signup"
				style="display: flex; align-items: center; gap: 9px; background: var(--amber); color: #241505; font-weight: 700; font-size: 15px; padding: 14px 24px; border-radius: 8px;"
				>Créer un compte gratuit</a
			>
		</div>
		<a href="/login" style="font-size: 14px; color: var(--ink-soft);"
			>Déjà un compte&nbsp;? <span style="color: var(--teal); font-weight: 600;">Se connecter</span></a
		>
	</div>

	<!-- FOOTER -->
	<div style="border-top: 1px solid var(--line); padding: 24px 32px;">
		<div style="max-width: 1180px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
			<p style="font-size: 13px; color: var(--ink-soft);">Callback &mdash; coach d'entretien IA, gratuit.</p>
			<div style="display: flex; gap: 20px;">
				<a href="#features" style="font-size: 13px; color: var(--ink-soft);">Fonctionnalités</a>
				<a href="/login" style="font-size: 13px; color: var(--ink-soft);">Se connecter</a>
			</div>
		</div>
	</div>
</div>

<style>
	.landing {
		--bg: #0a1210;
		--bg-raised: #101c19;
		--ink: #e7f2ef;
		--ink-soft: #9db3ae;
		--teal: oklch(78% 0.13 185);
		--teal-dim: oklch(45% 0.07 185);
		--amber: oklch(74% 0.13 60);
		--line: #223a35;
		--red: #ef7a6d;

		width: 100%;
		font-family: 'IBM Plex Sans', system-ui, sans-serif;
		color: var(--ink);
		background:
			linear-gradient(var(--bg), var(--bg)),
			repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.028) 0px, rgba(255, 255, 255, 0.028) 1px, transparent 1px, transparent 64px),
			repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.028) 0px, rgba(255, 255, 255, 0.028) 1px, transparent 1px, transparent 64px);
	}
	.landing,
	.landing * {
		box-sizing: border-box;
	}
	.landing a {
		color: var(--teal);
		text-decoration: none;
	}
	.landing a:hover {
		color: #cdeee8;
	}
	.landing h1,
	.landing h2,
	.landing h3 {
		font-family: 'Space Grotesk', system-ui, sans-serif;
		font-weight: 600;
		margin: 0;
		color: var(--ink);
	}
	.landing .mono {
		font-family: 'IBM Plex Mono', monospace;
	}
	.landing p {
		margin: 0;
	}
	.hero-photo {
		position: relative;
		width: 100%;
		min-height: 680px;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}
	.hero-bg {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		object-position: center 25%;
		z-index: 0;
	}
	.hero-overlay {
		position: absolute;
		inset: 0;
		z-index: 1;
		background: linear-gradient(0deg, var(--bg) 0%, rgba(10, 18, 16, 0.55) 22%, rgba(10, 18, 16, 0.15) 40%, transparent 58%);
	}
	.hero-top {
		position: relative;
		z-index: 2;
		max-width: 560px;
		padding: 72px 48px 0;
		text-shadow: 0 2px 14px rgba(0, 0, 0, 0.65), 0 1px 3px rgba(0, 0, 0, 0.5);
	}
	.landing h1.hero-giant {
		position: relative;
		z-index: 2;
		font-size: clamp(72px, 13vw, 168px);
		line-height: 0.85;
		font-weight: 700;
		letter-spacing: -0.02em;
		color: #fff;
		padding: 0 40px 36px;
		margin: 0;
	}
	@media (max-width: 780px) {
		.hero-photo {
			min-height: 560px;
		}
		.hero-top {
			padding: 56px 24px 0;
		}
		.landing h1.hero-giant {
			font-size: clamp(48px, 16vw, 90px);
			padding: 0 24px 28px;
		}
	}
	.roadmap {
		position: relative;
		margin-top: 56px;
	}
	.roadmap-line {
		position: absolute;
		top: 22px;
		left: 0;
		right: 0;
		height: 2px;
		background-image: repeating-linear-gradient(90deg, var(--line) 0 10px, transparent 10px 18px);
		z-index: 0;
	}
	.roadmap-grid {
		position: relative;
		z-index: 1;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 32px;
	}
	.roadmap-node {
		width: 46px;
		height: 46px;
		border-radius: 50%;
		background: var(--bg);
		border: 2px solid var(--teal);
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}
	@media (max-width: 680px) {
		.roadmap-line {
			display: none;
		}
		.roadmap-grid {
			grid-template-columns: 1fr;
			gap: 36px;
		}
	}
	@keyframes cb-ripple {
		0% {
			transform: scale(0.82);
			opacity: 0.55;
		}
		70% {
			opacity: 0.12;
		}
		100% {
			transform: scale(1.8);
			opacity: 0;
		}
	}
	@keyframes cb-pulse-dot {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.3;
		}
	}
</style>