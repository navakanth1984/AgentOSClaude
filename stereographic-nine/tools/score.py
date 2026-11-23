"""UNKNOWN 9 — procedural score + ambience, locked to video.html's timeline (v6/v7 motion, 31 s).

Open-source only: numpy + the standard library. Deterministic (seeded), so every run gives the same WAV.
Each cue below reads the same constants as the film (T_HOPF0, T_SNAP, strike peaks, glitch hash ...),
so a sound lands on the exact frame of the visual it belongs to.

usage:  python score.py out.wav            (48 kHz, 24-bit stereo; v7 organic score)
        python score.py out.wav --future   (v8 futuristic score: FM / data / laser layers + the 16-24 s swirl)
"""
import sys, wave
import numpy as np

FS, DUR = 48000, 31.0
N = int(FS * DUR)
t = np.arange(N) / FS
rng = np.random.default_rng(9)
PHI = (1 + 5 ** 0.5) / 2
FUT = '--future' in sys.argv

# ---- film timeline (copied from video.html) ----
T_HOPF0, T_HOPF1, T_BST0, T_BST1, T_FREEZE = 12.2, 16.4, 21.0, 24.8, 24.9
T_SNAP, T_SWAP0, T_SWAP1, T_CRED, T_END = 25.6, 26.8, 27.75, 28.9, 30.8
STRIKES = [(np.pi / 2 + 0.6 + 2 * np.pi * k) / 1.25 for k in range(6)]   # peaks of sin(1.25t - 0.6)^5


def H1(n):                                           # the film's hash: same glitch frames, same sound frames
    s = np.sin(n) * 43758.5453
    return s - np.floor(s)


def seg(a, b): return np.clip((t - a) / (b - a), 0, 1)
def smooth(u): return u * u * (3 - 2 * u)
def pulse(c, w): return np.exp(-((t - c) / w) ** 2)
def env_ad(c, att, dec):                             # attack/exponential-decay envelope starting at c
    x = t - c
    return np.where(x < 0, np.exp(-(x / att) ** 2) * (x > -4 * att), np.exp(-x / dec))


def osc(freq):                                       # phase-continuous oscillator for a frequency curve
    return 2 * np.pi * np.cumsum(np.broadcast_to(freq, t.shape)) / FS


def additive(freq, n_harm, bright, odd_only=False):
    """band-limited saw/square-ish tone; `bright` (array or scalar) = harmonic roll-off frequency in Hz"""
    ph, out = osc(freq), np.zeros(N)
    for n in range(1, n_harm + 1):
        if odd_only and n % 2 == 0:
            continue
        a = np.exp(-n * np.asarray(freq) / bright) / n
        a = np.where(n * np.asarray(freq) < FS / 2.2, a, 0)
        out += a * np.sin(n * ph + rng.uniform(0, 2 * np.pi))
    return out


# ---- time-varying filtering through a short-time Fourier transform ----
NF, HOP = 2048, 512
WIN = np.hanning(NF + 1)[:-1]
FREQS = np.fft.rfftfreq(NF, 1 / FS)


def stft_filter(x, gain_fn):
    """gain_fn(frame_time, freqs) -> gain per bin. Hann analysis/synthesis, overlap-add, normalised."""
    pad = np.concatenate([np.zeros(NF), x, np.zeros(NF)])
    out, norm = np.zeros_like(pad), np.zeros_like(pad)
    for s in range(0, len(pad) - NF, HOP):
        tc = (s + NF / 2 - NF) / FS
        spec = np.fft.rfft(pad[s:s + NF] * WIN) * gain_fn(tc, FREQS)
        out[s:s + NF] += np.fft.irfft(spec, NF) * WIN
        norm[s:s + NF] += WIN ** 2
    return (out / np.maximum(norm, 1e-6))[NF:NF + N]


def band(fc, q):                                     # gaussian band-pass on a log-frequency axis
    return lambda f: np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) * q) ** 2)


def stereo(mono, pan):                               # equal-power pan, pan in [-1, 1] (array ok)
    a = (np.asarray(pan) + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)])


def reverb(x, secs=3.2, wet=0.35):
    """FFT convolution with a decorrelated, decaying-noise impulse response (a cheap 'cathedral of space')."""
    L = int(secs * FS)
    tt = np.arange(L) / FS
    out = []
    for ch in range(2):
        ir = rng.standard_normal(L) * np.exp(-tt * 6.9 / secs)
        ir = np.convolve(ir, np.ones(8) / 8, 'same')            # soften the top end a little
        ir /= np.sqrt(np.sum(ir ** 2))
        n = 1 << int(np.ceil(np.log2(N + L)))
        y = np.fft.irfft(np.fft.rfft(x[ch], n) * np.fft.rfft(ir, n), n)[:N]
        out.append(y)
    return (1 - wet) * x + wet * np.array(out)


