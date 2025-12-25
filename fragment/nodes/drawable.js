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
        this.targetCanvas = this.findAncestorOfType(Canvas) ||
            this.gameManager.windowManager.globalCanvas;
        this.targetCanvas.registerDrawable(this);
    }

    update(dt) {
        super.update(dt);
        this.updatePixiTransform();
    }

    updatePixiTransform() {
        if (!this.pixiSprite) return;
        this.pixiSprite.position.set(this.worldPosition.x, this.worldPosition.y);
        this.pixiSprite.rotation = this.worldRotation * Math.PI / 180;
        this.pixiSprite.scale.set(this.worldScale.x, this.worldScale.y);
    }

    destroySelf() {
        this.targetCanvas.unregisterDrawable(this);
        super.destroySelf();
    }

    get drawPriority() {
        return this._properties['drawPriority'] || 0;
    }

    set drawPriority(priority) {
        this._properties['drawPriority'] = parseInt(priority);
        if (this.pixiSprite) {
            this.pixiSprite.zIndex = this._properties['drawPriority'];
        }
    }
}
