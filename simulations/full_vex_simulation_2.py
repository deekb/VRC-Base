import threading

import pyglet

pyglet.options["debug_gl"] = False

controller_back = pyglet.image.load("./Controller_front.png")

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = int(WINDOW_WIDTH * (controller_back.height / controller_back.width))

LEFT_TRIGGER_BOUNDING_BOX = [(127, 403), (263, 402), (259, 345), (101, 345)]

RIGHT_TRIGGER_BOUNDING_BOX = [
    (WINDOW_WIDTH - 127, 403),
    (WINDOW_WIDTH - 263, 402),
    (WINDOW_WIDTH - 259, 345),
    (WINDOW_WIDTH - 101, 345),
]

LEFT_BUMPER_BOUNDING_BOX = [
    (89, 311),
    (240, 315),
    (258, 308),
    (262, 261),
    (251, 251),
    (87, 253),
    (76, 263),
]

RIGHT_BUMPER_BOUNDING_BOX = [
    (WINDOW_WIDTH - 89, 311),
    (WINDOW_WIDTH - 240, 315),
    (WINDOW_WIDTH - 258, 308),
    (WINDOW_WIDTH - 262, 261),
    (WINDOW_WIDTH - 251, 251),
    (WINDOW_WIDTH - 87, 253),
    (WINDOW_WIDTH - 76, 263),
]

COMPETITION_SWITCH_PORT_BOUNDING_BOX = [(447, 336), (551, 336), (551, 253), (446, 253)]

BUTTON_LEFT_CENTER_POINT = (223, 168)
BUTTON_RIGHT_CENTER_POINT = (354, 168)
BUTTON_UP_CENTER_POINT = ((223 + 354) / 2, 170 + (223 - 354) / 2)
BUTTON_DOWN_CENTER_POINT = ((223 + 354) / 2, 170 - (223 - 354) / 2)

offset = 424

BUTTON_A_CENTER_POINT = (354 + offset, 168)
BUTTON_B_CENTER_POINT = ((223 + 354) / 2 + offset, 170 + (223 - 354) / 2)
BUTTON_X_CENTER_POINT = ((223 + 354) / 2 + offset, 170 - (223 - 354) / 2)
BUTTON_Y_CENTER_POINT = (223 + offset, 168)

LEFT_JOYSTICK_CENTER_POINT = (153, 302)
RIGHT_JOYSTICK_CENTER_POINT = (849, 302)

JOYSTICK_RADIUS = 64

BUTTON_RADIUS = 28

BRAIN_SCREEN_WIDTH = 480
BRAIN_SCREEN_HEIGHT = 240

log_window = None

competition_switch_inserted = False


class MomentaryButton:
    def __init__(self, sprite, initial_state=False):
        self.pressed = initial_state
        self.sprite = sprite

    def set_state(self, state):
        self.pressed = state

    def get_state(self):
        return self.pressed

    def press(self):
        self.set_state(True)

    def release(self):
        self.set_state(False)


class ToggleButton:
    def __init__(self, sprite, initial_state=False):
        self.pressed = initial_state
        self.sprite = sprite

    def set_state(self, state):
        self.pressed = state

    def get_state(self):
        return self.pressed

    def toggle(self):
        self.set_state(not self.get_state())


