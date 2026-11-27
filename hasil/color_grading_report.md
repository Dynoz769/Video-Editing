# Color grading report

## Footage
- **Main camera** (IMG_2836, 3 files): iPhone 17, 4K30, **HLG HDR (BT.2020)**. The lighting is a library ceiling with fluorescent tubes mixed with daylight from the windows.
- **Angle clips** (IMG_37xx): iPhone 15 Pro Max, 4K30, SDR BT.709.
- **As shot:**
  - The angle clips were about one stop under-exposed (average luma 75–100 of 255).
  - Clips facing the light wood shelves came out warm and saturated (V average about 139–141). Clips facing the dark shelves came out cooler and flatter (V about 134).
  - After conversion to SDR, the main camera had a pink cast on the ceiling and blue in the shadows.

## 1. HDR to SDR (main camera only)
`zscale (HLG, npl=203 reference white) → linear → BT.709 primaries → tonemap=hable (desat=2) → BT.709 transfer`.

| Option tested | Result |
|---|---|
| mobius, npl=100 | Too bright (faces at 0.69) |
| mobius, npl=203 | Faces at 0.64, oversaturated highlights |
| Direct HLG to BT.709 without tone mapping | Clipped, washed out |
| **hable, desat=2 (chosen)** | Most natural, closest to the angle clips |

## 2. Per-camera correction (a 33³ 3D LUT generated for each source)
Each camera gets its own correction. There is no shared LUT.

1. **Measure:** faces were detected (OpenCV) in 5–6 frames per camera. The median face RGB and brightness, plus neutral grey surfaces, were measured.
2. **White balance:** red and blue gains were set to bring skin to a common target (R/G ≈ 1.36, B/G ≈ 0.82), applied at 75% strength and limited to ±10–12%. Overall brightness is preserved.
3. **Exposure:** a power curve brings faces toward a target brightness of 0.56 (gamma limited to 0.75–1.4).
4. **Main camera fixes:** pink removed from the highlights (-1.5% R) and blue removed from the shadows. All three main files are corrected separately to match each other; after correction their average brightness is 0.495–0.501.

| Camera | Face Y before | Face RGB before | gain R | gain B | gamma |
|---|---|---|---|---|---|
| main (1) | 0.382 | 0.494 / 0.353 / 0.310 | 0.987 | 0.958 | 0.75 |
| main2 | 0.335 | 0.424 / 0.302 / 0.282 | 0.988 | 0.918 | 0.75 |
| main3 | 0.376 | 0.478 / 0.353 / 0.302 | 1.005 | 0.970 | 0.75 |
| 3709 | 0.522 | 0.690 / 0.486 / 0.369 | 0.971 | 1.062 | 0.891 |
| 3710 | 0.515 | 0.671 / 0.482 / 0.373 | 0.983 | 1.045 | 0.873 |
| 3717 | 0.497 | 0.627 / 0.467 / 0.373 | 1.006 | 1.016 | 0.830 |
| 3718 | 0.473 | 0.616 / 0.443 / 0.361 | 0.987 | 1.008 | 0.774 |
| 3720 | 0.462 | 0.608 / 0.431 / 0.345 | 0.977 | 1.023 | 0.751 |
| 3721 | 0.521 | 0.651 / 0.494 / 0.416 | 1.020 | 0.977 | 0.891 |
| 3722 | 0.530 | 0.678 / 0.494 / 0.412 | 0.996 | 0.990 | 0.913 |
| 3724 | 0.590 | 0.776 / 0.549 / 0.420 | 0.974 | 1.056 | 1.099 |
| 3725 | 0.472 | 0.592 / 0.447 / 0.365 | 1.016 | 0.999 | 0.771 |
| 3726 | 0.432 | 0.561 / 0.404 / 0.322 | 0.986 | 1.023 | 0.750 |
| 3727 | 0.565 | 0.729 / 0.529 / 0.435 | 0.992 | 1.000 | 1.016 |
| 3728 | 0.515 | 0.667 / 0.482 / 0.388 | 0.989 | 1.016 | 0.873 |
| 3730 | 0.529 | 0.663 / 0.498 / 0.416 | 1.014 | 0.984 | 0.911 |
| 3731 | 0.506 | 0.655 / 0.475 / 0.380 | 0.991 | 1.020 | 0.852 |
| 3733 | 0.492 | 0.659 / 0.455 / 0.373 | 0.963 | 1.010 | 0.818 |
| 3734 | 0.514 | 0.667 / 0.482 / 0.384 | 0.988 | 1.023 | 0.870 |
| 3735 | 0.516 | 0.667 / 0.482 / 0.396 | 0.990 | 1.001 | 0.876 |
| 3737 | 0.498 | 0.647 / 0.467 / 0.384 | 0.989 | 1.001 | 0.831 |

## 3. The look (same for every camera after correction)
**Why this look:** the setting is a warm library (orange chairs, wood shelves, a gold and black batik shirt, dark suits) and the topic is romance and feeling. That suits a **warm, natural, documentary-podcast** look. Teal-and-orange was deliberately avoided: it would push the orange chairs and skin too far.

- **Contrast:** a soft S-curve on brightness (pivot 0.45, strength 0.10), with a gentle highlight roll-off above 0.82 so the ceiling lights don't clip harshly.
- **Black and white points:** blacks lifted to 3% for a slightly atmospheric feel without crushing; whites capped at 97.5% so they stay clean.
- **Color:** slight warmth in the midtones (+1.2% R, -1.0% B, mostly in the middle of the tonal range). The cool-shadow tint from an earlier test was removed because it turned the dark shelves blue.
- **Saturation:** 0.96 overall. Skin hues (5–60°) keep their natural saturation, and skin chroma is capped at 0.5 so it can't go orange or red.
- **Vignette:** a subtle vignette in the final pass (angle 0.42).

## 4. Zoomed shots
- Close-ups are cropped from 4K at 2112×1188 and scaled down to 1080p. Push-ins of up to 1.10× therefore never go beyond the source's real resolution.
- Angle-clip punch-ins (1.18×) are within the 2× headroom of 4K.
- Sub-pixel scaling (bicubic warpAffine, Lanczos pre-scale). No sharpening added and no noise added.

## 5. Quality check
- `color_check.jpg` shows one graded frame from every camera.
- Frame pairs on both sides of cuts were checked in the final render (see `editing_report.md`).
- **Result:** consistent white balance (neutral greys, no pink ceiling, no blue shelves), similar face brightness across cameras, and natural brown skin with no orange or grey cast.
- **Remaining difference:** the main camera is slightly softer in contrast than the angle clips, because of the HDR conversion. It isn't distracting at cuts.
