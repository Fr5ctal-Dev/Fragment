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
        super.fullInit();
        this.targetCanvas = null;
        this.updateTargetCanvas();
    }

    update(dt) {
        super.update(dt);
        this.updatePixiTransform();
    }

    updatePixiTransform() {
        if (this.destroyed) return;
        this.pixiSprite.position.set(this.worldPosition.x, this.worldPosition.y);
        this.pixiSprite.rotation = this.worldRotation * Math.PI / 180;
        this.pixiSprite.scale.set(this.worldScale.x, this.worldScale.y);
    }

    updateTargetCanvas() {
        let target = this.findAncestorOfType(Canvas)
        if (target === null || target.destroyed) {
            target = this.gameManager.windowManager.globalCanvas;
        }
        if (this.targetCanvas === target) {
            return;
        }
        if (this.targetCanvas !== null && !this.targetCanvas.destroyed) {
            this.targetCanvas.unregisterDrawable(this);
        }
        this.targetCanvas = target;
        this.targetCanvas.registerDrawable(this);
    }

    destroySelf() {
        if (!this.targetCanvas.destroyed) {
            this.targetCanvas.unregisterDrawable(this);
        }
        this.pixiSprite.destroy({ texture: true });
        super.destroySelf();
    }

    get drawPriority() {
        return this._properties['drawPriority'];
    }

    set drawPriority(priority) {
        this._properties['drawPriority'] = parseInt(priority);
        this.pixiSprite.zIndex = this._properties['drawPriority'];
    }
}
