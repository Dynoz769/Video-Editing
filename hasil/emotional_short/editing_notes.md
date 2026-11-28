# "Jangan Kau tolak rinduku": emotional short

**Final:** `final/emotional_podcast_final.mp4`. 36.3 s, 1080×1920 (9:16), 30 fps (same as the source), H.264 High CRF 18, AAC 192k 48 kHz, 49 MB. Made for TikTok, Reels and Shorts.

## 1. Analysis
| Question | Answer |
|---|---|
| Main topic | Pure love and longing, as expressed by the sufi poet Rabiatul Adawiyah and recited by Dr. Satria Abadi |
| Deepest message | True love wants nothing in return, neither reward (heaven) nor escape (hell); it only asks that the longing not be rejected |
| Most powerful sentence | "Tetapi kalau jiwa ini ada rindu kepada-Mu, ya Tuhan… maka jangan Kau tolak rinduku ini." |
| Emotions | Curiosity, then reverence, then a quiet ache of longing (*rindu*), then reflection |
| Progression | A provocative hook, who she was, the verse building up, the peak, a silence, a human reaction, an ending that lingers |
| Palette | **Nostalgic and devotional**: warm amber highlights, muted saturation (0.80, skin 0.92), soft deeper shadows, highlight roll-off, grain. Sadness-blue and teal were rejected as wrong for this topic |
| Motion | A serif kinetic verse revealed word by word as it's spoken, amber glow on syurga / neraka / cintai / jiwa / rindu / Tuhan, light leaks, haze, drifting dust |
| Music | Original D-minor piano and pads (i–VI–III–VII), composed in code. No third-party music |
| Where it slows down | The peak: one long, tight take with a slow push-in, darker exposure and a stronger vignette, plus a golden light rising on "rindu" |
| Ending | The music cuts out on "rinduku ini", 0.5 s of silence, Alice: "Itu dahsyat sekali.", the doctor's smile in slow motion fades to black, the final line in serif |

## 2. Story (output time, then source session time)
| Time | Beat | Dialogue (sesi_podcast) | Shot |
|---|---|---|---|
| 0.0–4.2 | **Hook** | "Seandainya syurga itu untukku, saya tidak perlukan syurga itu." (1066.3–1070.1) | Angle 3734, tight close-up, fade up from black, push-in 1.00 to 1.08 |
| 4.2–14.8 | **Development** | "Rabiatul Adawiyah yang saya ceritakan itu, orang menganggap dia seperti orang yang tidak punya apa, yang bertentangan dengan agama, tapi luapan perasaan itu…" (1047.6–1059.9, "dia, dia" stutter removed) | Main cam medium, then 3734 pull-out, then a wide "environment" frame. Title card: Rabiatul Adawiyah, penyair sufi · Basrah, abad ke-8 |
| 14.8–21.4 | Verse | "Berikan saja syurga itu kepada orang yang Kau cintai. Kalau neraka itu untukku, saya tak perlu neraka itu." (1070.4–1076.9) | 3734 slow pull-out, then main cam |
| 21.4–28.9 | **Emotional peak** | "Tetapi kalau jiwa ini ada rindu kepada-Mu, ya Tuhan, kata dia, maka jangan Kau tolak rinduku ini." (1081.2–1088.1) | 3734 tight, one long take, push-in 1.00 to 1.11, exposure ×0.88, strong vignette, rising golden light |
| 28.9–29.1 | Silence | No dialogue, just room tone | Holds on the doctor |
| 29.1–30.6 | Human response | Alice: "Itu dahsyat sekali." (1088.1–1089.6) | Main cam on Alice |
| 30.6–33.8 | **Final impact** | No dialogue: piano note and wind | The doctor's smile in 0.5× slow motion (frame-blended), fading to black |
| 33.8–36.3 | Lingering line | Text: "…maka jangan Kau tolak rinduku ini." Rabiatul Adawiyah, as recited by Dr. Satria Abadi | Black |

