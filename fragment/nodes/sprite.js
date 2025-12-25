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

    /**
     * Load a texture from a source path asynchronously.
     * @param {string} source - The path to the image file.
     */
    async loadTexture(source) {
        try {
            this.spriteTexture = await PIXI.Assets.load(source);
            this.pixiSprite.texture = this.spriteTexture;
        } catch (error) {
            console.error(`Failed to load texture: ${source}`, error);
        }
    }
}
