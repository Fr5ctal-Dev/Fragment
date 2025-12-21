// Node registry and exports

import { Node } from '/fragment/nodes/node.js';
import { Node2D } from '/fragment/nodes/node2d.js';
import { Canvas } from '/fragment/nodes/canvas.js';
import { Drawable } from '/fragment/nodes/drawable.js';
import { Camera } from '/fragment/nodes/camera.js';
import { Sprite } from '/fragment/nodes/sprite.js';

export const NODES = {
  'Node': Node,
  'Node2D': Node2D,
  'Canvas': Canvas,
  'Drawable': Drawable,
  'Camera': Camera,
  'Sprite': Sprite
};

export { Node, Node2D, Canvas, Drawable, Camera, Sprite };
