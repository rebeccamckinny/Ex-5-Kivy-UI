import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.Joystick import Joystick
from threading import Thread
from time import sleep
from kivy.animation import Animation
from kivy.uix.slider import Slider
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'
LEAVING_SCREEN_NAME = 'LeavingScreen'
joystick = Joystick(0, False)


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    value = StringProperty()
    condition = ObjectProperty()
    joy_x_val = ObjectProperty(0, 0)
    joy_y_val = ObjectProperty(0, 0)
    x_and_y_val = ObjectProperty(0, 0)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.clicks = 0
        self.condition = False

    def joy_update(self):  # This should be inside the MainScreen Class
        while True:

            self.ids.joy_label.center_x = (joystick.get_axis('x')) * (self.width / 2) + (self.width / 2)
            self.ids.joy_label.center_y = (joystick.get_axis('y')) * -(self.height / 2) + (self.height / 2)

            self.ids.joy_label.text = " x= {:.3f} y= {:.3f}".format((joystick.get_axis('x')), ((-1)*joystick.get_axis('y')))

            self.ids.joy_button.text = str(joystick.get_button_state(0))

            sleep(.1)

    def start_joy_thread(self):  # This should be inside the MainScreen Class
        Thread(target=self.joy_update).start()

    def counter(self):
        print("inside counter Function")
        self.clicks = self.clicks + 1
        self.value = str(self.clicks)

    def motor_pressed(self):
        print("inside Motor_pressed Function")
        self.condition = not self.condition

    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='main', text="Test", pause_duration=5)

    def leaving_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'LeavingScreen'

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class LeavingScreen(Screen):

    def __init__(self, **kwargs):
        print('inleavingpage')
        Builder.load_file('leavingpage.kv')
        super(LeavingScreen, self).__init__(**kwargs)

    def return_action(self):
        SCREEN_MANAGER.current = 'main'

    def animate(self):
        self.anim = Animation(x=50) + Animation(size=(80, 80), duration=2.)
        self.anim.start(self.ids.image_button)


class AdminScreen(Screen):

    def __init__(self, **kwargs):
        Builder.load_file('AdminScreen.kv')
        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"
        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(LeavingScreen(name=LEAVING_SCREEN_NAME))
"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
