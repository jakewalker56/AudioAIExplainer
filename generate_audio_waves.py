import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import librosa
import librosa.display
import scipy.io.wavfile as wav
from scipy.signal import spectrogram

def save_spectrogram(signal, sample_rate, spectrogram_path):
    # Compute spectrogram
    f, t_spec, Sxx = spectrogram(signal, sample_rate, nperseg=1024)

    # Plot
    plt.figure(figsize=(8, 4))
    plt.pcolormesh(t_spec, f, 10*np.log10(Sxx), shading='gouraud')
    plt.colorbar(label="Power (dB)")
    plt.title("Spectrogram of 12 kHz Tone")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [s]")
    plt.ylim(0, 20000)  # up to 20 kHz (human hearing limit)

    # Save image
    plt.savefig(spectrogram_path, dpi=150, bbox_inches="tight")
    plt.close()

def save_waveform(signal, duration, zoom, waveform_path):
    # Waveform plot
    time_axis = np.linspace(0, duration, len(signal))
    plt.figure(figsize=(8, 4))
    plt.plot(time_axis, signal, lw=0.5)
    plt.title("Waveform of Tone")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.xlim(0, zoom)  # zoom into first 2ms for clarity
    
    # Save image
    plt.savefig(waveform_path, dpi=150, bbox_inches="tight")
    plt.close()

def save_spectrogram_and_waveform(signal, sample_rate, duration, path):
    # Plot waveform and spectrogram side by side
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

    # Waveform plot
    time_axis = np.linspace(0, duration, len(signal))
    ax1.plot(time_axis, signal, lw=0.5)
    ax1.set_title("Waveform of 12 kHz Tone")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Amplitude")
    ax1.set_xlim(0, 0.002)  # zoom into first 2ms for clarity

    # Spectrogram plot
    f, t_spec, Sxx = spectrogram(signal, sample_rate, nperseg=1024)
    pcm = ax2.pcolormesh(t_spec, f, 10*np.log10(Sxx), shading='gouraud')
    fig.colorbar(pcm, ax=ax2, label="Power (dB)")
    ax2.set_title("Spectrogram of 12 kHz Tone")
    ax2.set_ylabel("Frequency [Hz]")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylim(0, 20000)

    # Save combined image
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


# python -c "import generate_audio_waves; generate_audio_waves.three_wave_interference_wav()"
def three_wave_interference_wav():

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



# python -c "import generate_audio_waves; generate_audio_waves.single_500hz_wave_wav()"
def single_500hz_wave_wav():
    # Parameters
    sample_rate = 44100  # CD quality
    duration = 3.0       # seconds
    frequency = 500   # Hz

    # Generate time axis
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Generate sine wave
    signal = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Save as WAV file
    output_path = "docs/assets/single_500hz_wave.wav"
    wav.write(output_path, sample_rate, (signal * 32767).astype(np.int16))

    save_waveform(signal, duration, 0.01, "docs/assets/single_500hz_wave.png")
