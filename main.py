from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFilter


WIDTH = 1400
HEIGHT = 1000
SUPERSAMPLE = 2
OUTPUT_PATH = Path("output/pelican_bike.png")


Color = tuple[int, int, int] | tuple[int, int, int, int]
Point = tuple[float, float]


class ScaledDraw:
    """Tiny adapter that keeps drawing code in design pixels while rendering larger."""

    def __init__(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        self.draw = draw
        self.scale = scale

    def _n(self, value: float) -> int:
        return int(round(value * self.scale))

    def _xy(self, xy: Sequence[float] | Sequence[Point]) -> tuple[int, ...] | list[tuple[int, int]]:
        if xy and isinstance(xy[0], (tuple, list)):  # type: ignore[index]
            return [(self._n(x), self._n(y)) for x, y in xy]  # type: ignore[misc]
        return tuple(self._n(value) for value in xy)  # type: ignore[arg-type]

    def _width(self, width: int) -> int:
        return max(1, self._n(width))

    def line(
        self,
        xy: Sequence[float] | Sequence[Point],
        fill: Color,
        width: int = 1,
        joint: str | None = None,
    ) -> None:
        kwargs = {"fill": fill, "width": self._width(width)}
        if joint is not None:
            kwargs["joint"] = joint
        self.draw.line(self._xy(xy), **kwargs)

    def ellipse(
        self,
        xy: Sequence[float],
        fill: Color | None = None,
        outline: Color | None = None,
        width: int = 1,
    ) -> None:
        self.draw.ellipse(self._xy(xy), fill=fill, outline=outline, width=self._width(width))

    def rectangle(
        self,
        xy: Sequence[float],
        fill: Color | None = None,
        outline: Color | None = None,
        width: int = 1,
    ) -> None:
        self.draw.rectangle(self._xy(xy), fill=fill, outline=outline, width=self._width(width))

    def polygon(
        self,
        xy: Sequence[Point],
        fill: Color | None = None,
        outline: Color | None = None,
        width: int = 1,
    ) -> None:
        points = self._xy(xy)
        self.draw.polygon(points, fill=fill)
        if outline is not None:
            self.draw.line([*points, points[0]], fill=outline, width=self._width(width), joint="curve")

    def arc(
        self,
        xy: Sequence[float],
        start: float,
        end: float,
        fill: Color,
        width: int = 1,
    ) -> None:
        self.draw.arc(self._xy(xy), start, end, fill=fill, width=self._width(width))

    def pieslice(
        self,
        xy: Sequence[float],
        start: float,
        end: float,
        fill: Color | None = None,
        outline: Color | None = None,
        width: int = 1,
    ) -> None:
        self.draw.pieslice(self._xy(xy), start, end, fill=fill, outline=outline, width=self._width(width))


def ellipse_bbox(cx: float, cy: float, rx: float, ry: float) -> tuple[float, float, float, float]:
    return (cx - rx, cy - ry, cx + rx, cy + ry)


def add_shadow(
    base: Image.Image,
    shape: Image.Image,
    blur: int,
    offset: tuple[int, int],
    opacity: int,
    scale: int,
) -> None:
    alpha = shape.getchannel("A").filter(ImageFilter.GaussianBlur(blur * scale))
    shadow = Image.new("RGBA", base.size, (31, 40, 46, opacity))
    shifted = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shifted.paste(shadow, (offset[0] * scale, offset[1] * scale), alpha)
    base.alpha_composite(shifted)
    base.alpha_composite(shape)


def draw_polyline(
    draw: ScaledDraw,
    points: Sequence[Point],
    fill: Color,
    width: int,
    joint: str = "curve",
) -> None:
    draw.line(points, fill=fill, width=width, joint=joint)


def draw_spokes(draw: ScaledDraw, center: Point, radius: int, count: int = 32) -> None:
    cx, cy = center
    for i in range(count):
        angle = (math.tau / count) * i
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        draw.line((cx, cy, x, y), fill=(125, 139, 146), width=2)


def draw_wheel(draw: ScaledDraw, center: Point, radius: int) -> None:
    cx, cy = center
    draw.ellipse(ellipse_bbox(cx, cy, radius + 9, radius + 9), outline=(42, 54, 58), width=16)
    draw.ellipse(ellipse_bbox(cx, cy, radius + 2, radius + 2), outline=(30, 38, 42), width=4)
    draw.ellipse(ellipse_bbox(cx, cy, radius - 2, radius - 2), outline=(207, 218, 221), width=5)
    draw_spokes(draw, center, radius - 12)
    draw.ellipse(ellipse_bbox(cx, cy, radius - 52, radius - 52), outline=(187, 199, 203), width=3)
    draw.ellipse(ellipse_bbox(cx, cy, 17, 17), fill=(66, 82, 90), outline=(237, 243, 242), width=4)


def draw_background(draw: ScaledDraw) -> None:
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(148 + (246 - 148) * t)
        g = int(202 + (231 - 202) * t)
        b = int(221 + (207 - 221) * t)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))

    sun_cx, sun_cy = 1120, 170
    for radius, alpha in [(150, 32), (105, 38), (68, 54)]:
        draw.ellipse(ellipse_bbox(sun_cx, sun_cy, radius, radius), fill=(255, 232, 151, alpha))
    draw.ellipse(ellipse_bbox(sun_cx, sun_cy, 48, 48), fill=(255, 222, 108, 235))

    cloud_color = (255, 255, 250, 190)
    for cx, cy, scale in [(240, 170, 1.0), (470, 120, 0.72), (990, 285, 0.85)]:
        draw.ellipse(ellipse_bbox(cx, cy, 92 * scale, 34 * scale), fill=cloud_color)
        draw.ellipse(ellipse_bbox(cx - 58 * scale, cy + 7 * scale, 64 * scale, 28 * scale), fill=cloud_color)
        draw.ellipse(ellipse_bbox(cx + 63 * scale, cy + 9 * scale, 58 * scale, 25 * scale), fill=cloud_color)

    draw.rectangle((0, 696, WIDTH, HEIGHT), fill=(116, 166, 135))
    draw.rectangle((0, 745, WIDTH, HEIGHT), fill=(96, 145, 112))
    draw.rectangle((0, 790, WIDTH, 880), fill=(87, 128, 107))
    draw.rectangle((0, 835, WIDTH, HEIGHT), fill=(232, 211, 164))
    draw.rectangle((0, 888, WIDTH, HEIGHT), fill=(219, 189, 135))

    for x in range(-80, WIDTH + 80, 90):
        draw.arc((x, 812, x + 120, 900), 210, 330, fill=(191, 154, 100), width=3)
    for x in range(0, WIDTH, 34):
        h = 7 + (x * 17) % 21
        draw.line((x, 745, x + 7, 745 - h), fill=(73, 120, 83), width=3)


