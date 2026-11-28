"""Dialogue edit + original procedural score + sound design for the emotional short."""
import json, sys, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, sosfilt
S = sys.argv[1]; D = f"{S}/short2"; SR = 48000
plan = json.load(open(f"{D}/plan.json")); TAIL = 2.8
TOTAL = round((sum(p["frames"] for p in plan) / 30 + TAIL) * 30) / 30
n = int(round(TOTAL * SR))
rng = np.random.default_rng(7)
# ---------------- dialogue
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f"{S}/aud/sesi_podcast.m4a", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
src = np.frombuffer(raw, np.float32)
AUD = {"H_hook": (1253.32, 1255.72), "M1_wide": (1180.00, 1183.60), "M1_cu": (1183.60, 1189.42), "M2_cu": (1209.42, 1214.50),
       "M2_main": (1214.50, 1220.70), "T1": (1227.10, 1232.00), "T2_alice": (1232.00, 1234.20), "T3": (1234.20, 1237.25),
       "P1_ask": (1255.95, 1261.70), "P2_alice": (1261.70, 1263.30), "P3_yes": (1263.30, 1267.27), "E_end": (1325.75, 1332.20)}
dia = np.zeros(n, np.float32); speech = []
for p in plan:
    if p["name"] not in AUD: continue
    a0, a1 = AUD[p["name"]]; T0 = p["master_T"][0]
    seg = src[int(a0 * SR):int(a1 * SR)].copy(); f = int(0.015 * SR)
    seg *= {'P2_alice': 3.0}.get(p['name'], 1.0)
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
peak0 = TL["P1_ask"]; peak_end = TL["P3_yes"] + 3.97; react = TL["P2_alice"]; endt = TL["E_end"]
ask_t = TL["P1_ask"] + (1260.10 - 1255.95)   # "...apa?"
# hook: single felt-piano dyad + air
put(mus, pad([45, 52], 3.2, att=0.4, rel=1.2, bright=900, amp=0.7), 0.0)
put(mus, piano(64, 3.0, .5), 0.25, 0.8); put(mus, piano(57, 3.0, .35), 0.26, 0.7)
# social-media section: filtered Am pad + soft digital pulse (sine plucks, 0.5 s grid) = the "copied" world
ms0 = TL["M1_wide"]; ms1 = TL["T1"]
put(mus, pad([45, 52, 57, 60], ms1 - ms0 + 0.8, att=1.2, rel=1.5, bright=650, amp=0.8), ms0 - 0.2)
L = int(0.25 * SR); tt = np.arange(L) / SR
for k, t0 in enumerate(np.arange(ms0 + 0.5, ms1 - 0.3, 0.5)):
    m = [69, 76, 72, 76][k % 4]; pl = np.sin(2 * np.pi * hz(m) * tt) * np.exp(-tt * 28) * 0.18
    put(mus, pl, t0, 1.0, pan=0.4 if k % 2 else -0.4)
# turn: warmth arrives - F then C, warm piano
put(mus, pad([41, 48, 57, 60, 64], 5.5, att=1.5, bright=1600, amp=0.9), TL["T1"] - 0.3)
put(mus, pad([36, 43, 52, 55, 60], 5.0, bright=1700, amp=0.9), TL["T3"] - 1.0)
for t0, m, v in [(TL["T1"] + 0.3, 72, .6), (TL["T1"] + 2.4, 71, .5), (TL["T2_alice"] + 0.3, 69, .55), (TL["T3"] + 0.5, 67, .6), (TL["T3"] + 2.2, 64, .5)]:
    put(mus, piano(m, 3.2, v), t0, 0.9, pan=rng.uniform(-.25, .25))
# peak: Am -> (breath on "apa?") -> warm F(add9) swell on Alice's answer -> C on "Betul"
put(mus, pad([45, 52, 57, 60], ask_t - peak0 + 0.4, att=1.0, rel=0.4, bright=1200, amp=0.8), peak0)
put(mus, piano(69, 2.5, .5), peak0 + 0.4, 0.8)
sw = pad([41, 48, 55, 57, 60, 67], TL["P3_yes"] - react + 1.2, att=1.4, rel=0.8, bright=2600, amp=1.25); put(mus, sw, react - 0.25)
put(mus, pad([36, 43, 52, 55, 60, 64], peak_end - TL["P3_yes"] + 1.5, att=1.0, rel=1.2, bright=2600, amp=1.2), TL["P3_yes"] + 0.2)
for t0, m, v in [(react + 0.1, 72, .6), (TL["P3_yes"] + 0.3, 76, .6), (TL["P3_yes"] + 1.9, 74, .5)]:
    put(mus, piano(m, 3.0, v), t0, 0.9)
gate = np.ones(n); a = int((ask_t - 0.2) * SR); b = int((react - 0.3) * SR)
gate[a:b] = np.linspace(1, 0.15, b - a)   # breath of near-silence after "apa?"
mus *= gate
# ending: C major melody, settles on Fadd9 -> C
put(mus, pad([48, 55, 60, 64, 67], TOTAL - endt + 0.2, att=1.0, rel=3.0, bright=1500, amp=0.75), endt)
for t0, m, v in [(endt + 0.3, 72, .55), (endt + 1.8, 74, .45), (endt + 3.2, 76, .5), (endt + 4.9, 72, .5), (endt + 6.6, 67, .4)]:
    put(mus, piano(m, 4.0, v), t0, 0.9)
mus = np.stack([fftconvolve(mus[c], IR[c])[:n] * 0.5 + mus[c] * 0.75 for c in range(2)])
# ---------------- sound design
def noise_band(dur, lo, hi):
    L = int(dur * SR); x = rng.standard_normal(L); return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
room = noise_band(TOTAL, 80, 2500) * 0.0014; put(sfx, np.stack([room, np.roll(room, 997)]), 0)                  # room tone
br = noise_band(1.2, 300, 5000); e = np.sin(np.linspace(0, np.pi, len(br))) ** 2; put(sfx, br * e * 0.04, 0.0)
L = int(0.9 * SR); sw_ = noise_band(0.9, 1500, 9000) * np.sin(np.linspace(0, np.pi, L)) ** 3; put(sfx, sw_ * 0.05, TL["M1_wide"] - 0.45)   # soft whoosh into the "screen" world
L = int(2.0 * SR); rv = noise_band(2.0, 200, 9000) * np.exp(-np.arange(L) / SR * 2.5)
rv = fftconvolve(rv, IR[0])[:L][::-1]; rv /= np.abs(rv).max(); put(sfx, rv * 0.08, TL["T1"] - 1.9)                                   # reverse swell into the turn
L = int(2.2 * SR); tt = np.arange(L) / SR; hit = np.sin(2 * np.pi * (48 * tt + 6 * (1 - np.exp(-tt * 8)))) * np.exp(-tt * 2.4)
put(sfx, hit * 0.16, react - 0.05)                                                                                                    # warm low hit on the answer
wd = noise_band(TOTAL - endt, 150, 1200); wd *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * np.arange(len(wd)) / SR)) * np.linspace(1, 0, len(wd)) ** 0.7
put(sfx, wd * 0.02, endt)
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
