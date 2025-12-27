import { Node } from '/fragment/nodes/node.js';

export class Canvas extends Node {
    /**
     * Canvas will "render" all drawable descendants captured by its active camera.
     */
    constructor(gameManager, properties, uuid = null, parent = null, scene = null, isGlobalCanvas = false) {
        super(gameManager, properties, uuid, parent, scene);
        this.activeCamera = null;
        this.registeredNodes = [];

        this.isGlobalCanvas = isGlobalCanvas;

        if (!this.isGlobalCanvas) {
            this.gameManager.windowManager.registerCanvas(this);
        }
    }

    get size() {
        return this.gameManager.windowManager.windowSize;
    }

    registerCamera(camera) {
        if (this.activeCamera === camera) {
            throw new Error('This camera is already registered as the active camera on this canvas.');
        }
        if (this.activeCamera !== null) {
            this.unregisterActiveCamera();
        }
        this.activeCamera = camera;
        this.gameManager.windowManager.app.stage.addChild(camera.pixiContainer);
        // Add previously unadded children
        this.registeredNodes.forEach(node => this.activeCamera.pixiContainer.addChild(node.pixiSprite));
    }

    unregisterActiveCamera() {
        if (this.activeCamera === null) {
            throw new Error('No active camera to unregister from this canvas.');
        }
        this.activeCamera.pixiContainer.removeChildren();
        this.gameManager.windowManager.app.stage.removeChild(this.activeCamera.pixiContainer);
        this.activeCamera = null;
    }

    registerDrawable(drawable) {
        if (this.registeredNodes.includes(drawable)) {
            throw new Error('Drawable already registered on this canvas.');
        }
        this.registeredNodes.push(drawable);
        if (this.activeCamera) {
            this.activeCamera.pixiContainer.addChild(drawable.pixiSprite);
        }
    }

    unregisterDrawable(drawable) {
        const index = this.registeredNodes.indexOf(drawable);
        if (index === -1) {
            throw new Error('Drawable not registered on this canvas.');
        }
        this.registeredNodes.splice(index, 1);
        if (this.activeCamera) {
            this.activeCamera.pixiContainer.removeChild(drawable.pixiSprite);
        }
    }

    destroySelf() {
        if (!this.isGlobalCanvas) {
            this.gameManager.windowManager.unregisterCanvas(this);
        }
        if (this.activeCamera !== null) {
            this.unregisterActiveCamera();
        }
        this.registeredNodes = [];
        super.destroySelf();
    }
}
