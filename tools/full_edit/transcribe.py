import sys, json, glob, os
import numpy as np
from scipy.io import wavfile
from faster_whisper import WhisperModel
S=sys.argv[1]
m=WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4)
for w in sorted(glob.glob(f"{S}/wav/*.wav")):
    out=f"{S}/tr/{os.path.basename(w)[:-4]}.json"
    if os.path.exists(out): continue
    segs,info=m.transcribe(wavfile.read(w)[1].astype(np.float32)/32768.0, word_timestamps=True, vad_filter=True, beam_size=5)
    d={"lang":info.language,"p":info.language_probability,"segments":[{"start":s.start,"end":s.end,"text":s.text,"words":[[x.start,x.end,x.word,x.probability] for x in s.words]} for s in segs]}
    json.dump(d,open(out,"w"),ensure_ascii=False)
    print(os.path.basename(w), d["lang"], len(d["segments"]), flush=True)