Left out: "Kata dia kan, neraka itu diberikan kepada orang yang…" (an unfinished sentence), and everything else in the conversation.

## 3. Picture
- **Crops:** 9:16 crops from the 4K sources, framed on detected faces with the face in the upper third. Scaling is 1.13–1.35× from 4K, which is still sharp.
- **Camera motion:** each shot has an eased push-in or pull-out plus a small drift; no shake.
- **Color:** each camera's own correction LUT (from the full edit), then the `rindu.cube` look, a per-shot exposure setting and a vignette. Then light leaks and dust (screen blend) and film grain (`noise=alls=6`).
- **Overlays:** `assets/overlays/light_leak_dust_haze.mp4`, generated procedurally:
  - a warm sweep on the hook;
  - a memory flare on the context;
  - haze from the top;
  - a side glow on the verse;
  - a golden light rising on "rindu";
  - warmth at the ending;
  - 60 drifting dust specks throughout.

## 4. Typography and subtitles
- **Verse (the poem):** Cormorant Garamond Medium Italic, 96 px. Each row is revealed word by word at the moment it's spoken (alpha fade 320 ms plus a 10 px rise). Keywords are amber with a soft glow, and "rindu" / "rinduku" grow slowly to 107%.
- **Narration and reaction:** Inter SemiBold 48, white, soft outline, "luapan perasaan" in amber.
- **Placement:** text sits in the lower-middle area (y 1268–1452). That keeps it clear of the face (upper third) and of the platform's interface at the bottom (bottom 400 px are kept clear). A soft dark gradient sits behind the text area.
- **Timing:** words come from the verified full-edit transcript (Whisper large-v3 text on medium-model timestamps checked against the audio). `subtitles/subtitles.srt` contains only the spoken lines.

## 5. Sound
- **Dialogue:** the separate recorder audio; 80 Hz high-pass, EQ (-2 dB at 300 Hz, +1.5 dB at 3.5 kHz), light noise reduction, 2.5:1 compression.
- **Score** (`assets/music/original_score_rindu.wav`, original, generated):
  - a D2/A2 drone under the hook;
  - Dm(add9) and Bbmaj7 pads with sparse reverb piano for the context;
  - F and C/E for the verse;
  - a strings-like Bb swell at the peak, which **stops dead** on "rinduku ini";
  - a single D5 piano note over a Dm(add9) pad at the ending.
- **Sound design** (`assets/sound_effects/sound_design.wav`): room tone, a breath swell at 0 s, a reverse swell into the peak, a low hit (44 Hz) at the peak, soft wind on the fade-out.
- **Mix:** music ducks about 17 dB under speech and comes up in the gaps. Final level -13.8 LUFS, -1.5 dB true peak, LRA 5.8; no clipping.

## 6. Quality checks
| Check | Result |
|---|---|
| Duration | 36.3 s (limit 60 s) |
| Format | 1080×1920, 30 fps, 1,089 frames, H.264 + AAC; decodes with no errors |
| Lip sync (7 dialogue shots) | -10.1 to +4.5 ms (under 1 frame) |
| Black frames | Only the closing card (34.6 s to the end) |
| Loudness | -13.8 LUFS, -1.5 dB true peak |
| Visual stills (10 moments, plus the closing card) | Faces framed, text readable over the batik shirt (thanks to the gradient), no text on faces, consistent warm grade |
| Fixed during review | Face drifting out of frame at the end of the hook, peak and ending (crops re-centred on detected faces); a hand across the face at the end of the peak (silence shortened 1.0 to 0.5 s); music too loud (normalised); wide word gaps (switched to one event per row); a blurred last word on the closing card (blur reset) |

## Files
- **`final/`:** the finished video.
- **`previews/`:** a 540×960 preview.
- **`subtitles/`:** `subtitles.srt` and `short.ass` (styled).
- **`assets/`:** music, sound design, the overlay layer, motion-graphic stills.
- **`project/editing_files/`:** every script, the look LUT and the shot plan, so the edit can be rebuilt.

Source footage and audio were not modified.
