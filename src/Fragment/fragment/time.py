class Clock:
    @property
    def dt(self):
        return globalClock.dt

    @property
    def total_frame_count(self):
        return globalClock.frame_count

    @property
    def fps(self):
        return globalClock.get_average_frame_rate()


clock = Clock()
