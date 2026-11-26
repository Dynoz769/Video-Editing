# Video Editing Workflow

This file tells Claude how to edit the videos in this repo. Read it before starting any edit.

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
