export class Vector2 {
    constructor(x = 0, y = 0) {
        this.x = x;
        this.y = y;
    }

    static toVector2(...args) {
        if (args.length === 1) {
            const arg = args[0];
            if (arg instanceof Vector2) {
                return arg;
            }
            else if (typeof arg === 'number') {
                return new Vector2(arg.valueOf(), arg.valueOf());
            }
            else if (Array.isArray(arg) && arg.length === 2) {
                return new Vector2(arg[0], arg[1]);
            }
        }
        else if (args.length === 2) {
            return new Vector2(args[0], args[1]);
        }
        throw new Error(`Cannot convert to Vector2: ${args}`);
    }

    add(other) {
        return new Vector2(this.x + other.x, this.y + other.y);
    }

    sub(other) {
        return new Vector2(this.x - other.x, this.y - other.y);
    }

    mul(scalar) {
        return new Vector2(this.x * scalar, this.y * scalar);
    }

    div(scalar) {
        return new Vector2(this.x / scalar, this.y / scalar);
    }

    rotate(angle) {
        const rad = (angle * Math.PI) / 180;
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        return new Vector2(
            this.x * cos - this.y * sin,
            this.x * sin + this.y * cos
        )
    }

    get(index) {
        return index === 0 ? this.x : this.y;
    }

    get length() {
        return Math.sqrt(this.x * this.x + this.y * this.y);
    }
}