mix = {k: np.zeros((2, N)) for k in ('amb', 'drone', 'tone', 'fx', 'hit')}

# 1) SPACE AMBIENCE: dark wind that opens up as the camera dollies in (0–9 s), never quite silent
fade = smooth(seg(0, 1.5)) * (1 - smooth(seg(T_END + 0.05, DUR)))
open_ = smooth(seg(2, 9.5))
for ch, side in enumerate((-1, 1)):
    w = rng.standard_normal(N)
    mix['amb'][ch] = stft_filter(w, lambda tc, f: (f > 25) * np.exp(-f / (180 + 900 * np.clip((tc - 2) / 7.5, 0, 1)))) * 0.9
mix['amb'] *= fade * (0.55 + 0.45 * open_)

# 2) DRONE in D: sub + fifth + octave, band-limited saws whose "filter" opens with the dot growing into the nine
bright = 120 + 1400 * open_ + 900 * smooth(seg(T_HOPF0, 14)) * (1 - smooth(seg(T_FREEZE, T_SNAP)))
d1 = 36.71 * (1 + 0.002 * np.sin(2 * np.pi * 0.07 * t))
dr = (0.9 * np.sin(osc(d1)) + 0.55 * additive(73.42 * 1.0015, 24, bright) + 0.45 * additive(73.42 * 0.9985, 24, bright)
      + 0.35 * additive(110.0, 18, bright) + 0.18 * additive(146.83, 14, bright * 0.8))
dr *= fade * (0.25 + 0.75 * smooth(seg(0.5, 9))) * (1 - 0.85 * smooth(seg(T_FREEZE, T_SNAP - 0.05))) \
      * (1 - 0.6 * smooth(seg(T_SNAP, T_SNAP + 0.3)) + 0.6 * smooth(seg(T_SNAP + 0.4, 27)))
mix['drone'] += stereo(dr, 0.25 * np.sin(2 * np.pi * 0.05 * t)) * 0.5

# 3) THE DOT: glassy high partials, tremolo, centred — it is the point of light before it is a shape
glass = sum(a * np.sin(osc(f * (1 + 0.0008 * np.sin(2 * np.pi * 0.3 * t + i)))) for i, (f, a) in
            enumerate([(1174.66, 1), (1760.0, 0.6), (2637.0, 0.35), (3951.0, 0.18)]))
glass *= (0.6 + 0.4 * np.sin(2 * np.pi * 5.3 * t)) * smooth(seg(0.8, 4)) * (1 - smooth(seg(9.5, 12.2))) * 0.08 * (0.25 if FUT else 1)
mix['tone'] += stereo(glass, 0)

# 4) LUNGES: a heartbeat thump on every strike peak (the creature leans toward the lens)
for c in STRIKES:
    thump = np.sin(osc(42 + 60 * np.exp(-np.clip(t - c + 0.05, 0, None) / 0.06))) * env_ad(c - 0.05, 0.01, 0.35)
    second = np.sin(osc(40 + 40 * np.exp(-np.clip(t - c - 0.22, 0, None) / 0.05))) * env_ad(c + 0.22, 0.01, 0.3) * 0.6
    mix['hit'] += stereo((thump + second) * (0.45 if c < T_SNAP else 0.25), 0)

# 5) BREATH 9.3–12.3 + reverse swell into the IMAX cut at 12.2 (dead stop on the cut)
sw = np.where(t < T_HOPF0, (np.clip((t - 10.4) / (T_HOPF0 - 10.4), 0, 1)) ** 3, 0)
for ch in range(2):
    mix['fx'][ch] += stft_filter(rng.standard_normal(N),
                                 lambda tc, f: band(400 + 3600 * np.clip((tc - 10.4) / 1.8, 0, 1) ** 2, 1.4)(f)) * sw * 0.9

