import sys, json, os, numpy as np
from scipy.io import wavfile
from faster_whisper import WhisperModel
S=sys.argv[1]
m=WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
PROMPT=("Podcast dalam Bahasa Melayu bersama Dr. Satria Abadi dari Bogor, Indonesia. Pengacara: Alice Catherine dan Muhammad Hasid. "
        "Topik: romantisisme, romantisme, akal dan perasaan, falsafah, filosofi, empati, simpati, belas kasihan, alam, "
        "Jalaluddin Ar-Rumi, Rabiatul Adawiyah, Hamka, syair, puisi, pensyarah, lecturer, postdoctoral, PhD.")
for n in ["intro","pengenalan_diri","sesi_podcast"]:
    out=f"{S}/trl/{n}.json"
    if os.path.exists(out): continue
    a=wavfile.read(f"{S}/a16/{n}.wav")[1].astype(np.float32)/32768.0
    segs,info=m.transcribe(a, language="ms", word_timestamps=True, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=400),
                           beam_size=5, condition_on_previous_text=False, initial_prompt=PROMPT)
    d={"segments":[{"start":s.start,"end":s.end,"text":s.text,"words":[[x.start,x.end,x.word,x.probability] for x in s.words]} for s in segs]}
    json.dump(d,open(out,"w"),ensure_ascii=False); print(n,len(d["segments"]),flush=True)
