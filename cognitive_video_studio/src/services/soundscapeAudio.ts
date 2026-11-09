// Soundscape Audio Engine using Web Audio API
// Provides clean, subtle cinematic room tone, atmospheric pads, and refined foley accents.
// Free of any sub-bass thumping, repetitive kick sweeps, or harsh acoustic beating.

class SoundscapeEngine {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;

  // Ambience Nodes (A2)
  private ambienceGain: GainNode | null = null;
  private ambienceFilter: BiquadFilterNode | null = null;
  private ambienceNoiseNode: AudioBufferSourceNode | null = null;

  // Score Drone Nodes (A3) - Pure Smooth Sine (No Detuned Beating)
  private scoreGain: GainNode | null = null;
  private droneOsc: OscillatorNode | null = null;
  private droneFilter: BiquadFilterNode | null = null;

  // Foley Nodes (A4) - Soft Textures Only
  private foleyGain: GainNode | null = null;
  private lastTriggeredTimes: { [key: string]: number } = {};

  public init() {
    if (this.ctx) return;
    try {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.ctx = new AudioCtx();

      // Master Output - Gentle, balanced volume
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.3, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);

      // Track A2: Subtle Ambience Sub-Mix (Soft filtered air, no rumble)
      this.ambienceGain = this.ctx.createGain();
      this.ambienceGain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      this.ambienceFilter = this.ctx.createBiquadFilter();
      this.ambienceFilter.type = 'bandpass';
      this.ambienceFilter.frequency.setValueAtTime(500, this.ctx.currentTime);
      this.ambienceFilter.Q.setValueAtTime(0.8, this.ctx.currentTime);

      // Smooth Pink/Brown Noise Generator (Low-pass filtered gentle air)
      const bufferSize = this.ctx.sampleRate * 2;
      const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      let lastOut = 0.0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        // Soft single-pole lowpass filter for gentle room air
        lastOut = (lastOut + 0.02 * white) / 1.02;
        output[i] = lastOut * 0.25;
      }

      this.ambienceNoiseNode = this.ctx.createBufferSource();
      this.ambienceNoiseNode.buffer = noiseBuffer;
      this.ambienceNoiseNode.loop = true;
      this.ambienceNoiseNode.connect(this.ambienceFilter);
      this.ambienceFilter.connect(this.ambienceGain);
      this.ambienceGain.connect(this.masterGain);
      this.ambienceNoiseNode.start();

      // Track A3: Tension Drone Sub-Mix - Single Pure Sine Pad (Zero Thumping Beating)
      this.scoreGain = this.ctx.createGain();
      this.scoreGain.gain.setValueAtTime(0.15, this.ctx.currentTime);

      this.droneFilter = this.ctx.createBiquadFilter();
      this.droneFilter.type = 'lowpass';
      this.droneFilter.frequency.setValueAtTime(180, this.ctx.currentTime);

      this.droneOsc = this.ctx.createOscillator();
      this.droneOsc.type = 'sine'; // Pure smooth sine - no harsh harmonics or flutter
      this.droneOsc.frequency.setValueAtTime(65.4, this.ctx.currentTime); // C2

      this.droneOsc.connect(this.droneFilter);
      this.droneFilter.connect(this.scoreGain);
      this.scoreGain.connect(this.masterGain);
      this.droneOsc.start();

