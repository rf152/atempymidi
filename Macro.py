from pythonosc import udp_client
import time

import yaml

import threading

import simpleaudio as sa

client = udp_client.SimpleUDPClient("127.0.0.1", 3333)

def loadMacros(controller, path="macros.yml"):
    macros = []
    with open(path, "r") as stream:
        try:
            yml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for id in range(64):
    # for id, macro in yml["macros"].items():
        try:
            macro = yml["macros"][id]
            _macro = Macro(macro, id)
            controller.lightOn(id, _macro.colour)
        except KeyError:
            _macro = NoMacro()
        macros.insert(id, _macro)

    
    return macros


class InvalidMacroConfigException(Exception):
    pass


class MacroStep:
    def __init__(self, yml):
        if yml["type"] not in ("sleep", "osc", "audio"):
            raise KeyError
        self._type = yml["type"]

        if yml["type"] == "sleep":
            self._duration = yml["duration"]
        
        if yml["type"] == "osc":
            self._path = yml["path"]
        
        if yml["type"] == "audio":
            self._path = yml["path"]
    def run(self):
        if self._type == "osc":
            client.send_message(self._path, None)
        elif self._type == "sleep":
            time.sleep(self._duration)
        elif self._type == "audio":
            self._playing = True
            wave_obj = sa.WaveObject.from_wave_file(self._path)
            play_obj = wave_obj.play()
            while self._playing and play_obj.is_playing():
                pass
            if play_obj.is_playing():
                play_obj.stop()
    def stop(self):
        self._playing = False

class Macro:
    _runningSem = threading.Semaphore()
    _stepSem = threading.Semaphore()
    _stopSem = threading.Semaphore()
    _stop = False
    _running = False
    colour = "green"

    def __init__(self, yml, id):
        self._id = id
        try:
            self._name = yml["name"]
        except KeyError:
            raise InvalidMacroConfigException("Invalid Macro Config")
        try:
            assert(len(yml["steps"]) > 0)
            self._steps = []
            for step in yml["steps"]:
                self._steps.append(MacroStep(step))
        except:
            raise InvalidMacroConfigException("Invalid Macro Config in macro '{}'".format(self._name))
        
        try:
            self.colour = yml["colour"]
        except KeyError:
            pass
        self._running = False
        
    def run(self, controller):
        self._runningSem.acquire()
        if self._running:
            self.stop()
            self._runningSem.release()
            return
        self._runningSem.release()
        thread = threading.Thread(target=self._threadRun, args=(controller,))
        thread.start()

    def stop(self):
        self._stepSem.acquire()
        self._stopSem.acquire()
        self._stop = True
        self._stopSem.release()
        i = self._step
        self._steps[i].stop()
        self._stepSem.release()

    def _threadRun(self, controller):
        self._runningSem.acquire()
        if self._running:
            return
        self._running = True
        self._runningSem.release()
        self._stopSem.acquire()
        if self._stop:
            self._stopSem.release()
            self._runningSem.acquire()
            self._running = False
            self._runningSem.release()
            controller.lightOn(self._id, self.colour, False)
            return
        self._stopSem.release()
        controller.lightOn(self._id, self.colour, True)
        for i in range(len(self._steps)):
            self._stepSem.acquire()
            self._step = i
            self._stepSem.release()
            step = self._steps[i]
            step.run()
        controller.lightOn(self._id, self.colour, False)
        self._runningSem.acquire()
        self._running = False
        self._runningSem.release()
        self._stopSem.acquire()
        self._stop = False
        self._stopSem.release()

    def __str__(self):
        return "Macro '{}'".format(self._name)
    def __unicode__(self):
        return u"Macro '{}'".format(self._name)
    def __repr__(self):
        return u"Macro '{}'".format(self._name)

class NoMacro:
    def run(self, controller):
        pass
    def stop(self):
        pass

    def __str__(self):
        return "Not a Macro"
    def __unicode__(self):
        return u"Not a Macro"
    def __repr__(self):
        return u"Not a Macro"