from vex import *
import sys

brain = Brain()


class BinarySemaphore:
    """
    Represents a binary semaphore (thread lock) with two states, locked and unlocked
    and methods to acquire and release the lock.

    See Also:
        https://en.m.wikipedia.org/wiki/Semaphore_(programming)
    """

    def __init__(self):
        self.locked = False
        self.attempting_acquisition = False

    def is_locked(self):
        """
        Returns True if the semaphore is locked or an acquisition attempt is in progress, False otherwise.
        """
        return self.locked or self.attempting_acquisition

    def acquire(self):
        """
        Acquires the lock. If the lock is already held by another thread, this method will block until the lock is released.
        """
        self.attempting_acquisition = True
        while self.locked:
            pass
        self.locked = True
        self.attempting_acquisition = False

    def release(self):
        """
        Releases the lock.
        """
        self.locked = False


class SafeList:
    """
    A thread-safe wrapper for a list using BinarySemaphore to prevent simultaneous access.
    """

    def __init__(self):
        """
        Initializes the SafeList with an empty list and a BinarySemaphore.
        """
        self._list = []
        self._lock = BinarySemaphore()

    def _safe_method_call(self, method, *args, **kwargs):
        """
        Acquires the lock, executes the specified method with the given arguments,
        and then releases the lock.
        """
        self._lock.acquire()
        # brain.screen.print("SMCA")
        try:
            return method(*args, **kwargs)
        finally:
            # brain.screen.print("SMCR")
            self._lock.release()

    def append(self, item):
        """
        Appends an item to the list in a thread-safe manner.
        """
        self._safe_method_call(self._list.append, item)

    def remove(self, item):
        """
        Removes the first occurrence of the specified item from the list in a thread-safe manner.
        """
        self._safe_method_call(self._list.remove, item)

    def pop(self, index=-1):
        """
        Removes and returns the item at the specified index in a thread-safe manner.
        If no index is specified, removes and returns the last item in the list.
        """
        return self._safe_method_call(self._list.pop, index)

    def __getitem__(self, index):
        """
        Retrieves the item at the specified index in a thread-safe manner.
        """
        return self._safe_method_call(self._list.__getitem__, index)

    def __setitem__(self, index, value):
        """
        Sets the item at the specified index to the given value in a thread-safe manner.
        """
        self._safe_method_call(self._list.__setitem__, index, value)

    def __len__(self):
        """
        Returns the number of items in the list in a thread-safe manner.
        """
        return self._safe_method_call(len, self._list)

    def __str__(self):
        """
        Returns a string representation of the list in a thread-safe manner.
        """
        return self._safe_method_call(str, self._list)

    def __bool__(self):
        """
        Returns True if the list is not empty, False otherwise.
        """
        return self._safe_method_call(bool, self._list)


class SerialCommunication:
    def __init__(self):
        self.incoming_messages = SafeList()
        self.outgoing_messages = SafeList()

        Thread(self.get_loop)
        Thread(self.send_loop)

    def get_loop(self):
        while True:
            self.incoming_messages.append(sys.stdin.readline().strip("\n"))
            wait(10, MSEC)

    def read_file(self):
        file_contents = ""
        self.send("Ready to receive file, please provide filename")
        while not self.has_incoming_messages():
            wait(10, MSEC)
        filename = self.receive()
        # brain.screen.print("Receiving file: " + filename)
        # brain.screen.next_row()

        while True:
            chunk = self.receive(True)
            brain.screen.print("Read chunk: " + chunk)
            brain.screen.next_row()

            if "\xd1" not in chunk:
                file_contents += chunk + "\n"
            else:
                break
        return filename, file_contents

    def send_loop(self):
        while True:
            if self.has_outgoing_messages():
                sys.stdout.write(str(self.outgoing_messages.pop(0)).encode() + b"\n")
            wait(10, MSEC)

    def has_incoming_messages(self):
        return bool(self.incoming_messages)

    def has_outgoing_messages(self):
        return bool(self.outgoing_messages)

    def send(self, message):
        self.outgoing_messages.append(message)

    def receive(self, blocking=False):
        if blocking:
            while not self.has_incoming_messages():
                wait(10, MSEC)
        if self.has_incoming_messages():
            return self.incoming_messages.pop(0)
        return None


