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

        # 실선 original path를 추가합니다.
        original_path = full_path.copy().set_color(WHITE)
        self.add(original_path)

        # Original Path 텍스트를 추가합니다.
        original_path_text = Text("Original Path", font_size=24).set_color(WHITE)
        original_path_text.next_to(dashed_path, RIGHT, buff=0.5)
        self.add(original_path_text)

        # path 시작점 근처에 작은 원을 추가하여 강조합니다.
        start_circle = Circle(radius=0.1, color=WHITE).move_to(start_point)
        self.add(start_circle)

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
