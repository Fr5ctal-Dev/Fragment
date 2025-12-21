import { Manager } from '/fragment/core/manager.js';
import { NODES } from '/fragment/nodes/index.js';

const nameRefResponse = await fetch('fragment/nodes/name_ref.json');
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
    const content = await response.json();

    // Parse node paths from JSON string keys
    const sceneContent = {};
    for (const [jsonKey, nodeData] of Object.entries(content)) {
      const pathList = JSON.parse(jsonKey);
      // Use JSON.stringify to create a consistent key for lookups
      const pathKey = JSON.stringify(pathList);
      sceneContent[pathKey] = nodeData;
    }

    if (Object.keys(sceneContent).length === 0) {
      return;
    }

    const tempNodeStorage = {};

    for (const pathKey in sceneContent) {
      const pathList = JSON.parse(pathKey);
      const properties = {};

      for (const [name, value] of Object.entries(sceneContent[pathKey]['properties'])) {
        properties[name] = value['value']; // value of property
      }

      let nodeClass;
      if (properties['Node/Script']) {
        const scriptPath = properties['Node/Script'];
        const module = await import(`../../${scriptPath}`);
        nodeClass = module.Node;
      } else {
        nodeClass = NODES[sceneContent[pathKey]['type']];
      }

      // Find parent node
      const parentKey = JSON.stringify(pathList.slice(0, -1));
      const parent = pathList.length > 1 ? tempNodeStorage[parentKey] : null;

      const node = new nodeClass(
        this.gameManager,
        this.convertNodeProperties(properties),
        pathList[pathList.length - 1], // uuid
        parent,
        this
      );

      node.initializeProperties(node.properties);

      if (pathList.length === 1) {
        this.rootNode = node;
      }

      tempNodeStorage[pathKey] = node;
      this.registerNode(node);
    }
    // Call fullInit after all nodes are created
    for (const node of Object.values(tempNodeStorage)) {
      node.fullInit();
    }
    // Call on_start on all nodes
    for (const node of Object.values(tempNodeStorage)) {
      node.on_start();
    }
  }

  registerNode(node) {
    this.nodeStorage.push(node);
  }

  unregisterNode(node) {
    const index = this.nodeStorage.indexOf(node);
    if (index > -1) {
      this.nodeStorage.splice(index, 1);
    }
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
      if (PROPERTY_NAME_REFERENCE[key] !== undefined) {
        newProperties[PROPERTY_NAME_REFERENCE[key]] = properties[key];
      }
    }
    return newProperties;
  }

  update(dt) {
    super.update(dt);
    for (const node of this.nodeStorage) {
      node.update(dt);
    }
  }

  destroy() {
    super.destroy();
    if (this.rootNode !== null) {
      this.rootNode.destroy();
    }
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
    const scene = new Scene(this.gameManager, scenePath);
    await scene.init();

    if (this.currentScene) {
      this.currentScene.destroy();
    }
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
