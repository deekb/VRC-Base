import math


class LinearRegressor:
    def __init__(self):
        self.x_intercept = None
        self.y_intercept = None
        self.slope = None
        self.inverted = None

    @staticmethod
    def validate_points(points):
        points = list(points)
        n = len(points)

        unique_points = False
        if n >= 1:
            for point in points:
                if point != points[0]:
                    unique_points = True
                    break
        if not unique_points:
            raise ValueError("The number of unique data points must be greater than 1.")

    def fit(self, points):
        points = list(points)

        self.validate_points(points)

        x_data = [point[0] for point in points]
        y_data = [point[1] for point in points]

        n = len(points)

        unique_points = False
        if n >= 1:
            for point in points:
                if point != points[0]:
                    unique_points = True
                    break
        if not unique_points:
            raise ValueError("The number of unique data points must be greater than 1.")

        # Calculate the sums
        sum_x = sum(x_data)
        sum_y = sum(y_data)
        sum_xy = sum(x * y for x, y in zip(x_data, y_data))
        sum_x_squared = sum(x**2 for x in x_data)

        # Calculate the slope and y-intercept
        try:
            self.slope = (n * sum_xy - sum_x * sum_y) / (
                n * sum_x_squared - (sum_x**2)
            )
        except ZeroDivisionError:
            print("Error: ", n, sum_x, sum_y, sum_xy, sum_x_squared)
            print(x_data, y_data)
            self.slope = None
        self.y_intercept = (sum_y - self.slope * sum_x) / n
        try:
            self.x_intercept = -self.y_intercept / self.slope
        except ZeroDivisionError:
            if sum_y == 0:
                self.x_intercept = 0
            else:
                self.x_intercept = None

        return self

    def smart_fit(self, points):
        self.validate_points(points)

        x_data = [point[0] for point in points]
        y_data = [point[1] for point in points]

        x_range = max(x_data) - min(x_data)
        y_range = max(y_data) - min(y_data)

        if x_range >= y_range:
            self.inverted = False
            self.fit(points)
        else:
            x_data, y_data = y_data, x_data
            self.inverted = True
            self.fit(zip(x_data, y_data))

        # un-invert the result is necessary
        if self.inverted:
            try:
                self.y_intercept = (-1 / self.slope) * self.y_intercept
                self.slope = 1 / self.slope
                self.x_intercept = -self.y_intercept / self.slope
            except ZeroDivisionError:
                self.x_intercept, self.y_intercept = self.y_intercept, self.x_intercept
                self.slope = math.copysign(math.inf, self.slope)

        return self

    def predict_y(self, x_list):
        if math.isinf(self.slope):
            y_list = [self.y_intercept for _ in x_list]
        else:
            y_list = [(self.slope * x) + self.y_intercept for x in x_list]
        return y_list

    def predict_x(self, y_list):
        if self.slope == 0:
            x_list = [self.x_intercept for _ in y_list]
        else:
            x_list = [(y - self.y_intercept) / self.slope for y in y_list]
        return x_list
