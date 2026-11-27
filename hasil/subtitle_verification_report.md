# Subtitle verification report

## Method
1. **Transcription:** Whisper **large-v3** (faster-whisper, int8, CPU). Language fixed to Malay (`ms`), voice-activity filter on, beam 5. Each segment was transcribed independently so errors don't carry over. The model was primed with the names and key terms (Satria Abadi, Alice Catherine, Muhammad Hasid, romantisisme, Jalaluddin Ar-Rumi, Rabiatul Adawiyah, Hamka, falsafah, empati…).
2. **Second model for timing:** the earlier Whisper **medium** pass was kept as a second reference. Large-v3 recognises words much better, but its word timestamps ran up to **1.2 s early**. I checked this against the audio energy at the cut points. For example, "Apakah" sits at 1155.5 s in the audio, while large-v3 put it at 1154.3 s and medium at 1155.5 s.
   - **Fix:** the large-v3 text was aligned to the medium transcript word by word (difflib sequence matching), and each matched word takes medium's timestamps. Words with no match are interpolated between the matched words on either side.
3. **Gaps:** two stretches the voice filter skipped were re-transcribed with the filter off:
   - 1355–1372 s turned out to be off-mic crew chatter, so it was cut.
   - 1529–1543 s recovered the line "…seperti itu. Itu empati."
4. **Line by line review:** every one of the 500 generated lines was read in context and checked against both transcripts and the topic of the conversation.
   - **421 lines corrected:** names, terms, punctuation, capitals, misheard words, and lines where one speaker's word ended up on the next speaker's line.
   - **13 fragments deleted:** these were merged into the neighbouring line.
   - **487 subtitle lines in the final video.**
5. **Speaker splits:** lines are split at every speaker change. Speakers come from the turn map, which was checked against the transcript; Alice is also detected by voice pitch (above 170 Hz). In the SRT, a line never mixes two speakers.
6. **Timing:**
   - Each line appears 60 ms before its first word and stays up to 350 ms after its last word, but never overlaps the next line.
   - Lip sync in the final render was measured by cross-correlating camera audio with the final audio; see `audio_sync_report.json`.

## Main corrections (recognised → corrected)
| Recognised | Corrected |
|---|---|
| Fu hantar | food hunter |
| UPS ini | UPSI ini |
| PSD | PhD |
| Satria Wadi / Sitar Sajar | Satria Abadi / "sebentar sahaja tadi" |
| cerita-cerita masa tu | cita-cita masa tu |
| tekat | tekad |
| Brunei Rusalam | Brunei Darussalam |
| dia lalu Dengar Arumi / si Rumi | Jalaluddin Ar-Rumi / Ar-Rumi |
| Robiatul / Pergatul / Radiyatul Adawiyah | Rabiatul Adawiyah |
| sair / sayar-sayar | syair / syair-syair |
| Tuhanan, kesintaan | ketuhanan, kecintaan |
| surga | syurga |
| Lulus lah eh | Relaks lah eh |
| akar dan juga perasaan | akal dan juga perasaan |
| orang sentis | orang saintis |
| hanya semua | hanya semu (Indonesian: "illusory", repeated later as "nilai yang semu") |
| Palsapah, paksa pahal | falsafah |
| itulah hal game | Itulah halnya |
| penyakapan | percakapan |
| fokus (end of question) | podcast |
| Elis | Alice |
| saya maaf-maaf | saya Muhammad Hasid, dan saya Alice Catherine |
| melinggarkan masa | melengahkan masa |

The doctor's Indonesian wording is kept as spoken (berbeda, bagian, karena, kakek, nurut) and not converted to Malay. Casual phrasing (je, lah, macam tu, okay) is also kept.

## Unclear dialogue: not fully confirmed
I could not listen to the audio directly. These lines are the best reading from two speech-recognition passes plus context:

| Time in session | Subtitle used | Note |
|---|---|---|
| 0:00 (intro) | "Terdapat **saat-saat** dalam kehidupan" | Both models heard "sangat-sangat". "saat-saat" fits the grammar and meaning. |
| 6:45 | "mengagumi filosof **Al-Qidri**" | Name unclear (also heard as "Al Kedri"). Possibly Kahlil Gibran or Al-Kindi. Kept as heard. |
| 9:28 | "memang orang filosofi, yang memang … penyair-penyair terdahulu" | One phrase was unintelligible ("di Kuala Sapa" / "dipilosofi"), so it was left out rather than guessed. |
| 17:21 | "meluapkan sebuah perasaan **politik**" | Heard as "perasaan tak politik" or "kapalitik". |
| 21:13 | "kita punya **tajuk hari ini**" | Heard as "lagu dan mati" or "tajuk dan makin". Context points to "tajuk". |
| 23:40 | "kita **awek-awek**" | Heard as "awik-awik" or "berjauh-jauh". |
| 26:21 | "kita **sembang-sembang**" | Heard as "sembar-sembar" or "semah-semah". |
| 26:56 | "kerana sudi hadir pada pagi ini" | Garbled in both passes ("hadir kami pada menyapukan pada keadaan ini"). The meaning of the closing thanks is kept; the wording is approximate. |

## Final check
- 487 lines, none duplicated, no empty lines. Each line has at most 42 characters on one row.
- Style:
  - Inter SemiBold 50 px, bottom centre, with a soft blurred outline and shadow for contrast.
  - Each phrase fades in with a 6 px upward drift.
  - Keyword highlighting is selective: about 35 topic words and names (romantisme, akal, perasaan, empati, names of poets…) appear in amber. Other words aren't animated.
- Subtitles sit below every graphic and away from faces. Name cards were moved above the subtitle line. Checked on stills of the final render.
