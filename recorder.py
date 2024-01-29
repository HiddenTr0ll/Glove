import settings
from settings import *
from mido import Message, MetaMessage, MidiFile, MidiTrack

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

    def startMovementPlayback(self):
        pass

    def pauseMovementPlayback(self):
        pass

    def stopmovementPlayback(self):
        pass
