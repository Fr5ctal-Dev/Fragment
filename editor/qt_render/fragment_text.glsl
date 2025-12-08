#version 330 core

uniform sampler2D fontTexture;
uniform vec4 textColor;

in vec2 fragmentTexCoord;
out vec4 color;

void main() {
    vec4 texColor = texture(fontTexture, fragmentTexCoord);
    color = texColor * textColor;
}
