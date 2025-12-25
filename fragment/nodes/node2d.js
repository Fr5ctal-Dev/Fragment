import { Node } from '/fragment/nodes/node.js';
import { Vector2 } from '/fragment/types/vector.js';

export class Node2D extends Node {
    get position() {
        return this._properties['position'];
    }

    set position(position) {
        this._properties['position'] = Vector2.toVector2(position);
    }

    /**
     * The global position of node.
     */
    get worldPosition() {
        if (!this.parent || !this.parent.worldPosition) {
            return this.position;
        }

        const worldOffset = this.position.rotate(this.parent.worldRotation);
        return this.parent.worldPosition.add(worldOffset);
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
    get worldRotation() {
        if (!this.parent || this.parent.worldRotation === undefined) {
            return this.rotation;
        }

        return this.rotation + this.parent.worldRotation;
    }

    get scale() {
        return this._properties['scale'];
    }

    set scale(scale) {
        this._properties['scale'] = Vector2.toVector2(scale);
    }

    /**
     * The global scale of node.
     */
    get worldScale() {
        if (!this.parent || !this.parent.worldScale) {
            return this.scale;
        }

        return new Vector2(
            this.parent.worldScale.x * this.scale.x,
            this.parent.worldScale.y * this.scale.y
        );
    }
}
