/**
 * Hero Animation - Three.js 3D Version
 * Interactive 3D background with mouse/scroll tracking
 * Colors: Cyan (#00D9FF), Green (#10B981), White (#FFFFFF)
 * Requires: Three.js library
 */

class HeroAnimationThree {
  constructor(containerId = 'hero-animation-container') {
    // Check if Three.js is loaded
    if (typeof THREE === 'undefined') {
      console.error('Three.js is required for HeroAnimationThree');
      return;
    }

    this.container = document.getElementById(containerId);
    this.width = window.innerWidth;
    this.height = window.innerHeight;

    // Scene setup
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75, this.width / this.height, 0.1, 10000);
    this.camera.position.z = 100;

    this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    this.renderer.setSize(this.width, this.height);
    this.renderer.setClearColor(0x0a1a2e, 1);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.container.appendChild(this.renderer.domElement);

    // Style canvas
    this.renderer.domElement.style.position = 'absolute';
    this.renderer.domElement.style.top = '0';
    this.renderer.domElement.style.left = '0';
    this.renderer.domElement.style.zIndex = '0';
    this.renderer.domElement.style.pointerEvents = 'none';

    // Colors
    this.colors = {
      cyan: 0x00D9FF,
      green: 0x10B981,
      white: 0xFFFFFF,
      navy: 0x0a1a2e
    };

    // Animation state
    this.time = 0;
    this.mouseX = 0;
    this.mouseY = 0;
    this.scrollY = 0;
    this.fps = 30;
    this.frameTime = 1000 / this.fps;
    this.lastFrameTime = 0;

    // Objects array
    this.gridLines = [];
    this.particles = [];
    this.diamondVertices = [];