class ControllerTopViewWindow(pyglet.window.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.set_caption("Controller Top View")

        self.controller_top_view_image = pyglet.image.load("./Controller_top.png")
        self.controller_top_view_sprite = pyglet.sprite.Sprite(
            self.controller_top_view_image
        )
        self.controller_top_view_sprite.height = height
        self.controller_top_view_sprite.width = width
        self.batch = pyglet.graphics.Batch()

        self.left_trigger_polygon = pyglet.shapes.Polygon(
            *LEFT_TRIGGER_BOUNDING_BOX, color=(0, 225, 0), batch=self.batch
        )

        self.right_trigger_polygon = pyglet.shapes.Polygon(
            *RIGHT_TRIGGER_BOUNDING_BOX,
            color=(0, 225, 0),
            batch=self.batch,
        )

        self.left_bumper_polygon = pyglet.shapes.Polygon(
            *LEFT_BUMPER_BOUNDING_BOX,
            color=(0, 225, 0),
            batch=self.batch,
        )

        self.right_bumper_polygon = pyglet.shapes.Polygon(
            *RIGHT_BUMPER_BOUNDING_BOX,
            color=(0, 225, 0),
            batch=self.batch,
        )

        self.competition_switch_port_polygon = pyglet.shapes.Polygon(
            *COMPETITION_SWITCH_PORT_BOUNDING_BOX,
            color=(0, 0, 0),
            batch=self.batch,
        )

        self.left_trigger = MomentaryButton(self.left_trigger_polygon)
        self.right_trigger = MomentaryButton(self.right_trigger_polygon)
        self.left_bumper = MomentaryButton(self.left_bumper_polygon)
        self.right_bumper = MomentaryButton(self.right_bumper_polygon)
        self.competition_switch = ToggleButton(self.competition_switch_port_polygon)

    def on_draw(self):
        global competition_switch_inserted
        self.clear()
        self.controller_top_view_sprite.draw()
        if self.left_bumper.get_state():
            self.left_bumper.sprite.draw()
        if self.right_bumper.get_state():
            self.right_bumper.sprite.draw()
        if self.left_trigger.get_state():
            self.left_trigger.sprite.draw()
        if self.right_trigger.get_state():
            self.right_trigger.sprite.draw()
        if self.competition_switch.get_state():
            self.competition_switch.sprite.color = (0, 255, 0)
        else:
            self.competition_switch.sprite.color = (255, 0, 0)
        self.competition_switch.sprite.draw()
        competition_switch_inserted = self.competition_switch.get_state()

    def on_mouse_press(self, x, y, *_):
        point = (x, y)

        if point in self.left_trigger.sprite:
            self.left_trigger.press()
            log_window.append_to_log("Left trigger press")
        elif point in self.right_trigger.sprite:
            self.right_trigger.press()
            log_window.append_to_log("Right trigger press")
        elif point in self.left_bumper.sprite:
            self.left_bumper.press()
            log_window.append_to_log("Left bumper press")
        elif point in self.right_bumper.sprite:
            self.right_bumper.press()
            log_window.append_to_log("Right bumper press")
        elif point in self.competition_switch.sprite:
            self.competition_switch.toggle()
            if self.competition_switch.get_state():
                log_window.append_to_log("Competition switch inserted")
            else:
                log_window.append_to_log("Competition switch removed")
        else:
            log_window.append_to_log(f"Press at {x, y}")

    def on_mouse_release(self, x, y, *_):
        point = (x, y)
        if point in self.left_trigger.sprite:
            self.left_trigger.release()
            log_window.append_to_log("Left trigger release")
        elif point in self.right_trigger.sprite:
            self.right_trigger.release()
            log_window.append_to_log("Right trigger release")
        elif point in self.left_bumper.sprite:
            self.left_bumper.release()
            log_window.append_to_log("Left bumper release")
        elif point in self.right_bumper.sprite:
            self.right_bumper.release()
            log_window.append_to_log("Right bumper release")


class ControllerFrontViewWindow(pyglet.window.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.set_caption("Controller Front View")

        self.controller_front_view_image = pyglet.image.load("./Controller_front.png")
        self.controller_front_view_sprite = pyglet.sprite.Sprite(
            self.controller_front_view_image
        )
        self.controller_front_view_sprite.height = height
        self.controller_front_view_sprite.width = width

        self.button_left_circle = pyglet.shapes.Circle(
            *BUTTON_LEFT_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.button_right_circle = pyglet.shapes.Circle(
            *BUTTON_RIGHT_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.button_up_circle = pyglet.shapes.Circle(
            *BUTTON_DOWN_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.button_down_circle = pyglet.shapes.Circle(
            *BUTTON_UP_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.button_a_circle = pyglet.shapes.Circle(
            *BUTTON_A_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.button_b_circle = pyglet.shapes.Circle(
            *BUTTON_B_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.button_x_circle = pyglet.shapes.Circle(
            *BUTTON_X_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.button_y_circle = pyglet.shapes.Circle(
            *BUTTON_Y_CENTER_POINT, BUTTON_RADIUS, color=(0, 255, 0)
        )

        self.left_joystick_circle = pyglet.shapes.Circle(
            *LEFT_JOYSTICK_CENTER_POINT, JOYSTICK_RADIUS, color=(0, 255, 0)
        )

        self.right_joystick_circle = pyglet.shapes.Circle(
            *RIGHT_JOYSTICK_CENTER_POINT, JOYSTICK_RADIUS, color=(0, 255, 0)
        )

        self.button_left = MomentaryButton(self.button_left_circle)
        self.button_right = MomentaryButton(self.button_right_circle)
        self.button_up = MomentaryButton(self.button_up_circle)
        self.button_down = MomentaryButton(self.button_down_circle)

        self.button_a = MomentaryButton(self.button_a_circle)
        self.button_b = MomentaryButton(self.button_b_circle)
        self.button_x = MomentaryButton(self.button_x_circle)
        self.button_y = MomentaryButton(self.button_y_circle)

    def on_draw(self):
        self.clear()
        self.controller_front_view_sprite.draw()
        for button in (
            self.button_left,
            self.button_right,
            self.button_up,
            self.button_down,
            self.button_a,
            self.button_b,
            self.button_x,
            self.button_y,
        ):
            if button.get_state():
                button.sprite.draw()
        self.left_joystick_circle.draw()
        self.right_joystick_circle.draw()

    def on_mouse_press(self, x, y, *_):
        point = (x, y)

        if point in self.button_left.sprite:
            self.button_left.press()
            log_window.append_to_log("Button Left press")
        elif point in self.button_right.sprite:
            self.button_right.press()
            log_window.append_to_log("Button Right press")
        elif point in self.button_up.sprite:
            self.button_up.press()
            log_window.append_to_log("Button Up press")
        elif point in self.button_down.sprite:
            self.button_down.press()
            log_window.append_to_log("Button Down press")
        elif point in self.button_a.sprite:
            self.button_a.press()
            log_window.append_to_log("Button A press")
        elif point in self.button_b.sprite:
            self.button_b.press()
            log_window.append_to_log("Button B press")
        elif point in self.button_x.sprite:
            self.button_x.press()
            log_window.append_to_log("Button X press")
        elif point in self.button_y.sprite:
            self.button_y.press()
            log_window.append_to_log("Button Y press")
        else:
            log_window.append_to_log(f"Press at {x, y}")

    def on_mouse_release(self, x, y, *_):
        point = (x, y)
        if point in self.button_left.sprite:
            self.button_left.release()
            log_window.append_to_log("Button Left release")
        elif point in self.button_right.sprite:
            self.button_right.release()
            log_window.append_to_log("Button Right release")
        elif point in self.button_up.sprite:
            self.button_up.release()
            log_window.append_to_log("Button Up release")
        elif point in self.button_down.sprite:
            self.button_down.release()
            log_window.append_to_log("Button Down release")
        elif point in self.button_a.sprite:
            self.button_a.release()
            log_window.append_to_log("Button A release")
        elif point in self.button_b.sprite:
            self.button_b.release()
            log_window.append_to_log("Button B release")
        elif point in self.button_x.sprite:
            self.button_x.release()
            log_window.append_to_log("Button X release")
        elif point in self.button_y.sprite:
            self.button_y.release()
            log_window.append_to_log("Button Y release")
        else:
            log_window.append_to_log(f"Press at {x, y}")


class LogWindow(pyglet.window.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.set_caption("Log Window")

        self.document = pyglet.text.document.FormattedDocument("Started log\n")

        self.document.set_style(
            0,
            len(self.document.text),
            dict(font_name="Arial", font_size=16, color=(255, 255, 255, 255)),
        )

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=True
        )

        self.caret = pyglet.text.caret.Caret(self.layout, color=(150, 255, 150))

        self.push_handlers(self.caret)

        self.caret.set_style(dict(font_name="Arial"))

        self.queue = []

    def on_draw(self):
        self.clear()
        for _ in range(len(self.queue)):
            self.document.insert_text(len(self.document.text), self.queue.pop(-1))
        self.layout.view_y = -self.layout.content_height

        self.layout.draw()
        self.push_handlers(self.caret)

    def append_to_log(self, text, end="\n"):
        self.queue.append(text + end)


class BrainScreenWindow(pyglet.window.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.set_caption("Brain Screen")

        self.batch = pyglet.graphics.Batch()
        self.on_screen_objects = []

    def on_draw(self):
        self.clear()
        for obj in self.on_screen_objects:
            obj.batch = self.batch
        self.batch.draw()

    def draw_circle(self, x, y, radius):
        self.on_screen_objects.append(
            pyglet.shapes.Circle(x, y, radius, color=(50, 225, 30))
        )

    def draw_rectangle(self, x, y, width, height):
        self.on_screen_objects.append(
            pyglet.shapes.Rectangle(x, y, width, height, color=(50, 225, 30))
        )


class CompetitionSwitchWindow(pyglet.window.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.set_caption("Competition Switch")

    def on_draw(self):
        global competition_switch_inserted
        self.clear()
        self.set_visible(competition_switch_inserted)


def pyglet_thread_function():
    global log_window
    controller_top_view_window = ControllerTopViewWindow(WINDOW_WIDTH, WINDOW_HEIGHT)
    controller_front_view_window = ControllerFrontViewWindow(
        WINDOW_WIDTH, WINDOW_HEIGHT
    )
    controller_top_view_window_location = controller_top_view_window.get_location()
    controller_front_view_window.set_location(
        controller_top_view_window_location[0] + controller_top_view_window.width,
        controller_top_view_window_location[1],
        )
    log_window = LogWindow(WINDOW_WIDTH, WINDOW_HEIGHT)
    log_window.set_location(
        controller_top_view_window_location[0]
        + controller_top_view_window.width
        + controller_front_view_window.width,
        controller_top_view_window_location[1],
        )
    brain_screen_window = BrainScreenWindow(WINDOW_WIDTH, WINDOW_HEIGHT)
    competition_switch_window = CompetitionSwitchWindow(WINDOW_WIDTH, WINDOW_HEIGHT)
    brain_screen_window.draw_circle(100, 100, 10)
    brain_screen_window.draw_circle(50, 100, 10)
    brain_screen_window.draw_circle(100, 50, 30)
    pyglet.app.run()


if __name__ == "__main__":
    pyglet_thread = threading.Thread(target=pyglet_thread_function)
    pyglet_thread.start()
    pyglet_thread.join()
