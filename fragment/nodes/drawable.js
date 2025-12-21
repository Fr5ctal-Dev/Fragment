import { Node2D } from '/fragment/nodes/node2d.js';
import { Canvas } from '/fragment/nodes/canvas.js';

export class Drawable extends Node2D {
  /**
   * Drawable locates nearest Canvas ancestor (if none found, it uses the global canvas)
   * and renders itself there.
   */
  constructor(...args) {
    super(...args);
    this.pixiSprite = new PIXI.Sprite();
    this.pixiSprite.anchor.set(0.5, 0.5); // Center anchor
  }

  fullInit() {
    this.targetCanvas = this.find_ancestor_of_type(Canvas) ||
                        this.gameManager.windowManager.globalCanvas;
    this.targetCanvas.registerDrawable(this);
  }

  update(dt) {
    super.update(dt);
    this.updatePixiTransform();
  }

  updatePixiTransform() {
    if (!this.pixiSprite) return;
    this.pixiSprite.position.set(this.world_position.x, this.world_position.y);
    this.pixiSprite.rotation = this.world_rotation * Math.PI / 180;
    this.pixiSprite.scale.set(this.world_scale.x, this.world_scale.y);
  }

  destroy_self() {
    this.targetCanvas.unregisterDrawable(this);
    super.destroy_self();
  }

  get draw_priority() {
    return this._properties['draw_priority'] || 0;
  }

  set draw_priority(priority) {
    this._properties['draw_priority'] = parseInt(priority);
    if (this.pixiSprite) {
      this.pixiSprite.zIndex = this._properties['draw_priority'];
    }
  }
}