def draw_bicycle(draw: ScaledDraw) -> None:
    rear = (455, 720)
    front = (930, 720)
    crank = (660, 710)
    seat = (610, 555)
    handle = (860, 540)
    fork_top = (835, 590)

    draw_wheel(draw, rear, 142)
    draw_wheel(draw, front, 142)

    frame = (201, 68, 78)
    frame_dark = (136, 45, 53)
    metal = (48, 63, 69)

    draw_polyline(draw, (rear, crank, front, fork_top, seat, rear), frame_dark, 17)
    draw_polyline(draw, (rear, crank, front, fork_top, seat, rear), frame, 11)
    draw_polyline(draw, (seat, crank), frame, 13)
    draw_polyline(draw, (seat, handle), frame, 12)
    draw.line((*fork_top, *front), fill=metal, width=12)
    draw.line((fork_top[0] - 20, fork_top[1] - 22, handle[0] + 55, handle[1] - 18), fill=metal, width=11)
    draw.arc((handle[0] + 28, handle[1] - 54, handle[0] + 112, handle[1] + 30), 195, 330, fill=metal, width=11)

    draw.line((seat[0] - 46, seat[1] - 18, seat[0] + 56, seat[1] - 22), fill=(73, 60, 52), width=22)
    draw.line((seat[0] - 31, seat[1] - 26, seat[0] + 45, seat[1] - 28), fill=(98, 81, 69), width=9)
    draw.line((seat[0] - 5, seat[1] - 12, seat[0], seat[1] + 44), fill=metal, width=9)

    draw.ellipse(ellipse_bbox(crank[0], crank[1], 38, 38), outline=(221, 211, 177), width=5)
    draw.ellipse(ellipse_bbox(crank[0], crank[1], 34, 34), outline=(50, 63, 67), width=9)
    draw.line((crank[0] - 7, crank[1] + 3, crank[0] - 72, crank[1] + 52), fill=metal, width=8)
    draw.line((crank[0] + 8, crank[1] - 4, crank[0] + 78, crank[1] - 62), fill=metal, width=8)
    draw.line((crank[0] - 100, crank[1] + 72, crank[0] - 52, crank[1] + 36), fill=(54, 65, 69), width=8)
    draw.line((crank[0] + 56, crank[1] - 82, crank[0] + 108, crank[1] - 52), fill=(54, 65, 69), width=8)
    draw.ellipse(ellipse_bbox(crank[0], crank[1], 10, 10), fill=(238, 242, 236), outline=(50, 63, 67), width=3)


