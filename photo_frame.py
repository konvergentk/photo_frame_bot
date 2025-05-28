import io
from PIL import Image, ImageOps, ImageColor
from dataclasses import dataclass


@dataclass
class FrameSettings:
    border_color: str = "white"
    border_thickness: str = "10%"  # в пикселях или процентах, например '10%'
    aspect_ratio: str = "square"
    quality: int = 95


def parse_color(color):
    try:
        return ImageColor.getrgb(color)
    except Exception as e:
        raise ValueError(f"Ошибка цвета: {color}. {e}")


def parse_thickness(thickness, image_size):
    """Толщина рамки в пикселях"""
    if isinstance(thickness, str) and thickness.endswith("%"):
        percent = float(thickness.strip("%")) / 100
        return int(min(image_size) * percent)
    else:
        return int(thickness)


def parse_aspect_ratio(ratio):
    presets = {
        "square": (1, 1),
        "portrait": (4, 5),
        "story": (9, 16),
        "landscape": (16, 9),
    }
    if ratio in presets:
        return presets[ratio]
    elif ":" in ratio:
        w, h = map(int, ratio.split(":"))
        return (w, h)
    else:
        raise ValueError(f"Неверное соотношение: {ratio}")


class FrameProcessor:
    def __init__(self, settings: FrameSettings):
        self.settings = settings

    def process(self, input_stream) -> io.BytesIO:
        img = Image.open(input_stream)
        img = ImageOps.exif_transpose(img)

        original_width, original_height = img.size
        original_ratio = original_width / original_height

        aspect_w, aspect_h = parse_aspect_ratio(self.settings.aspect_ratio)
        target_ratio = aspect_w / aspect_h

        border_thickness = parse_thickness(self.settings.border_thickness, img.size)
        border_color = parse_color(self.settings.border_color)

        if original_ratio > target_ratio:
            new_width = original_width
            new_height = int(original_width / target_ratio)
        else:
            new_height = original_height
            new_width = int(original_height * target_ratio)

        background = Image.new(
            "RGB",
            (new_width + 2 * border_thickness, new_height + 2 * border_thickness),
            border_color,
        )

        offset_x = (background.width - original_width) // 2
        offset_y = (background.height - original_height) // 2
        background.paste(img, (offset_x, offset_y))

        output = io.BytesIO()
        background.save(output, format="JPEG", quality=self.settings.quality, optimize=True, subsampling=0)
        output.seek(0)
        return output