# 6) THE IMAX CUT (12.2 s): BRAAM — brass-like stacked saws, filter slammed open, sub drop, noise impact
bra_env = env_ad(T_HOPF0, 0.008, 2.2)
bra_b = 6000 * np.exp(-np.clip(t - T_HOPF0, 0, None) / 0.9) + 150
braam = sum(a * additive(f, 40, bra_b) for f, a in [(36.71, 1.0), (73.42, 0.9), (110.0, 0.6), (174.61, 0.35)])
mix['hit'] += stereo(braam * bra_env * 0.55, 0)
sub = np.sin(osc(30 + 70 * np.exp(-np.clip(t - T_HOPF0, 0, None) / 0.25))) * env_ad(T_HOPF0, 0.005, 1.4)
mix['hit'] += stereo(sub * 0.7, 0)
crack = rng.standard_normal((2, N)) * env_ad(T_HOPF0, 0.002, 0.12)
mix['hit'] += crack * 0.35

# 7) HOPF FLOW 12.2–16.4: every point loops its circle once; a chord that circles the stereo field once and
#    inverts (minor -> its mirror) at θ = π, when the nine is its own antipode
th = 2 * np.pi * smooth(seg(T_HOPF0, T_HOPF1))
inv = smooth(np.clip((th - np.pi + 0.4) / 0.8, 0, 1))
chord_a = [293.66, 349.23, 440.0]                    # D F A
chord_b = [293.66, 233.08, 196.0]                    # mirrored about D: D Bb G
hopf = np.zeros(N)
for fa, fb in zip(chord_a, chord_b):
    f = fa * (1 - inv) + fb * inv
    hopf += additive(f, 10, 900) + 0.5 * np.sin(osc(f * 2.003))
hopf *= smooth(seg(T_HOPF0 + 0.2, 13.2)) * (1 - smooth(seg(16.0, 17.2))) * 0.07 * (0.5 if FUT else 1)
mix['tone'] += stereo(hopf, 0.8 * np.sin(th))

# 8) DOUBLE ROTATION 16.4–24.9: two tick trains at 4 Hz and 4/φ Hz — the golden ratio means they never re-align,
#    exactly like the rotation itself; a low pulse underneath, tension climbing
def ticks(rate, t0, t1, f, decay, phase=0):
    out = np.zeros(N)
    k = np.ceil((t0 - phase) * rate)
    while (c := phase + k / rate) < t1:
        i0 = int(c * FS); L = int(decay * 6 * FS)
        seg_t = np.arange(min(L, N - i0)) / FS
        out[i0:i0 + len(seg_t)] += np.sin(2 * np.pi * f * seg_t) * np.exp(-seg_t / decay)
        k += 1
    return out
grow = smooth(seg(16.4, 18)) * (1 - smooth(seg(24.3, T_FREEZE)))
tickA = ticks(4.0, 16.4, T_FREEZE, 3200, 0.012) * (0.5 + 0.5 * smooth(seg(16.4, 24)))
tickB = ticks(4.0 / PHI, 16.4, T_FREEZE, 2140, 0.018, 0.11)
climb = 0.6 + 1.4 * smooth(seg(16.4, T_FREEZE))           # tension builds all the way into the boost
mix['fx'] += stereo(tickA * grow * 0.13 * climb, -0.5) + stereo(tickB * grow * 0.13 * climb, 0.5)
lowp = np.sin(osc(55)) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.0 * t)) ** 4 * grow * 0.25 * climb
mix['drone'] += stereo(lowp, 0)

# 9) CONFORMAL BOOST 21–24.8: everything pours into one point — a Shepard tone (endlessly rising) + riser
shep = np.zeros(N)
rise = np.clip((t - T_BST0) / (T_FREEZE - T_BST0), 0, 1)
for o in range(7):
    oct_pos = (o + 1.6 * rise) % 7                     # each voice climbs 1.6 octaves across the boost
    f = 55 * 2 ** oct_pos
    w = np.exp(-0.5 * ((oct_pos - 3.5) / 1.3) ** 2)    # bell over octaves: voices fade in low, out high
    shep += w * np.sin(osc(f))
shep *= smooth(seg(T_BST0 - 1.5, 22.5)) * (t < T_FREEZE) * (0.4 + 0.6 * rise) * 0.24
mix['tone'] += stereo(shep, 0)
for ch in range(2):
    mix['fx'][ch] += stft_filter(rng.standard_normal(N),
                                 lambda tc, f: band(300 * 2 ** (4.5 * np.clip((tc - 21.5) / 3.4, 0, 1)), 1.1)(f)) \
                     * smooth(seg(20.5, 24.6)) * (t < T_FREEZE) * 0.9

