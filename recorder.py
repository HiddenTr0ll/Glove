import settings
from settings import *
from mido import Message, MetaMessage, MidiFile, MidiTrack
from os import listdir
import csv

dataCount = 1000000


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

    def startKeyRecording(self):
        if not self.recordingKeys:
            self.keyRecordingFile = MidiFile()
            self.keyRecordingTrack = MidiTrack()
            self.keyRecordingFile.tracks.append(self.keyRecordingTrack)
            self.keyRecordingTrack.append(Message('program_change', program=12, time=0))
            self.lastTick = glfw.get_time()
            self.keyCount = 0
            self.recordingKeys = True

    def recordKeys(self, toPress, toRelease):
        if self.recordingKeys:
            delta = int(1000*(glfw.get_time() - self.lastTick))
            keyIndex: int
            for keyIndex in toPress:
                self.keyRecordingTrack.append(Message("note_on", note=48+keyIndex, velocity=64, time=delta))
            for keyIndex in toRelease:
                self.keyRecordingTrack.append(Message("note_off", note=48+keyIndex, velocity=64, time=delta))
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
            self.movementData = np.zeros((dataCount, 9))
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
                self.playbackDict = {}
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

    def pauseMovementPlayback(self):
        self.playbackPaused = not self.playbackPaused

    def stopMovementPlayback(self):
        self.playbackData = None
        self.playingMovement = False
        self.playbackPaused = True

    def updateMovement(self):
        if not self.playbackPaused:
            pass
            # TODO implement rotationlist updates here
