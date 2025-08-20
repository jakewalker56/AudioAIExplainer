import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import librosa
import librosa.display
import scipy.io.wavfile as wav
from scipy.signal import spectrogram
import os
from scipy.io import wavfile
from pydub import AudioSegment
from scipy.io import wavfile
from scipy.signal import stft, istft, get_window

from pydub.utils import which


# ---------- Loading (.wav and .m4a) ----------
def _ensure_ffmpeg():
    if which("ffmpeg") is None or which("ffprobe") is None:
        raise RuntimeError("FFmpeg/ffprobe not found. Add to PATH or install (winget/choco).")

def load_audio(filepath):
    """
    Returns mono float32 signal (not re-normalized if already float), and sample_rate.
    WAV via SciPy; M4A via pydub/ffmpeg.
    """
    ext = os.path.splitext(filepath)[1].lower()
    abs_path = os.path.abspath(filepath)

    if ext == ".wav":
        sr, data = wavfile.read(abs_path)
        # Convert to float32 in [-1,1] if integer PCM; keep floats as-is
        if np.issubdtype(data.dtype, np.integer):
            max_abs = np.iinfo(data.dtype).max
            y = (data.astype(np.float32) / max_abs)
        else:
            y = data.astype(np.float32)
    elif ext == ".m4a":
        _ensure_ffmpeg()
        a = AudioSegment.from_file(abs_path)  # format inferred
        sr = a.frame_rate
        samples = np.array(a.get_array_of_samples())
        if a.channels == 2:
            samples = samples.reshape(-1, 2).mean(axis=1)  # to mono
        y = samples.astype(np.float32) / (2**15)  # pydub gives int16-range arrays
    else:
        raise ValueError("Unsupported file format: use .wav or .m4a")

    # If stereo (WAV path), downmix to mono by averaging
    if y.ndim == 2:
        y = y.mean(axis=1).astype(np.float32)
    return y, sr

# ---------- STFT → dB (relative to peak) ----------
def stft_db_relative(y, sr, n_fft=1024, hop_length=None, window="hann", top_db=80):
    """
    Amplitude STFT → dB relative to the max within this spectrogram.
    Returns f (Hz), t (s), and S_db (dB, 0 is max, clipped to [−top_db, 0]).
    """
    if hop_length is None:
        hop_length = n_fft // 4  # common ML default

    w = get_window(window, n_fft, fftbins=True)
    noverlap = n_fft - hop_length
    f, t, Zxx = stft(y, fs=sr, window=w, nperseg=n_fft, noverlap=noverlap,
                     boundary=None, padded=False)
    mag = np.abs(Zxx)
    eps = 1e-12
    S_db = 20.0 * np.log10(np.maximum(mag, eps))
    S_db_rel = S_db - np.max(S_db)             # 0 dB at the plot's peak
    S_db_rel = np.maximum(S_db_rel, -float(top_db))  # clip dynamic range
    return f, t, S_db_rel

# ---------- Plot helper ----------
def save_spectrogram(f, t, S_db, sr, top_db, title, spectrogram_path, fmin = None, fmax = None):
     # Defaults & bounds
    if fmin is None: fmin = 0.0
    if fmax is None: fmax = sr / 2.0
    fmin = float(max(0.0, fmin))
    fmax = float(min(sr / 2.0, fmax))
    if fmin >= fmax:
        raise ValueError(f"fmin ({fmin}) must be < fmax ({fmax}).")

    # Mask frequency band (inclusive)
    band_mask = (f >= fmin) & (f <= fmax)
    if not np.any(band_mask):
        raise ValueError("No frequency bins fall within the requested range.")

    f_band = f[band_mask]
    S_band = S_db[band_mask, :]

    vmin, vmax = -float(top_db), 0.0

    plt.figure(figsize=(10, 4))
    plt.pcolormesh(t, f_band, S_band, shading="gouraud", vmin=vmin, vmax=vmax)
    cbar = plt.colorbar()
    cbar.set_label("dB (relative to peak)")
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    plt.ylim(fmin, fmax)
    plt.title(title if title else f"Spectrogram (rel. peak) [{fmin:.0f}-{fmax:.0f} Hz]")
    plt.tight_layout()

    plt.savefig(spectrogram_path, dpi=150, bbox_inches="tight")
    #plt.show()

