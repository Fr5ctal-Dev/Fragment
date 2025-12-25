import { Node } from '/fragment/nodes/node.js';

export class Canvas extends Node {
    /**
     * Canvas will render all drawable descendants captured by its cameras.
     */
    constructor(gameManager, properties, uuid = null, parent = null, scene = null, isGlobalCanvas = false) {
        super(gameManager, properties, uuid, parent, scene);
        this.activeCamera = null;
        this.registeredNodes = [];

        if (!isGlobalCanvas) {
            this.gameManager.windowManager.registerCanvas(this);
        }
    }

    get size() {
        return this.gameManager.windowManager.windowSize;
    }

    registerCamera(camera) {
        this.activeCamera = camera;
        this.gameManager.windowManager.app.stage.addChild(camera.pixiContainer);
        // Add previously unadded children
        this.registeredNodes.forEach(node => this.activeCamera.pixiContainer.addChild(node.pixiSprite));
    }

    unregisterCamera(camera) {
        if (this.activeCamera === camera) {
            this.activeCamera = null;
        }
    }

    registerDrawable(drawable) {
        this.registeredNodes.push(drawable);
        if (this.activeCamera) {
            this.activeCamera.pixiContainer.addChild(drawable.pixiSprite);
        }
    }

    unregisterDrawable(drawable) {
        this.registeredNodes.splice(this.registeredNodes.indexOf(drawable), 1);
        if (this.activeCamera) {
            this.activeCamera.pixiContainer.removeChild(drawable.pixiSprite);
        }
    }
}
