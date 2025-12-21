import { Node2D } from '/fragment/nodes/node2d.js';
import { Canvas } from '/fragment/nodes/canvas.js';

export class Camera extends Node2D {
  /**
   * The camera node detects the nearest canvas (if none found, it uses the global canvas)
   * and renders onto that canvas. All the drawable descendants of that canvas will be
   * rendered by the camera.
   */
  constructor(...args) {
    super(...args);
    // Camera uses top-left anchor (0, 0), but rotation is still (0.5, 0.5)
    this.pixiContainer = new PIXI.Container({
      isRenderGroup: true,
    });
    this.pixiContainer.sortableChildren = true;
  }

  fullInit() {
    this.targetCanvas = this.find_ancestor_of_type(Canvas) ||
                        this.gameManager.windowManager.globalCanvas;
    this.targetCanvas.registerCamera(this);
  }

  update(dt) {
    super.update(dt);
    this.updatePixiTransform();
  }

  updatePixiTransform() {
    if (!this.pixiContainer) return;
    this.pixiContainer.position.set(-this.world_position.x, -this.world_position.y);
    this.pixiContainer.rotation = -this.world_rotation * Math.PI / 180;
    this.pixiContainer.scale.set(this.zoom, this.zoom);
  }

  get view_size() {
    /**
     * The view size of the camera, calculated by dividing its target canvas size with the zoom.
     */
    return this.targetCanvas.size.div(this.zoom);
  }

  get zoom() {
    return this._properties['zoom'] || 1.0;
  }

  set zoom(zoom) {
    this._properties['zoom'] = parseFloat(zoom);
  }
}