    this.setupScene();
    this.setupEventListeners();
    this.animate();
  }

  setupScene() {
    // Holographic grid
    this.createGrid();

    // Rotating diamond
    this.createDiamond();

    // Orbiting particles
    this.createOrbitingParticles();

    // Data stream particles
    this.createDataStreamParticles();

    // Lighting
    const light = new THREE.PointLight(0x00D9FF, 0.5);
    light.position.set(0, 0, 100);
    this.scene.add(light);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
    this.scene.add(ambientLight);
  }

  createGrid() {
    const gridSize = 500;
    const gridSpacing = 100;
    const gridMaterial = new THREE.LineBasicMaterial({
      color: this.colors.cyan,
      transparent: true,
      opacity: 0.3
    });

    // Vertical lines
    for (let x = -gridSize; x <= gridSize; x += gridSpacing) {
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array([x, -gridSize, 0, x, gridSize, 0]);
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const line = new THREE.Line(geometry, gridMaterial);
      this.scene.add(line);
      this.gridLines.push(line);
    }

    // Horizontal lines
    for (let y = -gridSize; y <= gridSize; y += gridSpacing) {
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array([-gridSize, y, 0, gridSize, y, 0]);
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const line = new THREE.Line(geometry, gridMaterial);
      this.scene.add(line);
      this.gridLines.push(line);
    }
  }

  createDiamond() {
    const diamondSize = 80;
    const geometry = new THREE.BufferGeometry();

    // Diamond vertices
    const vertices = new Float32Array([
      diamondSize, 0, 0,      // top
      0, diamondSize, 0,      // right
      -diamondSize, 0, 0,     // bottom
      0, -diamondSize, 0      // left
    ]);

    const indices = [0, 1, 1, 2, 2, 3, 3, 0];

    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    geometry.setIndex(new THREE.BufferAttribute(new Uint16Array(indices), 1));

    const material = new THREE.LineBasicMaterial({
      color: this.colors.cyan,
      linewidth: 3,
      transparent: true,
      opacity: 0.8
    });

    this.diamond = new THREE.LineSegments(geometry, material);
    this.scene.add(this.diamond);

    // Diamond glow (sphere outline)
    const sphereGeometry = new THREE.SphereGeometry(100, 32, 32);
    const sphereMaterial = new THREE.MeshBasicMaterial({
      color: this.colors.cyan,
      wireframe: true,
      transparent: true,
      opacity: 0.1
    });
    this.diamondGlow = new THREE.Mesh(sphereGeometry, sphereMaterial);
    this.scene.add(this.diamondGlow);
  }

  createOrbitingParticles() {
    const particleGeometry = new THREE.IcosahedronGeometry(3, 4);
    const particleMaterial = new THREE.MeshBasicMaterial({
      color: this.colors.green,
      transparent: true,
      opacity: 0.8
    });

    for (let i = 0; i < 12; i++) {
      const particle = new THREE.Mesh(particleGeometry, particleMaterial.clone());
      particle.userData.angle = (i / 12) * Math.PI * 2;
      particle.userData.speed = 0.3 + Math.random() * 0.2;
      particle.userData.radius = 120 + Math.random() * 30;
      this.scene.add(particle);
      this.particles.push(particle);
    }
  }

  createDataStreamParticles() {
    const pointGeometry = new THREE.BufferGeometry();
    const positions = [];

    for (let i = 0; i < 200; i++) {
      positions.push(
        (Math.random() - 0.5) * 200,  // x
        (Math.random() - 0.5) * 200,  // y
        (Math.random() - 0.5) * 100   // z
      );
    }

    pointGeometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3));

    const pointMaterial = new THREE.PointsMaterial({
      color: this.colors.green,
      size: 2,
      transparent: true,
      opacity: 0.6
    });

    this.dataPoints = new THREE.Points(pointGeometry, pointMaterial);
    this.scene.add(this.dataPoints);
  }

  setupEventListeners() {
    window.addEventListener('mousemove', (e) => {
      this.mouseX = (e.clientX / this.width) * 2 - 1;
      this.mouseY = -(e.clientY / this.height) * 2 + 1;
    });

    window.addEventListener('scroll', () => {
      this.scrollY = window.scrollY;
    });

    window.addEventListener('resize', () => {
      this.width = window.innerWidth;
      this.height = window.innerHeight;
      this.camera.aspect = this.width / this.height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(this.width, this.height);
    });
  }

  animate = (currentTime = 0) => {
    if (currentTime - this.lastFrameTime < this.frameTime) {
      requestAnimationFrame(this.animate);
      return;
    }

    this.lastFrameTime = currentTime;
    this.time += this.frameTime / 1000;

    // Camera parallax from mouse
    this.camera.position.x = this.mouseX * 30;
    this.camera.position.y = this.mouseY * 20 - this.scrollY * 0.1;
    this.camera.lookAt(0, 0, 0);

    // Rotate diamond
    if (this.diamond) {
      this.diamond.rotation.z += 0.002;
    }
    if (this.diamondGlow) {
      this.diamondGlow.rotation.x += 0.0005;
      this.diamondGlow.rotation.y += 0.0008;
    }

    // Update orbiting particles
    this.particles.forEach(particle => {
      particle.userData.angle += particle.userData.speed * 0.01;
      particle.position.x = Math.cos(particle.userData.angle) * particle.userData.radius;
      particle.position.y = Math.sin(particle.userData.angle) * particle.userData.radius;
      particle.position.z = Math.cos(particle.userData.angle * 0.5) * 30;

      // Pulsing glow
      const pulseMaterial = particle.material;
      pulseMaterial.opacity = 0.5 + 0.5 * Math.sin(this.time * 2 + particle.userData.angle);
    });

    // Rotate data points
    if (this.dataPoints) {
      this.dataPoints.rotation.x += 0.0001;
      this.dataPoints.rotation.y += 0.0002;

      // Animate positions
      const positions = this.dataPoints.geometry.attributes.position.array;
      for (let i = 0; i < positions.length; i += 3) {
        positions[i] += Math.sin(this.time + i) * 0.1;
        positions[i + 1] += Math.cos(this.time + i) * 0.1;
      }
      this.dataPoints.geometry.attributes.position.needsUpdate = true;
    }

    // Update grid opacity based on time
    const gridAlpha = 0.3 + 0.2 * Math.sin(2 * Math.PI * this.time / 3);
    this.gridLines.forEach(line => {
      line.material.opacity = gridAlpha;
    });

    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(this.animate);
  };
}

// Load Three.js library and initialize
function initThreeAnimation() {
  if (typeof THREE !== 'undefined') {
    new HeroAnimationThree('hero-animation-container');
  } else {
    // Load Three.js from CDN if not already loaded
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
    script.onload = () => {
      new HeroAnimationThree('hero-animation-container');
    };
    document.head.appendChild(script);
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initThreeAnimation);
} else {
  initThreeAnimation();
}
