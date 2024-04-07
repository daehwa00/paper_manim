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
