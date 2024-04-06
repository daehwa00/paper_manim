from manim import *
import numpy as np
from PIL import Image


class ImageScene(ThreeDScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_path = "PixelArtCat.png"  # 이미지 경로 설정
        self.image_height = 3  # 매닉에서의 이미지 높이 설정
        self.pixel_stroke_width = 1  # 픽셀 테두리의 너비
        self.pixel_stroke_opacity = 0.0  # 픽셀 테두리의 불투명도
        self.grayscale = False  # 회색조 변환 여부

    def get_pixel_value_array(self):
        # 이미지 파일을 열고, RGB 값만 포함하는 numpy 배열로 변환
        image = Image.open(self.image_path)
        return np.array(image)[:, :, :3]

    def create_pixel_grid_patch(self, array):
        patch_size = 4
        height, width, _ = array.shape
        num_patches = height // patch_size * width // patch_size
        patch_groups = VGroup()

        for p_i in range(0, height, patch_size):
            for p_j in range(0, width, patch_size):
                pixel_grid = VGroup()  # 각 패치별 비주얼 그룹 생성
                for i in range(p_i, p_i + patch_size):
                    for j in range(p_j, p_j + patch_size):
                        pixel = Square(side_length=1, fill_opacity=1.0)
                        value = array[i, j]
                        color = value / 255
                        pixel.set_fill(color=rgb_to_color(color))
                        pixel.move_to(
                            ((j - p_j) - patch_size / 2) * RIGHT
                            + ((i - p_i) - patch_size / 2) * DOWN
                        )
                        pixel.set_stroke(width=self.pixel_stroke_width)
                        pixel_grid.add(pixel)
                pixel_grid.move_to(
                    ((p_j + patch_size / 2) - width / 2) * RIGHT
                    + ((p_i + patch_size / 2) - height / 2) * DOWN
                )
                patch_groups.add(pixel_grid)
        patch_groups.scale_to_fit_height(self.image_height)
        return patch_groups

    def construct(self):
        pixel_values = self.get_pixel_value_array()
        pixel_grid_patches = self.create_pixel_grid_patch(pixel_values)
        for patch in pixel_grid_patches:
            self.add(patch)
        self.wait(3)  # 애니메이션이 실행되는 시간
        # 카메라 방향을 점진적으로 변경
        self.move_camera(
            phi=60 * DEGREES,  # 위에서 내려다보는 각도
            run_time=3,  # 카메라 이동에 걸리는 시간 (초)
        )

        # 첫 번째 패치의 x, y 위치 가져오기
        base_x, base_y, _ = pixel_grid_patches[0].get_center()

        # 패치들을 차례대로 나타나게 하고, z축으로 쌓아 올림
        z_increment = 0.3  # z축 높이 증가량
        for i, patch in enumerate(pixel_grid_patches):
            # 모든 패치를 첫 번째 패치의 x, y 위치로 설정
            x, y, _ = patch.get_center()
            patch.move_to(np.array([base_x, base_y, i * z_increment]))
            self.add(patch)
            self.wait(0.2)

        self.wait(3)  # 애니메이션이 실행되는 시간