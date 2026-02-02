from struct import unpack, pack
from typing import BinaryIO, Tuple, Any, Union
import bpy

# blender functions

def show_uv_invalid(tool_name):
    def draw(self, context):
        self.layout.label(text="UV out of range!")
    bpy.context.window_manager.popup_menu(draw_func=draw, title=tool_name, icon="ERROR")

def show_not_read_nsbtx(tool_name):
    """Shows a pop-up to tell the user the file couldn't be read"""
    def draw(self, context):
        self.layout.label(text="NSBTX File could not be read!")
    bpy.context.window_manager.popup_menu(draw_func=draw, title=tool_name, icon="ERROR")

def show_tex_not_found(tool_name,texName):
    """Shows a pop-up to tell the user the file couldn't be read"""
    def draw(self, context):
        self.layout.label(text="Texture "+texName+" not found in NSBTX!")
    bpy.context.window_manager.popup_menu(draw_func=draw, title=tool_name, icon="ERROR")

def show_pal_not_found(tool_name,texName):
    """Shows a pop-up to tell the user the file couldn't be read"""
    def draw(self, context):
        self.layout.label(text="Palette "+texName+" not found in NSBTX!")
    bpy.context.window_manager.popup_menu(draw_func=draw, title=tool_name, icon="ERROR")

# file read functions


def read_str(file: BinaryIO, count: int) -> str:
    """Reads and returns a string.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        count : int
            How many bytes to read.

        Returns
        -------
        str
            The string read.
        """
    return file.read(count).decode("utf-8", "ignore").rstrip('\x00')


def read_integer(file: BinaryIO, endian="<") -> int:
    """Reads and returns an integer.

    Parameters
    ----------
    file : BinaryIO
        The file read.

    endian :
        Endian of what's being read.

    Returns
    -------
    int
        The integer read.
    """

    return unpack(endian + "I", file.read(4))[0]


def read_short(file: BinaryIO, endian="<") -> int:
    """Reads and returns a short.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        endian :
            Endian of what's being read.

        Returns
        -------
        int
            The short read.
        """

    return unpack(endian + "H", file.read(2))[0]


def read_byte(file: BinaryIO, endian="<") -> int:
    """Reads and returns a byte.

        Parameters
        ----------
        file : BinaryIO
            The file read.

        endian :
            Endian of what's being read.

        Returns
        -------
        int
            The byte read.
        """

    return unpack(endian + "B", file.read(1))[0]


# file write functions


def write_aligned(file: BinaryIO, divide_by: int):
    """Writes the file until at an alignment.

    Parameters
    ----------
    file : BinaryIO
        The file read.
    divide_by : int
        Alignment to write to.
    """
    while file.tell() % divide_by:
        write_byte(file, "<", 0)


def write_string(file: BinaryIO, *value: bytes):
    """Writes a tuple of strings to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        value : tuple
            The strings to write.

    """
    for values in value:
        file.write(pack(str(len(values)) + "s", values))


def write_float(file: BinaryIO, endian: str, *value: float):
    """Writes a tuple of floats to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The floats to write.

    """
    file.write(pack(endian + str(len(value)) + "f", *value))


def write_integer(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of integers to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The integers to write.

    """
    file.write(pack(endian + str(len(value)) + "I", *value))

def write_signed_integer(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of integers to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The integers to write.

    """
    file.write(pack(endian + str(len(value)) + "i", *value))


def write_short(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of shorts to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The shorts to write.

    """
    file.write(pack(endian + str(len(value)) + "H", *value))

def write_signed_short(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of shorts to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The shorts to write.

    """
    file.write(pack(endian + str(len(value)) + "h", *value))


def write_byte(file: BinaryIO, endian: str, *value: int):
    """Writes a tuple of bytes to a file.

        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        endian :
            Endian of what's being wrote.

        value : tuple
            The bytes to write.

    """
    file.write(pack(endian + str(len(value)) + "B", *value))


def write_string_set_length(file: BinaryIO, value: str, length: int):
    """Writes a string of at most a given length, and ensures padding up to that length
    
        Parameters
        ----------
        file : BinaryIO
            The file to write to.

        value : str
            The bytes to write.
        
        length : int
            The length the string should be written

    """
    if (len(value) >= length):
        value = value[:length-1]
    
    file.write(value.encode('ascii'))
    
    writtenCount = len(value)
    while writtenCount < length:
        write_byte(file, "<", 0)
        writtenCount += 1