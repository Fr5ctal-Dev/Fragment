import { Drawable } from '/fragment/nodes/drawable.js';

export class Sprite extends Drawable {
  constructor(...args) {
    super(...args);
    this.spriteTexture = null;
  }

  get image_source() {
    return this._properties['image_source'];
  }

  set image_source(source) {
    this._properties['image_source'] = source;
    this.loadTexture(this._properties['image_source']);
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
