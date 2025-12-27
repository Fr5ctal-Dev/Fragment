import { Manager } from '/fragment/core/manager.js';
import { WindowManager } from '/fragment/core/window.js';
import { Clock } from '/fragment/core/clock.js';
import { SceneManager } from '/fragment/core/scene-manager.js';

export class GameManager extends Manager {
    /**
     * The GameManager serves as the top-level manager, supervising all
     * other managers within the application. It is responsible for overseeing
     * core components such as task scheduling, window management, scene handling,
     * and other high-level systems.
     */
    constructor(projectPath) {
        super(null);
        this.gameManager = this;
        this.projectPath = projectPath;
        this.clock = new Clock(this);
        this.windowManager = new WindowManager(this);
        this.sceneManager = new SceneManager(this);

        this.ticker = new PIXI.Ticker();
        this.ticker.add((ticker) => {
            this.update(this.clock.dt);
        });
        this.ticker.maxFPS = 0;
        this.ticker.minFPS = 60;
    }

    async init() {
        await this.windowManager.init();
    }

    update(dt) {
        super.update(dt);
        this.clock.update(dt);
        this.sceneManager.update(dt);
        this.windowManager.update(dt);
    }

    destroy() {
        super.destroy();
        this.ticker.stop();
        this.ticker.destroy();
        this.clock.destroy();
        this.sceneManager.destroy();
        this.windowManager.destroy();
    }

    run() {
        this.ticker.start();
    }
}
