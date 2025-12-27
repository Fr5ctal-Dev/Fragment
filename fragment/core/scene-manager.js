import { Manager } from '/fragment/core/manager.js';
import { NODES } from '/fragment/nodes/index.js';

const nameRefResponse = await fetch('/fragment/nodes/name_ref.json');
const nameRefContent = await nameRefResponse.json();

const PROPERTY_NAME_REFERENCE = {};
for (const category of Object.values(nameRefContent)) {
    Object.assign(PROPERTY_NAME_REFERENCE, category);
}

export class Scene extends Manager {
    /**
     * The manager responsible for scene and node instantiation, modification, management and deletion.
     * The scene manager takes in a scene file and instantiates nodes accordingly.
     */
    constructor(gameManager, scene) {
        super(gameManager);
        this.projectPath = gameManager.projectPath;
        this.scene = scene;
        this.rootNode = null;
        this.nodeStorage = []; // So you don't need to DFS the node tree every frame
    }

    async init() {
        /**
         * Fully initialize the scene.
         * It creates, initializes and configures nodes based on its scene file.
         */
        const response = await fetch(this.scene);
        const sceneContent = await response.json();

        if (Object.keys(sceneContent).length === 0) {
            return;
        }

        const tempNodeStorage = {};

        for (const pathKey in sceneContent) {
            const properties = {};

            for (const [name, value] of Object.entries(sceneContent[pathKey]['properties'])) {
                properties[name] = value['value']; // value of property
            }

            let nodeClass;
            if (properties['Node/Script']) {
                const scriptPath = properties['Node/Script'];
                const module = await import(`/${scriptPath}`);
                nodeClass = module.Node;
            } else {
                nodeClass = NODES[sceneContent[pathKey]['type']];
            }

            // Find parent node
            const parent = sceneContent[pathKey]['parent'] ? tempNodeStorage[sceneContent[pathKey]['parent']] : null;

            const node = new nodeClass(
                this.gameManager,
                this.convertNodeProperties(properties),
                sceneContent[pathKey]['uuid'],
                parent,
                this
            );

            node.initializeProperties(node.properties);

            if (parent === null) {
                this.rootNode = node;
            }

            tempNodeStorage[pathKey] = node;
            this.registerNode(node);
        }
        // Call fullInit after all nodes are created
        for (const node of Object.values(tempNodeStorage)) {
            if (!node.destroyed) {
                node.fullInit();
            }
        }
        // Call onStart on all nodes
        for (const node of Object.values(tempNodeStorage)) {
            if (!node.destroyed) {
                node.onStart();
            }
        }
    }

    registerNode(node) {
        if (this.nodeStorage.includes(node)) {
            throw new Error('Node already registered in scene.');
        }
        this.nodeStorage.push(node);
    }

    unregisterNode(node) {
        const index = this.nodeStorage.indexOf(node);
        if (index === -1) {
            throw new Error('Node not registered in scene.');
        }
        this.nodeStorage.splice(index, 1);
    }

    /**
     * Converts node property name from editor -> core
     * @param {Object} properties - The properties of a node
     * @returns {Object} The modified properties in terms of converting naming used in editor
     *                   to the naming used in the core node classes
     */
    convertNodeProperties(properties) {
        const newProperties = {};
        for (const key in properties) {
            if (PROPERTY_NAME_REFERENCE[key] !== null) {
                newProperties[PROPERTY_NAME_REFERENCE[key]] = properties[key];
            }
        }
        return newProperties;
    }

    update(dt) {
        super.update(dt);
        const nodesToUpdate = [...this.nodeStorage];
        for (const node of nodesToUpdate) {
            if (!node.destroyed) {
                node.update(dt);
            }
        }
    }

    destroy() {
        super.destroy();
        if (this.rootNode !== null && !this.rootNode.destroyed) {
            this.rootNode.destroy();
        }
        this.nodeStorage = [];
    }
}

export class SceneManager extends Manager {
    /**
     * The manager that manages scene objects.
     */
    constructor(gameManager) {
        super(gameManager);
        this.currentScene = null;
    }

    async instantiateScene(scenePath) {
        /**
         * Instantiates a scene based on scene file.
         * @param {string} scenePath - The scene file path
         */
        if (this.currentScene) {
            this.currentScene.destroy();
        }

        const scene = new Scene(this.gameManager, scenePath);
        await scene.init();

        this.currentScene = scene;
    }

    update(dt) {
        super.update(dt);
        if (this.currentScene) {
            this.currentScene.update(dt);
        }
    }

    destroy() {
        super.destroy();
        if (this.currentScene) {
            this.currentScene.destroy();
        }
    }
}
