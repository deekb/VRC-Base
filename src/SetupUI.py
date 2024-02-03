import Constants
import math
from vex import *


class SetupUI:
    def __init__(self, terminal, screen):
        self.terminal = terminal

        if self.terminal:
            self.print = self.terminal.print
            self.clear = self.terminal.clear
        else:
            self.print = self.clear = lambda *args, **kwargs: None

        self.screen = screen

        self.page = 0
        self.previous_page = None

        self.screen_pressing = False
        self.press_location = (0, 0)

        self.ring_1_rotation_rad = (
            self.ring_2_rotation_rad
        ) = self.ring_3_rotation_rad = 0

        self.team = None
        self.robot_position = (0, 0)
        self.previous_team = None

        self.finished = False
        self.tau = math.pi * 2
        self.electrons = []
        self.ring_1_rotation_rad = (
            self.ring_2_rotation_rad
        ) = self.ring_3_rotation_rad = 0
        self.phosphorus_logo_center = (
            Constants.screen_size_x / 2,
            54 + Constants.phosphorus_bmp_size_y / 2,
        )

    def top_left_button_pressed(self):
        if self.screen_pressing:
            return (
                self.press_location[0] < Constants.button_size_x
                and self.press_location[1] < Constants.button_size_y
            )
        else:
            return False

    def top_right_button_pressed(self):
        if self.screen_pressing:
            return (
                self.press_location[0]
                > Constants.screen_size_x - Constants.button_size_x
                and self.press_location[1] < Constants.button_size_y
            )
        else:
            return False

    def bottom_left_button_pressed(self):
        if self.screen_pressing:
            return (
                self.press_location[0] < Constants.button_size_x
                and self.press_location[1]
                > Constants.screen_size_y - Constants.button_size_y
            )
        else:
            return False

    def bottom_right_button_pressed(self):
        if self.screen_pressing:
            return (
                self.press_location[0]
                > Constants.screen_size_x - Constants.button_size_x
                and self.press_location[1]
                > Constants.screen_size_y - Constants.button_size_y
            )
        else:
            return False

    def draw_button(self, file_name, position):
        if position == Constants.top | Constants.left:
            self.screen.draw_image_from_file(file_name, 0, 0)
        elif position == Constants.top | Constants.right:
            self.screen.draw_image_from_file(
                file_name, Constants.screen_size_x - Constants.button_size_x, 0
            )
        elif position == Constants.bottom | Constants.left:
            self.screen.draw_image_from_file(
                file_name, 0, Constants.screen_size_y - Constants.button_size_y
            )
        elif position == Constants.bottom | Constants.right:
            self.screen.draw_image_from_file(
                file_name,
                Constants.screen_size_x - Constants.button_size_x,
                Constants.screen_size_y - Constants.button_size_y,
            )

    def go_to_next_page(self):
        self.page += 1

    def go_to_previous_page(self):
        self.page -= 1

    def handle_user_input(self):
        self.screen_pressing = self.screen.pressing()
        if self.screen_pressing:
            self.press_location = (self.screen.x_position(), self.screen.y_position())

        if self.page == -1 and self.top_left_button_pressed():
            self.go_to_next_page()
        elif self.page == 0:
            if self.bottom_left_button_pressed():
                self.go_to_previous_page()
            elif self.bottom_right_button_pressed():
                self.go_to_next_page()
        elif self.page == 1:
            if self.top_left_button_pressed():
                self.go_to_previous_page()
            elif self.top_right_button_pressed():
                while self.screen.pressing():
                    wait(5, MSEC)
                self.go_to_next_page()
            elif self.press_location[1] < Constants.screen_size_y * 0.75:
                # Check selected team
                if self.press_location[0] < Constants.screen_size_x * 0.5:
                    self.team = Constants.Team.red
                else:
                    self.team = Constants.Team.blue
            else:
                self.team = Constants.Team.skills
        elif self.page == 2:
            if self.top_left_button_pressed():
                self.go_to_previous_page()
            elif self.top_right_button_pressed():
                self.finished = True
            elif self.press_location[0] < Constants.screen_size_x / 2:
                if self.press_location[1] < Constants.screen_size_y / 2:
                    # Top half
                    self.robot_position = Constants.blue
                elif self.press_location[1] > Constants.screen_size_y / 2:
                    # Bottom half
                    self.robot_position = Constants.red

                if self.press_location[0] < Constants.screen_size_x / 4:
                    # Left half
                    if self.robot_position == Constants.blue:
                        # Left half is offensive for blue
                        self.robot_position |= Constants.offensive
                    elif self.robot_position == Constants.red:
                        # Left half is defensive for blue
                        self.robot_position |= Constants.defensive
                elif self.press_location[0] > Constants.screen_size_x / 4:
                    # Right half
                    if self.robot_position == Constants.blue:
                        # Right half is defensive for blue
                        self.robot_position |= Constants.defensive
                    elif self.robot_position == Constants.red:
                        # Left half is offensive for blue
                        self.robot_position |= Constants.offensive

    def render_page(self):
        if self.page == -1:
            self.screen.clear_screen()
            self.screen.set_fill_color(Color.BLACK)
            self.screen.set_pen_color(Color.WHITE)

            self.draw_button(
                Constants.deploy_directory + "Back_Button.bmp",
                Constants.top | Constants.left,
            )

            self.screen.set_cursor(5, 1)
            # self.print("Title: " + Constants.__title__)
            # self.print("Description: " + Constants.__description__)
            # self.print("Team: " + Constants.__team__)
            # self.print("URL: " + Constants.__download_url__)
            # self.print("Version: " + Constants.__version__)
            # self.print("Author: " + Constants.__author__)
            # self.print("Author Email: " + Constants.__author_email__)
            # self.print("License: " + Constants.__license__)
        elif self.page == 0:
            self.screen.set_fill_color(Color.TRANSPARENT)
            self.screen.set_pen_color(Color.WHITE)
            self.screen.set_pen_width(1)
            self.draw_button(
                Constants.deploy_directory + "Start_Screen_No_Phosphorus.bmp",
                Constants.top | Constants.left,
            )
            self.screen.draw_image_from_file(
                Constants.deploy_directory + "Phosphorus_White_Text.bmp",
                Constants.screen_size_x / 2 - Constants.phosphorus_bmp_size_x / 2,
                54,
            )
            self.draw_button(
                Constants.deploy_directory + "Start_Button.bmp",
                Constants.bottom | Constants.right,
            )
            self.draw_button(
                Constants.deploy_directory + "Info_Button.bmp",
                Constants.bottom | Constants.left,
            )

            self.screen.draw_circle(
                self.phosphorus_logo_center[0], self.phosphorus_logo_center[1], 33
            )
            self.screen.draw_circle(
                self.phosphorus_logo_center[0], self.phosphorus_logo_center[1], 46
            )
            self.screen.draw_circle(
                self.phosphorus_logo_center[0], self.phosphorus_logo_center[1], 59
            )

            self.electrons.clear()
        elif self.page == 1:
            self.screen.set_fill_color(Color.TRANSPARENT)
            self.screen.set_pen_color(Color.WHITE)
            self.screen.set_pen_width(3)

            self.draw_button(
                Constants.deploy_directory + "Team_Selection.bmp",
                Constants.top | Constants.left,
            )
            self.draw_button(
                Constants.deploy_directory + "Back_Button.bmp",
                Constants.top | Constants.left,
            )
            self.draw_button(
                Constants.deploy_directory + "Next_Button.bmp",
                Constants.top | Constants.right,
            )

            self.team = None
            self.previous_team = None
        elif self.page == 2:
            self.screen.set_fill_color(Color.BLACK)
            self.screen.set_pen_color(Color.TRANSPARENT)
            self.draw_button(
                Constants.deploy_directory + "Robot_Placement_Selection.png",
                Constants.top | Constants.left,
            )
            self.draw_button(
                Constants.deploy_directory + "Back_Button.bmp",
                Constants.top | Constants.left,
            )
            self.draw_button(
                Constants.deploy_directory + "Next_Button.bmp",
                Constants.top | Constants.right,
            )
            while self.screen_pressing:
                self.handle_user_input()

    def tick_page(self):
        if self.page == 0:
            wait(50, MSEC)

            self.screen.set_fill_color(Color.BLACK)

            for electron in self.electrons:
                self.screen.draw_circle(electron[0], electron[1], 5)

            self.screen.set_fill_color(Color.TRANSPARENT)
            self.screen.set_pen_color(Color.WHITE)

            self.screen.draw_circle(
                self.phosphorus_logo_center[0], self.phosphorus_logo_center[1], 33
            )
            self.screen.draw_circle(
                self.phosphorus_logo_center[0], self.phosphorus_logo_center[1], 46
            )
            self.screen.draw_circle(
                self.phosphorus_logo_center[0], self.phosphorus_logo_center[1], 59
            )

            self.screen.set_fill_color(Color.CYAN)
            self.screen.set_pen_color(Color.TRANSPARENT)
            self.ring_1_rotation_rad += 0.17
            self.ring_2_rotation_rad += 0.08
            self.ring_3_rotation_rad += 0.05

            self.electrons.clear()

            for index in range(0, 2):
                self.electrons.append(
                    (
                        self.phosphorus_logo_center[0]
                        + math.sin(self.ring_1_rotation_rad + self.tau * (index / 2))
                        * 33,
                        self.phosphorus_logo_center[1]
                        + math.cos(self.ring_1_rotation_rad + self.tau * (index / 2))
                        * 33,
                    )
                )

            for index in range(0, 8):
                self.electrons.append(
                    (
                        self.phosphorus_logo_center[0]
                        + math.sin(self.ring_2_rotation_rad + self.tau * (index / 8))
                        * 46,
                        self.phosphorus_logo_center[1]
                        + math.cos(self.ring_2_rotation_rad + self.tau * (index / 8))
                        * 46,
                    )
                )

            for index in range(0, 5):
                self.electrons.append(
                    (
                        self.phosphorus_logo_center[0]
                        + math.sin(self.ring_3_rotation_rad + self.tau * (index / 5))
                        * 59,
                        self.phosphorus_logo_center[1]
                        + math.cos(self.ring_3_rotation_rad + self.tau * (index / 5))
                        * 59,
                    )
                )

            for electron in self.electrons:
                self.screen.draw_circle(electron[0], electron[1], 5)

        if self.page == 1:
            if self.screen_pressing:
                if self.team != self.previous_team:
                    self.previous_team = self.team
                    self.draw_button(
                        Constants.deploy_directory + "Team_Selection.bmp",
                        Constants.top | Constants.left,
                    )
                    self.draw_button(
                        Constants.deploy_directory + "Back_Button.bmp",
                        Constants.top | Constants.left,
                    )
                    self.draw_button(
                        Constants.deploy_directory + "Next_Button.bmp",
                        Constants.top | Constants.right,
                    )
                    if self.team == Constants.Team.red:
                        self.screen.draw_rectangle(
                            0,
                            0,
                            Constants.screen_size_x * 0.5,
                            Constants.screen_size_y * 0.65,
                        )
                    elif self.team == Constants.Team.blue:
                        self.screen.draw_rectangle(
                            Constants.screen_size_x * 0.5,
                            0,
                            Constants.screen_size_x,
                            Constants.screen_size_y * 0.65,
                        )
                    elif self.team == Constants.Team.skills:
                        self.screen.draw_rectangle(
                            0,
                            Constants.screen_size_y * 0.65,
                            Constants.screen_size_x,
                            Constants.screen_size_y,
                        )
        if self.page == 2:
            if self.screen_pressing:
                self.screen.set_fill_color(Color.BLACK)
                self.screen.set_pen_color(Color.TRANSPARENT)
                self.draw_button(
                    Constants.deploy_directory + "Robot_Placement_Selection.png",
                    Constants.top | Constants.left,
                )
                self.draw_button(
                    Constants.deploy_directory + "Back_Button.bmp",
                    Constants.top | Constants.left,
                )
                self.draw_button(
                    Constants.deploy_directory + "Next_button.bmp",
                    Constants.top | Constants.right,
                )
                if self.robot_position == Constants.red | Constants.offensive:
                    self.screen.draw_circle(185, 225, 20)
                elif self.robot_position == Constants.red | Constants.defensive:
                    self.screen.draw_circle(50, 225, 20)
                elif self.robot_position == Constants.blue | Constants.offensive:
                    self.screen.draw_circle(59, 23, 20)
                elif self.robot_position == Constants.blue | Constants.defensive:
                    self.screen.draw_circle(170, 32, 20)

    def tick(self):
        self.handle_user_input()
        if self.page != self.previous_page:
            self.previous_page = self.page
            self.render_page()
        else:
            self.tick_page()
