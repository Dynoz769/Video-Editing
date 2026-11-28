"""Dialogue edit + original procedural score + sound design for the emotional short."""
import json, sys, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, sosfilt
S = sys.argv[1]; D = f"{S}/short"; SR = 48000
plan = json.load(open(f"{D}/plan.json")); TAIL = 2.5
TOTAL = round((sum(p["frames"] for p in plan) / 30 + TAIL) * 30) / 30
n = int(round(TOTAL * SR))
rng = np.random.default_rng(7)
# ---------------- dialogue
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f"{S}/aud/sesi_podcast.m4a", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
src = np.frombuffer(raw, np.float32)
AUD = {"A_hook": (1066.30, 1070.12), "B1_ctx": (1047.55, 1049.95), "B2_ctx": (1051.70, 1056.33), "B3_env": (1056.33, 1059.85),
       "C1_verse": (1070.40, 1074.30), "C2_verse": (1074.30, 1076.95), "D_peak": (1081.15, 1088.10), "E_react": (1088.12, 1089.58)}
dia = np.zeros(n, np.float32); speech = []
for p in plan:
    if p["name"] not in AUD: continue
    a0, a1 = AUD[p["name"]]; T0 = p["master_T"][0]
    seg = src[int(a0 * SR):int(a1 * SR)].copy(); f = int(0.015 * SR)
    seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    st = int((p["tl"] + a0 - T0) * SR); dia[st:st + len(seg)] += seg
    speech.append((p["tl"] + a0 - T0, p["tl"] + a1 - T0))
wavfile.write(f"{D}/dia_raw.wav", SR, dia)
# dialogue chain (same as full edit) + loudness handled at the end
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{D}/dia_raw.wav", "-af",
                "volume=-8dB,highpass=f=80,equalizer=f=300:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=1.5,lowpass=f=16000,"
                "afftdn=nr=8:nf=-42:tn=1,acompressor=threshold=-24dB:ratio=2.5:attack=10:release=200:makeup=3dB:knee=4",
                "-c:a", "pcm_f32le", f"{D}/dia.wav"], check=True)
dia = wavfile.read(f"{D}/dia.wav")[1].astype(np.float32)[:n]
dia = np.pad(dia, (0, n - len(dia)))
# ---------------- instruments
t_all = np.arange(n) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def ir(sec=3.2, damp=6000):
    L = int(sec * SR); e = np.exp(-np.arange(L) / SR * 6.5 / sec)
    x = rng.standard_normal((2, L)) * e
    return sosfilt(butter(2, damp, 'low', fs=SR, output='sos'), x)
IR = ir()
def piano(m, dur=3.5, vel=1.0):
    L = int(dur * SR); t = np.arange(L) / SR; f0 = hz(m); y = np.zeros(L)
    for k, a in enumerate([1, .45, .22, .12, .07, .04], 1):
        fk = f0 * k * np.sqrt(1 + 0.0004 * k * k)
        y += a * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.1 + 0.9 * k))
    att = np.minimum(1, t / 0.006); y *= att * vel
    y += 0.02 * vel * rng.standard_normal(L) * np.exp(-t * 60)  # hammer
    return y
def pad(ms, dur, att=1.8, rel=2.2, bright=1800, amp=1.0):
    L = int(dur * SR); t = np.arange(L) / SR; y = np.zeros((2, L))
    for m in ms:
        for ch, det in ((0, -0.08), (1, 0.08)):
            for d in (-det, 0, det):
                f = hz(m + d * 0.1)
                y[ch] += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    y = sosfilt(butter(2, bright, 'low', fs=SR, output='sos'), y)
    env = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel).clip(0, 1)
    return y * env * amp / (len(ms) * 3)
mus = np.zeros((2, n)); sfx = np.zeros((2, n))
def put(buf, x, at, gain=1.0, pan=0.0):
    st = int(at * SR)
    if st >= n: return
    if x.ndim == 1: x = np.stack([x * (1 - pan) ** 0.5, x * (1 + pan) ** 0.5]) / 1.2
    L = min(x.shape[1], n - st); buf[:, st:st + L] += gain * x[:, :L]
