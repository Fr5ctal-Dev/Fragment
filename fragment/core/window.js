import * as PIXI from 'pixi.js';

import { Manager } from '/fragment/core/manager.js';
import { Vector2 } from '/fragment/types/vector.js';
import { Canvas } from '/fragment/nodes/canvas.js';

export class WindowManager extends Manager {
    constructor(gameManager, windowTitle = 'Made with Fragment') {
        super(gameManager);

        this.app = new PIXI.Application();
        this.windowTitle = windowTitle;
        this.canvases = [];
        this.globalCanvas = new Canvas(this.gameManager, {}, null, null, null, true); // isGlobalCanvas = true;
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

    registerCanvas(canvas) {
        if (this.canvases.includes(canvas)) {
            throw new Error('Canvas is already registered to the WindowManager.');
        }
        this.canvases.push(canvas);
    }

    unregisterCanvas(canvas) {
        const index = this.canvases.indexOf(canvas);
        if (index === -1) {
            throw new Error('Canvas is not registered to the WindowManager.');
        }
        this.canvases.splice(index, 1);
    }

    destroy() {
        super.destroy();
        this.globalCanvas.destroy();
        this.app.destroy(true, true);
    }
}
