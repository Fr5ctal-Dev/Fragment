from .core.game_manager import GameManager

def setup(scene, project_path):
    game_manager = GameManager(project_path)
    game_manager.scene_manager.instantiate_scene(scene)
    game_manager.run()
