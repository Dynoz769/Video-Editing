# Video-Editing

Raw multi-camera footage and separated audio go in. A finished video, color-graded and with subtitles, comes out in `hasil/`.

## Folder layout

```
raw/
  camera/   camera footage, one file per angle (cam1_wide.mp4, cam2_closeup.mp4, ...)
  audio/    separated audio, one file per mic or a master mix (mic1_host.wav, mix.wav)
  music/    optional background music
  assets/   optional logos, fonts, images, a speaker names list
hasil/      final deliverables (written by the editor)
CLAUDE.md   editing workflow and quality rules
```

## File naming
- Cameras: `camN_<shot>.ext`, for example `cam1_wide.mp4`. `cam1` is used as the main camera unless you name another one.
- Audio: `micN_<speaker>.wav` for each speaker's mic, or `mix.wav` for a single master track.
- Speaker names: list them in `raw/assets/speakers.txt`, one line each, like `mic1 = Name, Title`. These become the lower-third name cards.
- Use letters, numbers and underscores only. No spaces.

## Uploading media
Large media files are stored with Git LFS. The rules are in `.gitattributes`.

```
git lfs install
git add raw/
git commit -m "Add raw footage"
git push
```

GitHub rejects any file over 100 MB unless it's stored with LFS. If the files are too big for LFS, share a Google Drive folder or a direct download link instead.

## Output (`hasil/`)

| File | Contents |
|------|----------|
| `final.mp4` | Edited, color-graded video with subtitles (H.264/AAC) |
| `subtitles.srt`, `subtitles.ass` | Plain and animated subtitles |
| `transcript.txt` | Full transcript |
| `edl.json` | Timeline: cuts, angles, zooms, graphics, color values |
| `color_check.jpg` | Color QC contact sheet |
| `report.md` | What was done, the tools used, the QC results |

## Workflow
1. Sync the audio
2. Identify the speakers
3. Transcribe
4. Switch cameras
5. Add zooms
6. Correct and grade the color
7. Add subtitles
8. Add graphics
9. Process the audio
10. Render
11. Quality control

`CLAUDE.md` has the full details.
