from .node import Node


class Timeline(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeline = self._properties['timeline'][0]
        self.is_playing = [False, None, None]
        self.prev_time = 0
        taskMgr.add(self._update_timeline, 'update_timeline')

    def _update_timeline(self, task):
        if self.is_playing[0]:
            self.on_next_frame(self.timeline[self.is_playing[1]])
            self.is_playing[1] += int(task.time * 1000) - self.prev_time
            self.prev_time = int(task.time * 1000)
            if self.is_playing[1] >= len(self.timeline):
                if self.is_playing[2] > 1 or self.is_playing[2] == -1:
                    self.is_playing = [True, 0, max(self.is_playing[2] - 1, -1)]
                else:
                    self.is_playing = [False, None, None]
        return task.cont

    def on_next_frame(self, value):
        pass

    def play(self):
        self.loop(1)

    def loop(self, times=-1):
        self.is_playing = [True, 0, times]

    def stop(self):
        self.is_playing = [False, None, None]
