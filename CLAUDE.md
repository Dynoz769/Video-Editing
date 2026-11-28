# Video Editing Workflow

This file tells Claude how to edit the videos in this repo. Read it before starting any edit.

## Quick start: user sends only a link
The user (writes in Malay; reply in Malay) will often send just a Google Drive link (a file or a folder), maybe with no other words. Do this:

1. **Download straight away.**
   - List the folder with the Google Drive connector (`search_files` with `'<folderId>' in ancestors`).
   - Fetch each file with `curl -L "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"` into the scratchpad `dl/`, never into the repo.
   - This needs the `video-editing` cloud environment (it allows Drive, Hugging Face and fonts).
2. **Inspect:**
   - `ffprobe` every file;
   - a contact sheet of thumbnails;
   - audio files vs camera files; HDR (HLG) or SDR;
   - a quick transcript to learn the topic and speakers.
3. **Propose templates from `TEMPLATES.md`, then ask once.**
   - The catalogue has codes: A (full edits), B (vertical shorts), C (trailers), D (events), E (education), F (promo), G (extras).
   - After inspecting, write a short menu in chat. Give 3–4 recommended template codes that fit this footage, each with one line on why, and for shorts the actual moment and hook line from the transcript.
   - Then use AskUserQuestion (max 4 questions, in Malay, recommended first). Typically:
     - which template(s) (multiSelect);
     - which moment or topic for the shorts;
     - colour or music overrides, if relevant;
     - whether more files are coming, and whether the speaker names are right.
   - The user can also reply with codes in free text (e.g. `A1 + B1 + B4`) or "pilih sendiri" (you choose).
4. **Then edit straight through without stopping:**
   1. Sync.
   2. Transcript.
   3. Timeline.
   4. Grade.
   5. Graphics.
   6. Audio.
   7. Render.
   8. Quality checks.
   9. Save to `hasil/<project>/`.
   10. Send the video in chat (if over the upload limit, send a smaller copy).
5. Report briefly in Malay. Push only when the user says "push".

## Reusable tools (`tools/`)
- **`tools/full_edit/`:**
  - `sync.py` (audio cross-correlation);
  - `transcribe*.py` (faster-whisper; medium for timing, large-v3 for text);
  - `faces.py` + `mklut.py` (face-based per-camera 3D LUTs);
  - `build_full.py` (timeline, speaker turns, shot planner, ASS motion graphics, subtitles);
  - `reframe.py` (face-tracked crops);
  - `render_shots.py` (shot renderer with sub-pixel zooms);
  - `tm.txt` (the HLG to SDR conversion filter).
- **`tools/emotional_short/`:** 9:16 renderer with per-shot tint and saturation, procedural music and sound design (`make_audio*.py`), light-leak and dust overlay (`make_leak*.py`), kinetic typography (`make_ass*.py`), look LUT (`mk_look.py`).
- These were written for the "Romantisisme" project. Adapt the paths, shot lists and word times; don't rebuild from scratch.

## Motion graphics: HyperFrames is the default (user's choice)
For every new edit, build titles, kinetic text, captions, cards, diagrams and overlays as a **HyperFrames** composition (HTML + GSAP rendered to MP4). Don't use ASS for new work. The ASS scripts in `tools/` are the fallback, and are kept only for the existing videos.

- **Install:**
  - In the scratchpad: `npm init -y && npm install hyperframes@0.9.40 gsap@3.12.5`.
  - Pin a version at least 2 weeks old: the package releases several times a day.
  - Requires Node ≥ 22 (installed); Chrome and FFmpeg are present.
- **Privacy:**
  - Always `export DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1`.
  - Never run the docs' "usage beacon" (`npx hyperframes events`), `auth`, `share` or `publish`.
- **GSAP:** CDNs are blocked here. Copy `node_modules/gsap/dist/gsap.min.js` to the project's `assets/` and load `assets/gsap.min.js`.
- **Pipeline:**
  1. Cut, grade and reframe the footage with the Python/ffmpeg tools, producing a joined, graded `assets/*.mp4`.
  2. Build `index.html`: a muted `<video class="clip">` plus GSAP graphics. Start from `tools/hyperframes/template_vertical.html`; for 16:9 use 1920×1080.
  3. Run `npx hyperframes render -o out.mp4 -f 30 --quiet`.
  4. Mux the processed audio in with ffmpeg. Or use `<audio id=… data-volume>` in the composition.
  - Graphics-only alternative: `--format mov` (ProRes 4444 with alpha), then overlay with ffmpeg.
- **Rules from its docs:**
  - Every timed element has `class="clip"`, `data-start` and `data-duration`.
  - Build one paused timeline and register it as `window.__timelines["<composition-id>"] = tl`.
  - Use `fromTo`, not `from`. Don't use `Math.random()` or timers.
  - Animate children of a `.clip`, not the clip itself.
  - Fonts: Inter, Montserrat, EB Garamond and Playfair Display are bundled; other fonts need `@font-face` from `assets/fonts/`.
  - Before rendering, run `npx hyperframes lint .` (or `check --json`).
  - Full reference: `node_modules/hyperframes/dist/skills/hyperframes/` (SKILL.md, references/format.md, captions.md, overlays.md, motion.md, types/vertical.md).
