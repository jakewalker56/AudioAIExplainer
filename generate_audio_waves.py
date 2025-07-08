import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import librosa
import librosa.display

# === Parameters ===
frequencies = [220, 2240, 2030]        # Hz
amplitudes = [1.0, 0.8, 0.6]         # relative amplitudes
phases = [0, np.pi/4, np.pi/2]       # radians

sample_rate = 44100  # Hz
bit_depth = 16       # bits per sample
duration_seconds = 3.0  # total length of audio output

# === Time Vector ===
t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False)

# === Generate the Composite Waveform ===
wave = np.zeros_like(t)
for freq, amp, phase in zip(frequencies, amplitudes, phases):
    wave += amp * np.sin(2 * np.pi * freq * t + phase)

# === Normalize for Audio Output ===
max_val = np.max(np.abs(wave))
if max_val > 0:
    wave_normalized = wave / max_val
else:
    wave_normalized = wave

audio_data = np.int16(wave_normalized * (2**(bit_depth - 1) - 1))

# === Export to WAV File ===
write("interference_pattern.wav", sample_rate, audio_data)

# === Plotting 3 Periods of the Lowest Frequency ===
f_min = min(frequencies)
T_min = 1 / f_min
window_duration = 30 * T_min
num_samples_to_plot = int(sample_rate * window_duration)
t_plot = t[:num_samples_to_plot]
wave_plot = wave[:num_samples_to_plot]

plt.figure(figsize=(10, 4))
plt.plot(t_plot, wave_plot)
plt.title("Wave Interference Pattern (3 periods of lowest frequency)")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.show()

# === Load the Audio Data ===
audio_path = "interference_pattern.wav"
y, sr = librosa.load(audio_path, sr=None)  # Use original sample rate

# === Compute the Mel-Spectrogram ===
S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=128, power=2.0)

# === Convert to Decibel Scale (Log Scale) ===
S_dB = librosa.power_to_db(S, ref=np.max)

# === Display the Mel-Spectrogram ===
plt.figure(figsize=(10, 4))
librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', cmap='viridis')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel-Spectrogram of Interference Pattern')
plt.tight_layout()
plt.show()