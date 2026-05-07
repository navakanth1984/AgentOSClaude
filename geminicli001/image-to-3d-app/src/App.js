import React, { useState, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import './index.css';

function ThreeDImage({ imageUrl }) {
  const mesh = useRef();
  const texture = new THREE.TextureLoader().load(imageUrl);

  const shaderArgs = React.useMemo(
    () => ({
      uniforms: {
        time: { value: 0 },
        texture: { value: texture },
      },
      vertexShader: `
        uniform float time;
        uniform sampler2D texture;
        varying vec2 vUv;
        void main() {
          vUv = uv;
          vec4 tex = texture2D(texture, uv);
          float brightness = (tex.r + tex.g + tex.b) / 3.0;
          float displacement = sin(brightness * 10.0 + time * 2.0) * 0.5;
          vec3 newPosition = position + normal * displacement;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D texture;
        varying vec2 vUv;
        void main() {
          gl_FragColor = texture2D(texture, vUv);
        }
      `,
    }),
    [texture]
  );

  useFrame((state) => {
    if (mesh.current) {
      mesh.current.material.uniforms.time.value = state.clock.getElapsedTime();
      mesh.current.rotation.y += 0.005;
    }
  });

  return (
    <mesh ref={mesh}>
      <planeGeometry args={[4, 4, 256, 256]} />
      <shaderMaterial args={[shaderArgs]} />
    </mesh>
  );
}

function App() {
  const [imageUrl, setImageUrl] = useState(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="App">
      <div className="upload-container">
        <input type="file" onChange={handleImageUpload} accept="image/*" />
      </div>
      <div className="canvas-container">
        {imageUrl ? (
          <Canvas>
            <ambientLight intensity={0.2} />
            <spotLight position={[5, 5, 5]} angle={0.3} penumbra={1} intensity={2} castShadow />
            <ThreeDImage imageUrl={imageUrl} />
            <OrbitControls />
          </Canvas>
        ) : (
          <div className="placeholder">
            <p>Please upload an image to see the 3D version</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;