def save_waveform(signal, sample_rate, zoom, waveform_path):
    # Waveform plot
    time_axis = np.linspace(0, len(signal) / sample_rate, len(signal))
    plt.figure(figsize=(8, 4))
    plt.plot(time_axis, signal, lw=0.5)
    plt.title("Waveform")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.xlim((len(signal) / sample_rate ) / 2, (len(signal) / sample_rate) / 2 + zoom)  # zoom into middle for clarity
    
    # Save image
    plt.savefig(waveform_path, dpi=150, bbox_inches="tight")
    plt.close()


def mask_spectrogram_and_reconstruct(
    Zxx, f, t, sr, mask,
    *,
    top_db=80,
    drop_to_db=None,             # if None, uses top_db
    window="hann",
    hop_length=None,             # if None, inferred from t (preferred) or set to n_fft//4
    out_png="masked_spectrogram.png",
    out_wav="masked_audio.wav",
    wav_dtype="int16"            # "int16" or "float32"
):
    """
    Apply a boolean mask over frequency bins of a complex STFT and reconstruct audio.

    Parameters
    ----------
    Zxx : 2D np.ndarray (complex), shape (len(f), len(t))
        Complex STFT (e.g., from scipy.signal.stft) using one-sided spectrum.
    f : 1D np.ndarray
        Frequency axis in Hz (as returned by stft).
    t : 1D np.ndarray
        Time axis in seconds (as returned by stft).
    sr : int
        Sample rate in Hz.
    mask : 1D array-like of bool, len == len(f)
        True: keep this frequency bin; False: drop (set to floor level).
    top_db : float
        Dynamic range for the PNG (vmin=-top_db, vmax=0).
    drop_to_db : float or None
        Floor level to assign to dropped bins (relative to spectrogram peak, in dB).
        If None, uses top_db (i.e., floor = -top_db).
    window : str or array-like
        Window used for ISTFT (should match what was used for STFT; e.g., "hann").
    hop_length : int or None
        Hop length in samples. If None, inferred from t (preferred). If t is None or
        degenerate, defaults to n_fft//4.
    out_png : str
        Where to save the masked spectrogram image (PNG).
    out_wav : str
        Where to save the reconstructed audio (WAV).
    wav_dtype : {"int16","float32"}
        Sample format for the saved WAV.

    Returns
    -------
    y_rec : 1D np.ndarray (float)
        Reconstructed audio.
    """
    Zxx = np.asarray(Zxx)
    f = np.asarray(f)
    t = np.asarray(t)
    mask = np.asarray(mask).astype(bool)

    if Zxx.shape[0] != len(f):
        raise ValueError("Zxx.shape[0] must equal len(f).")
    if Zxx.shape[1] != len(t):
        raise ValueError("Zxx.shape[1] must equal len(t).")
    if len(mask) != len(f):
        raise ValueError("mask length must equal len(f).")

    n_fft = 2 * (len(f) - 1)   # one-sided STFT size
    if hop_length is None:
        if len(t) > 1:
            # infer hop from time step
            hop_length = int(round(np.mean(np.diff(t)) * sr))
        else:
            hop_length = n_fft // 4  # fallback
    noverlap = n_fft - hop_length

    # Split magnitude and phase
    eps = 1e-12
    mag = np.abs(Zxx)
    phase = Zxx / np.maximum(mag, eps)  # unit-magnitude complex phase

    # Compute peak magnitude for relative dB scaling
    mag_peak = float(np.max(mag) + eps)
    if drop_to_db is None:
        drop_to_db = float(top_db)
    floor_mag = mag_peak * (10.0 ** (-(drop_to_db) / 20.0))  # amplitude floor

    # Apply mask in magnitude domain (False -> floor)
    mag_masked = mag.copy()
    mag_masked[~mask, :] = floor_mag

    # For plotting: convert to relative dB and clip to [-top_db, 0]
    S_db = 20.0 * np.log10(np.maximum(mag_masked, eps) / mag_peak)
    S_db = np.maximum(S_db, -float(top_db))


    # Save PNG
    plt.figure(figsize=(10, 4))
    plt.pcolormesh(t, f, S_db, shading="gouraud", vmin=-float(top_db), vmax=0.0)
    cbar = plt.colorbar()
    cbar.set_label("dB (relative to peak)")
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    plt.ylim(f[0], f[np.where(mask)[0][-1] + 1])
    plt.title("Masked spectrogram (rel. peak)")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()

    # Reconstruct complex STFT with original phase
    Zxx_masked = mag_masked * phase

    # ISTFT (use same n_fft/hop/window family as used in STFT)
    win = get_window(window, n_fft, fftbins=True)
    _, y_rec = istft(
        Zxx_masked,
        fs=sr,
        window=win,
        nperseg=n_fft,
        noverlap=noverlap,
        input_onesided=True,
        boundary=None
    )

    # Save WAV
    if wav_dtype == "int16":
        y_clip = np.clip(y_rec, -1.0, 1.0)
        wavfile.write(out_wav, sr, (y_clip * 32767.0).astype(np.int16))
    elif wav_dtype == "float32":
        wavfile.write(out_wav, sr, y_rec.astype(np.float32))
    else:
        raise ValueError("wav_dtype must be 'int16' or 'float32'")

    return y_rec


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


