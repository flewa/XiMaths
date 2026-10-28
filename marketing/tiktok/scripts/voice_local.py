"""Voix off gratuite et illimitée, avec des modèles libres qui tournent sur la machine.

- Chatterbox Multilingual (Resemble AI, licence MIT) dit les phrases ; son timbre vient
  d'une référence française produite par Kokoro (Apache 2.0, voix « ff_siwis »).
- Chaque phrase est transcrite par Whisper (faster-whisper) et comparée au script : en
  dessous du seuil, elle est refaite, puis confiée à Kokoro si Chatterbox échoue encore.
- La voix complète de la vidéo est ensuite découpée par scène, avec ses mots horodatés,
  par scripts/voice-import.ts.

Installation (Python 3.12 ou 3.13, processeur suffisant, sans carte graphique) :

    uv venv .venv-voix
    VIRTUAL_ENV=.venv-voix uv pip install --torch-backend cpu chatterbox-tts kokoro faster-whisper num2words "setuptools<81"

Usage, depuis marketing/tiktok :

    .venv-voix/bin/python scripts/voice_local.py                  # toutes les vidéos
    .venv-voix/bin/python scripts/voice_local.py 04-defi-chrono   # une seule

Les modèles se téléchargent depuis Hugging Face au premier lancement.
"""

import difflib
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
from num2words import num2words

ROOT = Path(__file__).resolve().parent.parent
SR = 24000
# Chatterbox parle posément ; une voix off TikTok va plus vite.
TEMPO = 1.12
GAP = 0.25
ATTEMPTS = 3
GOOD = 0.92
ACCEPTABLE = 0.85

# Ce que les voix locales lisent mal : la marque, LaTeX, les sigles. Le texte affiché
# (sous-titres) reste celui du script.
SAY = [
    (r"\bXiMaths\b", "Ksi mat"),
    (r"\bLaTeX\b", "latèque"),
    (r"\bMPSI\b", "èm pé èss i"),
    (r"\bPSI\b", "pé èss i"),
    (r"\bMP\b", "èm pé"),
    (r"\bL1\b", "elle un"),
    (r"\bM2\b", "èm deux"),
    (r"\bDS\b", "dé èss"),
    (r"\bIA\b", "i-a"),
]

REFERENCE = (
    "Bonjour à tous. Aujourd'hui, on parle de mathématiques, de méthode et de régularité. "
    "Chaque semaine, un peu de travail, et les progrès arrivent vite."
)


def spoken(text):
    for pattern, replacement in SAY:
        text = re.sub(pattern, replacement, text)
    return text


def normalize(text):
    # Whisper écrit les nombres en chiffres, le script en lettres.
    text = re.sub(r"\d+", lambda match: num2words(int(match.group()), lang="fr"), text)
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", text)


def videos():
    code = 'import { VIDEOS } from "./src/videos"; console.log(JSON.stringify(VIDEOS.map((v) => ({ id: v.id, voices: v.scenes.map((s) => s.voice) }))))'
    out = subprocess.run(["npx", "tsx", "-e", code], cwd=ROOT, check=True, capture_output=True, text=True)
    return json.loads(out.stdout)


def finish(audio, tempo):
    """Silences de début et de fin retirés, débit accéléré sans changer la hauteur."""
    with tempfile.TemporaryDirectory() as work:
        source, target = Path(work, "in.wav"), Path(work, "out.wav")
        sf.write(source, audio, SR)
        trim = "silenceremove=start_periods=1:start_threshold=-45dB"
        chain = f"{trim},areverse,{trim},areverse" + (f",atempo={tempo}" if tempo != 1 else "")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", source, "-af", chain, "-ar", str(SR), "-ac", "1", target], check=True)
        return sf.read(target)[0]


class Voices:
    def __init__(self):
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        from faster_whisper import WhisperModel
        from kokoro import KPipeline

        self.kokoro = KPipeline(lang_code="f", repo_id="hexgrad/Kokoro-82M")
        self.chatterbox = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
        self.whisper = WhisperModel("small", device="cpu", compute_type="int8")
        self.reference = Path(tempfile.gettempdir(), "xi-reference-fr.wav")
        sf.write(self.reference, self.say_kokoro(REFERENCE, speed=1.0), SR)

    def say_kokoro(self, text, speed=1.1):
        return np.concatenate([audio for _, _, audio in self.kokoro(text, voice="ff_siwis", speed=speed)])

    def say_chatterbox(self, text, seed):
        torch.manual_seed(seed)
        wav = self.chatterbox.generate(
            text, language_id="fr", audio_prompt_path=str(self.reference), exaggeration=0.55, cfg_weight=0.5
        )
        return librosa.resample(wav.squeeze(0).numpy(), orig_sr=self.chatterbox.sr, target_sr=SR)

    def heard(self, audio):
        segments, _ = self.whisper.transcribe(librosa.resample(audio, orig_sr=SR, target_sr=16000), language="fr", beam_size=5)
        return " ".join(segment.text for segment in segments).strip()

    def score(self, audio, text):
        heard = self.heard(audio)
        return difflib.SequenceMatcher(None, normalize(text), normalize(heard)).ratio(), heard

    def scene(self, text, seed):
        """La meilleure prise de Chatterbox, ou celle de Kokoro si aucune n'est assez fidèle."""
        best = None
        for attempt in range(ATTEMPTS):
            audio = finish(self.say_chatterbox(spoken(text), seed + attempt), TEMPO)
            score, heard = self.score(audio, text)
            if best is None or score > best[0]:
                best = (score, heard, audio, "chatterbox")
            if score >= GOOD:
                break
        if best[0] < ACCEPTABLE:
            audio = finish(self.say_kokoro(spoken(text)), 1)
            score, heard = self.score(audio, text)
            if score > best[0]:
                best = (score, heard, audio, "kokoro")
        return best

    def words(self, path):
        segments, _ = self.whisper.transcribe(
            librosa.load(path, sr=16000)[0], language="fr", beam_size=5, word_timestamps=True
        )
        return [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segments for w in s.words]


def main():
    only = sys.argv[1:]
    voices = Voices()
    for index, video in enumerate(videos()):
        if only and video["id"] not in only:
            continue
        parts, report = [], []
        for number, text in enumerate(video["voices"]):
            score, heard, audio, engine = voices.scene(text, seed=1000 * index + 10 * number)
            line = f"{video['id']} · {number + 1} · {engine} · {score:.2f} · {heard}"
            print(line, flush=True)
            report.append(line)
            parts += [audio, np.zeros(int(GAP * SR))]
        with tempfile.TemporaryDirectory() as work:
            full, words = Path(work, "voix.wav"), Path(work, "mots.json")
            sf.write(full, np.concatenate(parts[:-1]), SR)
            words.write_text(json.dumps(voices.words(full), ensure_ascii=False))
            subprocess.run(["npx", "tsx", "scripts/voice-import.ts", video["id"], str(full), str(words)], cwd=ROOT, check=True)
        # Ce que Whisper a entendu, prise retenue par prise retenue : à relire avant de publier.
        Path(ROOT, "public", "voice", video["id"], "rapport.txt").write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
