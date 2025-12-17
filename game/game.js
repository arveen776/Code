const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const livesElement = document.getElementById('lives');
const levelElement = document.getElementById('level');
const highScoreElement = document.getElementById('highScore');
const powerUpText = document.getElementById('powerUpText');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const restartBtn = document.getElementById('restartBtn');
const gameOverDiv = document.getElementById('gameOver');
const levelCompleteDiv = document.getElementById('levelComplete');
const finalScoreElement = document.getElementById('finalScore');
const finalLevelElement = document.getElementById('finalLevel');

// Game state
let gameRunning = false;
let gamePaused = false;
let score = 0;
let lives = 5;
let level = 1;
let highScore = localStorage.getItem('breakoutHighScore') || 0;
let animationId;

// Paddle
const paddle = {
    x: canvas.width / 2 - 100,
    y: canvas.height - 30,
    width: 200,
    height: 15,
    speed: 10,
    dx: 0
};

// Ball
const ball = {
    x: canvas.width / 2,
    y: canvas.height - 50,
    radius: 10,
    dx: 0,
    dy: 0,
    speed: 3.5,
    launched: false,
    stuckToPaddle: false
};

// Bricks
let bricks = [];
const brickRows = 8;
const brickCols = 10;
const brickWidth = 70;
const brickHeight = 25;
const brickPadding = 5;
const brickOffsetTop = 50;
const brickOffsetLeft = 35;

// Particles
let particles = [];

// Power-ups
let powerUps = [];
let activePowerUp = null;
let powerUpTimer = 0;

// Colors for different brick types
const brickColors = [
    '#e74c3c', '#e67e22', '#f39c12', '#27ae60',
    '#3498db', '#9b59b6', '#e91e63', '#00bcd4'
];

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.color = color;
        this.life = 30;
        this.size = Math.random() * 3 + 2;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life--;
        this.vy += 0.1; // gravity
    }

    draw() {
        ctx.save();
        ctx.globalAlpha = this.life / 30;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
}

class PowerUp {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 30;
        this.height = 30;
        this.speed = 2;
        this.type = Math.random() > 0.5 ? 'expand' : 'multiply';
        this.rotation = 0;
    }

    update() {
        this.y += this.speed;
        this.rotation += 0.1;
    }

    draw() {
        ctx.save();
        ctx.translate(this.x + this.width / 2, this.y + this.height / 2);
        ctx.rotate(this.rotation);
        
        if (this.type === 'expand') {
            ctx.fillStyle = '#27ae60';
            ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
            ctx.fillStyle = 'white';
            ctx.font = 'bold 20px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('+', 0, 0);
        } else {
            ctx.fillStyle = '#e74c3c';
            ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
            ctx.fillStyle = 'white';
            ctx.font = 'bold 20px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('❤', 0, 0);
        }
        
        ctx.restore();
    }

    collect() {
            if (this.type === 'expand') {
            paddle.width = Math.min(paddle.width + 40, 300);
            powerUpText.textContent = 'Power-up: Expanded Paddle!';
            setTimeout(() => {
                powerUpText.textContent = '';
                paddle.width = 200;
            }, 7000);
        } else {
            // Multiply ball - instead of speed, give extra life
            lives++;
            livesElement.textContent = lives;
            powerUpText.textContent = 'Power-up: Extra Life!';
            setTimeout(() => {
                powerUpText.textContent = '';
            }, 3000);
        }
    }
}

function createBricks() {
    bricks = [];
    for (let r = 0; r < brickRows; r++) {
        bricks[r] = [];
        for (let c = 0; c < brickCols; c++) {
            const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
            const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
            bricks[r][c] = {
                x: brickX,
                y: brickY,
                width: brickWidth,
                height: brickHeight,
                visible: true,
                color: brickColors[r % brickColors.length],
                points: (brickRows - r) * 10
            };
        }
    }
}

function drawPaddle() {
    const gradient = ctx.createLinearGradient(paddle.x, paddle.y, paddle.x, paddle.y + paddle.height);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    ctx.fillStyle = gradient;
    ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
    
    // Add shine effect
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.fillRect(paddle.x, paddle.y, paddle.width, 5);
}

function drawBall() {
    const gradient = ctx.createRadialGradient(ball.x, ball.y, 0, ball.x, ball.y, ball.radius);
    gradient.addColorStop(0, '#fff');
    gradient.addColorStop(1, '#667eea');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fill();
    
    // Add highlight
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.beginPath();
    ctx.arc(ball.x - 3, ball.y - 3, 3, 0, Math.PI * 2);
    ctx.fill();
}

