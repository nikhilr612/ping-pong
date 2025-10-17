# make_sounds.py
"""
Generate simple ping pong sound effects using only Python's standard library.

Creates:
  assets/paddle.wav
  assets/wall.wav
  assets/score.wav
"""

import os, math, wave, struct

# Create assets directory if missing
os.makedirs("assets", exist_ok=True)

def make_tone(filename, freq=440, duration_ms=120, volume=0.5, sample_rate=44100):
    """
    Generate a sine wave tone and write it to a .wav file.
    """
    n_samples = int(sample_rate * duration_ms / 1000.0)
    amplitude = int(volume * 32767)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            val = int(amplitude * math.sin(2 * math.pi * freq * t))
            wf.writeframes(struct.pack('<h', val))

def make_chirp(filename, freq1, freq2, duration_ms=180, volume=0.5, sample_rate=44100):
    """
    Generate a simple chirp (frequency sweep) for scoring feedback.
    """
    n_samples = int(sample_rate * duration_ms / 1000.0)
    amplitude = int(volume * 32767)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            freq = freq1 + (freq2 - freq1) * (i / n_samples)
            val = int(amplitude * math.sin(2 * math.pi * freq * t))
            wf.writeframes(struct.pack('<h', val))

def main():
    print("🎵 Generating sound assets in ./assets ...")
    make_tone("assets/paddle.wav", freq=800, duration_ms=80, volume=0.4)
    make_tone("assets/wall.wav", freq=500, duration_ms=100, volume=0.4)
    make_chirp("assets/score.wav", freq1=600, freq2=1000, duration_ms=180, volume=0.5)
    print("✅ Done!  Generated paddle.wav, wall.wav, and score.wav")

if __name__ == "__main__":
    main()