# 10) FREEZE -> SNAP: a vacuum (near silence, 24.9–25.6), a reversed inhale, then THE SNAP at 25.6
inhale = np.where(t < T_SNAP, np.clip((t - 25.05) / (T_SNAP - 25.05), 0, 1) ** 4, 0)
for ch in range(2):
    mix['fx'][ch] += stft_filter(rng.standard_normal(N), lambda tc, f: band(2500, 0.8)(f)) * inhale * 0.7
snap_env = env_ad(T_SNAP, 0.003, 1.8)
snap = (np.sin(osc(28 + 90 * np.exp(-np.clip(t - T_SNAP, 0, None) / 0.18))) * 1.0
        + sum(a * additive(f, 40, 5000 * np.exp(-np.clip(t - T_SNAP, 0, None) / 0.6) + 120)
              for f, a in [(36.71, 0.8), (55.0, 0.6), (73.42, 0.6), (155.56, 0.25)]))   # Eb: a sour edge
mix['hit'] += stereo(snap * snap_env * 0.6, 0) + rng.standard_normal((2, N)) * env_ad(T_SNAP, 0.002, 0.2) * 0.45
metal = sum(np.sin(osc(f)) * env_ad(T_SNAP, 0.002, d) for f, d in [(523, 2.5), (1187, 1.8), (1913, 1.2), (2871, 0.9)])
mix['tone'] += stereo(metal * 0.05, 0)

# 11) "UNKNOWN" BURNS IN (25.35–26.55): crackling embers, sparse and hot
burn = smooth(seg(25.35, 26.0)) * (1 - 0.5 * smooth(seg(27, 29))) * fade
crk = np.zeros((2, N))
idx = np.where(rng.random(N) < 0.0009)[0]
for i in idx:
    L = min(int(0.004 * FS), N - i)
    crk[rng.integers(2), i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (0.0008 * FS)) * rng.uniform(0.2, 1)
mix['fx'] += crk * burn * 0.5

# 12) GLITCH STUTTERS: exactly the 1/9-s slots where the film's spike hash fires (t > 26.5)
for k in range(int(26.5 * 9), int(DUR * 9) + 1):
    if H1(k * 7.7) > 0.86 and k / 9 >= 26.5:
        i0, L = int(k / 9 * FS), int(FS / 9)
        L = min(L, N - i0)
        tt = np.arange(L) / FS
        sq = np.sign(np.sin(2 * np.pi * (180 + 600 * H1(k * 1.3)) * tt))
        sq = np.round(sq * np.sin(2 * np.pi * 37 * tt) * 4) / 4                    # crushed
        g = np.exp(-tt / 0.06) * 0.09
        mix['fx'][:, i0:i0 + L] += np.stack([sq * g, np.roll(sq, 37) * g])

# 13) TITLE SWAP: whoosh across 26.8–27.75 (left -> right, like the nine), hit on 27.75; shimmers for SOON / credit
swp = np.clip((t - T_SWAP0) / (T_SWAP1 - T_SWAP0), 0, 1)
wh = stft_filter(rng.standard_normal(N), lambda tc, f: band(700 + 2600 * np.sin(np.pi * np.clip((tc - T_SWAP0) / 0.95, 0, 1)), 1.2)(f))
mix['fx'] += stereo(wh * np.sin(np.pi * swp) ** 2 * 0.8, -0.9 + 1.8 * swp)
mix['hit'] += stereo(np.sin(osc(34 + 60 * np.exp(-np.clip(t - T_SWAP1, 0, None) / 0.1))) * env_ad(T_SWAP1, 0.003, 0.9) * 0.55, 0)
mix['hit'] += stereo(braam * env_ad(T_SWAP1, 0.005, 1.2) * 0.25, 0)
for c, f0 in [(27.6, 2349.3), (28.5, 1760.0)]:
    sh = sum(np.sin(osc(f0 * m)) * a for m, a in [(1, 1), (1.5, 0.5), (2, 0.3)])
    mix['tone'] += stereo(sh * smooth(seg(c, c + 0.4)) * env_ad(c + 0.4, 0.01, 1.6) * 0.03, 0.3 if c < 28 else -0.3)


