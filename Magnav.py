from manim import *
import numpy as np


class MagneticMapScene(Scene):
    def construct(self):
        magnetic_map_image = ImageMobject("magnetic_map.png")
        magnetic_map_image.scale_to_fit_height(6)
        self.add(magnetic_map_image)

        MagneticMapText = Text("Magnetic Map").scale(0.5)
        MagneticMapText.next_to(magnetic_map_image, UP, buff=0.3)
        self.play(FadeIn(MagneticMapText))

        start_point = magnetic_map_image.get_corner(DL)
        control_point = magnetic_map_image.get_center() + 2 * UP + 2 * LEFT
        end_point = magnetic_map_image.get_corner(UR)
        full_path = CubicBezier(start_point, control_point, control_point, end_point)

        airplane = SVGMobject("white_airplane.svg").scale(0.3)
        airplane.move_to(start_point)
        airplane.rotate(-PI / 4)
        self.add(airplane)

        dashed_path = DashedVMobject(full_path.copy(), num_dashes=100, color=WHITE)
        self.add(dashed_path)

        original_path_legend_line = Line(ORIGIN, RIGHT * 0.5, color=WHITE)
        original_path_legend_text = Text("Original Path", font_size=24).next_to(
            original_path_legend_line, RIGHT, buff=0.1
        )

        legend_group = VGroup(original_path_legend_line, original_path_legend_text)
        legend_group.next_to(magnetic_map_image, RIGHT, buff=1)

        self.add(legend_group)

        path_tracker = ValueTracker(0)

        dashed_path.add_updater(
            lambda m: m.become(
                DashedVMobject(
                    full_path, num_dashes=100, color=WHITE
                ).pointwise_become_partial(full_path, 0, path_tracker.get_value())
            )
        )

        airplane.previous_angle = 0

        def update_airplane(mob, dt):
            alpha = path_tracker.get_value()
            new_point = full_path.point_from_proportion(alpha)
            mob.move_to(new_point)
            if alpha > 0:
                previous_point = full_path.point_from_proportion(max(0, alpha - 0.01))
                direction = new_point - previous_point
                new_angle = np.arctan2(direction[1], direction[0])
                angle_change = new_angle - mob.previous_angle
                mob.rotate(angle_change)
                mob.previous_angle = new_angle

        airplane.add_updater(update_airplane)

        self.play(path_tracker.animate.set_value(1), run_time=4, rate_func=linear)
        airplane.remove_updater(update_airplane)
        dashed_path.remove_updater(lambda m: m)
        self.wait()


class ThreeDSurfacePlot(ThreeDScene):
    def construct(self):
        resolution_fa = 24
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)

        gaussians = [
            (np.array([0, 0]), np.array([[1, 0], [0, 1]])),
            (np.array([2, 2]), np.array([[0.5, 0.3], [0.3, 0.5]])),
            (np.array([-2, -1]), np.array([[0.5, 0], [0, 0.5]])),
            (np.array([1, -3]), np.array([[0.3, -0.1], [-0.1, 0.3]])),
            (np.array([-3, 2]), np.array([[0.4, 0.3], [0.3, 0.4]])),
            # 추가된 가우시안 분포들
            (np.array([3, -2]), np.array([[0.2, 0], [0, 0.2]])),
            (np.array([-2, 3]), np.array([[0.3, 0.2], [0.2, 0.3]])),
            (np.array([0, 3]), np.array([[0.4, -0.1], [-0.1, 0.4]])),
            (np.array([-3, -3]), np.array([[0.5, 0.1], [0.1, 0.5]])),
            (np.array([3, 3]), np.array([[0.3, 0], [0, 0.3]])),
            (np.array([-1, 4]), np.array([[0.4, 0.2], [0.2, 0.4]])),
            (np.array([4, -1]), np.array([[0.6, -0.2], [-0.2, 0.6]])),
            (np.array([-4, -4]), np.array([[0.3, 0.1], [0.1, 0.3]])),
            (np.array([4, 4]), np.array([[0.5, -0.1], [-0.1, 0.5]])),
        ]

        axes = ThreeDAxes()
        self.add(axes)

        for mean, cov in gaussians:
            gauss_plane = (
                Surface(
                    lambda u, v: self.param_gauss(u, v, mean, cov),
                    resolution=(resolution_fa, resolution_fa),
                    v_range=[-2, +2],
                    u_range=[-2, +2],
                )
                .scale(2, about_point=ORIGIN)
                .set_style(fill_opacity=1, stroke_color=GREEN)
                .set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.5)
            )
            self.add(gauss_plane)

    def param_gauss(self, u, v, mean, cov):
        x, y = u, v
        pos = np.array([x, y])
        diff = pos - mean
        inv_cov = np.linalg.inv(cov)
        z = np.exp(-0.5 * (diff.T @ inv_cov @ diff))
        return np.array([x, y, z])
