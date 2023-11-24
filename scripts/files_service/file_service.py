import os

from scripts.files_service.beat_map import BeatMap


SongFolderLocation = "C:\\Users\\jordy\\AppData\\Local\\osu!\\Songs"


class FileService:
    def __init__(self):
        test = 1

    def get_song_folders(self):
        for file_location in os.listdir(SongFolderLocation):
            file_location = os.path.join(SongFolderLocation, file_location)
            if os.path.isdir(file_location):
                yield SongFolder(file_location)


class SongFolder:
    def __init__(self, folder_name):
        self.FolderPath = folder_name
        self.FileNames = os.listdir(self.FolderPath)
        self.BeatMaps = self.get_beat_maps()
        self.WavFileFolder = self.create_wav_file_folder()

    def get_beat_maps(self):
        for file_name in self.FileNames:
            if ".osu" in file_name:
                file_path = os.path.join(self.FolderPath, file_name)
                yield BeatMap(file_path)

    def create_wav_file_folder(self):
        wav_file_folder_location = os.path.join(self.FolderPath, "wav_file_folder")
        if not os.path.exists(wav_file_folder_location):
            os.mkdir(wav_file_folder_location)
        return wav_file_folder_location
