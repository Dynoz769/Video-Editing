# Full video: HyperFrames version

**File:** `final_video_hyperframes.mp4`. 23:46 (1426.47 s), 1920×1080, 30 fps, H.264 High CRF 22, AAC 192k 48 kHz, 537 MB.

This uses the same edit as `hasil/final_video.mp4`: the same cuts, camera choices, colour grade, corrected subtitles and audio. Every graphic and every subtitle was rebuilt in **HyperFrames** (HTML + GSAP).

## What changed
- **Glass panels:** cards, name cards and the chapter tag use a translucent dark background with a backdrop blur, a soft shadow and an amber accent bar. They slide in with eased GSAP motion (power3).
- **SVG icons:** pin, book, heart, leaf, phone, scale, quote marks, gift, people, spark. They pop in with a "back" ease.
- **Animated diagrams:**
  - Step lists draw a vertical line, and each step slides in when it's mentioned.
  - Comparisons draw a divider and reveal the right-hand column on cue.
- **Title and chapter cards:** text sharpens from blurred (`filter: blur`), lines draw in, a soft radial band sits behind the text.
- **Progress bar:** fills linearly across the whole session, under the chapter tag.
- **Particles:** seeded and deterministic (mulberry32), drifting around each graphic.
- **Subtitles:** 487 corrected lines, Inter 700 at 48 px, revealed phrase by phrase (fade + 8 px rise), with the same keyword highlighting in amber. There's a soft dark gradient along the bottom for contrast.

## How it was made
1. `base.mp4`: the graded shots joined, with a vignette and a keyframe every 30 frames.
2. `tools/hyperframes/gen_full.py` builds the composition (`composition/index.html`): 57 graphic clips, 487 subtitle clips, 1,147 GSAP tweens. It's graphics only, on a transparent background. Lint: 0 errors.
3. `tools/hyperframes/mk_chunks.py` splits the composition into five 300 s chunks. Each chunk drives the master timeline with `tweenFromTo`, so one container restart can't wipe out the whole render.
4. Each chunk is rendered as WebM VP9 **with an alpha channel** (`hyperframes@0.9.40`, about 14 min per chunk, CPU-only Chrome).
5. ffmpeg overlays the graphics on `base.mp4` and adds the processed audio (advanced 33 ms to compensate for the encoder).

**Why not one render with the video inside:** HyperFrames first extracts every frame of the video, which came to 8.5 GB against its 2 GB limit. The first full render was also lost to a container restart after 56 minutes, which is why it's now split into chunks.

## Quality checks
| Check | Result |
|---|---|
| Duration / frames | 1426.467 s / 42,794 frames (same as the timeline) |
| Decode | No errors |
| Black frames | Only the intended ones: opening fade, section breaks at 24.6 s and 42.8 s, end card |
| Loudness | -14.1 LUFS, -1.3 dB peak |
| Lip sync, 5 checkpoints (0:00–23:28) | -7.9 to +6.8 ms |
| Stills (`qc_stills.jpg`, 19 moments) | Every graphic appears on time, nothing covers a face, text is readable |

The chunked render was also verified at a chunk boundary: at 5:00–5:06, the subtitle and quote card match the full timeline exactly.
