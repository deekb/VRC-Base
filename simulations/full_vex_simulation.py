import pyglet
from pyglet import image, shapes, text

controller_back = image.load("./Controller_front.png")
controller_top = image.load("./Controller_top.png")
icon = image.load("./Vex_Simulation_Logo.png")

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

left_trigger_pressed = False
right_trigger_pressed = False
left_bumper_pressed = False
right_bumper_pressed = False
competition_switch_port_active = False
competition_switch_window_position = (0, 0)

batch = pyglet.graphics.Batch()

left_trigger_polygon = shapes.Polygon(
    *LEFT_TRIGGER_BOUNDING_BOX, color=(50, 225, 30), batch=batch
)

right_trigger_polygon = shapes.Polygon(
    *RIGHT_TRIGGER_BOUNDING_BOX,
    color=(50, 225, 30),
    batch=batch,
)

left_bumper_polygon = shapes.Polygon(
    *LEFT_BUMPER_BOUNDING_BOX,
    color=(50, 225, 30),
    batch=batch,
)

right_bumper_polygon = shapes.Polygon(
    *RIGHT_BUMPER_BOUNDING_BOX,
    color=(50, 225, 30),
    batch=batch,
)

competition_switch_port_polygon = shapes.Polygon(
    *COMPETITION_SWITCH_PORT_BOUNDING_BOX,
    color=(255, 0, 0),
    batch=batch,
)


controller_front_view_window = pyglet.window.Window(
    WINDOW_WIDTH, WINDOW_HEIGHT, "Controller Front View"
)
controller_top_view_window = pyglet.window.Window(
    WINDOW_WIDTH, WINDOW_HEIGHT, "Controller Top View"
)
competition_switch_window = pyglet.window.Window(
    WINDOW_WIDTH, WINDOW_HEIGHT, "Competition switch"
)
log_window = pyglet.window.Window(
    WINDOW_WIDTH, WINDOW_HEIGHT, "Log window"
)
controller_front_view_window.set_icon(icon)
controller_top_view_window.set_icon(icon)
competition_switch_window.set_icon(icon)
log_window.set_icon(icon)


controller_back_sprite = pyglet.sprite.Sprite(controller_back)
controller_back_sprite.height = WINDOW_HEIGHT
controller_back_sprite.width = WINDOW_WIDTH


controller_top_sprite = pyglet.sprite.Sprite(controller_top)
controller_top_sprite.height = WINDOW_HEIGHT
controller_top_sprite.width = WINDOW_WIDTH


document = pyglet.text.document.FormattedDocument("Hello world\n")


def append_to_log(string, end="\n"):
    document.insert_text(len(document.text), string + end)


document.set_style(
    0,
    len(document.text),
    dict(font_name="Arial", font_size=16, color=(255, 255, 255, 255)),
)

layout = pyglet.text.layout.IncrementalTextLayout(document, WINDOW_WIDTH, WINDOW_HEIGHT, multiline=True)

caret = pyglet.text.caret.Caret(layout, color=(150, 255, 150))

log_window.push_handlers(caret)

caret.set_style(dict(font_name="Arial"))


@controller_front_view_window.event
def on_draw():
    global competition_switch_window_position
    if not controller_front_view_window.visible:
        return

    controller_front_view_window.clear()
    controller_back_sprite.draw()

    if left_trigger_pressed:
        left_trigger_polygon.draw()
    if right_trigger_pressed:
        right_trigger_polygon.draw()
    if left_bumper_pressed:
        left_bumper_polygon.draw()
    if right_bumper_pressed:
        right_bumper_polygon.draw()
    if competition_switch_port_active:
        competition_switch_port_polygon.color = (0, 255, 0)
        if not competition_switch_window.visible:
            competition_switch_window.set_visible(True)
            competition_switch_window.set_location(*competition_switch_window_position)

    else:
        competition_switch_port_polygon.color = (255, 0, 0)
        if competition_switch_window.visible:
            competition_switch_window.set_visible(False)
            competition_switch_window_position = (
                competition_switch_window.get_location()
            )

    competition_switch_port_polygon.draw()


@controller_top_view_window.event
def on_draw():
    controller_top_view_window.clear()
    controller_top_sprite.draw()


@controller_front_view_window.event
def on_mouse_press(x, y, *_):
    global left_trigger_pressed, right_trigger_pressed, left_bumper_pressed, right_bumper_pressed, competition_switch_port_active
    if (x, y) in left_trigger_polygon:
        left_trigger_pressed = True
        append_to_log("Left trigger press")
    elif (x, y) in right_trigger_polygon:
        right_trigger_pressed = True
        append_to_log("Right trigger press")
    elif (x, y) in left_bumper_polygon:
        left_bumper_pressed = True
        append_to_log("Left bumper press")
    elif (x, y) in right_bumper_polygon:
        right_bumper_pressed = True
        append_to_log("Right bumper press")
    elif (x, y) in competition_switch_port_polygon:
        competition_switch_port_active = not competition_switch_port_active
        if competition_switch_port_active:
            append_to_log("Competition switch inserted")
        else:
            append_to_log("Competition switch removed")
    else:
        append_to_log(f"Press at {x, y}")


@controller_front_view_window.event
def on_mouse_release(x, y, *_):
    global left_trigger_pressed, right_trigger_pressed, left_bumper_pressed, right_bumper_pressed
    if (x, y) in left_trigger_polygon:
        left_trigger_pressed = False
        append_to_log("Left trigger release")
    elif (x, y) in right_trigger_polygon:
        right_trigger_pressed = False
        append_to_log("Right trigger release")
    elif (x, y) in left_bumper_polygon:
        left_bumper_pressed = False
        append_to_log("Left bumper release")
    elif (x, y) in right_bumper_polygon:
        right_bumper_pressed = False
        append_to_log("Right bumper release")


@competition_switch_window.event
def on_draw():
    competition_switch_window.clear()


@log_window.event
def on_draw():
    log_window.clear()
    layout.draw()
    # layout.view_y = -layout.content_height
    log_window.push_handlers(caret)


pyglet.app.run()
