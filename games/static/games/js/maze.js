const canvas = document.getElementById("mazeCanvas");
const ctx = canvas.getContext("2d");
const timerEl = document.getElementById("timer");
const messageEl = document.getElementById("message");
const checkpointCountEl = document.getElementById("CheckpointCount");

const CELL_SIZE = 80;
const CROSS_RADIUS = 10;
const CROSS_IGNORE_HEAD = 20;

const maze = [
  [1,1,1,1,1,1,1],
  [1,0,0,0,1,0,1],
  [1,0,1,0,1,0,1],
  [1,0,1,0,0,0,1],
  [1,0,1,1,1,0,1],
  [1,0,0,0,0,0,1],
  [1,1,1,1,1,1,1]
];

const ROWS = maze.length;
const COLS = maze[0].length;

canvas.width  = COLS * CELL_SIZE;
canvas.height = ROWS * CELL_SIZE;

const start = { row: 1, col: 1 };
const end   = { row: 5, col: 5 };
const startCX = start.col * CELL_SIZE + CELL_SIZE / 2;
const startCY = start.row * CELL_SIZE + CELL_SIZE / 2;

let checkpoints = [];
function resetCheckpoints() {
  checkpoints = [
    { row: 1, col: 3, visited: false },
    { row: 3, col: 3, visited: false }
  ];
}
resetCheckpoints();

let drawing  = false;
let gameOver = false;
let won      = false;
let timeLeft = 60;
let timerInterval;
let trail = [];

let pulseActive = true;
let pulseRadius = 18;
let pulseDir    = 1;
let rafId       = null;

function animatePulse() {
  if (!pulseActive) return;
  pulseRadius += pulseDir * 0.4;
  if (pulseRadius > 34) pulseDir = -1;
  if (pulseRadius < 18) pulseDir =  1;

  drawMaze();
  redrawTrail();

  ctx.beginPath();
  ctx.arc(startCX, startCY, pulseRadius, 0, Math.PI * 2);
  ctx.strokeStyle = `rgba(34,197,94,${1 - (pulseRadius - 18) / 18})`;
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.font = "bold 13px system-ui";
  ctx.fillStyle = "#15803d";
  ctx.textAlign = "center";
  ctx.fillText("¡Empieza aquí!", startCX, startCY - 32);

  rafId = requestAnimationFrame(animatePulse);
}

function stopPulse() {
  pulseActive = false;
  if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
}

function startPulse() {
  pulseActive = true;
  pulseRadius = 18;
  pulseDir    = 1;
  animatePulse();
}

function drawMaze() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      ctx.fillStyle = maze[r][c] === 1 ? "#1f2937" : "#e5e7eb";
      ctx.fillRect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);
      ctx.strokeStyle = "#d1d5db";
      ctx.strokeRect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    }
  }
  drawCircle(start.col, start.row, "#22c55e");
  drawCircle(end.col,   end.row,   "#3b82f6");
  checkpoints.forEach(cp => {
    drawCircle(cp.col, cp.row, cp.visited ? "#10b981" : "#f59e0b", 12);
  });
}

function drawCircle(col, row, color, radius = 18) {
  ctx.beginPath();
  ctx.fillStyle = color;
  ctx.arc(
    col * CELL_SIZE + CELL_SIZE / 2,
    row * CELL_SIZE + CELL_SIZE / 2,
    radius, 0, Math.PI * 2
  );
  ctx.fill();
}

function redrawTrail() {
  if (trail.length < 2) return;
  ctx.beginPath();
  ctx.moveTo(trail[0].x, trail[0].y);
  ctx.strokeStyle = "#537fc6";
  ctx.lineWidth   = 14;
  ctx.lineCap     = "round";
  ctx.lineJoin    = "round";
  for (let i = 1; i < trail.length; i++) ctx.lineTo(trail[i].x, trail[i].y);
  ctx.stroke();
}

function fullRedraw() {
  drawMaze();
  redrawTrail();
}

function crossesOwnTrail(x, y) {
  const limit = trail.length - CROSS_IGNORE_HEAD;
  for (let i = 0; i < limit; i++) {
    const dx = trail[i].x - x;
    const dy = trail[i].y - y;
    if (Math.sqrt(dx * dx + dy * dy) < CROSS_RADIUS) return true;
  }
  return false;
}

function startTimer() {
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timeLeft--;
    timerEl.textContent = timeLeft;
    if (timeLeft <= 0) endGame(false, "⏱ Tiempo agotado");
  }, 1000);
}

function getPosition(e) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width  / rect.width;
  const scaleY = canvas.height / rect.height;
  return {
    x: (e.clientX - rect.left) * scaleX,
    y: (e.clientY - rect.top)  * scaleY
  };
}

function isStartPosition(x, y) {
  return Math.sqrt((x - startCX) ** 2 + (y - startCY) ** 2) < 30;
}

// ── Eventos ──────────────────────────────────────────────────────────────────
function startDrawing(e) {
  if (gameOver || won) return;
  const { x, y } = getPosition(e);
  if (!isStartPosition(x, y)) {
    endGame(false, "❌ Debes comenzar desde el punto verde");
    return;
  }
  drawing = true;
  trail   = [{ x, y }];
  stopPulse();
  fullRedraw();
}

function draw(e) {
  if (!drawing || gameOver || won) return;
  const { x, y } = getPosition(e);

  const row = Math.floor(y / CELL_SIZE);
  const col = Math.floor(x / CELL_SIZE);

  if (row < 0 || col < 0 || row >= ROWS || col >= COLS) return;

  if (maze[row][col] === 1) {
    endGame(false, "❌ Tocaste una pared"); return;
  }

  if (crossesOwnTrail(x, y)) {
    endGame(false, "❌ Cruzaste tu propio camino"); return;
  }

  trail.push({ x, y });
  fullRedraw();

  checkpoints.forEach(cp => {
    if (row === cp.row && col === cp.col && !cp.visited) {
      cp.visited = true;
      checkpointCountEl.textContent = checkpoints.filter(c => c.visited).length;
      fullRedraw();
    }
  });

  const allVisited = checkpoints.every(cp => cp.visited);
  if (row === end.row && col === end.col && allVisited) {
    endGame(true, "🎉 ¡Nivel completado!");
  }
}

function stopDrawing() {
  if (!won && !gameOver) endGame(false, "❌ No puedes soltar el trazo");
  drawing = false;
}

function endGame(success, text) {
  clearInterval(timerInterval);
  stopPulse();
  drawing = false;
  if (success) { won = true;      messageEl.className = "message success"; }
  else         { gameOver = true; messageEl.className = "message error"; }
  messageEl.textContent = text;
  fullRedraw();
}

function restartGame() {
  clearInterval(timerInterval);
  stopPulse();
  drawing = false; gameOver = false; won = false;
  timeLeft = 60;
  timerEl.textContent   = timeLeft;
  messageEl.textContent = "";
  trail = [];
  resetCheckpoints();
  checkpointCountEl.textContent = "0";
  startTimer();
  startPulse();
}

canvas.addEventListener("pointerdown",  startDrawing);
canvas.addEventListener("pointermove",  draw);
canvas.addEventListener("pointerup",    stopDrawing);
canvas.addEventListener("pointerleave", stopDrawing);

startTimer();
startPulse();