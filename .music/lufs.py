#!/usr/bin/python

import glob
import pyloudnorm
import multiprocessing
import numpy as np
import mutagen.flac
import mutagen.mp3
import pydub
import os


def show_audio(path):
    segment: pydub.AudioSegment = pydub.AudioSegment.from_file(path)
    size = os.stat(path).st_size
    duration = segment.frame_count() / segment.frame_rate
    print(f'{path} | {segment.sample_width * 8}bit {segment.frame_rate / 1000:.1f}KHz {size / duration / 1000:.0f}kbps')


def read_audio(path):
    segment: pydub.AudioSegment = pydub.AudioSegment.from_file(path)
    audio = np.array(segment.get_array_of_samples())
    audio = audio.astype(np.float64) / (1 << (segment.sample_width * 8 - 1))
    rate = segment.frame_rate
    return audio, rate


def calculate_lufs(audio, rate):
    meter = pyloudnorm.Meter(rate)
    loudness = meter.integrated_loudness(audio)
    return loudness


def calculate_peak(audio):
    return max(audio.max(), -audio.min())


def show_lufs(path):
    audio, rate = read_audio(path)
    lufs = calculate_lufs(audio, rate)
    if lufs is None:
        lufs = 0
    peak = calculate_peak(audio)
    print(f'{path} | LUFS {lufs:+.2f} dB | Peak {peak:.6f}')
    return lufs


def apply_lufs(path, target=-20):
    audio, rate = read_audio(path)
    lufs = calculate_lufs(audio, rate)
    if lufs is None:
        lufs = target
    peak = calculate_peak(audio)
    print(f'{path} | LUFS {lufs:+.2f} dB | Peak {peak:.6f}')
    gain = target - lufs
    set_replaygain(path, gain, peak)
    return lufs


def set_replaygain(path, gain, peak):
    if path.endswith('.flac'):
        audio = mutagen.flac.FLAC(path)
        audio["REPLAYGAIN_TRACK_GAIN"] = f"{gain:.2f} dB"
        audio["REPLAYGAIN_TRACK_PEAK"] = f"{peak:.6f}"
        audio.save()
    elif path.endswith('.mp3'):
        audio = mutagen.mp3.Open(path)
        audio["TXXX:REPLAYGAIN_TRACK_GAIN"] = f"{gain:.2f} dB"
        audio["TXXX:REPLAYGAIN_TRACK_PEAK"] = f"{peak:.6f}"
        audio.save()


def show_replaygain(path):
    if path.endswith('.flac'):
        audio = mutagen.flac.FLAC(path)
        print(f'{path} | Gain {audio["REPLAYGAIN_TRACK_GAIN"]} Peak {audio["REPLAYGAIN_TRACK_PEAK"]}')
    elif path.endswith('.mp3'):
        audio = mutagen.mp3.Open(path)
        print(f'{path} | Gain {audio["TXXX:REPLAYGAIN_TRACK_GAIN"]} Peak {audio["TXXX:REPLAYGAIN_TRACK_PEAK"]}')


pool = multiprocessing.Pool(multiprocessing.cpu_count() // 2)
paths = glob.glob('*.flac') + glob.glob('*.mp3')
pool.map(show_lufs, paths)
