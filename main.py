# Application starting point

from library import launch_library
import os

os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-frame-rate-limit --disable-gpu-vsync'

if __name__ == '__main__':
    launch_library()
