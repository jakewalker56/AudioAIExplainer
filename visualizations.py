import numpy as np
import matplotlib.pyplot as plt

# Parameters
fs = 20  # sampling rate (Hz)
N = 10   # number of samples
t = np.arange(N) / fs

# Create a 3 Hz sine wave sampled at 20 Hz over 10 samples
f_signal = 3  # Hz
x = np.sin(2 * np.pi * f_signal * t)

# Compute the DFT (zero-padded for higher resolution visualization)
pad_factor = 8
X = np.fft.fft(x, n=N * pad_factor)
freqs = np.fft.fftfreq(N * pad_factor, d=1/fs)

# Only keep the positive half of the spectrum
half = len(freqs) // 2
freqs = freqs[:half]
X = X[:half]

# Plot the magnitude spectrum
plt.figure(figsize=(10, 5))
plt.stem(freqs, np.abs(X))
plt.title("DFT of a 3 Hz Sine Wave (Sampled at 20 Hz, 10 Samples)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.tight_layout()
plt.show()
