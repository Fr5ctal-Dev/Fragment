from moderngl import Buffer, Program, Texture
import numpy as np


class Shader:

    MAX_TEXTURE_UNITS = 16

    def __init__(self, program: Program):
        self._program: Program = program

        self._fresh_ubo_binding: int = 1
        self._ubo_dict: dict[str, Buffer] = {}

        self._fresh_location: int = 1
        self._sampler2D_locations: dict[str, tuple[Texture, int]] = {}

    @property
    def program(self) -> Program:
        return self._program

    def __getitem__(self, key):
        if key in self._ubo_dict:
            return self._ubo_dict[key]
        elif key in self._sampler2D_locations:
            texture, _ = self._sampler2D_locations[key]
            return texture
        else:
            return self._program[key]

    def __setitem__(self, key, value):
        if key in self._ubo_dict:
            assert isinstance(
                value, bytes), 'Make sure to convert your data into bytes before writing it to the uniform buffer.'
            self._ubo_dict[key].write(value)
        elif isinstance(value, Texture):
            if self._fresh_location >= self.MAX_TEXTURE_UNITS:
                raise RuntimeError(f'Exceeded maximum number of texture units ({self.MAX_TEXTURE_UNITS}). '
                                   'Clear sampler2D uniforms between renders or reduce texture count.')
            self._program[key].value = self._fresh_location
            self._sampler2D_locations[key] = (value, self._fresh_location)
            self._fresh_location += 1
        else:
            self._program[key] = value

    def sample_ubo_binding(self) -> int:
        binding = self._fresh_ubo_binding
        self._fresh_ubo_binding += 1
        return binding

    def add_ubo(self, ubo: Buffer, name: str):
        self._ubo_dict[name] = ubo

    def bind_sampler2D_uniforms(self):
        for tex, location in self._sampler2D_locations.values():
            tex.use(location)

    def clear_sampler2D_uniforms(self):
        self._sampler2D_locations.clear()
        self._fresh_location = 1

    def release(self):
        for ubo in self._ubo_dict.values():
            ubo.release()
        self._program.release()
