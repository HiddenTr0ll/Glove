import settings
from settings import *
from mido import Message, MetaMessage, MidiFile, MidiTrack, second2tick, bpm2tempo
from os import listdir
import csv
from itertools import islice
from sortedcontainers import SortedDict
import pyrr

maxDataCount = 1000000


class Recorder():

    def __init__(self):
        self.keyRecordingFile: MidiFile
        self.keyRecordingFile = None
        self.keyRecordingTrack: MidiTrack
        self.keyRecordingTrack = None
        self.lastTick = 0
        self.recordingKeys = False
        self.recordingMovement = False
        self.movementData = None
        self.movementCount = 0
        self.keyCount = 0
        self.playbackData = None
        self.playbackDict = None
        self.playingMovement = False
        self.playbackPaused = True
        self.loadedLines = 0
        self.playbackProgress = None
        self.lastMovement = None

    def startKeyRecording(self):
        if not self.recordingKeys:
            self.keyRecordingFile = MidiFile()
            self.keyRecordingTrack = MidiTrack()
            self.keyRecordingFile.tracks.append(self.keyRecordingTrack)
            self.ticks_per_beat = self.keyRecordingFile.ticks_per_beat  # default: 480
            bpm = 120  # default midi tempo
            self.tempo = bpm2tempo(bpm)
            self.keyRecordingTrack.append(MetaMessage('set_tempo', tempo=self.tempo))
            self.keyRecordingTrack.append(MetaMessage('time_signature', numerator=4, denominator=4))
            self.keyRecordingTrack.append(Message('program_change', program=12, time=0))
            self.lastTick = glfw.get_time()
            self.keyCount = 0
            self.recordingKeys = True

    def recordKeys(self, toPress, toRelease):
        if self.recordingKeys:
            delta = second2tick(glfw.get_time() - self.lastTick, self.ticks_per_beat, self.tempo)
            keyIndex: int
            for keyIndex in toPress:
                self.keyRecordingTrack.append(Message("note_on", note=48+keyIndex, velocity=64, time=delta))
                delta = 0
            for keyIndex in toRelease:
                self.keyRecordingTrack.append(Message("note_off", note=48+keyIndex, velocity=64, time=delta))
                delta = 0
            keysPressed = len(toPress) + len(toRelease)
            if keysPressed > 0:
                self.lastTick = glfw.get_time()
                self.keyCount += keysPressed

    def stopKeyRecording(self):
        if self.recordingKeys:
            self.keyRecordingTrack.append(MetaMessage('end_of_track'))
            self.recordingKeys = False

    def saveKeyRecording(self, filename):
        if self.keyCount > 0:
            self.keyRecordingFile.save("midis/"+filename+'.mid')

    def startMovementRecording(self):
        if not self.recordingMovement:
            self.movementCount = 0
            self.movementData = np.zeros((maxDataCount, 9))
            self.recordingMovement = True

    def stopMovementRecording(self):
        if self.recordingMovement:
            self.recordingMovement = False

    def recordMovement(self, data):
        if self.recordingMovement:
            self.movementData[self.movementCount] = data
            self.movementCount += 1

    def saveMovementRecording(self, filename):
        if self.movementCount > 0:
            self.movementData = self.movementData[:self.movementCount]
            self.movementData[:, 1] -= np.min(self.movementData[:, 1])

            print("\nwriting to file...")

            if True:
                dataToWrite = [[int(round(d[1])), int(d[0]), d[2], d[3], d[4], d[5]]for d in self.movementData]
            else:
                dataToWrite = [[int(round(d[1])), int(d[0]), d[2], d[3], d[4], d[5], d[6], d[7], d[8]] for d in self.movementData]

            try:
                with open("recordings/"+filename+'.csv', "w") as csvfile:
                    csvfile.write("Sensors: lowerArm (0), thumb (1), index (2), mid (3), ring (4), pinky (5), palm (6)\n")
                    if True:
                        csvfile.write("Tick, Sensor, QuatI, QuatJ, QuatK, QuatSum\n")
                    else:
                        csvfile.write("Sensor, Tick, QuatI, QuatJ, QuatK, QuatSum, AccX, AccY, AccZ\n")

                    csv_writer = csv.writer(csvfile,
                                            delimiter=",",
                                            lineterminator="\n")
                    csv_writer.writerows(dataToWrite)
            except Exception as e:
                print("Error in write_CSV:")
                print(e)
                return 0
            return 1

    def startMovementPlayback(self, file):
        settings.disconnectGlove()
        try:
            with open("recordings/"+file) as csvfile:
                self.loadedLines = sum(1 for line in csvfile)-2
                if self.loadedLines <= 1:
                    raise Exception("No Data in CSV")
                csvfile.seek(0)
                for _ in range(2):  # skip header
                    next(csvfile)
                reader = csv.reader(csvfile)
                self.playbackDict = SortedDict()
                self.playbackData = np.zeros((self.loadedLines, 5))
                for index, row in enumerate(reader):
                    if int(row[0]) in self.playbackDict:  # if timestamp in dict
                        self.playbackDict[int(row[0])].append(index)
                    else:
                        self.playbackDict[int(row[0])] = [index]
                    self.playbackData[index] = row[1:]
        except Exception as e:
            print("Error in read CSV:")
            print(e)
        print(self.loadedLines, "lines of Data loadet")
        self.playingMovement = True
        self.playbackPaused = True
        self.playbackProgress = 0
        self.lastMovement = glfw.get_time()
        self.emulateMovement(True)

    def pauseMovementPlayback(self):
        self.playbackPaused = not self.playbackPaused
        if not self.playbackPaused:
            self.lastMovement = glfw.get_time()

    def stopMovementPlayback(self):
        self.playbackData = None
        self.playingMovement = False
        self.playbackPaused = True

    def setPlaybackProgress(self, progress):
        self.playbackProgress = progress
        self.lastMovement = glfw.get_time()
        pass

    def emulateMovement(self, forced):
        if not self.playbackPaused or forced:
            currentTick = 1000 * self.playbackProgress
            # check if playback is over
            if max(self.playbackDict) < currentTick:
                self.playbackPaused = True

            tick = closestTick(self.playbackDict, currentTick)
            for index in self.playbackDict[tick]:
                settings.rotationList[int(self.playbackData[index][0])] = pyrr.matrix44.create_from_quaternion(self.playbackData[index][1:])

            if tick > 0:  # if there is a previous tick
                neighbourTick = previousTick(self.playbackDict, tick)
            else:
                neighbourTick = nextTick(self.playbackDict, tick)
            for index in self.playbackDict[neighbourTick]:
                settings.rotationList[int(self.playbackData[index][0])] = pyrr.matrix44.create_from_quaternion(self.playbackData[index][1:])

            currentTime = glfw.get_time()
            delta = currentTime - self.lastMovement
            self.playbackProgress = self.playbackProgress+delta
            self.lastMovement = currentTime


def closestTick(sorted_dict, target):
    # only element 0 of part of dict from min -> end
    ticks = list(islice(sorted_dict.irange(minimum=target), 1))
    ticks.extend(islice(sorted_dict.irange(maximum=target, reverse=True), 1))
    # key(k)=abs(target - k) -> select value with the minimum difference to target
    return min(ticks, key=lambda k: abs(target - k))


def previousTick(sorted_dict, target):
    return list(islice(sorted_dict.irange(maximum=target, reverse=True), 2))[1]


def nextTick(sorted_dict, target):
    return list(islice(sorted_dict.irange(minimum=target), 2))[1]
