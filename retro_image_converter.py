from PIL import Image, ImageDraw, ImageOps, ImageEnhance
import math
import numpy as np
import os

def apply_lcd_pixel_effect(image, pixel_size=10, brightness_boost=1.5, orientation="vertical"):
    """
    LCDピクセル効果を適用（縦・横配置を選択可能）＋輝度補正。
    """
    image = image.resize((image.width // pixel_size, image.height // pixel_size), Image.Resampling.BOX)
    width, height = image.size
    lcd_image = Image.new("RGB", (width * pixel_size, height * pixel_size), "black")
    draw = ImageDraw.Draw(lcd_image)

    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            r = min(int(r * brightness_boost), 255)
            g = min(int(g * brightness_boost), 255)
            b = min(int(b * brightness_boost), 255)

            base_x = x * pixel_size
            base_y = y * pixel_size
            subpixel_size = pixel_size // 3

            if orientation == "vertical":
                draw.rectangle([base_x, base_y, base_x + subpixel_size, base_y + pixel_size], fill=(r, 0, 0))
                draw.rectangle([base_x + subpixel_size, base_y, base_x + 2 * subpixel_size, base_y + pixel_size], fill=(0, g, 0))
                draw.rectangle([base_x + 2 * subpixel_size, base_y, base_x + pixel_size, base_y + pixel_size], fill=(0, 0, b))
            elif orientation == "horizontal":
                draw.rectangle([base_x, base_y, base_x + pixel_size, base_y + subpixel_size], fill=(r, 0, 0))
                draw.rectangle([base_x, base_y + subpixel_size, base_x + pixel_size, base_y + 2 * subpixel_size], fill=(0, g, 0))
                draw.rectangle([base_x, base_y + 2 * subpixel_size, base_x + pixel_size, base_y + pixel_size], fill=(0, 0, b))

    return lcd_image


def apply_crt_warp_effect(image, strength=0.1):
    """
    CRT（ブラウン管）歪み効果を適用。
    """
    width, height = image.size
    center_x, center_y = width / 2, height / 2
    max_distance = math.sqrt(center_x**2 + center_y**2)
    warped_image = Image.new("RGB", (width, height), "black")
    warped_pixels = warped_image.load()
    original_pixels = image.load()

    for y in range(height):
        for x in range(width):
            dx, dy = x - center_x, y - center_y
            distance = math.sqrt(dx**2 + dy**2)
            distortion = 1 + strength * (distance / max_distance)**2
            src_x = center_x + dx / distortion
            src_y = center_y + dy / distortion
            x0, y0 = int(src_x), int(src_y)
            x1, y1 = min(x0 + 1, width - 1), min(y0 + 1, height - 1)
            a, b = src_x - x0, src_y - y0

            if 0 <= x0 < width and 0 <= y0 < height:
                pixel = tuple(
                    int(
                        (1 - a) * (1 - b) * original_pixels[x0, y0][i]
                        + a * (1 - b) * original_pixels[x1, y0][i]
                        + (1 - a) * b * original_pixels[x0, y1][i]
                        + a * b * original_pixels[x1, y1][i]
                    )
                    for i in range(3)
                )
                warped_pixels[x, y] = pixel

    return warped_image


def apply_refined_glitch_effect(image, shift_amount=5, intensity=0.8):
    """
    繊細なグリッチ効果を適用。
    """
    img_array = np.array(image)
    red_channel, green_channel, blue_channel = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
    shifted_red = np.roll(red_channel, shift_amount, axis=1)
    shifted_green = np.roll(green_channel, -shift_amount // 2, axis=0)
    blended_red = (intensity * shifted_red + (1 - intensity) * red_channel).astype(np.uint8)
    blended_green = (intensity * shifted_green + (1 - intensity) * green_channel).astype(np.uint8)
    refined_glitched_img = np.stack([blended_red, blended_green, blue_channel], axis=2)
    return Image.fromarray(refined_glitched_img)


def enhance_color_contrast(image, enhancement_factor=1.5):
    """
    色コントラストを強調。
    """
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(enhancement_factor)


def round_corners(image, radius=50):
    """
    四隅を丸くする。
    """
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255)
    rounded_image = Image.new("RGB", image.size)
    rounded_image.paste(image, mask=mask)
    return rounded_image


def retro_image_converter(input_path, orientation="vertical", apply_crt=False, apply_glitch=False, color_enhance=False):
    """
    レトロ加工を施す関数。
    - orientation: "vertical" または "horizontal"。
    - apply_crt: TrueでCRT歪み効果を適用。
    - apply_glitch: Trueでグリッチ効果を適用。
    - color_enhance: Trueで色コントラストを強調。
    """
    image = Image.open(input_path)
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_retro{ext}"

    image = apply_lcd_pixel_effect(image, pixel_size=10, brightness_boost=1.5, orientation=orientation)
    if apply_crt:
        image = apply_crt_warp_effect(image, strength=0.1)
    if apply_glitch:
        image = apply_refined_glitch_effect(image)
    if color_enhance:
        image = enhance_color_contrast(image, enhancement_factor=1.5)
    image = round_corners(image, radius=100)

    image.save(output_path)
    print(f"加工済み画像が保存されました: {output_path}")


if __name__ == "__main__":
    input_image = "/home/user/image.jpg/  # 入力ファイル名を指定
    orientation = input("縦配置（v）か横配置（h）を選んでください: ").lower()
    orientation = "vertical" if orientation == "v" else "horizontal"
    apply_crt = input("CRT効果を適用しますか？（y/n）: ").lower() == "y"
    apply_glitch = input("グリッチ効果を適用しますか？（y/n）: ").lower() == "y"
    color_enhance = input("色コントラストを強調しますか？（y/n）: ").lower() == "y"
    retro_image_converter(input_image, orientation=orientation, apply_crt=apply_crt, apply_glitch=apply_glitch, color_enhance=color_enhance)
