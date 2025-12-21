import { Manager } from '/fragment/core/manager.js';

export class Clock extends Manager {
  constructor(gameManager) {
    super(gameManager);
    // Use performance.now() for high-resolution time, convert to seconds
    this.previousTime = performance.now() / 1000;
    this.currentTime = performance.now() / 1000;
  }

  /**
   * Update the time of the clock using performance.now()
   */
  updateTime() {
    this.previousTime = this.currentTime;
    this.currentTime = performance.now() / 1000;
  }

  /**
   * Delta time (dt) between the current and the previous frame.
   * Delta time is the measure of the amount of time it took from
   * the previous frame to the current frame.
   * @returns {number} Delta time (dt) in seconds
   */
  get dt() {
    return this.currentTime - this.previousTime;
  }

  /**
   * Frames per second (fps) between current and the previous frame.
   * Frames per second (fps) is the number of frames that will pass in a second
   * calculated by 1/delta time (dt).
   * @returns {number} Frames per second (fps)
   */
  get fps() {
    return 1 / this.dt;
  }

  update(dt) {
    super.update(dt);
    this.updateTime();
  }
}