def md5(message):
    # Initialize variables
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476

    # Constants table
    K = bytearray(
        [
            0xD76AA478,
            0xE8C7B756,
            0x242070DB,
            0xC1BDCEEE,
            0xF57C0FAF,
            0x4787C62A,
            0xA8304613,
            0xFD469501,
            0x698098D8,
            0x8B44F7AF,
            0xFFFF5BB1,
            0x895CD7BE,
            0x6B901122,
            0xFD987193,
            0xA679438E,
            0x49B40821,
            0xF61E2562,
            0xC040B340,
            0x265E5A51,
            0xE9B6C7AA,
            0xD62F105D,
            0x02441453,
            0xD8A1E681,
            0xE7D3FBC8,
            0x21E1CDE6,
            0xC33707D6,
            0xF4D50D87,
            0x455A14ED,
            0xA9E3E905,
            0xFCEFA3F8,
            0x676F02D9,
            0x8D2A4C8A,
            0xFFFA3942,
            0x8771F681,
            0x6D9D6122,
            0xFDE5380C,
            0xA4BEEA44,
            0x4BDECFA9,
            0xF6BB4B60,
            0xBEBFBC70,
            0x289B7EC6,
            0xEAA127FA,
            0xD4EF3085,
            0x04881D05,
            0xD9D4D039,
            0xE6DB99E5,
            0x1FA27CF8,
            0xC4AC5665,
            0xF4292244,
            0x432AFF97,
            0xAB9423A7,
            0xFC93A039,
            0x655B59C3,
            0x8F0CCC92,
            0xFFEFF47D,
            0x85845DD1,
            0x6FA87E4F,
            0xFE2CE6E0,
            0xA3014314,
            0x4E0811A1,
            0xF7537E82,
            0xBD3AF235,
            0x2AD7D2BB,
            0xEB86D391,
        ]
    )

    # Initialize message length in bits
    message_len = len(message) * 8

    # Pre-processing: append a single '1' bit, append '0' bits until message length in bits is congruent to 448 modulo 512
    message += bytearray(b"\x80")
    message += bytearray(b"\x00" * ((56 - (len(message) % 64)) % 64))

    # Append original length in bits
    message += bytearray(message_len.to_bytes(8, "little"))

    # Process message in 512-bit chunks
    chunks = [message[i : i + 64] for i in range(0, len(message), 64)]

    for chunk in chunks:
        # Initialize hash value for this chunk
        a = h0
        b = h1
        c = h2
        d = h3

        # Process each 512-bit chunk in 16 32-bit words
        words = [int.from_bytes(chunk[i : i + 4], "little") for i in range(0, 64, 4)]

        # Main loop
        for i in range(64):
            if 0 <= i <= 15:
                f = (b & c) | ((~b) & d)
                g = i
            elif 16 <= i <= 31:
                f = (d & b) | ((~d) & c)
                g = (5 * i + 1) % 16
            elif 32 <= i <= 47:
                f = b ^ c ^ d
                g = (3 * i + 5) % 16
            elif 48 <= i <= 63:
                f = c ^ (b | (~d))
                g = (7 * i) % 16

            # Perform the round calculation
            temp = d
            d = c
            c = b
            b = (b + ((a + f + K[i] + words[g]) & 0xFFFFFFFF)) & 0xFFFFFFFF
            a = temp

        # Update hash values
        h0 = (h0 + a) & 0xFFFFFFFF
        h1 = (h1 + b) & 0xFFFFFFFF
        h2 = (h2 + c) & 0xFFFFFFFF
        h3 = (h3 + d) & 0xFFFFFFFF

    # Produce the final hash value
    digest = (
        bytearray(h0.to_bytes(4, "little"))
        + bytearray(h1.to_bytes(4, "little"))
        + bytearray(h2.to_bytes(4, "little"))
        + bytearray(h3.to_bytes(4, "little"))
    )

    return "".join(["{:02x}".format(byte) for byte in digest])


def main():
    brain.screen.print(md5(open("test.txt", "rb").read()))
    brain.screen.next_row()

    serial = SerialCommunication()
    while True:
        if serial.has_incoming_messages():
            received = serial.receive()
            brain.screen.print(received)
            brain.screen.next_row()
            if "tx" in received:
                file_path, file_contents = serial.read_file()
                brain.screen.clear_screen()
                brain.screen.set_cursor(1, 1)
                brain.screen.print("file path: " + file_path)
                brain.screen.next_row()
                brain.screen.print("file contents: " + file_contents)
                with open(file_path, "w") as f:
                    f.write(file_contents)
        serial.send("time:" + str(brain.timer.time(SECONDS)))
        wait(100, MSEC)


if __name__ == "__main__":
    main()
