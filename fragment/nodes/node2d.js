import { Node } from '/fragment/nodes/node.js';
import { Vector2 } from '/fragment/types/vector.js';

export class Node2D extends Node {
  get position() {
    return this._properties['position'];
  }

  set position(position) {
    this._properties['position'] = new Vector2(position);
  }

  /**
   * The global position of node.
   */
  get world_position() {
    if (!this.parent || !this.parent.world_position) {
      return this.position;
    }

    const worldOffset = this.position.rotate(this.parent.world_rotation);
    return this.parent.world_position.add(worldOffset);
  }

  get rotation() {
    return this._properties['rotation'];
  }

  set rotation(rotation) {
    this._properties['rotation'] = parseFloat(rotation);
  }

  /**
   * The global rotation of node.
   */
  get world_rotation() {
    if (!this.parent || this.parent.world_rotation === undefined) {
      return this.rotation;
    }

    return this.rotation + this.parent.world_rotation;
  }

  get scale() {
    return this._properties['scale'];
  }

  set scale(scale) {
    this._properties['scale'] = new Vector2(scale);
  }

  /**
   * The global scale of node.
   */
  get world_scale() {
    if (!this.parent || !this.parent.world_scale) {
      return this.scale;
    }

    return new Vector2(
      this.parent.world_scale.x * this.scale.x,
      this.parent.world_scale.y * this.scale.y
    );
  }
}
