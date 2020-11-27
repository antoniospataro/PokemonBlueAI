from pynput.keyboard import Key,Controller
from Joypad import Joypad
import time


#PRESS A STRING
#keyboard.type('Hello World')
#TAP A KEY
#keyboard.tap('a')

class Mover:
    def __init__(self):
        self.joypad = Joypad()
        self.keyboard = self.joypad.keyboard
        
    def switch(self):
        self.keyboard.press(Key.alt)
        self.keyboard.tap(Key.tab)
        time.sleep(0.1)
        self.keyboard.release(Key.alt)
        time.sleep(0.1)
        
    def trace(self):
        self.keyboard.type('trace_all')
        time.sleep(0.2)
        self.keyboard.tap(Key.enter)
        time.sleep(1.2)

    def findData(self):
        self.joypad.pressRight()
        time.sleep(0.2)
        self.joypad.pressA()
        time.sleep(1)
        self.joypad.pressDown()
        time.sleep(0.2)
        self.joypad.pressDown()
        time.sleep(0.2)
        self.joypad.pressDown()
        time.sleep(0.2)
        self.joypad.pressDown()
        self.joypad.pressB()
        self.joypad.pressLeft()

    
    #SWITCHA DA EMULATORE A GIOCO E STARTA LA BATTAGLIA
    def startBattle(self):
        time.sleep(3)
        self.joypad.pressA()
        time.sleep(7)
        self.joypad.pressA()
        time.sleep(9)
        self.findData()

        
    def firstDump(self):
        #inizia da terminale EMULATORE e metti seconda scelta TAB GIOCO
        time.sleep(5)
        self.trace()
        self.switch()
        self.startBattle()
        time.sleep(2)
        self.switch()
        self.trace()
        self.keyboard.type('trace_dump Dump.bin')
        self.keyboard.tap(Key.enter)
        time.sleep(0.2)
        self.switch()

    
    def otherDump(self):
        self.switch()
        self.keyboard.type('trace_clear')
        self.keyboard.tap(Key.enter)
        self.trace()
        self.switch()
        self.joypad.pressA()
        self.skipDialogue()
        self.findData()
        self.switch()
        self.trace()
        self.keyboard.type('trace_dump Dump.bin')
        self.keyboard.tap(Key.enter)
        time.sleep(0.5)
        self.switch()

    def pressMoveX(self,num):
        time.sleep(3)
        self.joypad.pressA()
        for i in range(1,num):
            self.joypad.pressDown()
        time.sleep(0.3)
        self.otherDump()
        time.sleep(0.3)
        
    def skipDialogue(self):
        time.sleep(3)
        self.joypad.pressB()
        time.sleep(3)
        self.joypad.pressB()
        time.sleep(3)
        self.joypad.pressB()
        time.sleep(3)
        self.joypad.pressB()
        time.sleep(3)
        self.joypad.pressB()