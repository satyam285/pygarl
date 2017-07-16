import serial

import sys

from pygarl.abstracts import AbstractDataReader, ControlSignal


class SerialDataReader(AbstractDataReader):
    """
    Used to get the data needed to make a sample from a serial connection
    """
    def __init__(self, serial_port, baud_rate=38400, timeout=1, expected_axis=6, verbose=False):
        AbstractDataReader.__init__(self)

        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.verbose = verbose
        self.expected_axis = expected_axis

        # Set the serial connection as None initially
        self.serial = None

    def open(self):
        """
        Open the serial connection using the parameters specified in the class constructor
        """
        # Make sure the serial connection is not open, if open raise an exception
        if self.serial is not None:
            raise RuntimeError("The serial connection is already opened")

        # Open the serial connection
        self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=self.timeout)

    def close(self):
        """
        Close the serial connection
        """
        # Check if the serial connection has been opened, if not raise an exception
        if self.serial is None:
            raise RuntimeError("The serial connection is not open, so it can't be closed.")

        # If the connection was open, close it
        self.serial.close()

        # Destroy the serial object
        self.serial = None

    def mainloop(self):
        """
        Endless loop that waits for data from the serial connection and dispatch events when they occur
        """
        # Enclosed in a try block to intercept a Ctrl+C press
        try:
            # Start the endless loop
            while True:
                # Read a line from the serial connection
                line = self.serial.readline()

                # This line is needed for backward compatibility
                # Converts the string into binary data for python > 3
                if sys.version_info >= (3,):
                    line = line.decode("utf-8")

                # Deleting the new line characters
                line = line.replace("\r\n", "")

                # If verbosity is true, print the received line
                if self.verbose:
                    print(line)

                # Analyze the received data, dispatching the correct event based on the content
                if line == "STARTING BATCH":
                    # Batch started, dispatch the START event
                    self.notify_signal(ControlSignal.START)
                elif line == "CLOSING BATCH":
                    # Batch closed, dispatch the STOP event
                    self.notify_signal(ControlSignal.STOP)
                elif line.startswith("START") and line.endswith("END"):
                    # Data line, parse the data
                    # A data line should have this format
                    # START -36 1968 16060 -108 258 -136 END

                    # Get the values by splitting the line
                    value_list = line.split(" ")

                    # Excluding START and END, there should be at least one value
                    # ( so the total length should be 2 + number of expected axis ).
                    if len(value_list) == (2 + self.expected_axis):
                        # Get the values contained in the list, by removing the first and last element ( START and END )
                        string_values = value_list[1:-1]

                        # Convert the values from string to float
                        values = list(map(lambda x: float(x), string_values))

                        # Dispatch the DATA event, sending the values
                        self.notify_data(values)
                    else:  # An error occurred, dispatch the ERROR event
                        self.notify_signal(ControlSignal.ERROR)
                elif line == "":  # This could be a timeout
                    # Dispatch the TIMEOUT event
                    self.notify_signal(ControlSignal.TIMEOUT)
                else:  # This must be an error
                    # Dispatch the ERROR event
                    self.notify_signal(ControlSignal.ERROR)
        except KeyboardInterrupt:  # When Ctrl+C is pressed, the loop terminates
            print('CLOSED MAINLOOP!')