function drawBricks() {
    bricks.forEach(row => {
        row.forEach(brick => {
            if (brick.visible) {
                const gradient = ctx.createLinearGradient(
                    brick.x, brick.y, brick.x, brick.y + brick.height
                );
                gradient.addColorStop(0, brick.color);
                gradient.addColorStop(1, darkenColor(brick.color, 0.3));
                ctx.fillStyle = gradient;
                ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
                
                // Border
                ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
                ctx.lineWidth = 2;
                ctx.strokeRect(brick.x, brick.y, brick.width, brick.height);
            }
        });
    });
}

function darkenColor(color, amount) {
    const num = parseInt(color.replace("#", ""), 16);
    const r = Math.max(0, ((num >> 16) & 0xff) * (1 - amount));
    const g = Math.max(0, ((num >> 8) & 0xff) * (1 - amount));
    const b = Math.max(0, (num & 0xff) * (1 - amount));
    return `rgb(${Math.floor(r)}, ${Math.floor(g)}, ${Math.floor(b)})`;
}

function createParticles(x, y, color, count = 10) {
    for (let i = 0; i < count; i++) {
        particles.push(new Particle(x, y, color));
    }
}

function updateParticles() {
    particles = particles.filter(p => {
        p.update();
        return p.life > 0;
    });
}

function drawParticles() {
    particles.forEach(p => p.draw());
}

function updatePowerUps() {
    powerUps = powerUps.filter(pu => {
        pu.update();
        
        // Check collision with paddle
        if (pu.x < paddle.x + paddle.width &&
            pu.x + pu.width > paddle.x &&
            pu.y < paddle.y + paddle.height &&
            pu.y + pu.height > paddle.y) {
            pu.collect();
            return false;
        }
        
        // Remove if off screen
        return pu.y < canvas.height;
    });
}

function drawPowerUps() {
    powerUps.forEach(pu => pu.draw());
}

function movePaddle() {
    paddle.x += paddle.dx;
    
    // Keep paddle in bounds
    if (paddle.x < 0) {
        paddle.x = 0;
    } else if (paddle.x + paddle.width > canvas.width) {
        paddle.x = canvas.width - paddle.width;
    }
}

function moveBall() {
    if (!ball.launched) {
        ball.x = paddle.x + paddle.width / 2;
        ball.y = paddle.y - ball.radius - 5;
        return;
    }
    
    ball.x += ball.dx;
    ball.y += ball.dy;
    
    // Wall collisions
    if (ball.x + ball.radius > canvas.width || ball.x - ball.radius < 0) {
        ball.dx = -ball.dx;
        ball.x = Math.max(ball.radius, Math.min(canvas.width - ball.radius, ball.x));
    }
    
    if (ball.y - ball.radius < 0) {
        ball.dy = -ball.dy;
        ball.y = ball.radius;
    }
    
    // Paddle collision
    if (ball.y + ball.radius > paddle.y &&
        ball.y - ball.radius < paddle.y + paddle.height &&
        ball.x + ball.radius > paddle.x &&
        ball.x - ball.radius < paddle.x + paddle.width) {
        
        // Only bounce if ball is moving down (prevents getting stuck)
        if (ball.dy > 0) {
            // Calculate hit position on paddle (0 to 1)
            const hitPos = (ball.x - paddle.x) / paddle.width;
            // Reduced angle range for more controlled bounces
            const angle = (hitPos - 0.5) * Math.PI / 4; // -45 to 45 degrees (was 60)
            
            ball.dy = -Math.abs(ball.dy);
            ball.dx = Math.sin(angle) * ball.speed;
            ball.dy = Math.cos(angle) * ball.speed;
            
            // Ensure minimum upward velocity
            if (ball.dy > -2) {
                ball.dy = -2;
            }
            
            createParticles(ball.x, ball.y, '#667eea', 5);
        }
    }
    
    // Brick collisions
    bricks.forEach(row => {
        row.forEach(brick => {
            if (brick.visible) {
                if (ball.x + ball.radius > brick.x &&
                    ball.x - ball.radius < brick.x + brick.width &&
                    ball.y + ball.radius > brick.y &&
                    ball.y - ball.radius < brick.y + brick.height) {
                    
                    // Determine collision side
                    const ballCenterX = ball.x;
                    const ballCenterY = ball.y;
                    const brickCenterX = brick.x + brick.width / 2;
                    const brickCenterY = brick.y + brick.height / 2;
                    
                    const dx = ballCenterX - brickCenterX;
                    const dy = ballCenterY - brickCenterY;
                    
                    if (Math.abs(dx) > Math.abs(dy)) {
                        ball.dx = -ball.dx;
                    } else {
                        ball.dy = -ball.dy;
                    }
                    
                    brick.visible = false;
                    score += brick.points;
                    scoreElement.textContent = score;
                    
                    // Create particles
                    createParticles(brick.x + brick.width / 2, brick.y + brick.height / 2, brick.color, 15);
                    
                    // Chance to drop power-up (increased from 15% to 25%)
                    if (Math.random() < 0.25) {
                        // Randomly choose power-up type
            const powerUp = new PowerUp(brick.x + brick.width / 2, brick.y + brick.height / 2);
            powerUp.type = Math.random() < 0.6 ? 'expand' : 'multiply'; // 60% expand, 40% extra life
            powerUps.push(powerUp);
                    }
                    
                    // Check if all bricks destroyed
                    const allDestroyed = bricks.every(row => row.every(b => !b.visible));
                    if (allDestroyed) {
                        levelComplete();
                    }
                }
            }
        });
    });
    
    // Ball lost
    if (ball.y > canvas.height) {
        lives--;
        livesElement.textContent = lives;
        
        if (lives <= 0) {
            gameOver();
        } else {
            resetBall();
        }
    }
}

