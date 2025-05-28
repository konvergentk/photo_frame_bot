import os
from PIL import Image, ImageOps, ImageColor

def parse_color(color):
    try:
        return ImageColor.getrgb(color)
    except Exception as e:
        raise ValueError(f"Ошибка цвета: {color}. {e}")

def parse_thickness(thickness, image_size):
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
        raise ValueError(f"Неверный формат соотношения: {ratio}")

def add_frame_to_image(
    input_path,
    output_path,
    aspect_ratio=(1, 1),
    border_thickness=50,
    border_color=(255, 255, 255),
    quality=95,
):
    img = Image.open(input_path)
    img = ImageOps.exif_transpose(img)

    original_width, original_height = img.size
    original_ratio = original_width / original_height

    aspect_ratio = parse_aspect_ratio(aspect_ratio)
    border_color = parse_color(border_color)
    border_thickness = parse_thickness(border_thickness, img.size)

    target_ratio = aspect_ratio[0] / aspect_ratio[1]

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

    ext = os.path.splitext(output_path)[1].lower()
    save_kwargs = {}
    if ext in [".jpg", ".jpeg"]:
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
        save_kwargs["subsampling"] = 0

    background.save(output_path, **save_kwargs)

    return output_path
