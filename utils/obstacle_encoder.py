from PIL import Image

img = Image.open("Pathfinding_Obstacles.png")
x_size, y_size = img.size

bytes_for_size = 8

bit_list = []

# Analyze the image to determine obstacle positions
for y in range(y_size):
    for x in range(x_size):
        pixel = img.getpixel((x, y))
        bit_list.append(pixel != (0, 0, 0, 0))

bit_list_extra_size = len(bit_list) % 8

bit_list.extend([1] * bit_list_extra_size)  # Pad up to the nearest byte

byte_list = []

byte_index = 0
bit_index = 0
for bit in bit_list:
    if bit_index == 0:
        byte_list.append(int(bit))
    else:
        byte_list[byte_index] <<= 1
        byte_list[byte_index] |= bit

    bit_index += 1
    if bit_index % 8 == 0:
        byte_index += 1
        bit_index = 0

length_list = []

max_length = 2 ** (8 * bytes_for_size)

if x_size > max_length:
    raise ValueError(f"X size: {x_size} overflows the {bytes_for_size} bytes reserved for size, maximum size for {bytes_for_size} bytes is {max_length}")


for i in range(bytes_for_size):
    length_list.append(x_size & 0b11111111)
    x_size >>= 8

length_list.extend(byte_list)
byte_list = length_list

array_str = "".join([chr(byte) for byte in byte_list])

with open("obstacles.bin", "w") as f:
    f.write(array_str)
