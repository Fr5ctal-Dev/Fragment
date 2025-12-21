export class Color {
  constructor(r, g, b, a = 255) {
    // Handle different input formats
    if (typeof r === 'string') {
      // Hex string like '#FF0000' or '0xFF0000'
      const hex = r.replace('#', '');
      const value = parseInt(hex, 16);
      this.r = (value >> 16) & 0xFF;
      this.g = (value >> 8) & 0xFF;
      this.b = value & 0xFF;
      this.a = a;
    } else if (Array.isArray(r)) {
      // Array [r, g, b] or [r, g, b, a]
      this.r = r[0] || 0;
      this.g = r[1] || 0;
      this.b = r[2] || 0;
      this.a = r[3] !== undefined ? r[3] : 255;
    } else {
      // Individual components
      this.r = r;
      this.g = g;
      this.b = b;
      this.a = a;
    }
  }

  // Convert to hex number for PixiJS (0xRRGGBB format)
  toHex() {
    return (this.r << 16) | (this.g << 8) | this.b;
  }

  // Convert to hex string
  toHexString() {
    const hex = this.toHex().toString(16).padStart(6, '0');
    return `#${hex}`;
  }

  // Convert to RGBA string for CSS
  toRGBA() {
    return `rgba(${this.r}, ${this.g}, ${this.b}, ${this.a / 255})`;
  }

  // String representation
  toString() {
    return `Color(${this.r}, ${this.g}, ${this.b}, ${this.a})`;
  }

  // Common colors as static properties
  static get BLACK() { return new Color(0, 0, 0); }
  static get WHITE() { return new Color(255, 255, 255); }
  static get RED() { return new Color(255, 0, 0); }
  static get GREEN() { return new Color(0, 255, 0); }
  static get BLUE() { return new Color(0, 0, 255); }
  static get TRANSPARENT() { return new Color(0, 0, 0, 0); }
}
