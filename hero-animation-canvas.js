/**
 * Hero Animation - Canvas 2D Version
 * Interactive background with mouse/scroll tracking
 * Colors: Cyan (#00D9FF), Green (#10B981), White (#FFFFFF)
 */

class HeroAnimationCanvas {
  constructor(containerId = 'hero') {
    this.container = document.getElementById(containerId);
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');

    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.canvas.width = this.width;
    this.canvas.height = this.height;

    this.container.appendChild(this.canvas);
    this.canvas.style.position = 'absolute';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.zIndex = '0';
    this.canvas.style.pointerEvents = 'none';

    // Colors
    this.colors = {
      cyan: '#00D9FF',
      green: '#10B981',
      white: '#FFFFFF',
      navy: '#0a1a2e'
    };

    // Animation state
    this.time = 0;
    this.mouseX = this.width / 2;
    this.mouseY = this.height / 2;
    this.scrollY = 0;
    this.fps = 30;
    this.frameTime = 1000 / this.fps;
    this.lastFrameTime = 0;

    this.setupEventListeners();
    this.animate();
  }

  setupEventListeners() {
    window.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
    });

    window.addEventListener('scroll', () => {
      this.scrollY = window.scrollY;
    });

    window.addEventListener('resize', () => {
      this.width = window.innerWidth;
      this.height = window.innerHeight;
      this.canvas.width = this.width;
      this.canvas.height = this.height;
    });
  }

  animate = (currentTime = 0) => {
    if (currentTime - this.lastFrameTime < this.frameTime) {
      requestAnimationFrame(this.animate);
      return;
    }

    this.lastFrameTime = currentTime;
    this.time += this.frameTime / 1000;

    // Clear canvas
    this.ctx.fillStyle = this.colors.navy;
    this.ctx.fillRect(0, 0, this.width, this.height);

    // Calculate parallax offset from mouse
    const parallaxX = (this.mouseX - this.width / 2) * 0.02;
    const parallaxY = (this.mouseY - this.height / 2) * 0.02;
    const scrollEffect = this.scrollY * 0.5;

    const centerX = this.width / 2 + parallaxX;
    const centerY = this.height / 2 + parallaxY - scrollEffect;

    // Draw holographic grid
    this.drawGrid(centerX, centerY);

    // Draw rotating diamond
    this.drawDiamond(centerX, centerY);

    // Draw orbiting particles
    this.drawOrbitingParticles(centerX, centerY);

    // Draw data streams
    this.drawDataStreams(centerX, centerY);

    // Draw scanning lines
    this.drawScanningLines();

    // Draw corner elements
    this.drawCornerElements();

    requestAnimationFrame(this.animate);
  };

  drawGrid(centerX, centerY) {
    const gridAlpha = 0.5 + 0.5 * Math.sin(2 * Math.PI * this.time / 3);
    const gridAlphaInt = Math.floor(40 * gridAlpha);

    this.ctx.strokeStyle = `rgba(0, 217, 255, ${gridAlphaInt / 255})`;
    this.ctx.lineWidth = 1;

    // Vertical lines
    for (let x = 0; x < this.width; x += 150) {
      const startY = centerY - 300;
      const endY = centerY + 300;
      this.ctx.beginPath();
      this.ctx.moveTo(x, startY);
      this.ctx.lineTo(x, endY);
      this.ctx.stroke();
    }

    // Horizontal lines
    for (let y = centerY - 300; y < centerY + 300; y += 150) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width, y);
      this.ctx.stroke();
    }
  }

  drawDiamond(centerX, centerY) {
    const rotation = 2 * Math.PI * this.time / 5;
    const diamondSize = 250;

    const corners = [
      {
        x: centerX + diamondSize * Math.cos(rotation),
        y: centerY + diamondSize * Math.sin(rotation)
      },
      {
        x: centerX + diamondSize * Math.cos(rotation + Math.PI / 2),
        y: centerY + diamondSize * Math.sin(rotation + Math.PI / 2)
      },
      {
        x: centerX + diamondSize * Math.cos(rotation + Math.PI),
        y: centerY + diamondSize * Math.sin(rotation + Math.PI)
      },
      {
        x: centerX + diamondSize * Math.cos(rotation + 3 * Math.PI / 2),
        y: centerY + diamondSize * Math.sin(rotation + 3 * Math.PI / 2)
      }
    ];

    this.ctx.strokeStyle = 'rgba(0, 217, 255, 0.8)';
    this.ctx.lineWidth = 3;
    this.ctx.beginPath();
    this.ctx.moveTo(corners[0].x, corners[0].y);
    for (let i = 1; i < 4; i++) {
      this.ctx.lineTo(corners[i].x, corners[i].y);
    }
    this.ctx.closePath();
    this.ctx.stroke();

    // Diamond glow
    const glowAlpha = 0.3;
    this.ctx.strokeStyle = `rgba(0, 217, 255, ${glowAlpha})`;
    this.ctx.lineWidth = 1;
    for (let ring = 1; ring <= 3; ring++) {
      const ringSize = diamondSize + ring * 40;
      this.ctx.beginPath();
      this.ctx.arc(centerX, centerY, ringSize, 0, Math.PI * 2);
      this.ctx.stroke();
    }
  }

  drawOrbitingParticles(centerX, centerY) {
    const diamondSize = 250;

    for (let i = 0; i < 6; i++) {
      const angle = 2 * Math.PI * (this.time / 3 + i / 6);
      const x = centerX + (diamondSize + 180) * Math.cos(angle);
      const y = centerY + (diamondSize + 180) * Math.sin(angle);

      const glowAlpha = 0.5 + 0.5 * Math.sin(2 * Math.PI * (this.time + i) / 2);

      // Glow circle
      this.ctx.strokeStyle = `rgba(16, 185, 129, ${glowAlpha * 0.6})`;
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.arc(x, y, 25, 0, Math.PI * 2);
      this.ctx.stroke();

      // Core particle
      this.ctx.fillStyle = `rgba(16, 185, 129, ${glowAlpha})`;
      this.ctx.beginPath();
      this.ctx.arc(x, y, 12, 0, Math.PI * 2);
      this.ctx.fill();
    }
  }

  drawDataStreams(centerX, centerY) {
    for (let stream = 0; stream < 3; stream++) {
      const streamPos = (this.time * 200 + stream * 120) % 400;
      const streamX = centerX - 100 + stream * 100;

      for (let offset = 0; offset < streamPos; offset += 40) {
        const alpha = Math.max(0, 1 - Math.abs(offset - streamPos) / 200);

        this.ctx.fillStyle = `rgba(16, 185, 129, ${alpha * 0.7})`;
        this.ctx.beginPath();
        this.ctx.arc(streamX, centerY - 200 + offset, 6, 0, Math.PI * 2);
        this.ctx.fill();
      }
    }
  }

  drawScanningLines() {
    for (let y = 0; y < this.height; y += 4) {
      const lineAlpha = 0.3 + 0.7 * Math.sin(2 * Math.PI * (this.time + y / this.height) / 2);
      this.ctx.strokeStyle = `rgba(0, 217, 255, ${lineAlpha * 0.1})`;
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width, y);
      this.ctx.stroke();
    }
  }

  drawCornerElements() {
    const corners = [
      { x: 80, y: 80, color: 'rgba(0, 217, 255, 0.6)' },
      { x: this.width - 80, y: 80, color: 'rgba(0, 217, 255, 0.6)' },
      { x: 80, y: this.height - 80, color: 'rgba(16, 185, 129, 0.6)' },
      { x: this.width - 80, y: this.height - 80, color: 'rgba(255, 215, 0, 0.6)' }
    ];

    corners.forEach(corner => {
      const pulse = 0.5 + 0.5 * Math.sin(2 * Math.PI * this.time * 2);

      this.ctx.strokeStyle = corner.color;
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(corner.x - 40, corner.y - 40, 80, 80);

      this.ctx.fillStyle = corner.color;
      this.ctx.beginPath();
      this.ctx.arc(corner.x, corner.y, 10 * pulse, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new HeroAnimationCanvas('hero-animation-container');
  });
} else {
  new HeroAnimationCanvas('hero-animation-container');
}