# python -c "import generate_audio_waves; generate_audio_waves.single_wave_wav(500)"
def single_wave_wav(freq):
    # Parameters
    sample_rate = 44100  # CD quality
    duration = 3.0       # seconds
    frequency = freq   # Hz

    # Generate time axis
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Generate sine wave
    signal = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Save as WAV file
    output_path = "docs/assets/single_" + str(freq) + "hz_wave.wav"
    wav.write(output_path, sample_rate, (signal * 32767).astype(np.int16))

    save_waveform(signal, sample_rate, 0.01, "docs/assets/single_" + str(freq) + "hz_wave.png")

# python -c "import generate_audio_waves; generate_audio_waves.reconstructed_E2_wav()"
def reconstructed_E2_wav():
    y, sr = load_audio('./docs/assets/E2_guitar.m4a')
    
    n_fft = 4096
    hop_length = 1024
    w = get_window("hann", n_fft, fftbins=True)
    noverlap = n_fft - hop_length
    f, t, Zxx = stft(y, fs=sr, window=w, nperseg=n_fft, noverlap=noverlap,
                     boundary=None, padded=False)
    
    df = sr / n_fft
    freqs = [82, 164, 246, 328, 410]
    mask = abs(f - freqs[0]) <= df / 2 
    for freq in freqs:
        m1 = abs(f - freq) <= df / 2
        mask = mask | m1

    mask_spectrogram_and_reconstruct(
        Zxx, f, t, sr, mask,
        top_db=80,
        drop_to_db=None,             # if None, uses top_db
        window="hann",
        hop_length=None,             # if None, inferred from t (preferred) or set to n_fft//4
        out_png="./docs/assets/E2_masked_spectrogram.png",
        out_wav="./docs/assets/E2_masked_audio.wav",
        wav_dtype="int16"            # "int16" or "float32"
    )


# python -c "import generate_audio_waves; generate_audio_waves.analyze_audio_file('./docs/assets/E2_guitar.m4a')"
def analyze_audio_file(path): 
    y, sr = load_audio(path)
    f, t, S_db = stft_db_relative(y, sr, n_fft=4096, hop_length=1024, window="hann", top_db=80)
    save_spectrogram(f, t, S_db, sr, top_db=80,
                        title=f"Spectrogram (rel. peak, {os.path.basename(path)})", 
                        spectrogram_path="".join(os.path.splitext(path)[0:-1]) + "_spectrogram.png",
                        fmin = 0,
                        fmax = 8000)
    save_waveform(y, sr, 0.1, "".join(os.path.splitext(path)[0:-1]) + "_waveform.png")