def feather_polygon(cx: float, cy: float, angle: float, length: float, width: float) -> list[Point]:
    tip = (cx + math.cos(angle) * length, cy + math.sin(angle) * length)
    left = (cx + math.cos(angle + math.pi / 2) * width, cy + math.sin(angle + math.pi / 2) * width)
    right = (cx + math.cos(angle - math.pi / 2) * width, cy + math.sin(angle - math.pi / 2) * width)
    return [left, tip, right]


def draw_wing(draw: ScaledDraw) -> None:
    wing_shadow = (189, 196, 190)
    wing = (248, 247, 236)
    edge = (214, 219, 210)
    root = (650, 465)
    for i, angle in enumerate([2.56, 2.75, 2.94, 3.13, 3.32, 3.51]):
        length = 205 - i * 12
        width = 42 - i * 3
        cx = root[0] - i * 18
        cy = root[1] + i * 20
        draw.polygon(feather_polygon(cx + 8, cy + 7, angle, length, width), fill=wing_shadow)
        draw.polygon(feather_polygon(cx, cy, angle, length, width), fill=wing, outline=edge)

    draw.ellipse((470, 392, 705, 598), fill=wing, outline=edge, width=4)
    draw.arc((500, 413, 695, 590), 120, 245, fill=(225, 228, 218), width=5)


def draw_webbed_foot(draw: ScaledDraw, ankle: Point, toes: Sequence[Point]) -> None:
    foot = [(ankle[0] - 7, ankle[1]), *toes, (ankle[0] + 8, ankle[1] + 7)]
    draw.polygon(foot, fill=(202, 92, 55), outline=(158, 72, 49))
    for toe in toes:
        draw.line((ankle[0], ankle[1] + 2, toe[0], toe[1]), fill=(155, 70, 47), width=2)


