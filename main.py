from MidiController import MidiController
from Macro import loadMacros
from pygame.midi import MidiException
import time
import argparse

parser = argparse.ArgumentParser(description='Atem MIDI Surface')
parser.add_argument('-m', type=str, default='macros.yml',
                    help='the macro file to load', metavar="macros.yml")

args = parser.parse_args()

try:
    controller = MidiController(0, 1, False)
except MidiException:
    print("Error initialising MIDI")
    exit()

try:
    macros = loadMacros(controller, path="macros/{}".format(args.m))
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