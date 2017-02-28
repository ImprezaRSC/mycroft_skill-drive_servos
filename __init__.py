# DriveServos - Mycroft Skill by Nold 2017
import RPi.GPIO as GPIO
from time import sleep

from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'nold'

logger = getLogger(__name__)


class DriveServos(MycroftSkill):
    left_pin = 18
    right_pin = 17
    left_forward = 2.5
    left_backward = 20.5
    right_forward = 2.5
    right_backward = 20.5

    # 45deg =~ 1 second - for me
    minimal_move_degrees = 45
    minimal_mode_degrees_in_seconds = 1


    def __init__(self):
        super(DriveServos, self).__init__(name="DriveServos")

    def initialize(self):
        if self.config:
            self.left_pin = self.config.get('left_pin', 18)
            self.right_pin = self.config.get('right_pin', 17)
            self.left_forward = self.config.get('left_forward', 20.5)
            self.right_forward = self.config.get('right_forward', 2.5)
            self.left_backward = self.config.get('left_backward', 2.5)
            self.right_backward = self.config.get('right_backward', 20.5)
            self.minimal_move_degrees = self.config.get('minimal_move_degrees', 45)
            self.minimal_mode_degrees_in_seconds = self.config.get('minimal_move_degrees_in_seconds', 2)
        else:
            logger.warn("You havn't configured DriveServos!")

        intent = IntentBuilder("TurnLeft").require("LeftKeyword").build()
        self.register_intent(intent, self.handle_move_left)

        intent = IntentBuilder("TurnRight").require("RightKeyword").build()
        self.register_intent(intent, self.handle_move_right)

        intent = IntentBuilder("MoveForward").require("ForwardKeyword").build()
        self.register_intent(intent, self.handle_move_forward)

        intent = IntentBuilder("MoveBackward").require("BackwardKeyword").build()
        self.register_intent(intent, self.handle_move_backward)

        intent = IntentBuilder("TurnAround").require("TurnKeyword").build()
        self.register_intent(intent, self.handle_turn_around)

        #GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.left_pin, GPIO.OUT)
        GPIO.setup(self.right_pin, GPIO.OUT)
        self.right = GPIO.PWM(self.right_pin, 100)
        self.left = GPIO.PWM(self.left_pin, 100)

    def move(self, val_left, val_right, degrees):
        self.right.start(val_left)
        self.left.start(val_right)

        time = (float(self.minimal_mode_degrees_in_seconds) /
               float(self.minimal_move_degrees) * float(degrees))
        sleep(time)

        self.right.stop()
        self.left.stop()

    def handle_move_forward(self, message):
        self.move(self.left_forward, self.right_forward,
                    self.__get_degrees(message))

    def handle_move_left(self, message):
        self.move(self.left_backward, self.right_forward,
                    self.__get_degrees(message))

    def handle_move_right(self, message):
        self.move(self.left_forward, self.right_backward,
                    self.__get_degrees(message))

    def handle_move_backward(self, message):
        self.move(self.left_backward, self.right_backward,
                    self.__get_degrees(message))

    def handle_turn_around(self, message):
        self.move(self.left_backward, self.right_forward, 180)

    def stop(self):
        self.right.stop()
        self.left.stop()
        GPIO.cleanup()

    def __get_degrees(self, message):
        try:
            msg = message.data.get("Degrees")
            match = re.search("\d+", msg)
            degrees = int(match.group(0))
        except:
            degrees = self.minimal_move_degrees

        if not degrees:
            degrees = self.minimal_move_degrees

        return int(degrees)

def create_skill():
    return DriveServos()