def draw_pelican(draw: ScaledDraw) -> None:
    body = (246, 245, 232)
    body_shadow = (219, 222, 211)
    ink = (39, 47, 49)
    pouch = (238, 186, 104)
    beak = (243, 184, 73)
    leg = (226, 125, 72)

    draw.ellipse((542, 402, 800, 642), fill=body_shadow)
    draw.ellipse((530, 384, 790, 622), fill=body, outline=(210, 215, 205), width=4)
    draw_wing(draw)

    draw.line((560, 558, 666, 553), fill=(73, 60, 52), width=18)
    draw.line((580, 546, 650, 543), fill=(106, 86, 72), width=6)
    draw.ellipse((580, 520, 700, 585), fill=(235, 235, 222), outline=(207, 212, 202), width=3)
    draw.line((618, 575, 590, 690), fill=leg, width=16)
    draw.line((698, 570, 742, 642), fill=leg, width=16)
    draw.line((590, 690, 552, 746), fill=leg, width=13)
    draw.line((742, 642, 758, 650), fill=leg, width=13)
    draw_webbed_foot(draw, (552, 746), [(522, 755), (560, 766), (592, 752)])
    draw_webbed_foot(draw, (758, 650), [(725, 650), (760, 666), (793, 649)])

    neck_points = [(720, 408), (760, 315), (838, 295), (898, 338), (878, 410), (790, 432)]
    draw.line(neck_points, fill=body_shadow, width=75, joint="curve")
    draw.line([(x - 8, y - 7) for x, y in neck_points], fill=body, width=63, joint="curve")

    draw.ellipse((774, 238, 938, 382), fill=body, outline=(211, 216, 207), width=4)
    draw.pieslice((802, 170, 900, 284), 193, 353, fill=(255, 255, 248), outline=(217, 222, 214), width=3)
    draw.ellipse((873, 287, 889, 303), fill=ink)
    draw.ellipse((878, 291, 883, 296), fill=(255, 255, 255))

    upper_beak = [(912, 307), (1215, 331), (1233, 362), (914, 357)]
    lower_beak = [(905, 357), (1200, 367), (1150, 430), (938, 407)]
    draw.polygon(lower_beak, fill=pouch, outline=(192, 128, 70))
    draw.polygon(upper_beak, fill=beak, outline=(178, 119, 58))
    draw.line((948, 358, 1208, 360), fill=(147, 89, 49), width=4)
    draw.line((1213, 333, 1233, 362), fill=(103, 77, 48), width=4)
    draw.arc((943, 344, 1158, 433), 8, 168, fill=(212, 150, 82), width=4)
    draw.arc((952, 371, 1128, 439), 10, 172, fill=(183, 116, 65), width=3)
    draw.line((930, 397, 1126, 423), fill=(222, 166, 94), width=3)

    draw.ellipse((510, 560, 572, 610), fill=(230, 229, 217))
    draw.polygon([(765, 602), (820, 646), (742, 648)], fill=(226, 229, 219), outline=(205, 211, 201))


def draw_foreground(draw: ScaledDraw) -> None:
    draw.ellipse((285, 825, 1032, 900), fill=(112, 89, 67, 82))
    for x, y, color in [
        (210, 870, (230, 180, 88)),
        (260, 850, (232, 100, 91)),
        (1010, 858, (240, 210, 106)),
        (1080, 835, (228, 101, 95)),
        (1140, 874, (237, 186, 83)),
    ]:
        draw.line((x, y + 34, x + 4, y), fill=(74, 124, 83), width=4)
        draw.ellipse(ellipse_bbox(x, y, 13, 13), fill=color)
        draw.ellipse(ellipse_bbox(x + 15, y + 7, 10, 10), fill=color)


def render() -> Image.Image:
    scale = SUPERSAMPLE
    render_size = (WIDTH * scale, HEIGHT * scale)
    image = Image.new("RGBA", render_size, (255, 255, 255, 255))
    draw = ScaledDraw(ImageDraw.Draw(image, "RGBA"), scale)
    draw_background(draw)

    bicycle_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_bicycle(ScaledDraw(ImageDraw.Draw(bicycle_layer, "RGBA"), scale))
    add_shadow(image, bicycle_layer, blur=10, offset=(18, 26), opacity=80, scale=scale)

    bird_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_pelican(ScaledDraw(ImageDraw.Draw(bird_layer, "RGBA"), scale))
    add_shadow(image, bird_layer, blur=13, offset=(16, 21), opacity=54, scale=scale)

    draw_foreground(ScaledDraw(ImageDraw.Draw(image, "RGBA"), scale))
    resampling = getattr(Image, "Resampling", Image).LANCZOS
    return image.resize((WIDTH, HEIGHT), resampling).convert("RGB")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image = render()
    image.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
