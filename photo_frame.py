from PIL import Image, ImageOps, ImageColor
import os


def parse_color(color):
    try:
        return ImageColor.getrgb(color.strip())
    except Exception:
        raise ValueError(f"Некорректный цвет: {color}")


def parse_thickness(thickness_str, image_size):
    thickness_str = thickness_str.strip()
    if thickness_str.endswith("%"):
        percent = float(thickness_str.rstrip("%")) / 100
        return int(min(image_size) * percent)
    else:
        return int(thickness_str)


def parse_aspect_ratio(ratio_str):
    ratio_str = ratio_str.strip().lower()
    presets = {
        "square": (1, 1),
        "portrait": (4, 5),
        "story": (9, 16),
        "landscape": (16, 9),
    }
    if ratio_str in presets:
        return presets[ratio_str]
    elif ":" in ratio_str:
        w, h = map(int, ratio_str.split(":"))
        return w, h
    else:
        raise ValueError(f"Некорректное соотношение сторон: {ratio_str}")


def add_frame(input_path, output_path, color, thickness, aspect_ratio):
    img = Image.open(input_path)
    img = ImageOps.exif_transpose(img)

    border_color = parse_color(color)
    border_thickness = parse_thickness(thickness, img.size)
    target_ratio = parse_aspect_ratio(aspect_ratio)
    target_ratio_float = target_ratio[0] / target_ratio[1]

    original_width, original_height = img.size
    current_ratio = original_width / original_height

    if current_ratio > target_ratio_float:
        new_width = original_width
        new_height = int(original_width / target_ratio_float)
    else:
        new_height = original_height
        new_width = int(original_height * target_ratio_float)

    background = Image.new(
        "RGB",
        (new_width + 2 * border_thickness, new_height + 2 * border_thickness),
        border_color,
    )
    offset_x = (background.width - original_width) // 2
    offset_y = (background.height - original_height) // 2
    background.paste(img, (offset_x, offset_y))
    background.save(output_path, quality=95, optimize=True)
