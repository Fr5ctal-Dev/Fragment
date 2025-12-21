export class Vector2 {
  constructor(x = 0, y = 0) {
    // Handle different input types
    if (typeof x === 'object' && x !== null && !Array.isArray(x)) {
      // Object with x, y properties
      this.x = x.x !== undefined ? x.x : 0;
      this.y = x.y !== undefined ? x.y : 0;
    } else if (Array.isArray(x)) {
      // Array [x, y]
      this.x = x[0] !== undefined ? x[0] : 0;
      this.y = x[1] !== undefined ? x[1] : 0;
    } else {
      // Two separate numbers
      this.x = x;
      this.y = y;
    }
  }

  // Rotate vector by angle (in degrees)
  rotate(angle) {
    const rad = angle * Math.PI / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    return new Vector2(
      this.x * cos - this.y * sin,
      this.x * sin + this.y * cos
    );
  }

  // Vector addition
  add(other) {
    return new Vector2(this.x + other.x, this.y + other.y);
  }

  // Vector subtraction
  sub(other) {
    return new Vector2(this.x - other.x, this.y - other.y);
  }

  // Scalar multiplication
  mul(scalar) {
    return new Vector2(this.x * scalar, this.y * scalar);
  }

  // Scalar division
  div(scalar) {
    return new Vector2(this.x / scalar, this.y / scalar);
  }

  // Array-like access for compatibility
  get(index) {
    return index === 0 ? this.x : this.y;
  }

  // Array indexing support
  [0]() { return this.x; }
  [1]() { return this.y; }

  // Length/magnitude
  get length() {
    return Math.sqrt(this.x * this.x + this.y * this.y);
  }

  // String representation
  toString() {
    return `Vector2(${this.x}, ${this.y})`;
  }
}

export class Vector3 {
  constructor(x = 0, y = 0, z = 0) {
    // Handle different input types
    if (typeof x === 'object' && x !== null && !Array.isArray(x)) {
      // Object with x, y, z properties
      this.x = x.x !== undefined ? x.x : 0;
      this.y = x.y !== undefined ? x.y : 0;
      this.z = x.z !== undefined ? x.z : 0;
    } else if (Array.isArray(x)) {
      // Array [x, y, z]
      this.x = x[0] !== undefined ? x[0] : 0;
      this.y = x[1] !== undefined ? x[1] : 0;
      this.z = x[2] !== undefined ? x[2] : 0;
    } else {
      // Three separate numbers
      this.x = x;
      this.y = y;
      this.z = z;
    }
  }

  // Vector addition
  add(other) {
    return new Vector3(this.x + other.x, this.y + other.y, this.z + other.z);
  }

  // Vector subtraction
  sub(other) {
    return new Vector3(this.x - other.x, this.y - other.y, this.z - other.z);
  }

  // Scalar multiplication
  mul(scalar) {
    return new Vector3(this.x * scalar, this.y * scalar, this.z * scalar);
  }

  // Scalar division
  div(scalar) {
    return new Vector3(this.x / scalar, this.y / scalar, this.z / scalar);
  }

  // Array-like access for compatibility
  get(index) {
    if (index === 0) return this.x;
    if (index === 1) return this.y;
    return this.z;
  }

  // Length/magnitude
  get length() {
    return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
  }

  // String representation
  toString() {
    return `Vector3(${this.x}, ${this.y}, ${this.z})`;
  }
}
