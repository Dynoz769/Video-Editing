# Editing report: Podcast "Romantisisme", part 1

## Result
- `final.mp4`: 10:38 (638.0 s), 1920x1080 30 fps, H.264 High, yuv420p BT.709, AAC 48 kHz, faststart. Size 289 MB.
- Covers: intro (hook), the hosts' self-introductions, and the podcast session from 0:12 to 10:05 of `sesi_podcast.m4a`. That is the stretch covered by the first main-camera clip, IMG_2836.mov.
- Not included yet: `sesi_podcast` from 10:05 to 27:08 (waiting for the next main-camera clip), and `briefing` / `briefing_2` (left out as behind-the-scenes).

## Sources
- Main camera: IMG_2836.mov (iPhone 17, 4K HLG HDR, 10:05). Synced to `sesi_podcast` at +11.818 s. Drift about 10 ms over 10 minutes.
- Angles: 25 iPhone 15 Pro Max clips. Synced by audio cross-correlation. IMG_3716 (a false-start take) was excluded. IMG_3719, 3723, 3736 and 3713–3715 fall outside this part.
- Audio: `intro`, `pengenalan_diri`, `sesi_podcast` (.m4a) are the master track.

## Editing
- **Speakers.** Muhammad Hasid (host), Alice Catherine (host), Dr. Satria Abadi (guest). Identified from voice pitch (librosa pyin), plus manual turn checks against the transcript.
  - Fallback used: pyannote/resemblyzer could not be installed, and MFCC clustering could not separate the two male voices.
- **Cameras.** CU_D 30, WIDE 30, CU_H 9, CU_A 4, 3718 3, 3722 3, 3725 3, 3726 3, 3728 3, 3710 2, 3709 2, 3721 2, 3730 2, 3710_H 1, 3710_A 1, 3709_A 1, 3717 1, 3720 1, 3724 1.
  - CU_* shots are 4K crops of the main camera, face-tracked with OpenCV Haar at native 1080p resolution.
  - Cuts happen 3 frames before each new speaker starts. Shots are at least 2 s. A wide shot appears about every 4 shots for context.
- **Zoom.** Slow ease-in-out push-ins on every other shot (wide 1.12, close-up 1.10, angle 1.07). Rendered with sub-pixel precision (OpenCV warpAffine), never beyond the source's resolution.
- **Subtitles.** Inter SemiBold, 2–5 words per line. The active word is highlighted amber with a small pop, with a soft shadow and outline. Malay transcript from faster-whisper medium, with corrections to proper names and common misheard words.
- **Graphics.** One accent color (amber #F2B64F) and one font throughout:
  - Opening title card.
  - Lower-third name cards for all 3 speakers.
  - 13 context cards (origin, career, poets mentioned, the sufi vs scientist view, and so on).
  - "Bersambung" end card.
- **Color.**
  - HLG HDR is converted to SDR (zscale with Hable tone mapping, npl=203).
  - Then a separate 3D LUT per camera (`edl.json` > `color`): white balance from faces and neutral surfaces, faces brought to brightness 0.56, then one shared look with skin protection.
- **Audio.** Chain is in `edl.json` > `audio`. Result: -14.1 LUFS integrated, -1.3 dBFS peak, LRA 7.5.

## Quality checks (final render)
| Check | Result |
|---|---|
| Duration vs timeline | 638.000 s = 19140 frames (exact) |
| Decode `ffmpeg -v error` | No errors |
| blackdetect | Only intended: opening fade 0–0.7 s, section breaks at 24.6 s and 42.7 s (0.37 s), end card 636.2–638 s |
| silencedetect (-50 dB, 1.5 s) | Natural 1.5 s pause at 6:14; end tail |
| Loudness | -14.1 LUFS / -1.3 dBFS |
| Lip sync | Started at +23 to +43 ms, systematic (encoder priming). Fixed by shifting audio -33 ms. Now within ±10 ms at 5 checkpoints from start to end. |
| Color | `color_check.jpg`: every camera after grading. White balance, exposure and skin tones consistent. Pink ceiling and blue shadows on the main camera were fixed before rendering. |
| Graphics and subtitles | Checked on stills: no overlap with faces. Name cards were moved up so they don't hit the subtitles. |
| Zoom / cut | Push-in smooth, cut frames clean |

## Notes
- The spellings "Alice Catherine", "Muhammad Hasid" and "Satria Abadi" come from the transcript. Please confirm them.
- The transcript is automatic. A few words may still be wrong, for example "UICI", "Al Kedri" and "kameran".
- GitHub: `final.mp4` is **289 MB, over GitHub's 100 MB per-file limit**. It can only be pushed with Git LFS (already set up in `.gitattributes`; this uses LFS quota) or uploaded as a release asset.
