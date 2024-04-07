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

    def create_and_fade_outlines(self, pixel_grid_patches):
        create_animations = []
        fade_animations = []
        for patch in pixel_grid_patches:
            outline = SurroundingRectangle(patch, color=YELLOW, buff=0)
            outline.set_stroke(width=3)
            create_animations.append(Create(outline))
            fade_animations.append(FadeOut(outline))
        self.play(AnimationGroup(*create_animations, lag_ratio=0), run_time=2)
        self.wait(0.5)
        self.play(AnimationGroup(*fade_animations, lag_ratio=0), run_time=2)

    def move_camera_to_patches(self, pixel_grid_patches):
        base_x, base_y, base_z = pixel_grid_patches[0].get_center()
        z_increment = 0.3
        center_patch = pixel_grid_patches[len(pixel_grid_patches) // 2]
        target_position = np.array([base_x, base_y, base_z + len(pixel_grid_patches) // 2 * z_increment])
        self.move_camera(frame_center=[base_x, base_y, target_position[2]], run_time=1)

    def move_patches_along_bezier_path(self, pixel_grid_patches):
        animations = []
        for i, patch in enumerate(pixel_grid_patches):
            base_x, base_y, base_z = patch.get_center()
            z_increment = 0.3
            target_position = np.array([base_x, base_y, base_z + i * z_increment])
            bezier_path = self.create_bezier_path(patch.get_center(), target_position)
            anim = MoveAlongPath(patch, bezier_path)
            animations.append(anim)
        self.play(AnimationGroup(*animations, lag_ratio=0.1), run_time=2)

    def create_bezier_path(self, start_position, end_position):
        start_handle = start_position + np.array([2, 2, 0])
        end_handle = end_position + np.array([-2, 2, 0])
        bezier_path = CubicBezier(start_position, start_handle, end_handle, end_position)
        return bezier_path

    def construct(self):
        pixel_values = self.get_pixel_value_array()
        pixel_grid_patches = self.create_pixel_grid_patch(pixel_values)
        for patch in pixel_grid_patches:
            self.add(patch)
        self.wait(3)
        
        self.create_and_fade_outlines(pixel_grid_patches)
        self.move_camera_to_patches(pixel_grid_patches)
        self.move_patches_along_bezier_path(pixel_grid_patches)
        self.wait(1)