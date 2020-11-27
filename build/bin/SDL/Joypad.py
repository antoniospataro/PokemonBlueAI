from pynput.keyboard import Key,Controller
import time

class Joypad:
    def __init__(self):
        self.keyboard = Controller()

    def pressRight(self):
        self.keyboard.press(Key.right)
        time.sleep(0.2)
        self.keyboard.release(Key.right)
        time.sleep(0.5)

    def pressDown(self):
        self.keyboard.press(Key.down)
        time.sleep(0.2)
        self.keyboard.release(Key.down)
        time.sleep(0.5)

    def pressLeft(self):
        self.keyboard.press(Key.left)
        time.sleep(0.2)
        self.keyboard.release(Key.left)
        time.sleep(0.5)

    def pressA(self):
        self.keyboard.press('x')
        time.sleep(0.2)
        self.keyboard.release('x')
        time.sleep(0.5)

    def pressB(self):
        self.keyboard.press('z')
        time.sleep(0.2)
        self.keyboard.release('z')
        time.sleep(0.5)
