// Capture micro -> PCM16 16kHz mono envoye au backend, et lecture des reponses
// audio PCM16 24kHz recues du backend (relais Gemini Live, voir
// backend/app/routers/voice.py + backend/app/services/voice_service.py).
//
// Pas de dependance externe : Web Audio API "brute" (ScriptProcessorNode).
// C'est une API depreciee au profit d'AudioWorklet, mais elle reste la plus
// simple a integrer sans fichier worklet separe, et elle est encore
// supportee partout — un compromis raisonnable pour ce projet.

const INPUT_SAMPLE_RATE = 16000;
const OUTPUT_SAMPLE_RATE = 24000;

/** @param {Float32Array} float32Array */
function floatTo16BitPCM(float32Array) {
	const out = new Int16Array(float32Array.length);
	for (let i = 0; i < float32Array.length; i++) {
		const s = Math.max(-1, Math.min(1, float32Array[i]));
		out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
	}
	return out;
}

/**
 * @param {Float32Array} buffer
 * @param {number} inputSampleRate
 * @param {number} outputSampleRate
 */
function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {
	if (outputSampleRate === inputSampleRate) return buffer;
	const ratio = inputSampleRate / outputSampleRate;
	const newLength = Math.round(buffer.length / ratio);
	const result = new Float32Array(newLength);
	let offsetResult = 0;
	let offsetBuffer = 0;
	while (offsetResult < newLength) {
		const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
		let accum = 0;
		let count = 0;
		for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
			accum += buffer[i];
			count++;
		}
		result[offsetResult] = count > 0 ? accum / count : 0;
		offsetResult++;
		offsetBuffer = nextOffsetBuffer;
	}
	return result;
}

/** @param {string} apiBaseUrl @param {string} sessionId */
export function wsUrlFor(apiBaseUrl, sessionId) {
	const url = new URL(`/ws/sessions/${sessionId}/voice`, apiBaseUrl);
	url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
	return url.toString();
}

/**
 * @typedef {{
 *   onStatus?: (state: string) => void,
 *   onTranscript?: (t: {role: string, text: string}) => void,
 *   onError?: (message: string) => void,
 *   onClose?: () => void,
 *   onVideoUnavailable?: () => void
 * }} VoiceHandlers
 */
export class VoiceInterview {
	/**
	 * @param {string} wsUrl
	 * @param {VoiceHandlers} handlers
	 * @param {{video?: boolean}} [options] `video: true` (par defaut) demande aussi la
	 *   camera pour un retour visuel de toi-meme, cote navigateur uniquement — cette
	 *   image n'est jamais envoyee au backend ni a Gemini, seul l'audio l'est.
	 */
	constructor(wsUrl, handlers = {}, options = {}) {
		this.wsUrl = wsUrl;
		this.handlers = handlers;
		this.wantVideo = options.video !== false;
		/** @type {WebSocket | null} */
		this.ws = null;
		/** @type {AudioContext | null} */
		this.audioContext = null;
		/** @type {MediaStream | null} */
		this.mediaStream = null;
		/** @type {MediaStreamAudioSourceNode | null} */
		this.sourceNode = null;
		/** @type {ScriptProcessorNode | null} */
		this.processorNode = null;
		/** @type {AnalyserNode | null} */
		this.inputAnalyser = null;
		/** @type {AudioContext | null} */
		this.playbackContext = null;
		/** @type {AnalyserNode | null} */
		this.outputAnalyser = null;
		this.playbackTime = 0;
		this.active = false;
		/** true si la camera a bien pu etre ouverte (false si refusee/absente). */
		this.videoAvailable = false;
	}

	async start() {
		this.ws = new WebSocket(this.wsUrl);
		this.ws.binaryType = 'arraybuffer';
		this.ws.onmessage = (event) => this._onMessage(event);
		this.ws.onerror = () => this.handlers.onError?.('Connexion WebSocket perdue.');
		this.ws.onclose = () => {
			this._stopMic();
			this.handlers.onClose?.();
		};

		await new Promise((resolve, reject) => {
			this.ws?.addEventListener('open', () => resolve(undefined), { once: true });
			this.ws?.addEventListener(
				'error',
				() => reject(new Error('Impossible de se connecter au serveur vocal.')),
				{ once: true }
			);
		});

		await this._startMic();
	}