function resetBall() {
    ball.x = paddle.x + paddle.width / 2;
    ball.y = canvas.height - 50;
    ball.dx = 0;
    ball.dy = 0;
    ball.launched = false;
}

function launchBall() {
    if (!ball.launched) {
        // More controlled launch - less random, more upward
        const angle = (Math.random() - 0.5) * Math.PI / 4; // Reduced from PI/3 to PI/4
        ball.dx = Math.sin(angle) * ball.speed;
        ball.dy = -Math.abs(Math.cos(angle) * ball.speed);
        // Ensure minimum upward velocity
        if (ball.dy > -2) {
            ball.dy = -2.5;
        }
        ball.launched = true;
    }
}

function levelComplete() {
    gameRunning = false;
    cancelAnimationFrame(animationId);
    level++;
    levelElement.textContent = level;
    // Slower speed increase per level
    ball.speed = 3.5 + level * 0.3;
    
    levelCompleteDiv.classList.remove('hidden');
    
    setTimeout(() => {
        levelCompleteDiv.classList.add('hidden');
        createBricks();
        resetBall();
        gameRunning = true;
        gameLoop();
    }, 2000);
}

function gameOver() {
    gameRunning = false;
    cancelAnimationFrame(animationId);
    
    if (score > highScore) {
        highScore = score;
        highScoreElement.textContent = highScore;
        localStorage.setItem('breakoutHighScore', highScore);
    }
    
    finalScoreElement.textContent = score;
    finalLevelElement.textContent = level;
    gameOverDiv.classList.remove('hidden');
}

function resetGame() {
    score = 0;
    lives = 5;
    level = 1;
    scoreElement.textContent = score;
    livesElement.textContent = lives;
    levelElement.textContent = level;
    ball.speed = 3.5;
    paddle.width = 200;
    powerUps = [];
    particles = [];
    powerUpText.textContent = '';
    
    createBricks();
    resetBall();
    gameOverDiv.classList.add('hidden');
    levelCompleteDiv.classList.add('hidden');
}

function draw() {
    // Clear canvas with dark background
    ctx.fillStyle = '#0a0e27';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid pattern
    ctx.strokeStyle = 'rgba(102, 126, 234, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 40) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 40) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
    }
    
    drawBricks();
    drawPaddle();
    drawBall();
    drawParticles();
    drawPowerUps();
}

function update() {
    if (!gameRunning || gamePaused) return;
    
    movePaddle();
    moveBall();
    updateParticles();
    updatePowerUps();
}

function gameLoop() {
    update();
    draw();
    if (gameRunning) {
        animationId = requestAnimationFrame(gameLoop);
    }
}

// Controls
const keys = {};

document.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
    
    if (e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        if (gameRunning && !gamePaused) {
            launchBall();
        }
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});

function handleInput() {
    if (keys['arrowleft'] || keys['a']) {
        paddle.dx = -paddle.speed;
    } else if (keys['arrowright'] || keys['d']) {
        paddle.dx = paddle.speed;
    } else {
        paddle.dx = 0;
    }
}

setInterval(() => {
    if (gameRunning && !gamePaused) {
        handleInput();
    }
}, 16);

// Button handlers
startBtn.addEventListener('click', () => {
    if (!gameRunning) {
        resetGame();
        gameRunning = true;
        gameLoop();
        startBtn.textContent = 'Restart';
    } else {
        resetGame();
        gameRunning = true;
        gameLoop();
    }
});

pauseBtn.addEventListener('click', () => {
    if (gameRunning && !gamePaused) {
        gamePaused = true;
        pauseBtn.textContent = 'Resume';
    } else if (gameRunning && gamePaused) {
        gamePaused = false;
        pauseBtn.textContent = 'Pause';
        gameLoop();
    }
});

restartBtn.addEventListener('click', () => {
    resetGame();
    gameRunning = true;
    gameLoop();
});

// Initialize
highScoreElement.textContent = highScore;
createBricks();
draw();
