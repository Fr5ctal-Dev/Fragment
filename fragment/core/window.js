import { Manager } from '/fragment/core/manager.js';
import { Vector2 } from '/fragment/types/vector.js';
import { Canvas } from '/fragment/nodes/canvas.js';

export class WindowManager extends Manager {
  constructor(gameManager, windowTitle = 'Made with Fragment') {
    super(gameManager);

    this.app = new PIXI.Application();
    this.windowTitle = windowTitle;
    this.canvases = [];
    this.globalCanvas = null;
  }

  async init() {
    await this.app.init({
      resizeTo: window,
      backgroundColor: 0x000000
    });
    this.app.canvas.style.position = 'absolute';

    document.body.appendChild(this.app.canvas);
  }

  get windowSize() {
    return new Vector2(this.app.screen.width, this.app.screen.height);
  }

  set windowSize(size) {
    this.app.renderer.resize(size.x, size.y);
  }

  setupCanvas() {
    this.globalCanvas = new Canvas(this.gameManager, {}, null, null, null, true); // isGlobalCanvas = true
  }

  registerCanvas(canvas) {
    this.canvases.push(canvas);
  }
}
