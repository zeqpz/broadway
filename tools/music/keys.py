"""Read a take's key and tempo-free length: chroma by FFT folded onto pitch classes, Krumhansl-Schmuckler profiles.
usage: python tools/music/keys.py <mp3>..."""
import sys
import numpy as np
import av
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
N = "C C# D Eb E F F# G Ab A Bb B".split()
for p in sys.argv[1:]:
    c = av.open(p)
    x = np.concatenate([f.to_ndarray().mean(0) for f in c.decode(audio=0)]).astype(np.float32)
    sr = c.streams.audio[0].rate
    n = 8192
    chroma = np.zeros(12)
    freqs = np.fft.rfftfreq(n, 1 / sr)
    ok = (freqs > 55) & (freqs < 2000)
    pc = (np.round(12 * np.log2(freqs[ok] / 440.0)) + 9) % 12
    for i in range(0, len(x) - n, n // 2):
        m = np.abs(np.fft.rfft(x[i:i + n] * np.hanning(n)))[ok]
        chroma += np.bincount(pc.astype(int), weights=m ** 2, minlength=12)
    chroma /= chroma.sum()
    best = max(((np.corrcoef(np.roll(prof, k), chroma)[0, 1], N[k] + (" major" if prof is MAJ else " minor"))
                for prof in (MAJ, MIN) for k in range(12)))
    print(f"{p[-40:]}  {len(x) / sr:5.1f}s  {best[1]:9s} r={best[0]:.2f}")
