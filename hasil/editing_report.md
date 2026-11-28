# Editing report: Podcast "Romantisisme" (full video)

## Result
| | |
|---|---|
| `final_video.mp4` | **23:46** (1426.47 s, 42,794 frames), 1920×1080 16:9, 30 fps, H.264 High yuv420p BT.709 CRF 22, AAC 192k 48 kHz, faststart. **507 MB** |
| `preview.mp4` | 1:10 highlight reel (title, Dr. Satria's introduction, career, saintis vs sufi, chapter 3, daun, Rabiatul quote, empati, ending). 20.8 MB |
| People | Hosts **Muhammad Hasid** and **Alice Catherine**; guest **Dr. Satria Abadi** (Bogor, Indonesia) |
| Language | Malay, with Indonesian from the guest and some English (lecturer, research, food hunter) |

## Structure (chronological, one continuous production)
| Timeline | Section | Source |
|---|---|---|
| 0:00 | Title "Romantisisme: antara akal dan perasaan", over the intro hook | `intro.m4a` 9.0–33.6 s + IMG_3710 |
| 0:25 | Hosts' self-introductions (name cards) | `pengenalan_diri.m4a` + IMG_3709 |
| 0:43 | **01 Mengenali Tetamu**: background, Bogor, career, childhood dream | `sesi_podcast` + main cam 1 + angles |
| 5:33 | **02 Apa Itu Romantisisme?**: definition, saintis vs sufi, poets | |
| 10:18 | **03 Akal & Perasaan** | main cam 2 |
| 12:01 | **04 Manusia & Alam**: daun keladi, ilmu padi | |
| 14:32 | **05 Berani Menjadi Diri Sendiri**: Rabiatul Adawiyah's verse | |
| 17:03 | **06 Romantisisme Masa Kini**: technology and social media | main cam 2 to 3 |
| 19:46 | **07 Empati**: empati, simpati, belas kasihan | main cam 3 |
| 22:23 | **08 Penutup**: gift (buah tangan), thanks, salam | |
| 23:42 | End card with credits | |

The two section breaks (intro to self-introductions, self-introductions to session) are 0.35–0.4 s dips to black. Inside the session, every cut is a straight cut onto a different camera.

## What was removed (session time)
| Removed | Reason |
|---|---|
| 10:04.5–11:02.0 | Alice's fumbled first attempt and restart ("okey tak apa start dulu") |
| 12:46.3–13:25.2 | Off-script chatter between questions |
| 18:45.3–19:15.2 | Host restarting the last question twice |
| 22:13.3–22:49.5 | False ending, then off-mic crew chatter (transcribed to confirm it wasn't a question) |
| 25:31.7–25:42.3 | Off-topic chatter |
| 31 pauses over 1.4 s | Shortened to about 0.5 s. Each tightened pause lands on a camera change, so there are no jump cuts |
| `briefing.m4a`, `briefing_2.m4a`, IMG_3713–3715, 3716, 3719 | Behind-the-scenes briefings, false start and pre-roll |

**Kept:** all of the guest's answers, the hosts' questions, and the natural banter ("Pernah dengar tak?", "food hunter", the gift exchange), because they carry the personality of the conversation.

## Camera editing
- **Primary camera:** main wide shot (IMG_2836 in 3 files). It also gives three **virtual close-ups**: 4K crops at full 1080p sharpness, framed on detected faces with room in the direction each person is looking:
  - CU_D, Dr. Satria at 38% across the frame.
  - CU_H, Hasid at 62%.
  - CU_A, Alice at 62%.
- **Angles:** 18 iPhone clips, all synced to the audio (`camera_analysis.json`).
- **Shot counts (235 shots):** CU_D 63, WIDE 59, CU_H 35, CU_A 10, angles 64, black 4.
- **Rules:**
  - The camera follows the speaker, cutting 3 frames (0.1 s) before the new speaker starts.
  - Turns under 2 s (backchannels like "betul", "ya") don't trigger a cut.
  - Minimum shot length is 2 s, with a typical rhythm of 5–9 s.
  - The same view never appears twice in a row, and a wide shot returns about every 5 shots for context.
- **Chapter starts:** each chapter opens on an **establishing wide shot**, so the chapter title sits over the empty ceiling.
- **Reaction shots:** during long answers from the doctor (over 25 s), there are periodic 2.6 s reaction shots of Hasid or Alice listening.
- **Shots chosen around graphics:** while a diagram is on screen, only shots with the doctor in the left or centre of the frame are used. That keeps the right third free for the graphic.
- **main3's sync step:** handled as two separate sync regions, so the step can't cause lip-sync errors.

## Zoom and camera movement
Zooms come in four kinds, in rotation:
- Push-in (1.0 → 1.07–1.12).
- Pull-out (1.10–1.12 → 1.0).
- Static punch-in (1.15–1.18, on 4K angles and the wide shot).
- Static.

They're spread evenly: 93 static shots, 78 push-ins, 56 pull-outs, 23 punch-ins. Moves use cosine easing over the full length of the shot. Close-up zooms never go beyond the source's real resolution, and the scaling is sub-pixel (bicubic warpAffine), so there's no stepping or jitter.

## Motion graphics (one design system)
One font (Inter), one accent color (amber #F2B64F), dark translucent panels with an accent bar, and matching entrance motion everywhere (30 px slide, 350–450 ms fade).

| Element | Purpose |
|---|---|
| Title sequence | Kicker, title, an animated line, slow scale and floating particles over a darkened intro shot |
| **Chapter tag + progress bar** (top left, the whole session) | Shows the current chapter and how far through the video you are (animated fill) |
| **8 chapter cards** | "BAB 0X" plus the title, a line that draws in, particles and a soft top gradient, over the establishing wide shot |
| Name cards | Alice, Hasid (self-introduction section), Dr. Satria (when he first speaks) |
| **Context graphics (17)** in the empty space on the right | |
| Card | Asal: Bogor, Indonesia (map-pin icon) |
| Timeline built step by step | Perjalanan kerjaya: 2004 pensyarah, then PhD, then pascadoktoral (Finland · Brunei · Malaysia), then pensyarah di Malaysia |
| Card | Cita-cita: menjadi pendidik (book icon) |
| Quote card | "Tiada batasan untuk mengejar cita-cita." |
| Card | Romantisisme = luapan perasaan dari dalam diri (heart icon) |
| Comparison | Saintis (alam seperti mesin) vs Sufi/Romantis (alam dirasai dengan jiwa) |
| List built step by step | Penyair: Jalaluddin Ar-Rumi, Rabiatul Adawiyah, Hamka |
| Comparison | Keseimbangan: Akal vs Perasaan (balance-scale and heart icons) |
| Comparison | Melihat daun yang gugur: Saintis (fotosintesis) vs Romantis |
| Card | Pepatah: "Seperti air di daun keladi" (leaf icon) |
| Comparison | Berani menjadi diri sendiri: pendirian sendiri vs aturan masyarakat |
| List + quote card | Meluahkan rasa melalui karya; Rabiatul Adawiyah's verse |
| Comparison | Romantis di era teknologi: media sosial (meniru) vs luapan emosi sendiri |
| Cards | Romantis melalui perbuatan; tak perlu selalu berpuisi |
| List built step by step | Tiga rasa: Empati, Belas kasihan, Simpati |
| Card | Buah tangan (gift icon) |
| End card | "Terima kasih" plus guest and host credits |
| Subtle background motion | Slow-drifting amber particles under each card, and lines that draw in. Kept low-opacity so they don't distract |
| Vignette | Subtle, cinematic (angle 0.42) |

Each graphic appears when its topic is being discussed and comes from the actual transcript. Transparent PNG renders of each graphic are in `assets/generated_graphics/`.

## Subtitles
Whisper large-v3 text with medium-model timing, checked against the audio. 487 lines, 421 corrected by hand. See `subtitle_verification_report.md`.
- **Style:** Inter SemiBold 50, bottom centre, soft blurred outline, phrase fade with a 6 px rise, about 35 keywords highlighted in amber.

## Color
Main camera HDR (HLG) is converted to SDR, then each of the 21 cameras gets its own 3D LUT (white balance from skin and neutral surfaces, exposure matched on faces), then one shared warm, natural look with skin protection. See `color_grading_report.md` and `color_check.jpg`.

## Audio
- **Source:** the separate recorder audio is the master track for all 39 segments, joined with 12 ms fades.
- **Chain:** high-pass 80 Hz; -2 dB at 300 Hz (less boxiness); +1.5 dB at 3.5 kHz (clarity); light noise reduction (afftdn); compression 2.5:1; true-peak limiter.
- **Result:** -14.1 LUFS integrated, -1.3 dB peak, LRA 5.9 LU. No clipping.
- **Sync:** audio advanced 33 ms to compensate for the encoder. See `audio_sync_report.json`.

## Quality checks (final render)
| Check | Result |
|---|---|
| Plays / decodes (`ffmpeg -v error`) | No errors |
| Streams | 1 video (1920×1080 16:9, 30 fps, 42,794 frames) + 1 audio (48 kHz). The first encode accidentally had 4 streams; fixed by remuxing |
| Duration | 1426.467 s, the same as the timeline |
| Black frames | Only the intended ones: 0–0.7 s (fade-in), 24.6 s and 42.8 s (section breaks, 0.4 s), 1421.7 s to the end (end card) |
| Frozen frames | Only the static end card (1423 s onward) |
| Silence (-50 dB, 1.5 s) | Natural 1.55 s pause at 6:02, end card |
| Loudness | -14.1 LUFS, -1.3 dB peak |
| Lip sync, 8 points (0:00–23:28, every main file plus angles) | -21 to +7 ms; **max 21 ms**, under one frame |
| Visual stills | 16 key moments, 3 cut pairs, 33 camera/view combinations. Graphics stay clear of faces, subtitles are readable, chapter titles sit over the ceiling, grading is consistent |
| Issues found and fixed during QC | Chapter tag too faint (dark pill added); progress bar wider than its pill (minimum width); a made-up word on a diagram ("setuju") removed; large-v3 timestamps up to 1.2 s early (aligned to medium timing); cut points corrected so they no longer clip words ("tanpa", "Okey Dr", "Apakah"); 4 shots under 2 s merged; first encode had 4 streams (remuxed) |

## Files in `hasil/`
`final_video.mp4`, `preview.mp4`, `subtitles.srt`, `subtitles.ass`, `transcript.txt`, `editing_report.md`, `editing_timeline.json`, `camera_analysis.json`, `audio_sync_report.json`, `subtitle_verification_report.md`, `color_grading_report.md`, `color_check.jpg`, `assets/generated_graphics/` (19 PNGs).

Source footage and audio were never modified. They're kept outside the repo, in the session's working folder (downloaded from Google Drive).
