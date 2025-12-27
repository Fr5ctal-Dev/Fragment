import { GameElement } from '/fragment/core/element.js';

export class Node extends GameElement {
    constructor(gameManager, properties, uuid = null, parent = null, scene = null) {
        super(gameManager);
        this.uuid = uuid;
        this.name = null;
        this.parent = null;
        this.scene = scene;
        this.children = [];
        this._properties = properties;
        this.destroyed = false;
        this.setParent(parent);
    }

    fullInit() {
        // Initialization called after all nodes are created
    }

    get properties() {
        return this._properties;
    }

    setParent(node) {
        if (this.parent) {
            const index = this.parent.children.indexOf(this);
            this.parent.children.splice(index, 1);
        }
        this.parent = node;
        if (node) {
            node.children.push(this);
        }
    }

    /**
     * Sets the properties in a dict onto the node.
     * @param {Object} properties - Properties to set
     */
    initializeProperties(properties) {
        for (const key in properties) {
            this[key] = properties[key];
        }
    }

    /**
     * Recursively performs an action on node and its children.
     * @param {Function} action - Action to perform on each node
     */
    traverse(action) {
        action(this);
        for (const child of [...this.children]) {
            child.traverse(action);
        }
    }

    /**
     * Finds nearest ancestor with a type satisfying nodeType.
     * @param {Function} nodeType - Node class/constructor to match
     */
    findAncestorOfType(nodeType) {
        if (this.parent === null) {
            return null;
        }

        let currentNode = this.parent;
        while (true) {
            if (currentNode instanceof nodeType) {
                return currentNode;
            }

            if (currentNode.parent === null) {
                return null;
            }
            currentNode = currentNode.parent;
        }
    }

    update(dt) {
        this.onUpdate();
    }

    /**
     * Destroys node and children.
     */
    destroy() {
        this.traverse(node => node.destroySelf());
    }

    /**
     * Destroys node without destroying children (or detaching them).
     * Avoid using this method. Please use destroy() instead as it is safer.
     */
    destroySelf() {
        this.onDestroy();
        this.setParent(null);
        if (this.scene !== null) {
            this.scene.unregisterNode(this);
        }
        this.destroyed = true;
    }

    isAncestor(node) {
        while (true) {
            if (node === this) {
                return true;
            }
            if (!node.parent) {
                return false;
            }
            node = node.parent;
        }
    }

    /**
     * Get the root node of the node tree the node is in.
     */
    get topNode() {
        let currentNode = this;
        while (true) {
            if (!currentNode.parent) {
                return currentNode;
            }
            currentNode = currentNode.parent;
        }
    }

    // Lifecycle hooks - override in subclasses
    onStart() { }
    onUpdate() { }
    onDestroy() { }
}
