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
        base_x, base_y, base_z = pixel_grid_patches[0].get_center()
        z_increment = 0.3

        # 가운데 패치 가져오기
        center_patch = pixel_grid_patches[len(pixel_grid_patches) // 2]

        animations = []
        # 첫 번째 패치를 제외한 모든 패치에 대해 이동 애니메이션 적용
        for i, patch in enumerate(pixel_grid_patches):
            # 각 패치를 첫 번째 패치의 x, y 위치로, z 위치는 순차적으로 증가시키기
            target_position = np.array([base_x, base_y, base_z + i * 0.5])
            patch.generate_target()  # 이동할 목표 생성
            patch.target.move_to(target_position)

            # 첫 번째 패치를 제외하고 이동 애니메이션을 animations 리스트에 추가
            if i != 0:
                animations.append(MoveToTarget(patch))
                

        # 모든 애니메이션을 동시에 실행
        self.play(AnimationGroup(*animations, lag_ratio=0.1), run_time=2)
        self.wait(1)


        self.wait(3)  # 애니메이션이 실행되는 시간