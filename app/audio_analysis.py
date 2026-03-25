import librosa, tempfile, os

def analyze_audio(file_path: str) -> dict:
    y, sr = librosa.load(file_path, duration=60)
    tempo_raw, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo_raw.item()) if hasattr(tempo_raw, "item") else float(tempo_raw)
    energy = float(librosa.feature.rms(y=y).mean())
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key_idx = int(chroma.mean(axis=1).argmax())
    keys = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    duration = librosa.get_duration(y=y, sr=sr)
    mood = "energetic" if energy > 0.05 else ("melancholic" if tempo < 90 else "upbeat")
    return {
        "bpm": float(tempo),
        "key": keys[key_idx],
        "energy": energy,
        "mood": mood,
        "duration": duration
    }

def build_prompt(title: str, style: str, analysis: dict) -> str:
    style_map = {
        "cinematic": "epic cinematic music video, film quality, dramatic lighting, 4K",
        "anime": "anime music video, vibrant colors, dynamic action sequences, Studio Ghibli inspired",
        "abstract": "abstract visual art, flowing colors, geometric shapes, psychedelic visuals",
        "neon": "neon cyberpunk city, rain-soaked streets, glowing lights, futuristic",
        "nature": "beautiful nature landscapes, golden hour, sweeping vistas, serene",
        "concert": "live concert performance, stage lights, crowd energy, rock concert atmosphere"
    }
    style_desc = style_map.get(style, style_map["cinematic"])
    return f"{style_desc}, {analysis['mood']} mood, {analysis['bpm']:.0f} BPM energy level, music video for '{title}', no text, no watermarks, high quality"
