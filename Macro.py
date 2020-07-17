from pythonosc import udp_client
import time

import yaml

import threading

client = udp_client.SimpleUDPClient("127.0.0.1", 3333)

def loadMacros(controller, path="macros.yml"):
    macros = []
    with open(path, "r") as stream:
        try:
            yml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            
    for id, macro in yml["macros"].items():
        _macro = Macro(macro, id)
        macros.insert(id, _macro)
        controller.lightOn(id, _macro.colour)

    
    return macros


class InvalidMacroConfigException(Exception):
    pass


class MacroStep:
    def __init__(self, yml):
        if yml["type"] not in ("sleep", "osc"):
            raise KeyError
        self._type = yml["type"]

        if yml["type"] == "sleep":
            self._duration = yml["duration"]
        
        if yml["type"] == "osc":
            self._path = yml["path"]
    def run(self):
        if self._type == "osc":
            client.send_message(self._path, None)
        elif self._type == "sleep":
            time.sleep(self._duration)

class Macro:
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
        
    def run(self, controller):
        thread = threading.Thread(target=self._threadRun, args=(controller,))
        thread.start()

    def _threadRun(self, controller):
        controller.lightOn(self._id, self.colour, True)
        for step in self._steps:
            step.run()
        controller.lightOn(self._id, self.colour, False)

    def __str__(self):
        return "Macro '{}'".format(self._name)
    def __unicode__(self):
        return u"Macro '{}'".format(self._name)
    def __repr__(self):
        return u"Macro '{}'".format(self._name)
