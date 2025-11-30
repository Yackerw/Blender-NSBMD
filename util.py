from struct import unpack, pack
from typing import BinaryIO, Tuple, Any, Union

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


