import math
import os
import random
import wave

import soundfile as sf

from scripts.audio_utilities.audio_utilities import convert_mp3_to_wav, play_wave_file, generate_seperated_audio_files
from scripts.files_service.beat_map import BeatMap
from scripts.files_service.file_service import FileService


def main():
    file_service = FileService()

    for song_folder in file_service.get_song_folders():
        print(song_folder.FolderPath)
        for beat_map in song_folder.BeatMaps:
            print(beat_map.GeneralInfo.AudioFilename)

            src_audio = os.path.join(song_folder.FolderPath, beat_map.GeneralInfo.AudioFilename)
            dst_audio = src_audio.replace(".mp3", ".wav")

            if not os.path.exists(dst_audio):
                convert_mp3_to_wav(src_audio, dst_audio)

            # play_wave_file(wave.open(dst_audio, 'rb'))

            # print(beat_map)
            # for timing_point in beat_map.TimingPoints:
            #     print(timing_point.BeatLength)

            generate_seperated_audio_files(song_folder, src_audio)

            # exit()

            drum_signal, drum_samplerate = sf.read(os.path.join(song_folder.WavFileFolder, "drums.wav"),
                                                   dtype='float32')
            bass_signal, bass_samplerate = sf.read(os.path.join(song_folder.WavFileFolder, "bass.wav"), dtype='float32')
            vocals_signal, vocals_samplerate = sf.read(os.path.join(song_folder.WavFileFolder, "vocals.wav"),
                                                       dtype='float32')
            other_signal, other_samplerate = sf.read(os.path.join(song_folder.WavFileFolder, "other.wav"),
                                                     dtype='float32')

            # plot_signal(signal)

            combined_beats = []

            combined_beats += list(get_segmented_unique_beats(drum_signal, drum_samplerate, beat_map))
            combined_beats += list(get_segmented_unique_beats(bass_signal, bass_samplerate, beat_map))
            combined_beats += list(get_segmented_unique_beats(vocals_signal, vocals_samplerate, beat_map))
            combined_beats += list(get_segmented_unique_beats(other_signal, other_samplerate, beat_map))

            random.shuffle(combined_beats)

            unique_times_beats = filter_duplicates(combined_beats, 419.58041958042 / 4)
            # unique_times_beats = list(combined_beats)

            lines = beat_map.ContentLines

            sorted_unique_beats = sorted(unique_times_beats, key=lambda x: x.Time, reverse=False)

            current_x = 250
            current_y = 250
            step_size = 100
            box_width = 512
            box_height = 385

            for beat in sorted_unique_beats:
                current_x, current_y = move_within_bounds(current_x, current_y, step_size, box_width, box_height)

                lines.append(
                    (str(int(current_x)) +
                     "," +
                     str(int(current_y)) +
                     "," +
                     str(beat.Time) +
                     ",1,0,0:0:0:0:\n"))

            generated_file_name = beat_map.MetaData.Artist + " - " + beat_map.MetaData.Title + " [Generated].osu"

            with open(os.path.join(song_folder.FolderPath, generated_file_name), "w") as file:
                file.writelines(lines)

            break


def move_within_bounds(current_x, current_y, step_size, box_width, box_height):
    # Randomize the angle within a certain range
    angle = random.uniform(0, 360)

    # Convert angle to radians
    angle_radians = math.radians(angle)

    # Calculate the new position
    new_x = current_x + step_size * math.cos(angle_radians)
    new_y = current_y + step_size * math.sin(angle_radians)

    # Check if the new position is within bounds
    if 0 <= new_x <= box_width and 0 <= new_y <= box_height:
        return new_x, new_y
    else:
        # If the new position is outside the bounds, reflect the position
        # to stay within the bounds
        new_x = max(0, min(new_x, box_width))
        new_y = max(0, min(new_y, box_height))

        # Change the direction by 180 degrees
        new_angle = (angle + 180) % 360
        new_angle_radians = math.radians(new_angle)

        # Calculate the new position after reflecting
        reflected_x = new_x + step_size * math.cos(new_angle_radians)
        reflected_y = new_y + step_size * math.sin(new_angle_radians)

        return reflected_x, reflected_y


def filter_duplicates(beats, distance_between_notes):
    seen_times = set()

    # distance_between_notes = list(beat_map.TimingPoints)[0].BPM

    # Keeping only unique times and filtering out beats within 45 units of existing beats
    for beat in beats:
        should_add = all(abs(beat.Time - existing_time) > distance_between_notes for existing_time in seen_times)
        if should_add:
            seen_times.add(beat.Time)
            yield beat


def get_segmented_unique_beats(signal, samplerate, beat_map):
    beats = []

    for index, item in enumerate(signal):
        item = item[0]

        beat = Beat(int(index / samplerate * 1000), item)
        beats.append(beat)
        # print(str(int(index / samplerate * 1000)) + ":  " + str(item))

    segment_length = int(0.41958041958042 * 16 * samplerate)

    # Split drum_signal into segments
    segments = [beats[i:i + segment_length] for i in range(0, len(beats), segment_length)]

    test = []

    # Process each segment using get_unique_beats
    for segment in segments:
        test += get_unique_beats(segment, samplerate, beat_map)

    return test


def get_unique_beats(beats, samplerate, beat_map):
    # Sorting beats based on values in descending order
    sorted_beats = sorted(beats, key=lambda x: x.Value, reverse=True)

    # Calculating the index to keep the top 1% of beats
    top_1_percent_index = int(0.0003 * len(sorted_beats))

    # Selecting the top 1% of beats
    top_1_percent_beats = sorted_beats[:top_1_percent_index]

    # Sorting the top_1_percent_beats based on time
    sorted_top_1_percent_beats = sorted(top_1_percent_beats, key=lambda x: x.Time)

    unique_times_beats = filter_duplicates(sorted_top_1_percent_beats, 419.58041958042 / 4)

    return unique_times_beats


class Beat:

    def __init__(self, time, value):
        self.Time = time
        self.Value = value


if __name__ == '__main__':
    main()