TL = {p["name"]: p["tl"] for p in plan}
peak0 = TL["D_peak"]; peak_end = TL["D_peak"] + (1088.10 - 1080.85); react = TL["E_react"]; endt = TL["F_end"]
# score: D minor, i - VI - III - VII ; drone under the hook
put(mus, pad([38, 45], 5.0, att=0.6, rel=1.5, bright=700, amp=0.9), 0.0)                       # D2 A2 drone
put(mus, pad([50, 53, 57, 64], 6.0, bright=1400, amp=0.8), TL["B1_ctx"] - 0.4)                  # Dm(add9)
put(mus, pad([46, 50, 53, 57], 5.5, bright=1500, amp=0.8), TL["B3_env"] - 0.6)                  # Bbmaj7
put(mus, pad([41, 48, 53, 57], 4.5, bright=1700, amp=0.9), TL["C1_verse"] - 0.3)               # F
put(mus, pad([36, 43, 52, 55], 3.6, bright=1700, amp=0.9), TL["C2_verse"] - 0.2)               # C/E
for t0, m, v in [(TL["B1_ctx"] + 0.2, 69, .8), (TL["B1_ctx"] + 1.7, 65, .6), (TL["B2_ctx"] + 0.9, 67, .7), (TL["B2_ctx"] + 2.8, 64, .55),
                 (TL["B3_env"] + 0.4, 62, .6), (TL["B3_env"] + 2.2, 65, .55), (TL["C1_verse"] + 0.3, 69, .7), (TL["C1_verse"] + 2.0, 72, .6),
                 (TL["C2_verse"] + 0.4, 67, .6), (TL["C2_verse"] + 1.9, 64, .55)]:
    put(mus, piano(m, 3.5, v), t0, 0.9, pan=rng.uniform(-.3, .3))
# peak: warm strings-like swell Bb -> Dm, piano thins out, then music stops on "rinduku ini"
sw = pad([46, 53, 58, 62, 65], peak_end - peak0 + 1.2, att=3.5, rel=1.0, bright=2400, amp=1.3)
put(mus, sw, peak0 - 0.2)
for t0, m, v in [(peak0 + 1.9, 74, .55), (peak0 + 4.6, 72, .5)]:
    put(mus, piano(m, 3.0, v), t0, 0.8)
gate = np.ones(n); a = int((peak_end - 0.05) * SR); b = int((peak_end + 0.35) * SR)
gate[a:b] = np.linspace(1, 0, b - a); gate[b:] = 0
mus *= gate
# ending: single piano note + soft pad, fading out into the black card
put(mus, pad([50, 57, 64, 69], TOTAL - endt + 0.2, att=1.2, rel=2.5, bright=1200, amp=0.7), endt)
put(mus, piano(74, 4.5, .65), endt + 0.35, 1.0); put(mus, piano(62, 5.0, .45), endt + 0.36, 0.8)
mus = np.stack([fftconvolve(mus[c], IR[c])[:n] * 0.55 + mus[c] * 0.7 for c in range(2)])
# ---------------- sound design
def noise_band(dur, lo, hi):
    L = int(dur * SR); x = rng.standard_normal(L); return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
room = noise_band(TOTAL, 80, 2500) * 0.0014; put(sfx, np.stack([room, np.roll(room, 997)]), 0)                  # room tone
br = noise_band(1.4, 300, 5000); e = np.sin(np.linspace(0, np.pi, len(br))) ** 2; put(sfx, br * e * 0.05, 0.0)   # breath swell at the hook
L = int(2.0 * SR); rv = noise_band(2.0, 200, 9000) * np.exp(-np.arange(L) / SR * 2.5)
rv = fftconvolve(rv, IR[0])[:L][::-1]; rv /= np.abs(rv).max(); put(sfx, rv * 0.10, peak0 - 1.9)            # reverse swell into the peak
L = int(2.2 * SR); tt = np.arange(L) / SR; hit = np.sin(2 * np.pi * (44 * tt + 6 * (1 - np.exp(-tt * 8)))) * np.exp(-tt * 2.2)
put(sfx, hit * 0.22, peak0 + 0.25)                                                                    # low cinematic hit
wd = noise_band(TOTAL - endt, 150, 1200); wd *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * np.arange(len(wd)) / SR)) * np.linspace(1, 0, len(wd)) ** 0.7
put(sfx, wd * 0.025, endt)                                                                             # soft wind at the ending
# ---------------- ducking (music sits ~18 dB under speech, rises in gaps)
env = np.zeros(n)
for a, b in speech: env[int(a * SR):int(b * SR)] = 1
k = int(0.25 * SR); env = np.convolve(env, np.ones(k) / k, mode="same")
duck = 1 - 0.55 * env
rms = np.sqrt((mus[:, mus.any(0)] ** 2).mean()); mus = mus / rms * 0.018
wavfile.write(f"{D}/mus_only.wav", SR, (mus.T).astype(np.float32)); wavfile.write(f"{D}/sfx_only.wav", SR, (sfx.T).astype(np.float32))
mix_m = mus * duck + sfx
wavfile.write(f"{D}/music_sfx.wav", SR, (mix_m.T).astype(np.float32))
mix = np.stack([dia, dia]) * 1.0 + mix_m
wavfile.write(f"{D}/mix_pre.wav", SR, (mix.T).astype(np.float32))
json.dump(dict(total=TOTAL, speech=speech, peak=[peak0, peak_end], react=react, end=endt), open(f"{D}/audio_meta.json", "w"), indent=1)
print("total", TOTAL)
