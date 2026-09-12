/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			fontFamily: {
				display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
				sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif']
			},
			colors: {
				ink: '#12201e',
				teal: {
					50: '#f0fdfa',
					100: '#ccfbf1',
					600: '#0d9488',
					700: '#0f766e',
					800: '#115e59',
					900: '#0b3d3a'
				},
				amber: {
					700: '#c2661f',
					900: '#8a4415'
				}
			}
		}
	},
	plugins: []
};