- **Speed:** about 11 frames per second for 1080p graphics (software WebGL, CPU only). A 300 s chunk takes about 14 minutes.
- **Long videos (over about 1 minute): use this proven pipeline, not a `<video>` inside the composition.**
  - HyperFrames extracts every video frame into a plan directory with a 2 GB cap; 23 minutes came to 8.5 GB, so the render failed.
  - The container can restart mid-render; that killed a 56-minute single render.
  - Instead:
    1. Make the composition graphics-only on a transparent background (`tools/hyperframes/gen_full.py`).
    2. Split it into 300 s chunks (`mk_chunks.py`: shifts clip timing and drives the master timeline with `tweenFromTo`).
    3. Render each chunk as `--format webm` (VP9 with alpha). Skip chunks that are already done.
    4. Join them in ffmpeg with `-c:v libvpx-vp9 -f concat` and `overlay` them on the graded base video.
- **Lint:** don't tween `letterSpacing` (lint error `gsap_non_transform_motion`); use opacity, y and blur.

## Setup and lessons learned (save credits: don't rediscover these)
- **Install:**
  - `pip install faster-whisper scipy librosa scikit-learn "opencv-python-headless<5"`. OpenCV 5 has no Haar cascades.
  - Load audio with scipy, not PyAV: faster-whisper's decoder breaks.
- **Hugging Face downloads** need these hosts: huggingface.co, cas-bridge.xethub.hf.co, cas-server.xethub.hf.co, us.aws.cdn.hf.co, cdn-lfs-us-1.hf.co.
- **Transcription:**
  - large-v3 has the better words but its timestamps run up to 1.2 s early. Align its text onto medium's word times (difflib), and check cut points against the audio energy.
  - Force `language="ms"`.
- **iPhone HLG:** `zscale npl=203` then `tonemap=hable:desat=2`. Mobius looks washed out and pink.
- **Sync:**
  - The master is the separate recorder audio.
  - Check several windows per clip: a recording can have a step of about 50 ms.
  - Small timing drifts in AAC are normal; shift the final audio by -33 ms and verify by cross-correlation.
- **ffmpeg:**
  - Use `-nostdin` inside `while read` loops.
  - Put `-passlogfile` before the output.
  - Don't combine `-map 0:v` with `-map "[v]"` (it doubles the streams).
  - Don't use `trim` on a long video (out of memory); seek with `-ss` per segment.
- **libass:**
  - Override tags carry over to the following words, so reset `\blur` and `\bord` on each word.
  - For word-by-word reveals, use one event per row with `\alpha` + `\t`, not absolute word positions.
- **Fonts:** Cormorant Garamond from the Google Fonts CSS API with an old-Safari user agent (gives WOFF, which works). Inter is installed.
- **Memory:** stream frames (Popen) and never hold a whole shot in memory.
- **Git LFS:** pushing needs the `lfs.github.com` host. The free quota is 1 GB storage; about 820 MB is already used.

## Input
- Raw media goes in these folders:
  - `raw/camera/`: the camera angles. `cam1` is the main camera.
  - `raw/audio/`: the separated audio.
  - `raw/music/`: optional background music.
  - `raw/assets/`: logos and fonts, plus `speakers.txt` for the speaker names.
- Naming rules are in `README.md`.
- Large files are stored with Git LFS. If `raw/` is empty or missing, stop and ask the user where the media is. Never use placeholder or invented footage.
- If the user gives a Google Drive folder or a direct URL instead, download the files into `raw/`.

## Output
- Save every deliverable in `hasil/`:
  - `final.mp4`: H.264 high profile, AAC 48 kHz, yuv420p, `+faststart`
  - `subtitles.srt` and `subtitles.ass`
  - `transcript.txt`
  - `edl.json`: the timeline (cuts, angles, zooms, graphics)
  - `report.md`: what was done, the tools and fallbacks used, and the QC results
- Keep temporary files in the scratchpad, not in the repo.

## Pipeline
1. **Inspect.** Run `ffprobe` on every file and record its duration, fps, resolution and audio streams.
2. **Sync.** Cross-correlate each camera's scratch audio against the separate audio track to find each offset. Use a Python/numpy or scipy FFT on 8 kHz mono WAVs. Target error is under one frame. The separate audio is the master track.
3. **Main camera.** Use the widest shot, or the one that runs the full length. It is the fallback angle.
4. **Speakers.** Diarize with pyannote if it's available. Otherwise use per-channel energy (one mic per speaker) or VAD and clustering. Map each speaker to the camera that frames them best.
5. **Transcript.** Use `openai-whisper` or `faster-whisper` with word timestamps, small or medium model on CPU. Detect the language automatically.
6. **Timeline.** Cut to the active speaker's camera.
   - Minimum shot length is about 2 s. Don't cut on short backchannel words.
   - Use the main camera for overlaps, silence and reactions longer than about 4 s.
   - Cut on sentence boundaries, slightly before the speaker starts (2–4 frames).
