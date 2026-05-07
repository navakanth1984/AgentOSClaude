const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// UI Elements
const startScreen = document.getElementById('start-screen');
const gameOverScreen = document.getElementById('game-over-screen');
const scoreDisplay = document.getElementById('score-display');
const finalScoreSpan = document.getElementById('final-score');
const startBtn = document.getElementById('start-btn');
const restartBtn = document.getElementById('restart-btn');

// Game State
let isPlaying = false;
let score = 0;
let animationId;
let lastTime = 0;
let speed = 300; // pixels per second

// Resize handling
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

// Game Objects
const player = {
    x: 50,
    y: 0,
    width: 50,
    height: 50,
    color: '#3498db',
    dy: 0,
    jumpForce: -12, // slightly reduced for smoother feel
    gravity: 0.6,
    grounded: false
};

let obstacles = [];

class Obstacle {
    constructor() {
        this.width = 40 + Math.random() * 30;
        this.height = 40 + Math.random() * 40;
        this.x = canvas.width;
        this.y = canvas.height - this.height; // ground level
        this.color = '#e74c3c';
        this.markedForDeletion = false;
    }

    update(dt) {
        this.x -= speed * dt;
        if (this.x + this.width < 0) {
            this.markedForDeletion = true;
            score += 10;
            scoreDisplay.textContent = `Score: ${score}`;
            // Increase speed slightly over time
            speed += 5;
        }
    }

    draw() {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

// Input Handling
function jump() {
    if (!isPlaying) return;
    if (player.grounded) {
        player.dy = player.jumpForce;
        player.grounded = false;
    }
}

window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' || e.code === 'ArrowUp') jump();
});
window.addEventListener('touchstart', (e) => {
    jump();
});
window.addEventListener('mousedown', (e) => {
    jump();
});

// Game Loop
let obstacleTimer = 0;
let obstacleInterval = 1500;
let nextObstacleInterval = 1500;

function update(deltaTime) {
    const dt = deltaTime / 1000; // convert to seconds

    // Player Physics
    player.dy += player.gravity;
    player.y += player.dy;

    // Ground Collision
    if (player.y + player.height > canvas.height) {
        player.y = canvas.height - player.height;
        player.dy = 0;
        player.grounded = true;
    }

    // Obstacle Spawning
    obstacleTimer += deltaTime;
    if (obstacleTimer > nextObstacleInterval) {
        obstacles.push(new Obstacle());
        obstacleTimer = 0;
        nextObstacleInterval = 1000 + Math.random() * 1500; // Random interval between 1s and 2.5s
    }

    // Update Obstacles & Check Collision
    obstacles.forEach(obs => {
        obs.update(dt);
        
        // AABB Collision Detection
        if (
            player.x < obs.x + obs.width &&
            player.x + player.width > obs.x &&
            player.y < obs.y + obs.height &&
            player.y + player.height > obs.y
        ) {
            gameOver();
        }
    });

    obstacles = obstacles.filter(obs => !obs.markedForDeletion);
}

function draw() {
    // Clear Screen
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Ground
    ctx.fillStyle = '#2c3e50'; // Same as background for now, or darker
    // ctx.fillRect(0, canvas.height - 10, canvas.width, 10);

    // Draw Player
    ctx.fillStyle = player.color;
    ctx.fillRect(player.x, player.y, player.width, player.height);

    // Draw Obstacles
    obstacles.forEach(obs => obs.draw());
}

function loop(timestamp) {
    if (!isPlaying) return;
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;

    update(deltaTime);
    draw();

    animationId = requestAnimationFrame(loop);
}

function startGame() {
    isPlaying = true;
    score = 0;
    speed = 300;
    obstacles = [];
    player.y = canvas.height - player.height;
    player.dy = 0;
    scoreDisplay.textContent = 'Score: 0';
    
    startScreen.classList.remove('active');
    gameOverScreen.classList.remove('active');
    
    lastTime = performance.now();
    animationId = requestAnimationFrame(loop);
}

function gameOver() {
    isPlaying = false;
    cancelAnimationFrame(animationId);
    finalScoreSpan.textContent = score;
    gameOverScreen.classList.add('active');
}

startBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent jump on button click
    startGame();
});

restartBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    startGame();
});
