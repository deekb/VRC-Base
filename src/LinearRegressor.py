"""
LinearRegressor

This module defines a LinearRegressor class for fitting linear regression models to data points and
predicting or extrapolating values based on the fitted model.

Author: Derek Michael Baier
Author Email: derek.m.baier@gmail.com

Disclaimer:
    This code is provided without any form of license. You are free to use, modify, and distribute
    this code for any purpose without the need for attribution.

Classes:
    - LinearRegressor: A class for fitting linear regression models to data points.

Methods:
    - __init__: Initializes a LinearRegressor object with attributes for line parameters.
    - _validate_points: Validates input data points.
    - fit: Fits a linear regression model to the input data points.
    - smart_fit: Fits a linear regression model, automatically selecting the orientation based on data scale.
    - predict_y: Predicts y values for given x values using the fitted linear regression model.
    - predict_x: Predicts x values for given y values using the fitted linear regression model.

Examples:
    Example usage of the LinearRegressor class can be found at the bottom of this file
    Or you can just run this file (provided you have matplotlib installed) to see a
    nice visual of what the module does
"""
import math


class LinearRegressor:
    def __init__(self):
        """
        Initialize LinearRegressor object with attributes for the line parameters.
        """
        self.x_intercept = None
        self.y_intercept = None
        self.slope = None
        self.inverted = None

    @staticmethod
    def _validate_points(points):
        """
        Validate the input data points.

        Args:
            points (iterable): Iterable containing data points.

        Raises:
            ValueError: If the number of unique data points is less than 2.

        Examples:
            Case 1: Valid points with unique data
            >>> LinearRegressor._validate_points([(1, 2), (3, 4), (5, 6)])

            Case 2: Valid points with duplicate data
            >>> LinearRegressor._validate_points([(1, 2), (3, 4), (1, 2)])

            Case 3: Invalid points - not tuples of two values
            >>> LinearRegressor._validate_points([(1, 2), (3, 4), 5])
            Traceback (most recent call last):
            ValueError: Invalid data points. Each point should be a tuple of two values.

            Case 4: Valid points with two unique data points
            >>> LinearRegressor._validate_points([(1, 2), (3, 4)])

            Case 5: Empty list of points
            >>> LinearRegressor._validate_points([])
            Traceback (most recent call last):
            ValueError: Invalid data points. The number of unique data points must be greater than 1.
        """
        unique_points = (
            len(set(points)) > 1
        )  # We convert the point list to a set to merge any duplicates
        if not unique_points:
            raise ValueError(
                "Invalid data points. The number of unique data points must be greater than 1."
            )

        if not all(isinstance(point, tuple) and len(point) == 2 for point in points):
            raise ValueError(
                "Invalid data points. Each point should be a tuple of two values."
            )

    def fit(self, points):
        """
        Fit a linear regression model to the input data points.

        Args:
            points (iterable): Iterable containing data points.

        Returns:
            LinearRegressor: Self for method chaining.

        Raises:
            ValueError: If the number of unique data points is less than 2.

        Notes:
            The `fit` method calculates the slope, y-intercept, and x-intercept based on the
            provided data points. However, in cases where the ranges of x and y values differ
            significantly, precision issues may arise. In such situations, consider using the
            `smart_fit` method for more accurate and stable results.

        Example:
            >>> data_points = [(1, 5), (2, 10), (3, 15)]
            >>> regressor = LinearRegressor().fit(data_points)
            >>> print(regressor.slope, regressor.y_intercept)
            5.0 0.0
            >>> print(regressor.x_intercept)
            0.0
        """
        points = list(points)
        n = len(points)

        self._validate_points(points)

        x_data = [point[0] for point in points]
        y_data = [point[1] for point in points]

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
            self.slope = None
        self.y_intercept = (sum_y - self.slope * sum_x) / n
        try:
            self.x_intercept = -self.y_intercept / self.slope
        except ZeroDivisionError:
            if sum_y == 0:
                self.x_intercept = 0
            else:
                self.x_intercept = None
        # Fix silly signed zeros
        self.x_intercept = 0.0 if self.x_intercept == -0.0 else self.x_intercept
        self.y_intercept = 0.0 if self.y_intercept == -0.0 else self.y_intercept
        self.slope = 0.0 if self.slope == -0.0 else self.slope
        return self

    def smart_fit(self, points):
        """
        Fit a linear regression model to the input data points, automatically selecting
        the orientation (inverted or not) based on the scale of the data.

        This method is useful when dealing with datasets where the ranges of the x and y
        values differ significantly. In such cases, choosing the correct orientation of
        the line (horizontal or vertical) can lead to more accurate and stable results.

        Args:
            points (iterable): Iterable containing data points.

        Returns:
            LinearRegressor: Self for method chaining.

        Notes:
            The `smart_fit` method considers the data ranges and chooses the orientation
            that minimizes the impact of potential precision issues, providing more robust
            results when dealing with imbalanced scales of x and y values.

            After fitting, the attributes `slope`, `y_intercept`, and `x_intercept` will
            be updated accordingly, and the `inverted` attribute will indicate whether
            the line orientation has been adjusted.

        Example:
            >>> data_points = [(1, 5), (2, 10), (3, 15)]
            >>> regressor = LinearRegressor().smart_fit(data_points)
            >>> print(regressor.slope, regressor.y_intercept)
            5.0 0.0
            >>> print(regressor.inverted)
            True
        """
        self._validate_points(points)

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

        # un-invert the result if necessary
        if self.inverted:
            try:
                self.y_intercept = (-1 / self.slope) * self.y_intercept
                self.slope = 1 / self.slope
                self.x_intercept = -self.y_intercept / self.slope
            except ZeroDivisionError:
                self.x_intercept, self.y_intercept = self.y_intercept, self.x_intercept
                self.slope = math.copysign(math.inf, self.slope)
        # Fix silly signed zeros
        self.x_intercept = 0.0 if self.x_intercept == -0.0 else self.x_intercept
        self.y_intercept = 0.0 if self.y_intercept == -0.0 else self.y_intercept
        self.slope = 0.0 if self.slope == -0.0 else self.slope
        return self

    def predict_y(self, x_values):
        """
        Predict y values for given x values using the fitted linear regression model.

        Args:
            x_values (iterable or float): List of x values or a single x value for which
                to predict y values.

        Returns:
            list or float: If a list is provided, returns a list of predicted y values
                corresponding to the input x values. If a single value is provided,
                returns the predicted y value for that x value.

        Example:
            >>> data_points = [(1, 5), (2, 10), (3, 15)]
            >>> regressor = LinearRegressor().smart_fit(data_points)

            # Example 1: Predicting for a list of x values
            >>> new_x_values = [4, 5, 6]
            >>> predicted_y_values = regressor.predict_y(new_x_values)
            >>> print("Predicted y values for new x values:", predicted_y_values)
            Predicted y values for new x values: [20.0, 25.0, 30.0]

            # Example 2: Predicting for a single x value
            >>> single_x_value = 7
            >>> predicted_y_value = regressor.predict_y(single_x_value)
            >>> print("Predicted y value for the single x value:", predicted_y_value)
            Predicted y value for the single x value: 35.0
        """
        if isinstance(x_values, (list, tuple)):
            return [(self.slope * x) + self.y_intercept for x in x_values]
        else:
            return (self.slope * x_values) + self.y_intercept

    def predict_x(self, y_values):
        """
        Predict x values for given y values using the fitted linear regression model.

        Args:
            y_values (iterable or float): List of y values or a single y value for which
                to predict x values.

        Returns:
            list or float: If a list is provided, returns a list of predicted x values
                corresponding to the input y values. If a single value is provided,
                returns the predicted x value for that y value.

        Example:
            >>> data_points = [(1, 5), (2, 10), (3, 15)]
            >>> regressor = LinearRegressor().smart_fit(data_points)

            # Example 1: Predicting for a list of y values
            >>> new_y_values = [18, 22, 28]
            >>> predicted_x_values = regressor.predict_x(new_y_values)
            >>> print("Predicted x values for new y values:", predicted_x_values)
            Predicted x values for new y values: [3.6, 4.4, 5.6]

            # Example 2: Predicting for a single y value
            >>> single_y_value = 30
            >>> predicted_x_value = regressor.predict_x(single_y_value)
            >>> print("Predicted x value for the single y value:", predicted_x_value)
            Predicted x value for the single y value: 6.0
        """
        if isinstance(y_values, (list, tuple)):
            return [(y - self.y_intercept) / self.slope for y in y_values]
        else:
            return (y_values - self.y_intercept) / self.slope


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import random

    # Generate a more diverse dataset for linear regression
    point_count = 30
    noise_standard_deviation = 1.4
    line_slope = 0.8

    # Generate data points with Gaussian noise
    example_data = [
        (x, x * line_slope + random.gauss(0, noise_standard_deviation))
        for x in range(1, point_count + 1)
    ]

    # Create a LinearRegressor instance and fit it to the example data
    regressor = LinearRegressor().smart_fit(example_data)

    # Display the fitted line and data points using matplotlib
    x_values = [point[0] for point in example_data]
    y_values = [point[1] for point in example_data]

    # Plot the data points
    plt.scatter(x_values, y_values, label="Data Points", color="blue", alpha=0.7)

    # Plot the actual line
    actual_line = [x * line_slope for x in x_values]
    plt.plot(
        x_values,
        actual_line,
        label="Actual Line",
        color="green",
        linestyle="--",
        linewidth=2,
    )

    # Plot the fitted line
    plt.plot(
        x_values,
        regressor.predict_y(x_values),
        label="Fitted Line",
        color="orange",
        linewidth=2,
    )

    # Label the axes
    plt.xlabel("X Values")
    plt.ylabel("Y Values")

    # Keep x and y axes the same scale so that we can see the slope
    plt.gca().set_aspect("equal")

    # Add grid lines for better visualization
    plt.grid(True, linestyle="--", alpha=0.7)

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()
