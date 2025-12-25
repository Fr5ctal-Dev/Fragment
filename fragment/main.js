import { GameManager } from '/fragment/core/game-manager.js';

/**
 * Starts an application.
 * @param {string} scene - The scene file path
 * @param {string} projectPath - The project path or the desired working directory
 */
export async function setup(scene, projectPath) {
    const gameManager = new GameManager(projectPath);
    await gameManager.init();
    await gameManager.sceneManager.instantiateScene(scene);
    gameManager.run();
}