# ======================= v8 --future: synthetic, digital, holographic layers =======================
if FUT:
    # SWIRL CLOCK — identical to video.html swirlPhase(): 0.35 -> 7 rev/s, exponential from 16 s, until the freeze
    SW0, SW1, SWR0 = 16.0, 24.0, 0.35
    SWK = np.log(20) / (SW1 - SW0)
    xs = np.clip(t, SW0, T_FREEZE) - SW0
    phi = 2 * np.pi * SWR0 / SWK * (np.exp(SWK * xs) - 1)          # swirl angle (rad) = the reticle's rotation
    rate = SWR0 * np.exp(SWK * xs)                                   # revolutions per second
    act = smooth(seg(15.7, 16.6)) * (1 - smooth(seg(24.1, T_FREEZE)))
    lvl = act * (0.5 + 0.5 * seg(16, 24) ** 0.8)                    # present from the first turn, louder as it speeds up
    front = 0.5 + 0.5 * np.cos(phi)                                  # 1 when the vortex passes in front of us
    # a) air vortex: band noise whose centre climbs with the speed, auto-panned on the swirl angle
    for ch, sgn in enumerate((-1, 1)):
        nz = stft_filter(rng.standard_normal(N),
                         lambda tc, f: band(450 * 2 ** (2.8 * np.clip((tc - 16) / 8, 0, 1)), 1.3)(f))
        g = np.sqrt(0.5 * (1 + sgn * np.sin(phi)))
        mix['fx'][ch] += nz * g * (0.35 + 0.65 * front) * lvl * 1.9
    # b) tonal vortex: detuned saws with a Doppler wobble on every pass; brighter when in front
    dop = 1 + 0.03 * np.minimum(rate / 7, 1) * np.sin(phi)
    vort = sum(a * additive(f * dop, 16, 600 + 2600 * front * (0.4 + 0.6 * seg(16, 24)))
               for f, a in [(110.0, 1.0), (110.6, 0.7), (164.81, 0.55), (220.0, 0.35)])
    mix['tone'] += stereo(vort * lvl * (0.35 + 0.65 * front) * 0.15, 0.85 * np.sin(phi))
    # c) one whoosh per revolution (they blur into a flutter as the rate passes ~4 rev/s)
    rev = np.floor(phi / (2 * np.pi))
    edge = np.where(np.diff(rev, prepend=rev[0]) > 0)[0]
    for i0 in edge:
        tc0 = i0 / FS
        if not (16.2 < tc0 < T_FREEZE):
            continue
        L = min(int(0.25 * FS), N - i0)
        x = np.arange(L) / FS
        burst = rng.standard_normal(L) * np.sin(np.pi * np.clip(x / 0.25, 0, 1)) ** 2
        mix['fx'][:, i0:i0 + L] += np.stack([burst, burst[::-1]]) * 0.06 * lvl[i0]

    # DATA PINGS (1-11 s): FM blips on D minor pentatonic, the point of light "computing" itself
    pent = 1174.66 * 2 ** (np.array([0, 3, 5, 7, 10, 12]) / 12)
    dot_env = smooth(seg(0.8, 4)) * (1 - smooth(seg(9.5, 12.2)))
    for c in np.sort(rng.uniform(0.9, 12.0, 70)):
        i0, L = int(c * FS), int(0.09 * FS)
        x = np.arange(L) / FS
        f = rng.choice(pent)
        e = np.exp(-x / 0.025)
        blip = np.sin(2 * np.pi * f * x + 2.5 * e * np.sin(2 * np.pi * f * 2.01 * x)) * e
        mix['tone'][:, i0:i0 + L] += stereo(blip * 0.11 * dot_env[i0], rng.uniform(-0.7, 0.7))

    # FM GROWL BASS under the drone: a machine breathing
    idx_t = 1.5 + 1.2 * np.sin(2 * np.pi * 0.11 * t) + 2.5 * smooth(seg(16.4, 24.5))
    growl = np.sin(osc(73.42) + idx_t * np.sin(osc(36.71)))
    growl *= fade * smooth(seg(4, 9)) * (1 - 0.9 * smooth(seg(T_FREEZE, T_FREEZE + 0.1))) * (1 - 0.6 * smooth(seg(T_SNAP + 1, 28)))
    mix['drone'] += stereo(growl * 0.35, 0)

    # HOLOGRAM ARPEGGIO over the Hopf flow: 16ths through the (inverting) chord, orbiting with the chord
    step = np.floor((t - T_HOPF0) * 8)
    nidx = np.mod(step, 3).astype(int)
    fa = np.array(chord_a)[nidx] * (1 - inv) + np.array(chord_b)[nidx] * inv
    pl = np.exp(-np.mod(t - T_HOPF0, 0.125) / 0.05)
    arp = (np.sin(osc(fa * 2)) + 0.4 * np.sign(np.sin(osc(fa * 2)))) * pl
    arp *= smooth(seg(T_HOPF0, 12.6)) * (1 - smooth(seg(16.0, 17.0))) * 0.06
    mix['tone'] += stereo(arp, 0.8 * np.sin(th + np.pi / 2))

    # LASER ZIPS on the visual scan sweeps (0.9, 12.2, 25.6 s) + FM metal on the two big hits
    for c, a in [(0.9, 0.5), (T_HOPF0, 1.0), (T_SNAP, 1.0)]:
        x = np.clip(t - c, 0, None)
        zip_ = np.sin(osc(200 + 5200 * np.exp(-x / 0.12))) * env_ad(c, 0.002, 0.3) * (t >= c)
        mix['fx'] += stereo(zip_ * 0.13 * a, 0)
    for c in (T_HOPF0, T_SNAP):
        e = env_ad(c, 0.002, 1.1)
        fm = np.sin(osc(220) + 4 * e * np.sin(osc(220 * 1.414)))
        mix['tone'] += stereo(fm * e * 0.09, 0)

    # DATA SPARKLES as UNKNOWN resolves (replaces most of the ember crackle)
    for c in np.sort(rng.uniform(25.4, 30.6, 90)):
        i0, L = int(c * FS), int(0.02 * FS)
        x = np.arange(L) / FS
        gr = np.sin(2 * np.pi * rng.uniform(6000, 11000) * x) * np.hanning(L)
        mix['tone'][:, i0:i0 + L] += stereo(gr * 0.05 * burn[i0], rng.uniform(-0.9, 0.9))

