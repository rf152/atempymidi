from MidiController import MidiController
from Macro import loadMacros
from pygame.midi import MidiException
import time

try:
    controller = MidiController(0, 1)
except MidiException:
    print("Error initialising MIDI")
    exit()

try:
    macros = loadMacros(controller)
    while True:
        time.sleep(0.0001)
        if controller.hasEvent():
            note = controller.getEvent()
            if note is not None:
                try:
                    macro = macros[note]
                except IndexError:
                    continue
                macro.run(controller)
except KeyboardInterrupt:
    pass
finally:
    controller.allOff()
    controller.close()