	async _startMic() {
		const wantVideo = this.wantVideo;
		try {
			this.mediaStream = await navigator.mediaDevices.getUserMedia(
				wantVideo ? { audio: true, video: { width: 320, height: 240 } } : { audio: true }
			);
			this.videoAvailable = wantVideo && this.mediaStream.getVideoTracks().length > 0;
		} catch (err) {
			if (!wantVideo) throw err;
			// Camera refusee/absente : on ne bloque pas l'entretien pour autant, on
			// retombe sur de l'audio seul.
			this.handlers.onVideoUnavailable?.();
			this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
			this.videoAvailable = false;
		}

		this.audioContext = new AudioContext();
		this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);

		this.inputAnalyser = this.audioContext.createAnalyser();
		this.inputAnalyser.fftSize = 256;
		this.sourceNode.connect(this.inputAnalyser);

		this.processorNode = this.audioContext.createScriptProcessor(4096, 1, 1);
		this.processorNode.onaudioprocess = (event) => {
			if (!this.active || this.ws?.readyState !== WebSocket.OPEN) return;
			const input = event.inputBuffer.getChannelData(0);
			const downsampled = downsampleBuffer(input, this.audioContext.sampleRate, INPUT_SAMPLE_RATE);
			const pcm16 = floatTo16BitPCM(downsampled);
			this.ws.send(pcm16.buffer);
		};
		this.sourceNode.connect(this.processorNode);
		// Necessaire pour que onaudioprocess se declenche sur certains navigateurs,
		// meme si on ne veut pas entendre le micro en direct.
		this.processorNode.connect(this.audioContext.destination);
		this.active = true;
	}

	/** Niveau du micro (0-1), pour animer la tuile "toi" pendant que tu parles. */
	getInputLevel() {
		return this._levelFromAnalyser(this.inputAnalyser);
	}

	/** Niveau de l'audio de reponse (0-1), pour animer la tuile de la persona. */
	getOutputLevel() {
		return this._levelFromAnalyser(this.outputAnalyser);
	}

	/** @param {AnalyserNode | null} analyser */
	_levelFromAnalyser(analyser) {
		if (!analyser) return 0;
		const data = new Uint8Array(analyser.frequencyBinCount);
		analyser.getByteTimeDomainData(data);
		let sumSquares = 0;
		for (let i = 0; i < data.length; i++) {
			const v = (data[i] - 128) / 128;
			sumSquares += v * v;
		}
		return Math.min(1, Math.sqrt(sumSquares / data.length) * 4);
	}

	_stopMic() {
		this.active = false;
		try {
			this.processorNode?.disconnect();
		} catch {
			/* deja deconnecte */
		}
		try {
			this.sourceNode?.disconnect();
		} catch {
			/* deja deconnecte */
		}
		this.mediaStream?.getTracks().forEach((t) => t.stop());
		this.audioContext?.close().catch(() => {});
	}

	/** @param {MessageEvent} event */
	_onMessage(event) {
		if (typeof event.data === 'string') {
			try {
				const payload = JSON.parse(event.data);
				if (payload.type === 'transcript') this.handlers.onTranscript?.(payload);
				else if (payload.type === 'status') this.handlers.onStatus?.(payload.state);
				else if (payload.type === 'error') this.handlers.onError?.(payload.message);
			} catch {
				// message texte non-JSON : on ignore
			}
			return;
		}
		this._playAudioChunk(event.data);
	}

	/** @param {ArrayBuffer} arrayBuffer */
	_playAudioChunk(arrayBuffer) {
		if (!this.playbackContext) {
			this.playbackContext = new AudioContext({ sampleRate: OUTPUT_SAMPLE_RATE });
			this.playbackTime = this.playbackContext.currentTime;
			this.outputAnalyser = this.playbackContext.createAnalyser();
			this.outputAnalyser.fftSize = 256;
			this.outputAnalyser.connect(this.playbackContext.destination);
		}
		const int16 = new Int16Array(arrayBuffer);
		const float32 = new Float32Array(int16.length);
		for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 0x8000;

		const buffer = this.playbackContext.createBuffer(1, float32.length, OUTPUT_SAMPLE_RATE);
		buffer.copyToChannel(float32, 0);

		const source = this.playbackContext.createBufferSource();
		source.buffer = buffer;
		source.connect(this.outputAnalyser);

		const now = this.playbackContext.currentTime;
		const startAt = Math.max(now, this.playbackTime);
		source.start(startAt);
		this.playbackTime = startAt + buffer.duration;
	}

	stop() {
		this._stopMic();
		if (this.ws?.readyState === WebSocket.OPEN) {
			try {
				this.ws.send(JSON.stringify({ type: 'end' }));
			} catch {
				/* la connexion peut deja etre en train de se fermer */
			}
		}
		this.ws?.close();
		this.playbackContext?.close().catch(() => {});
		this.playbackContext = null;
	}
}
