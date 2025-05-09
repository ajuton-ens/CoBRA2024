from pyPS4Controller.controller import Controller


class MyController(Controller):  # create a custom class for your controller and subclass Controller
    """
    If we want to bind an action to the X button on the controller, we need to override its respective methods.

    Some of the buttons have a binary On/Off state. For example the X, Circle, Square, and Triangle buttons.
    When overriding their respective methods there are no args in the function signature.

    Some controls like the L2, L3, R2 and R3 have a variable On state.
    When overriding their respective method, there is a value argument in the function signature 
    which indicates the degree of the input.

    You can put any custom code inside the functions bellow. I have put print statements in there just so you
    can copy/paste the code, connect controller, play with the inputs and see the result.

    All of  the functions that you can override are listed in this script.
    """

    def on_x_press(self):
        print("on_x_press")

    def on_x_release(self):
        print("on_x_release")

    def on_triangle_press(self):
        print("on_triangle_press")

    def on_triangle_release(self):
        print("on_triangle_release")

    def on_circle_press(self):
        print("on_circle_press")

    def on_circle_release(self):
        print("on_circle_release")

    def on_square_press(self):
        print("on_square_press")

    def on_square_release(self):
        print("on_square_release")

    def on_L1_press(self):
        print("on_L1_press")

    def on_L1_release(self):
        print("on_L1_release")

    def on_L2_press(self, value):
        print("on_L2_press: ", value)

    def on_L2_release(self):
        print("on_L2_release")

    def on_R1_press(self):
        print("on_R1_press")

    def on_R1_release(self):
        print("on_R1_release")

    def on_R2_press(self, value):
        print("on_R2_press: ", value)

    def on_R2_release(self):
        print("on_R2_release")

    def on_up_arrow_press(self):
        print("on_up_arrow_press")

    def on_up_down_arrow_release(self):
        print("on_up_down_arrow_release")

    def on_down_arrow_press(self):
        print("on_down_arrow_press")

    def on_left_arrow_press(self):
        print("on_left_arrow_press")

    def on_left_right_arrow_release(self):
        print("on_left_right_arrow_release")

    def on_right_arrow_press(self):
        print("on_right_arrow_press")

    def on_L3_up(self, value):
        print("on_L3_up: ", value)

    def on_L3_down(self, value):
        print("on_L3_down: ", value)

    def on_L3_left(self, value):
        print("on_L3_left: ", value)

    def on_L3_right(self, value):
        print("on_L3_right: ", value)

    def on_L3_release(self):
        print("on_L3_release")

    def on_R3_up(self, value):
        print("on_R3_up: ", value)

    def on_R3_down(self, value):
        print("on_R3_down: ", value)

    def on_R3_left(self, value):
        print("on_R3_left: ", value)

    def on_R3_right(self, value):
        print("on_R3_right: ", value)

    def on_R3_release(self):
        print("on_R3_release")

    def on_options_press(self):
        print("on_options_press")

    def on_options_release(self):
        print("on_options_release")


# now make sure the controller is paired over the Bluetooth and turn on the listener
MyController(interface="/dev/input/js0", connecting_using_ds4drv=False).listen()
