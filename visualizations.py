import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def sin_wave_DFT():
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

# python -c "import visualizations; visualizations.sin_pressure_wave_gif()"
def sin_pressure_wave_gif():
	# Parameters
	frames = 100
	x = np.linspace(0, 4*np.pi, 500)
	wave_speed = 0.2

	# Particle setup
	n_particles = 500
	particles_x = np.linspace(0, 4*np.pi, n_particles)
	particles_y = np.random.rand(n_particles) * 3 - 1.5

	# Figure setup
	fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

	# Sin wave plot
	line, = ax1.plot([], [], lw=2)
	ax1.set_xlim(0, 4*np.pi)
	ax1.set_ylim(-1.5, 1.5)
	ax1.set_title("Sound Wave as a Sinusoid")

	# Particle plot
	scat = ax2.scatter(particles_x, particles_y, c="blue")
	ax2.set_xlim(0, 4*np.pi)
	ax2.set_ylim(-1.5, 1.5)
	ax2.set_title("Pressure wave paassing through air particles")

	def init():
	    line.set_data([], [])
	    scat.set_offsets(np.c_[particles_x, particles_y])
	    return line, scat

	def animate_longitudinal(i):
	    t = i * wave_speed
	    y = np.sin(x - t)
	    line.set_data(x, y)
	    
	    # Particles oscillate horizontally (longitudinal motion)
	    particle_x = particles_x + 0.5 * np.sin(particles_x - t) - 1
	    scat.set_offsets(np.c_[particle_x, particles_y])
	    
	    return line, scat

	ani_longitudinal = animation.FuncAnimation(fig, animate_longitudinal, init_func=init, frames=frames, interval=50, blit=True)

	# Save as GIF
	gif_path_longitudinal = "assets/sin_pressure_wave.gif"
	ani_longitudinal.save(gif_path_longitudinal, writer="pillow")

