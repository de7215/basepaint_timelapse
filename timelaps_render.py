from dataclasses import dataclass
import numpy as np
import imageio
from typing import Tuple, List

RGB_LENGTH = 3


@dataclass
class TimelapseSettings:
    """Container for settings related to the timelapse rendering.

    Attributes:
        scale_factor (int): Scaling factor for each pixel.
        frame_rate (int): Frame rate for the generated video.
        desired_duration (int): Desired duration of the video in seconds.
    """
    scale_factor: int
    frame_rate: int
    desired_duration: int


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    """Convert a hexadecimal color value to an RGB tuple.

    Parameters:
        value (str): Hexadecimal color value.

    Returns:
        Tuple[int, int, int]: Corresponding RGB values.
    """
    value = value.lstrip('#')
    length = len(value)
    return tuple(int(value[i:i + length // RGB_LENGTH], 16) for i in range(0, length, length // RGB_LENGTH))


def get_nearest_size_divisible_by_16(dim: int) -> int:
    """Get the nearest size divisible by 16.

    Parameters:
        dim (int): Original dimension.

    Returns:
        int: Adjusted dimension.
    """
    return int(np.ceil(dim / 16.0)) * 16


def aligned_array(shape, dtype=np.uint8, align=16):
    """Creates an ndarray that is aligned to a specified number of bytes.

    Parameters:
        shape (tuple): Shape of the desired array.
        dtype (data-type): Desired data type.
        align (int): Byte-alignment value.

    Returns:
        ndarray: Aligned array.
    """
    n = np.prod(shape) * np.dtype(dtype).itemsize
    empty = np.empty(n + align, dtype=np.uint8)
    data_align = empty.ctypes.data % align
    offset = 0 if data_align == 0 else (align - data_align)
    return empty[offset:offset + n].view(dtype).reshape(shape)


def draw_pixel_on_canvas(canvas: np.ndarray, x: int, y: int, color: str, scale_factor: int) -> np.ndarray:
    """Draw a pixel on the given canvas using the specified color.

    Parameters:
        canvas (np.ndarray): The canvas to draw on.
        x (int): X-coordinate.
        y (int): Y-coordinate.
        color (str): Color value in hexadecimal.
        scale_factor (int): Scaling factor for pixel.

    Returns:
        np.ndarray: Updated canvas.
    """
    upscale_x, upscale_y = x * scale_factor, y * scale_factor
    canvas[upscale_y:upscale_y + scale_factor, upscale_x:upscale_x + scale_factor] = hex_to_rgb(color)
    return canvas


def render_timelapse_frames(output_path: str,
                            events: List[Tuple[int, int, int]],
                            palette: List[str],
                            settings: TimelapseSettings) -> None:
    """Creates a timelapse video from the events and the palette provided.

    Parameters:
        output_path (str): Path to save the generated video.
        events (list): List of events where each event is a tuple of x, y coordinates and color index.
        palette (list): List of color values.
        settings (TimelapseSettings): Settings for video rendering.
    """
    if len(events) == 0:
        return

    max_x, max_y = max(events, key=lambda p: p[0])[0], max(events, key=lambda p: p[1])[1]
    width, height = max_x + 1, max_y + 1
    upscale_width, upscale_height = width * settings.scale_factor, height * settings.scale_factor

    upscale_width = get_nearest_size_divisible_by_16(upscale_width)
    upscale_height = get_nearest_size_divisible_by_16(upscale_height)

    canvas = aligned_array((upscale_height, upscale_width, 3), dtype=np.uint8)

    num_frames = len(events)
    events_per_frame = num_frames // (settings.desired_duration * settings.frame_rate)
    if events_per_frame == 0:
        return

    frames = []

    for i, (x, y, color_index) in enumerate(events):
        color = palette[color_index]
        canvas = draw_pixel_on_canvas(canvas, x, y, color, settings.scale_factor)

        if i % events_per_frame == 0:
            frames.append(canvas.copy())

    with imageio.get_writer(output_path, fps=settings.frame_rate, codec='libx264', quality=9) as writer:
        for frame in frames:
            writer.append_data(frame)
