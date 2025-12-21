import { GameElement } from '/fragment/core/element.js';

export class Manager extends GameElement {
  constructor(gameManager) {
    super(gameManager);
    this.running = true;
  }

  /**
   * Update the manager.
   * @param {number} dt - The delta time between the current and previous frame
   */
  update(dt) {
    // Override in subclasses
  }

  /**
   * Destroy the manager.
   */
  destroy() {
    this.running = false;
  }
}
