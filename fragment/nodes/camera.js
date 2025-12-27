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
        this.pixiContainer.position.set(-this.worldPosition.x, -this.worldPosition.y);
        this.pixiContainer.rotation = -this.worldRotation * Math.PI / 180;
        this.pixiContainer.scale.set(this.zoom, this.zoom);
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
            this.targetCanvas.unregisterActiveCamera();
        }
        this.targetCanvas = target;
        this.targetCanvas.registerCamera(this);
    }

    destroySelf() {
        if (!this.targetCanvas.destroyed && this.targetCanvas.activeCamera === this) {
            this.targetCanvas.unregisterActiveCamera();
        }
        this.pixiContainer.destroy();
        super.destroySelf();
    }

    get viewSize() {
        /**
         * The view size of the camera, calculated by dividing its target canvas size with the zoom.
         */
        return this.targetCanvas.size.div(this.zoom);
    }

    get zoom() {
        return this._properties['zoom'];
    }

    set zoom(zoom) {
        this._properties['zoom'] = parseFloat(zoom);
    }
}
