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

    def create_pixel_grid_patch(self, array, opacity=0.0, patch_size=4):
        height, width, _ = array.shape
        patch_groups = VGroup()

        for p_i in range(0, height, patch_size):
            for p_j in range(0, width, patch_size):
                pixel_grid = VGroup()  # 각 패치별 비주얼 그룹 생성
                for i in range(p_i, p_i + patch_size):
                    for j in range(p_j, p_j + patch_size):
                        value = array[i, j]
                        color = value / 255
                        if np.sum(value) == 0:  # RGB 값이 (0, 0, 0)인 경우
                            pixel = Square(side_length=1, fill_opacity=0)
                        else:
                            pixel = Square(side_length=1, fill_opacity=1.0)
                            pixel.set_fill(
                                color=rgb_to_color(color), opacity=1.0
                            )  # 일반적인 경우 색상 설정
                        pixel.move_to(
                            ((j - p_j) - patch_size / 2) * RIGHT
                            + ((i - p_i) - patch_size / 2) * DOWN
                        )
                        pixel.set_stroke(width=self.pixel_stroke_width, opacity=opacity)
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

        prev_action_values = np.zeros((16, 16, 3))
        prev_action_values[3, 5] = [255, 0, 0]
        prev_action_values[7, 8] = [0, 255, 0]
        prev_action_values[10, 12] = [0, 0, 255]
        prev_action_map = self.create_pixel_grid_patch(
            prev_action_values, opacity=1, patch_size=1
        )

        prev_action_text = Text("Previous Action", font_size=24).next_to(
            prev_action_map, UP, buff=0.5
        )

        self.play(FadeIn(prev_action_map), FadeIn(prev_action_text), run_time=1)
        self.wait(1)
        self.play(FadeOut(prev_action_map), FadeOut(prev_action_text), run_time=1)

        create_animations = []
        fade_animations = []
        for patch in pixel_grid_patches:
            # 패치의 외곽선 생성
            outline = SurroundingRectangle(patch, color=YELLOW, buff=0)
            outline.set_stroke(width=3)  # 외곽선의 너비 설정

            # Create와 FadeOut 애니메이션을 animations 리스트에 추가
            create_animations.append(Create(outline))
            fade_animations.append(FadeOut(outline))

        # 모든 애니메이션을 한번에 실행
        self.play(AnimationGroup(*create_animations, lag_ratio=0), run_time=1)
        self.wait(0.5)  # Optional wait time between creation and fading out
        self.play(AnimationGroup(*fade_animations, lag_ratio=0), run_time=1)

        # 카메라 방향을 점진적으로 변경
        self.move_camera(
            phi=60 * DEGREES,  # 위에서 내려다보는 각도
            run_time=3,  # 카메라 이동에 걸리는 시간 (초)
        )

        # 첫 번째 패치의 x, y 위치 가져오기
        base_x, base_y, base_z = pixel_grid_patches[0].get_center()
        z_increment = 0.3

        # 가운데 패치 가져오기
        num_patches = len(pixel_grid_patches)
        animations = []
        # 첫 번째 패치를 제외한 모든 패치에 대해 이동 애니메이션 적용
        for i, patch in enumerate(pixel_grid_patches):
            # 각 패치를 첫 번째 패치의 x, y 위치로, z 위치는 순차적으로 증가시키기
            target_position = np.array([base_x, base_y, base_z + i * z_increment])
            # Define the control points for the CubicBezier curve
            start_anchor = patch.get_center()
            start_handle = start_anchor + np.array([2, 2, 0])  # First control point
            end_handle = target_position + np.array([-2, 2, 0])  # Second control point
            end_anchor = target_position  # End point of the Bezier curve

            # Create the CubicBezier curve
            bezier_path = CubicBezier(
                start_anchor, start_handle, end_handle, end_anchor
            )

            # Create an animation where the patch moves along the Bezier path
            anim = MoveAlongPath(patch, bezier_path)
            animations.append(anim)

            if i == num_patches // 2:
                self.move_camera(
                    frame_center=[base_x, base_y, target_position[2]], run_time=1
                )

        # 모든 애니메이션을 동시에 실행
        self.play(AnimationGroup(*animations, lag_ratio=0.1), run_time=2)
        self.wait(1)

        arrow_animations = []
        fade_arrows = []
        for i, patch in enumerate(pixel_grid_patches):
            start_pos = patch.get_center()
            end_pos = start_pos + np.array([2, 0, 0])
            arrow = Arrow(start=patch.get_center(), end=end_pos, color=RED)
            arrow_animations.append(GrowArrow(arrow))
            fade_arrows.append(FadeOut(arrow))

            if i == num_patches // 2:
                self.move_camera(frame_center=end_pos, run_time=1)
                center_arrow = arrow

        self.play(AnimationGroup(*arrow_animations, lag_ratio=0.1), run_time=1)

        model = Rectangle(height=3, width=2, color=BLUE).next_to(
            center_arrow, RIGHT, buff=1
        )
        model.rotate(PI / 2, axis=RIGHT)  # y축을 기준으로 90도 회전
        model_text = Text("Model", color=WHITE).scale(0.5).move_to(model.get_center())
        model_text.rotate(PI / 2, axis=RIGHT)  # Text도 같은 방향으로 회전

        self.play(Create(model), Write(model_text))

        # 패치들이 모델로 이동하는 애니메이션
        for patch, fade_arrow in zip(
            pixel_grid_patches, fade_arrows
        ):  # 패치와 화살표 애니메이션을 함께 처리
            self.play(
                patch.animate.next_to(model, LEFT, buff=0.1),  # 패치 이동
                fade_arrow,  # 화살표 사라짐
                run_time=0.1,
            )
            self.remove(patch)  # 패치 이동 후 제거

        self.wait(1)

        hidden_dim = 10
        # 변환된 출력 패치 생성
        output_patches = VGroup()
        for i in range(num_patches):
            # 각 패치는 1 * hidden_dim 차원을 갖습니다
            patch = Rectangle(height=0.2, width=hidden_dim * 0.2, color=GREEN).set_fill(
                GREEN, opacity=0.5
            )
            output_patches.add(patch)

            if i == num_patches // 2:
                center_patch = patch

        # 출력 패치를 세로로 배열하고 모델의 오른쪽에 위치시킵니다.
        output_patches.arrange(DOWN, buff=0.1).next_to(model, RIGHT * 3, buff=0.5)

        # BraceLabel 생성
        brace_top = BraceLabel(
            obj=output_patches,  # 대상 객체
            text=r"Hidden Dim",  # 텍스트 라벨
            brace_direction=UP,  # 괄호 방향
            label_constructor=Text,  # 라벨 생성자
            font_size=24,  # 폰트 크기
            buff=0.2,  # 괄호와 대상 객체 사이의 거리
        )

        brace_right = BraceLabel(
            obj=output_patches,  # 대상 객체
            text=r"Number of Patches",  # 텍스트 라벨
            brace_direction=RIGHT,  # 괄호 방향 (오른쪽)
            label_constructor=Text,  # 여기서는 Text를 사용하면 됩니다, MathTex는 수학적 표현에 더 적합
            font_size=24,  # 폰트 크기
            buff=0.2,  # 괄호와 대상 객체 사이의 거리
        )

        # output_patches와 brace를 모두 포함하는 그룹을 생성합니다.
        output_group = VGroup(output_patches, brace_top, brace_right)

        # 이제 output_group을 회전시킵니다.
        output_group.rotate(PI / 2, axis=RIGHT)  # y축을 기준으로 90도 회전

        self.move_camera(
            frame_center=center_patch.get_center(), phi=90 * DEGREES, run_time=3
        )
        # 출력 애니메이션을 output_group에 적용
        self.play(TransformFromCopy(model, output_patches))

        # 출력 패치와 brace를 화면에 추가
        self.play(Create(brace_top), Create(brace_right))

        self.wait(2)

        self.move_camera(frame_center=prev_action_map.get_center(), phi=0, run_time=3)
        self.play(FadeIn(prev_action_map), FadeIn(prev_action_text), run_time=1)

        self.play(
            *[FadeOut(obj) for obj in self.mobjects if obj != prev_action_map],
            run_time=1,
        )

        # 16 x 16 prev_action_map을 256 x 1로 flatten
        pixel_animations = []
        base_x, base_y, base_z = prev_action_map[0].get_center()
        x_increment = 0.2
        for i, patch in enumerate(prev_action_map):
            start_pos = patch.get_center()
            # 각 패치를 첫 번째 패치의 x, y 위치로, z 위치는 순차적으로 증가시키기
            target_position = np.array([base_x + i * x_increment, base_y, base_z])
            # Define the control points for the CubicBezier curve
            start_anchor = patch.get_center()
            start_handle = start_anchor + np.array([2, 2, 0])  # First control point
            end_handle = target_position + np.array([-2, 2, 0])  # Second control point
            end_anchor = target_position  # End point of the Bezier curve

            # Create the CubicBezier curve
            bezier_path = CubicBezier(
                start_anchor, start_handle, end_handle, end_anchor
            )

            # Create an animation where the patch moves along the Bezier path
            anim = MoveAlongPath(patch, bezier_path)
            pixel_animations.append(anim)

            if i == num_patches // 2:
                middle_pixel = patch

        self.play(AnimationGroup(*pixel_animations, lag_ratio=0.01), run_time=3)

        self.move_camera(
            frame_center=middle_pixel.get_center() + RIGHT * 20,
            run_time=1,
            focal_distance=10000,
        )

        self.wait(3)
