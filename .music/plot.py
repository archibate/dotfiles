#!/usr/bin/python


import numpy as np
import pyaudio
import matplotlib.pyplot as plt


chunk_size = 12000
fs = 48000
window_size = 48000
smoothing_window_size = 384
frequency_bins = 24000


# -24 dBFS = -5 dB (FFT)


p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs, input=True, frames_per_buffer=chunk_size)


def apply_log_scale_and_smoothing(magnitude_spectrum, smoothing_window_size):
    filter = np.blackman(smoothing_window_size)
    magnitude_spectrum = np.convolve(magnitude_spectrum, filter / filter.sum(), mode='same')
    magnitude_spectrum = 20 * np.log10(magnitude_spectrum + 1e-10)  # Add a small constant to avoid log(0)
    return magnitude_spectrum


audio_chunk = np.zeros(window_size, dtype=np.float32)

def get_response():
    global audio_chunk
    current_chunk = np.frombuffer(stream.read(chunk_size), dtype=np.float32)
    audio_chunk = np.concatenate([audio_chunk, current_chunk], axis=0)[-window_size:]
    windowed_chunk = audio_chunk * np.hanning(len(audio_chunk))

    fft_freq = np.fft.fftfreq(len(windowed_chunk), 1 / fs)
    fft_result = np.fft.fft(windowed_chunk)

    fft_freq = fft_freq[:len(fft_result) // 2]
    fft_result = fft_result[:len(fft_result) // 2]

    new_freq = np.logspace(np.log10(20), np.log10(20000), frequency_bins)
    fft_result = np.abs(fft_result)
    new_result = np.interp(new_freq, fft_freq, fft_result)

    magnitude_spectrum = apply_log_scale_and_smoothing(new_result, smoothing_window_size)

    return new_freq, magnitude_spectrum


plt.ion()
fig, ax = plt.subplots()
x, y = get_response()
line, = ax.plot(x, y)
ax.set_xlim(20, 20000)
ax.set_xscale('log')
ax.set_xlabel('Frequency [Hz]')
ax.set_ylim(-60, 40)
ax.set_ylabel('Magnitude [dB]')

for i in range(10000):
    if not plt.fignum_exists(fig.number):  # type: ignore
        break
    x, y = get_response()
    line.set_xdata(x)
    line.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.001)

print("Figure closed, exiting.")