7. **Zooms.** Do slow punch-ins of 1.0→1.08–1.15 over 3–6 s on emphasis moments, with ease-in-out. Never punch past the source's real resolution. Use a crop+scale expression or zoompan at the source fps.
8. **Subtitles.** Write an ASS file with 2–5 words per line and the active word highlighted (karaoke `\k` or a color change).
   - Use a clean sans font, like Inter or Montserrat, with a soft shadow.
   - Place them in the lower third, kept clear of on-screen graphics.
9. **Graphics.** Keep them minimal, using one accent color and one font throughout.
   - Lower-third name cards for each speaker the first time they appear.
   - Side-screen visuals for key topics: a keyword card, number or icon that matches what is being said. Pull keywords from the transcript.
   - Render them as PNG/MOV with alpha (Pillow or HTML+Playwright) and composite them with ffmpeg `overlay`, with fades.
10. **Audio.** Run highpass at 80 Hz, `afftdn` light denoise, compression, then `loudnorm` to -14 LUFS integrated and -1 dBTP. Add 10–20 ms fades at cuts. Add music only if the user provides it, ducked under speech.
11. **Color.** Grade each camera on its own. Never put one LUT or filter on everything.
    - **Analyze:** for each camera, sample about 10 frames. Use ffmpeg `signalstats` to measure YAVG/YMIN/YMAX, SATAVG and the U/V averages. Use a numpy check for clipping (Y above 235 or below 16) and a gray-world white balance estimate.
    - **Correct:** bring each camera to a shared baseline, using the main camera as the reference.
      - Exposure: midtones at Y ≈ 110–125, nothing clipped, nothing crushed.
      - White balance: neutral grays, with U/V averages near 128.
      - Contrast and saturation: matched to the main camera.
      - Tools: `eq` (brightness/contrast/gamma/saturation), `colorbalance` (shadows/mids/highlights), `colortemperature`, `curves`.
    - **Match:** match each camera to the main camera by histogram or mean/std per channel in Lab. Compare frames side by side at the cut points and keep adjusting until the difference is small (ΔE < 3 on skin and neutral gray patches).
    - **Look:** pick a palette that suits the lighting, set, wardrobe and mood. Don't default to teal-and-orange.
      - Base look: soft S-curve, lifted blacks around 3–5%, soft highlight roll-off.
      - Color: slight warmth in the mids, gentle cool in the shadows only if the scene suits it, overall saturation 0.9–1.05.
      - Apply this one look to every shot after correction.
    - **Skin:** keep hue near the skin-tone line (about 123° on a vectorscope). Not orange, red, pale or yellow, and no smoothing. If the look moves skin, use `hsl`/`huesaturation` to limit saturation in skin hues.
    - **Zoomed shots:** grade the same as the source. Add light `hqdn3d` before the punch-in if noise shows. Don't over-sharpen (`unsharp` amount ≤ 0.3 at most).
    - **Record** each camera's correction values and the final look in `edl.json` and `report.md`.
12. **Render.** Use a single ffmpeg pass where possible. Otherwise render the segments and concat them with the same codec settings.

## QC (all checks must pass before reporting done)
- `ffprobe` reads the file and its duration matches the timeline within ±0.1 s.
- `ffmpeg -v error -i final.mp4 -f null -` gives no errors.
- `blackdetect` finds no unintended black frames, and `silencedetect` finds no unintended dropouts.
- `ebur128` reads about -14 LUFS.
- Pull stills at the cuts, zooms and subtitle and graphic moments, and look at them. Check framing, overlaps and that the text is readable.
- Color QC:
  - Pull a still from every camera, plus a pair of frames at each cut, and look at them.
  - Check skin tone, exposure and white balance match, highlight and shadow detail, and saturation.
  - Re-run `signalstats` on the final render.
  - Save a contact sheet to `hasil/color_check.jpg`.
- Spot-check lip sync at the start, middle and end.
- If anything fails, fix it, render again and check again.

## Reporting
- List the files in `hasil/` with their sizes.
- Say whether `final.mp4` fits GitHub limits: under 50 MB is fine, 50–100 MB gives a warning, over 100 MB needs LFS or a release asset.
- Be clear about what is saved locally and what is pushed.

## Git rules
- Work on the assigned session branch.
- Commit or push only when the user explicitly says so.
- Never claim an upload that didn't happen.

## User preferences
- Keep the writing short and plain, with no filler.
- Never repeat a job or task that is already done, to save credits.
  - Before starting a step, check `hasil/` and the scratchpad. If its output already exists and the input hasn't changed, reuse it: sync offsets, transcript, timeline, graphics, rendered segments.
  - Don't reread a file that is already in context. Don't rerun commands whose results are known.
  - Run the slow steps (transcription, full renders) once. Only redo them when QC finds a real problem, and only the part that failed.
  - Keep replies short. Don't restate earlier output.
