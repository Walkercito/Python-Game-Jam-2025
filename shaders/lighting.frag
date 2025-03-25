#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform vec2 lightPos;
uniform float radius;
uniform float softness;
uniform float ambientDarkness;
uniform vec2 resolution;

void main() {
    vec2 pixelPos = gl_FragCoord.xy;
    float dist = distance(pixelPos, lightPos);
    
    // Calculate light intensity with smooth falloff
    float intensity = 1.0 - smoothstep(radius * (1.0 - softness), radius, dist);
    
    // Calculate ambient light (darker at edges)
    float ambient = 1.0 - ambientDarkness;
    
    // Final light value
    float light = ambient + intensity * (1.0 - ambient);
    
    // Output light color (black with alpha for darkness)
    FragColor = vec4(0.0, 0.0, 0.0, 1.0 - light);
}