      // Track A4: Foley Sub-Mix - Low Level for Soft Accents
      this.foleyGain = this.ctx.createGain();
      this.foleyGain.gain.setValueAtTime(0.18, this.ctx.currentTime);
      this.foleyGain.connect(this.masterGain);
    } catch (err) {
      console.warn('Web Audio API not supported or blocked by autoplay policy:', err);
    }
  }

  public update(
    currentTimeSec: number, 
    isPlaying: boolean,
    trackMutes: { a2?: boolean; a3?: boolean; a4?: boolean } = {}
  ) {
    if (!this.ctx) return;

    if (this.ctx.state === 'suspended' && isPlaying) {
      this.ctx.resume();
    }

    const t = this.ctx.currentTime;

    // Smooth silence on pause
    if (!isPlaying) {
      this.masterGain?.gain.setTargetAtTime(0, t, 0.05);
      return;
    } else {
      this.masterGain?.gain.setTargetAtTime(0.35, t, 0.05);
    }

    // A2 Ambience Mute & Mood Adaptation
    if (trackMutes.a2) {
      this.ambienceGain?.gain.setTargetAtTime(0, t, 0.05);
    } else {
      if (currentTimeSec < 8.5) {
        // Beat 1: Open Terrace Air
        this.ambienceGain?.gain.setTargetAtTime(0.12, t, 0.1);
        this.ambienceFilter?.frequency.setTargetAtTime(550, t, 0.2);
      } else if (currentTimeSec < 24.62) {
        // Beat 2 & 3: Living Room Room Tone
        this.ambienceGain?.gain.setTargetAtTime(0.08, t, 0.1);
        this.ambienceFilter?.frequency.setTargetAtTime(320, t, 0.2);
      } else {
        // Beat 4 & 5: Outdoor Highway Air
        this.ambienceGain?.gain.setTargetAtTime(0.15, t, 0.1);
        this.ambienceFilter?.frequency.setTargetAtTime(650, t, 0.2);
      }
    }

    // A3 Tension Drone Adaptation (Smooth harmonic frequency shifts, no detuning)
    if (trackMutes.a3) {
      this.scoreGain?.gain.setTargetAtTime(0, t, 0.05);
    } else {
      if (currentTimeSec < 8.5) {
        // Warm C2 (65.4 Hz)
        this.scoreGain?.gain.setTargetAtTime(0.15, t, 0.3);
        this.droneOsc?.frequency.setTargetAtTime(65.4, t, 0.3);
      } else if (currentTimeSec < 15.82) {
        // Smooth drop to Eb2 (77.8 Hz) for minor tension
        this.scoreGain?.gain.setTargetAtTime(0.18, t, 0.3);
        this.droneOsc?.frequency.setTargetAtTime(77.8, t, 0.3);
      } else if (currentTimeSec < 24.62) {
        // F2 (87.3 Hz)
        this.scoreGain?.gain.setTargetAtTime(0.2, t, 0.3);
        this.droneOsc?.frequency.setTargetAtTime(87.3, t, 0.3);
      } else {
        // A2 (110 Hz)
        this.scoreGain?.gain.setTargetAtTime(0.22, t, 0.3);
        this.droneOsc?.frequency.setTargetAtTime(110.0, t, 0.3);
      }
    }

    // A4 Foley Synchronized Triggers (Single precise triggers, zero continuous thumping)
    if (!trackMutes.a4) {
      // 00:08.5s Chair Floor Friction Scrape (High frequency texture, not a bass thump)
      if (Math.abs(currentTimeSec - 8.5) < 0.2 && !this.lastTriggeredTimes['chair_scrape']) {
        this.playChairScrape();
        this.lastTriggeredTimes['chair_scrape'] = currentTimeSec;
      }
      // 00:09.12s Patriarch Floor Hand Contact
      if (Math.abs(currentTimeSec - 9.12) < 0.2 && !this.lastTriggeredTimes['hand_contact']) {
        this.playHandContact();
        this.lastTriggeredTimes['hand_contact'] = currentTimeSec;
      }
      // 00:24.62s Wooden Club Contact (Crisp wooden tap)
      if (Math.abs(currentTimeSec - 24.62) < 0.2 && !this.lastTriggeredTimes['club_tap']) {
        this.playClubTap();
        this.lastTriggeredTimes['club_tap'] = currentTimeSec;
      }

      // Reset triggers when scrubbing backwards
      for (const k of Object.keys(this.lastTriggeredTimes)) {
        if (Math.abs(currentTimeSec - this.lastTriggeredTimes[k]) > 1.5) {
          delete this.lastTriggeredTimes[k];
        }
      }
    }
  }

  // Soft chair floor scrape texture (bandpass filtered noise, NO sub-bass kick)
  public playChairScrape() {
    if (!this.ctx || !this.foleyGain) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(220, t);
    osc.frequency.linearRampToValueAtTime(140, t + 0.2);

    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(400, t);
    filter.Q.setValueAtTime(1.5, t);

    g.gain.setValueAtTime(0.12, t);
    g.gain.linearRampToValueAtTime(0.001, t + 0.2);

    osc.connect(filter);
    filter.connect(g);
    g.connect(this.foleyGain);
    osc.start(t);
    osc.stop(t + 0.2);
  }

  // Soft palm contact (gentle high-passed tap, NO sub thump)
  public playHandContact() {
    if (!this.ctx || !this.foleyGain) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const g = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(160, t);
    osc.frequency.linearRampToValueAtTime(90, t + 0.12);

    g.gain.setValueAtTime(0.14, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.12);

    osc.connect(g);
    g.connect(this.foleyGain);
    osc.start(t);
    osc.stop(t + 0.12);
  }

  // Crisp wooden stick tap (dry wood acoustic resonance, NO bass boom)
  public playClubTap() {
    if (!this.ctx || !this.foleyGain) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const g = this.ctx.createGain();

    osc.type = 'square';
    osc.frequency.setValueAtTime(320, t);
    osc.frequency.exponentialRampToValueAtTime(180, t + 0.08);

    g.gain.setValueAtTime(0.1, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.09);

    osc.connect(g);
    g.connect(this.foleyGain);
    osc.start(t);
    osc.stop(t + 0.09);
  }

  public setMasterVolume(vol: number) {
    if (!this.ctx || !this.masterGain) return;
    this.masterGain.gain.setTargetAtTime(Math.max(0, Math.min(1, vol)), this.ctx.currentTime, 0.05);
  }

  public stopAll() {
    if (!this.ctx || !this.masterGain) return;
    this.masterGain.gain.setValueAtTime(0, this.ctx.currentTime);
  }
}

export const soundscape = new SoundscapeEngine();
