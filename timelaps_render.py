from dataclasses import dataclass

import cv2
import numpy as np
from typing import Tuple, List


RGB_LENGTH = 3


@dataclass
class TimelapseSettings:
    """
    scale_factor (int): Scaling factor for each pixel
    frame_rate (int): Frame rate for the generated video.
    desired_duration (int): Desired duration of the video in seconds.
    """
    scale_factor: int
    frame_rate: int
    desired_duration: int


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    """
    Convert a hexadecimal color value to an RGB tuple.

    Parameters:
        value (str): Hexadecimal color value.

    Returns:
        tuple: Corresponding RGB values.
    """
    value = value.lstrip('#')
    length = len(value)
    r, g, b = (int(value[i:i + length // RGB_LENGTH], 16) for i in range(0, length, length // RGB_LENGTH))
    return r, g, b


def initialize_canvas(upscale_width: int, upscale_height: int) -> np.ndarray:
    """
    Initialize a black canvas of given dimensions.

    Parameters:
        upscale_width (int): Width of canvas.
        upscale_height (int): Height of canvas.

    Returns:
        np.ndarray: Initialized canvas.
    """
    return np.zeros((upscale_height, upscale_width, 3), dtype=np.uint8)


def draw_pixel_on_canvas(canvas: np.ndarray, x: int, y: int, color: str, scale_factor: int) -> np.ndarray:
    """
    Draw a pixel on the given canvas using the specified color.

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
    """
    Creates a timelapse video from the events and the palette provided.

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
    canvas = initialize_canvas(upscale_width, upscale_height)

    num_frames = len(events)
    events_per_frame = num_frames // (settings.desired_duration * settings.frame_rate)
    if events_per_frame == 0:
        return
    out = cv2.VideoWriter(output_path,
                          cv2.VideoWriter_fourcc(*'mp4v'),
                          settings.frame_rate,
                          (upscale_width, upscale_height))

    for i, (x, y, color_index) in enumerate(events):
        color = palette[color_index]
        canvas = draw_pixel_on_canvas(canvas, x, y, color, settings.scale_factor)

        if i % events_per_frame == 0:
            out.write(canvas)
    out.release()
