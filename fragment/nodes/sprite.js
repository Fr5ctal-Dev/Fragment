import * as PIXI from 'pixi.js';

import { Drawable } from '/fragment/nodes/drawable.js';

export class Sprite extends Drawable {
    constructor(...args) {
        super(...args);
        this.spriteTexture = null;
    }

    get imageSource() {
        return this._properties['imageSource'];
    }

    set imageSource(source) {
        this._properties['imageSource'] = source;
        this.loadTexture(this._properties['imageSource']);
    }

    destroySelf() {
        if (this.spriteTexture) {
            this.spriteTexture.destroy();
            this.spriteTexture = null;
        }
        super.destroySelf();
    }

    /**
     * Load a texture from a source path asynchronously.
     * @param {string} source - The path to the image file.
     */
    async loadTexture(source) {
        try {
            if (this.spriteTexture) {
                this.spriteTexture.destroy();
                this.spriteTexture = null;
            }
            this.spriteTexture = await PIXI.Assets.load(source);
            if (!this.pixiSprite.destroyed) {
                this.pixiSprite.texture = this.spriteTexture;
            }
            else {
                this.spriteTexture.destroy();
            }
        } catch (error) {
            throw new Error(`Failed to load texture: ${source} ` + error);
        }
    }
}
