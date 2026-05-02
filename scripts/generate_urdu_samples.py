from gtts import gTTS
from pathlib import Path

OUT = Path("app/data")
OUT.mkdir(parents=True, exist_ok=True)

cases = [
    {
        "filename": "urdu_1.mp3",
        "text": "کیا آپ مجھے سن سکتے ہیں؟",
    },
    {
        "filename": "urdu_2.mp3",
        "text": "میں راستہ پوچھ رہا ہوں",
    },
    {
        "filename": "urdu_3.mp3",
        "text": "موسم کی اطلاع بتائیں",
    },
]

for c in cases:
    out = OUT / c["filename"]
    print(f"Generating {out}...")
    tts = gTTS(text=c["text"], lang="ur")
    tts.save(str(out))
print("Done.")
