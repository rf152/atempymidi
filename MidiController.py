import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import midi
import time

class MidiController:
    def __init__(self, input, output, flash=True):
        midi.init()
        while not midi.get_init():
            pass

        self._midiIn = midi.Input(input)
        self._midiOut = midi.Output(output)

        if flash:
            for i in (5,3,1,0):
                for j in range(64):
                    self._midiOut.note_on(j, i)
                    time.sleep(0.01)
    def close(self):
        self._midiIn.close()
        self._midiOut.close()
        midi.quit()
    
    def lightOn(self, note, colour, flash=False):
        colours = {"green": 1, "amber": 5, "red": 3}
        try:
            velocity = colours[colour]
            if flash:
                velocity += 1
            self._midiOut.note_on(note, velocity)
        except KeyError:
            return
        

    def lightOff(self, note):
        self._midiOut.note_on(note, 0)
        time.sleep(0.01)
    
    def allOff(self):
        for i in range(64):
            self.lightOff(i)
    
    def registerCallback(self, callable):
        self._callback = callable
    
    def hasEvent(self):
        return self._midiIn.poll()

    def getEvent(self):
        if self._midiIn.poll():
            msgin = self._midiIn.read(1)
            msg, note = (msgin[0][0][0], msgin[0][0][1])
            if not msg == 128:
                return None
            return note
        else:
            return None