# 14) FINAL HIT (30.8) and cut to black: everything else ducks out under it
end_mask = 1 - smooth(seg(T_END - 0.05, T_END + 0.02))
for k in ('amb', 'drone', 'tone', 'fx'):
    mix[k] *= end_mask
fin = (np.sin(osc(26 + 120 * np.exp(-np.clip(t - T_END, 0, None) / 0.12))) * 1.1
       + sum(a * additive(f, 40, 7000 * np.exp(-np.clip(t - T_END, 0, None) / 0.5) + 100) for f, a in [(36.71, 1), (73.42, 0.8), (110, 0.5)]))
mix['hit'] += stereo(fin * env_ad(T_END, 0.002, 0.6) * 0.7, 0) + rng.standard_normal((2, N)) * env_ad(T_END, 0.002, 0.15) * 0.4

# ---- mix: stems -> reverb -> glue -> master ----
if '--stems' in sys.argv:                                    # balance report: RMS dBFS per stem per 2-s window
    for k, v in mix.items():
        r = [20 * np.log10(np.sqrt(np.mean(v[:, int(a * FS):int((a + 2) * FS)] ** 2)) + 1e-9) for a in range(0, 31, 2)]
        print(f'{k:6s}', ' '.join(f'{x:6.1f}' for x in r))
# balance from the --stems report: beds ~10 dB under the hits so the cuts land (drone -12 dB, amb -7 dB, tones +5 dB)
bus = (mix['amb'] * 0.4 + mix['drone'] * 0.25 + mix['tone'] * 1.8 + mix['fx'] * 0.9 + mix['hit'] * 1.0)
bus = reverb(bus, 3.4, 0.32)
vac = smooth(seg(T_FREEZE, T_FREEZE + 0.15)) * (1 - smooth(seg(T_SNAP - 0.3, T_SNAP - 0.02)))
bus *= 1 - 0.85 * vac                                        # the vacuum: even the reverb is sucked out before the snap
bus *= np.clip((DUR - t) / 0.12, 0, 1)                       # hard cut to black, 120 ms release
bus /= np.max(np.abs(bus))
bus = np.tanh(bus * 1.2) / np.tanh(1.2)                      # gentle soft-clip glue on the peaks only
bus *= 10 ** (-1.0 / 20) / np.max(np.abs(bus))               # peak -1 dBFS

out = next((a for a in sys.argv[1:] if not a.startswith('--')), 'unknown9-score.wav')
pcm = np.clip(bus.T * (2 ** 23 - 1), -2 ** 23, 2 ** 23 - 1).astype('<i4')
raw = np.frombuffer(pcm.tobytes(), np.uint8).reshape(-1, 4)[:, :3].tobytes()   # 24-bit little-endian
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(3); w.setframerate(FS); w.writeframes(raw)
print(f'wrote {out}: {DUR:.1f} s, {FS} Hz, 24-bit stereo')
