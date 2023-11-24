import os.path

import pyaudio
import scipy
from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator
from matplotlib import pyplot as plt
from pydub import AudioSegment

CHUNK = 1024

audio_tracks = ["drums", "bass", "vocals", "other"]


def convert_mp3_to_wav(source, destination):
    sound = AudioSegment.from_mp3(source)
    sound.export(destination, format="wav")


def generate_seperated_audio_files(song_folder, src_audio):
    if all(os.path.isfile(os.path.join(song_folder.WavFileFolder, audio_track + ".wav")) for audio_track in audio_tracks):
        return

    # Using embedded configuration.
    # separator = Separator('spleeter:2stems')
    separator = Separator('spleeter:4stems')
    # separator = Separator('spleeter:5stems')

    audio_loader = AudioAdapter.default()
    sample_rate = 44100
    waveform, _ = audio_loader.load(src_audio, sample_rate=sample_rate)

    # Perform the separation :
    prediction = separator.separate(waveform)

    # separator.separate_to_file(src_audio, song_folder + "/seperatedAudio")

    for audio_track in audio_tracks:
        wav_file_path = os.path.join(song_folder.WavFileFolder, audio_track + ".wav")
        scipy.io.wavfile.write(wav_file_path, 44100, prediction[audio_track])

        # play_wave_file(wave.open(wav_file_path, 'rb'))


def play_wave_file(wave_file):
    # Instantiate PyAudio and initialize PortAudio system resources (1)
    p = pyaudio.PyAudio()

    # Open stream (2)
    stream = p.open(format=p.get_format_from_width(wave_file.getsampwidth()),
                    channels=wave_file.getnchannels(),
                    rate=wave_file.getframerate(),
                    output=True)

    # Play samples from the wave file (3)
    while len(data := wave_file.readframes(CHUNK)):  # Requires Python 3.8+ for :=
        stream.write(data)

    # Close stream (4)
    stream.close()

    # Release PortAudio system resources (5)
    p.terminate()


def plot_audio_signal(signal):
    plt.figure(1)
    plt.title("Signal Wave...")
    plt.plot(signal)
    plt.show()
