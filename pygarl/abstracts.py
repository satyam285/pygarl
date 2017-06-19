class ControlSignal:
    START = 0
    STOP = 1
    ERROR = 2


class AbstractDataReader(object):
    """
    Represents the Abstraction of the low level data receiver and manages the communication
    with the signal source, as an Arduino or GPIOs pins.
    """
    def __init__(self):
        self.managers = []

    def attach_manager(self, manager):
        """
        Attach a manager to the DataReader, so that when an event occurs the manager is notified
        """
        self.managers.append(manager)

    def detach_manager(self, manager):
        """
        Detach the manager from the DataReader
        """
        self.managers.remove(manager)

    def notify_data(self, data):
        """
        Notify a new set of data to all the attached managers
        :param data: Float array containing the sensor data, every element is an axis reading
        """
        # Cycle through all managers and call their receive_data method, notifying the data event
        for manager in self.managers:
            manager.receive_data(data)

    def notify_signal(self, signal):
        """
        Notify a ControlSignal to all the attached managers
        :param signal: One of the ControlSignal values
        :return: 
        """
        # Cycle through all managers and notify them of the new signal by calling their receive_signal method
        for manager in self.managers:
            manager.receive_signal(signal)

    def mainloop(self):
        """
        Not implemented yet, represents the method that endlessly loops listening for events
        """
        raise NotImplementedError("This method is not implemented in the abstract class.")


class AbstractSampleManager(object):
    """
    Represents the abstraction of a SampleManager, handles the packaging of data into Samples
    The logic involved vary based on the implementation.
    """
    def __init__(self, axis=6):
        """
        Initializes the buffer and the receivers list
        :param axis: Number of axis of the sensors
        """
        self.axis = axis
        self.buffer = []
        self.receivers = []

    def attach_receiver(self, receiver):
        """
        Attach a receiver to the SampleManager
        :param receiver: Receiver
        """
        self.receivers.append(receiver)

    def detach_receiver(self, receiver):
        """
        Detach the receiver from the SampleManager
        :param receiver:  Receiver
        """
        self.receivers.remove(receiver)

    def notify_receivers(self, sample):
        """
        Notify a sample to all the receivers
        :param sample: Sample
        """
        # Cycle through all receivers, sending them the Sample
        for receiver in self.receivers:
            receiver.receive_sample(sample)

    def receive_data(self, data):
        raise NotImplementedError("This method is not implemented in the abstract class.")

    def receive_signal(self, signal):
        raise NotImplementedError("This method is not implemented in the abstract class.")

    def package_sample(self):
        raise NotImplementedError("This method is not implemented in the abstract class.")


class Receiver(object):
    """
    Represents the entity that receives a sample and processes it
    """
    def receive_sample(self, sample):
        raise NotImplementedError("This method is not implemented in the abstract class.")