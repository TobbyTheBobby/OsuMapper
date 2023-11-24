class BeatMap:
    def __init__(self, file_path):
        content = open(file_path, "r")
        self.File = content
        self.GeneralInfo = GeneralInfo(content)
        self.MetaData = MetaData(content)
        self.TimingPoints = get_timing_points(content)
        self.HitObjects = get_hit_objects(content)

        self.ContentLines = self.content_lines_without_hit_objects(open(file_path, "r").readlines())

    def __str__(self):
        description = self.MetaData.Title + " by " + self.MetaData.Artist

        return description

    def content_lines_without_hit_objects(self, lines):
        timing_points_index = None

        for i, line in enumerate(lines):
            if "[HitObjects]" in line:
                timing_points_index = i
                break

        return lines[:timing_points_index + 1]


class GeneralInfo:
    def __init__(self, content):
        self.AudioFilename = str(value_from_key(content, "AudioFilename")[1:])
        self.AudioLeadIn = int(value_from_key(content, "AudioLeadIn"))
        self.PreviewTime = int(value_from_key(content, "PreviewTime"))
        self.Countdown = int(value_from_key(content, "Countdown"))
        self.SampleSet = str(value_from_key(content, "SampleSet"))
        self.StackLeniency = float(value_from_key(content, "StackLeniency"))
        self.Mode = int(value_from_key(content, "Mode"))
        self.LetterboxInBreaks = int(value_from_key(content, "LetterboxInBreaks"))
        self.WidescreenStoryboard = int(value_from_key(content, "WidescreenStoryboard"))


class Editor:
    def __init__(self, content):
        self.Bookmarks = list(value_from_key(content, "Bookmarks").split(","))
        self.DistanceSpacing = float(value_from_key(content, "DistanceSpacing"))
        self.BeatDivisor = int(value_from_key(content, "BeatDivisor"))
        self.GridSize = int(value_from_key(content, "GridSize"))
        self.TimelineZoom = float(value_from_key(content, "TimelineZoom"))


class MetaData:
    def __init__(self, content):
        self.Title = value_from_key(content, "Title")
        self.Artist = value_from_key(content, "Artist")


class TimingPoint:
    def __init__(self, content_row):
        data = content_row.split(",")
        self.Time = int(data[0])
        self.BeatLength = float(data[1])
        self.BPM = 60 / self.BeatLength
        self.Meter = int(data[2])
        self.SampleSet = int(data[3])
        self.SampleIndex = int(data[4])
        self.Volume = int(data[5])
        self.Uninherited = int(data[6])
        self.Effects = int(data[7])


class HitObject:
    def __init__(self, content_row):
        data = content_row.split(",")
        self.X = int(data[0])
        self.Y = int(data[1])
        # converts integer to list of individual bit values
        self.Type = [int(x) for x in '{0:07b}'.format(int(data[2]))]
        self.HitSound = [int(x) for x in '{0:07b}'.format(int(data[3]))]
        self.ObjectParams = data[4]
        self.HitSample = data[5]


def value_from_key(content, key):
    for sentence_row in content:
        sentence_row = sentence_row.replace("\n", "")
        if key in sentence_row:
            return sentence_row.split(":")[1]


def get_timing_points(content):
    for content_row in get_section_rows(content, "TimingPoints"):
        yield TimingPoint(content_row)


def get_hit_objects(content):
    for content_row in get_section_rows(content, "HitObjects"):
        yield HitObject(content_row)


def get_section_rows(content, section_key):
    adding_data = False

    for content_row in content:

        print(adding_data)
        print(content_row)

        if adding_data and content_row == "\n":
            break

        content_row = content_row.replace("\n", "")

        if adding_data:
            yield content_row
            continue

        section_header = "[" + section_key + "]"

        if section_header in content_row:
            adding_data = True
