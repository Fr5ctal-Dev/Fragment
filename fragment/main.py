from .core.game_manager import GameManager

def setup(scene: str, project_path: str) -> None:
    """Starts an application.

    Args:
        scene (str): The scene file path.
        project_path (str): The project path or the desired working directory.
    """
    game_manager = GameManager(project_path)
    game_manager.scene_manager.instantiate_scene(scene)
    game_manager.run()
