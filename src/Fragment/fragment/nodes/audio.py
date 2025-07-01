from .node import Node


class Audio(Node):
    def _get_node(self):
        node = super()._get_node()
        self.audio = loader.load_sfx(self._properties['sound'])
        return node

    def play(self):
        self.loop(1)

    def loop(self, loop_count=0):
        self.audio.set_loop_count(loop_count)
        self.audio.play()

    def stop(self):
        self.audio.stop()

    @property
    def is_playing(self):
        return self.audio.status() == self.audio.PLAYING

    @property
    def speed(self):
        return self._properties['speed']

    @speed.setter
    def speed(self, speed):
        self._properties['speed'] = speed
        self.audio.set_play_rate(speed)

    @property
    def volume(self):
        return self._properties['volume']

    @volume.setter
    def volume(self, volume):
        self._properties['volume'] = volume
        self.audio.set_volume(volume)
