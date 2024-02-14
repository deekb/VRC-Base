bytes_for_size = 8


class PathfindingEnvironment:
    def __init__(self):
        self.obstacle_list = []
        self.width = None

    def load_from_file(self, file_object):
        with file_object as f:
            file_contents = f.read()
            length_list = [ord(char) for char in file_contents[:bytes_for_size]]
            length_byte = 0
            for byte in reversed(length_list):
                length_byte <<= 8
                length_byte |= byte

            self.width = length_byte
            print(f"Set width to {self.width}")
            self.obstacle_list = [ord(char) for char in file_contents[bytes_for_size:]]

    def load_from_list(self, obstacle_list, width):
        self.obstacle_list = obstacle_list
        self.width = width

    def get_at(self, x, y):
        bit_index = (y * self.width) + x

        byte_index = bit_index // 8

        bit_of_byte = bit_index % 8

        target_byte = self.obstacle_list[byte_index]

        target_bit = target_byte & (1 << (7 - bit_of_byte))

        return bool(target_bit)


pathfinding_environment = PathfindingEnvironment()

pathfinding_environment.load_from_file(open("obstacles.bin", "r"))


for y in range(0, 122):
    for x in range(0, 122):
        print("X" if pathfinding_environment.get_at(x, y) else "-", end="")
    print()
