const LEVELS = [
  {
    timeLimit: 60,
    cellSize: 80,
    maze: [
      [1,1,1,1,1,1,1],
      [1,0,0,0,1,0,1],
      [1,0,1,0,1,0,1],
      [1,0,1,0,0,0,1],
      [1,0,1,1,1,0,1],
      [1,0,0,0,0,0,1],
      [1,1,1,1,1,1,1]
    ],
    start: { row: 1, col: 1 },
    end:   { row: 5, col: 5 },
    checkpoints: [
      { row: 1, col: 3 },
      { row: 3, col: 3 }
    ]
  },
  {
    timeLimit: 50,
    cellSize: 70,
    maze: [
      [1,1,1,1,1,1,1,1,1],
      [1,0,0,0,0,0,0,0,1],
      [1,0,1,1,1,1,1,0,1],
      [1,0,1,0,0,0,1,0,1],
      [1,0,1,0,1,0,1,0,1],
      [1,0,1,0,0,0,1,0,1],
      [1,0,1,1,1,1,1,0,1],
      [1,0,0,0,0,0,0,0,1],
      [1,1,1,1,1,1,1,1,1]
    ],
    start: { row: 1, col: 1 },
    end:   { row: 7, col: 7 },

    checkpoints: [
      { row: 1, col: 6 },
      { row: 3, col: 4 },
      { row: 7, col: 2 }
    ]
  },

  {
    timeLimit: 70,
    cellSize: 60,
    maze: [
      [1,1,1,1,1,1,1,1,1,1,1],
      [1,0,0,0,1,0,0,0,1,0,1],
      [1,0,1,0,1,0,1,0,1,0,1],
      [1,0,1,0,0,0,1,0,0,0,1],
      [1,0,1,1,1,1,1,1,1,0,1],
      [1,0,0,0,0,0,0,0,0,0,1],
      [1,0,1,1,1,1,1,1,1,0,1],
      [1,0,0,0,1,0,0,0,1,0,1],
      [1,1,1,0,1,0,1,0,1,0,1],
      [1,0,0,0,0,0,1,0,0,0,1],
      [1,1,1,1,1,1,1,1,1,1,1]
    ],

    start: { row: 1, col: 1 },
    end:   { row: 9, col: 9 },

    checkpoints: [
      { row: 1, col: 7 },
      { row: 5, col: 5 },
      { row: 9, col: 3 }
    ]
  }
];

const PADDING_BY_LEVEL = [
  10,
  14,
  18
];

const canvas = document.getElementById("mazeCanvas");
const ctx = canvas.getContext("2d");
const timerEl = document.getElementById("timer");
const messageEl = document.getElementById("message");
const checkpointCountEl = document.getElementById("CheckpointCount");
const levelEl = document.getElementById("levelIndicator");
const CROSS_RADIUS = 10;
const CROSS_IGNORE_HEAD = 20;
let currentLevelIndex = 0;
let CELL_SIZE;
let maze;
let start;
let end;
let checkpoints;
let timeLimit;
let padding = 10;
let drawing = false;
let gameOver = false;
let won = false;
let timeLeft = 60;
let timerInterval;
let trail = [];

let startCX;
let startCY;

let pulseActive = true;
let pulseRadius;
let pulseDir;

let rafId = null;

function loadLevel(index) {

  const level = LEVELS[index];

  CELL_SIZE = level.cellSize;
  maze = level.maze;
  start = level.start;
  end = level.end;
  timeLimit = level.timeLimit;

  padding = PADDING_BY_LEVEL[index];

  canvas.width =
    maze[0].length * CELL_SIZE;

  canvas.height =
    maze.length * CELL_SIZE;

  startCX =
    start.col * CELL_SIZE +
    CELL_SIZE / 2;

  startCY =
    start.row * CELL_SIZE +
    CELL_SIZE / 2;

  checkpoints =
    level.checkpoints.map(cp => ({
      ...cp,
      visited: false
    }));

  checkpointCountEl.textContent = "0";

  document.getElementById(
    "checkpointTotal"
  ).textContent =
    checkpoints.length;

  if (levelEl) {

    levelEl.textContent =
      `Nivel ${index + 1} / ${LEVELS.length}`;
  }

  drawing = false;
  gameOver = false;
  won = false;

  timeLeft = timeLimit;

  trail = [];

  timerEl.textContent = timeLeft;

  messageEl.textContent = "";
  messageEl.className = "message";
}

function animatePulse() {
  if (!pulseActive) return;
  pulseRadius += pulseDir * 0.4;

  if (
    pulseRadius >
    startCX * 0.5
  ) {
    pulseDir = -1;
  }

  if (
    pulseRadius <
    CELL_SIZE * 0.22
  ) {
    pulseDir = 1;
  }

  drawMaze();
  redrawTrail();

  ctx.beginPath();

  ctx.arc(
    startCX,
    startCY,
    pulseRadius,
    0,
    Math.PI * 2
  );

  ctx.strokeStyle =
    "rgba(34,197,94,0.6)";

  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.font =
    `bold ${Math.max(10, CELL_SIZE * 0.16)}px system-ui`;

  ctx.fillStyle = "#15803d";
  ctx.textAlign = "center";

  ctx.fillText(
    "¡Empieza aquí!",
    startCX,
    startCY - CELL_SIZE * 0.5
  );

  rafId =
    requestAnimationFrame(
      animatePulse
    );
}

function stopPulse() {

  pulseActive = false;

  if (rafId) {

    cancelAnimationFrame(rafId);

    rafId = null;
  }
}

function startPulse() {

  pulseActive = true;

  pulseRadius =
    CELL_SIZE * 0.22;

  pulseDir = 1;

  animatePulse();
}

function drawMaze() {

  ctx.clearRect(
    0,
    0,
    canvas.width,
    canvas.height
  );

  for (
    let r = 0;
    r < maze.length;
    r++
  ) {

    for (
      let c = 0;
      c < maze[0].length;
      c++
    ) {

      ctx.fillStyle =
        maze[r][c] === 1
          ? "#1f2937"
          : "#e5e7eb";

      ctx.fillRect(
        c * CELL_SIZE,
        r * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
      );

      ctx.strokeStyle =
        "#d1d5db";

      ctx.strokeRect(
        c * CELL_SIZE,
        r * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
      );
    }
  }

  drawCircle(
    start.col,
    start.row,
    "#22c55e"
  );

  drawCircle(
    end.col,
    end.row,
    "#3b82f6"
  );

  checkpoints.forEach(cp => {

    drawCircle(
      cp.col,
      cp.row,
      cp.visited
        ? "#10b981"
        : "#f59e0b",
      CELL_SIZE * 0.15
    );
  });
}

function drawCircle(
  col,
  row,
  color,
  radius = null
) {

  radius =
    radius ??
    CELL_SIZE * 0.22;

  ctx.beginPath();
  ctx.fillStyle = color;
  ctx.arc(
    col * CELL_SIZE +
    CELL_SIZE / 2,

    row * CELL_SIZE +
    CELL_SIZE / 2,

    radius,
    0,
    Math.PI * 2
  );
  ctx.fill();
}

function redrawTrail() {
  if (trail.length < 2)
    return;

  ctx.beginPath();

  ctx.moveTo(
    trail[0].x,
    trail[0].y
  );

  ctx.strokeStyle =
    "#537fc6";

  ctx.lineWidth =
    CELL_SIZE * 0.17;

  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  for (
    let i = 1;
    i < trail.length;
    i++
  ) {

    ctx.lineTo(
      trail[i].x,
      trail[i].y
    );
  }

  ctx.stroke();
}

function fullRedraw() {
  drawMaze();
  redrawTrail();
}

function crossesOwnTrail(x, y) {

  const limit =
    trail.length -
    CROSS_IGNORE_HEAD;

  for (
    let i = 0;
    i < limit;
    i++
  ) {

    const dx =
      trail[i].x - x;

    const dy =
      trail[i].y - y;

    if (
      Math.sqrt(
        dx * dx +
        dy * dy
      ) < CROSS_RADIUS
    ) {
      return true;
    }
  }

  return false;
}

function startTimer() {

  clearInterval(
    timerInterval
  );

  timerInterval =
    setInterval(() => {

      timeLeft--;

      timerEl.textContent =
        timeLeft;

      if (timeLeft <= 0) {

        endGame(
          false,
          "⏱ Tiempo agotado"
        );
      }

    }, 1000);
}

function getPosition(e) {

  const rect =
    canvas.getBoundingClientRect();

  const scaleX =
    canvas.width /
    rect.width;

  const scaleY =
    canvas.height /
    rect.height;

  return {
    x:
      (e.clientX - rect.left)
      * scaleX,

    y:
      (e.clientY - rect.top)
      * scaleY
  };
}

function isStartPosition(x, y) {

  return (
    Math.sqrt(
      (x - startCX) ** 2 +
      (y - startCY) ** 2
    ) <
    CELL_SIZE * 0.37
  );
}

function startDrawing(e) {

  if (gameOver || won)
    return;

  const { x, y } =
    getPosition(e);

  if (
    !isStartPosition(x, y)
  ) {

    endGame(
      false,
      "❌ Debes comenzar desde el punto verde"
    );

    return;
  }

  drawing = true;

  trail = [{ x, y }];

  stopPulse();
  fullRedraw();
}

function draw(e) {

  if (
    !drawing ||
    gameOver ||
    won
  ) {
    return;
  }

  const { x, y } =
    getPosition(e);

  const prev =
    trail[trail.length - 1];

  const dx =
    x - prev.x;

  const dy =
    y - prev.y;

  const dist =
    Math.sqrt(
      dx * dx +
      dy * dy
    );

  const steps =
    Math.ceil(dist / 4);

  for (
    let i = 1;
    i <= steps;
    i++
  ) {

    const ix =
      prev.x +
      (dx * i) / steps;

    const iy =
      prev.y +
      (dy * i) / steps;

    const row =
      Math.floor(
        iy / CELL_SIZE
      );

    const col =
      Math.floor(
        ix / CELL_SIZE
      );

    const localX =
      ix % CELL_SIZE;

    const localY =
      iy % CELL_SIZE;

    if (
      row < 0 ||
      col < 0 ||
      row >= maze.length ||
      col >= maze[0].length
    ) {
      return;
    }

    if (
      maze[row][col] === 1
    ) {

      endGame(
        false,
        "❌ Tocaste una pared"
      );

      return;
    }

    if (
      localX < padding ||
      localX >
      CELL_SIZE - padding ||
      localY < padding ||
      localY >
      CELL_SIZE - padding
    ) {

      endGame(
        false,
        "❌ Tocaste el borde"
      );

      return;
    }

    if (
      crossesOwnTrail(
        ix,
        iy
      )
    ) {

      endGame(
        false,
        "❌ Cruzaste tu propio camino"
      );

      return;
    }

    trail.push({
      x: ix,
      y: iy
    });
  }

  fullRedraw();

  const lastRow =
    Math.floor(
      y / CELL_SIZE
    );

  const lastCol =
    Math.floor(
      x / CELL_SIZE
    );

  checkpoints.forEach(cp => {

    if (
      lastRow === cp.row &&
      lastCol === cp.col &&
      !cp.visited
    ) {

      cp.visited = true;

      checkpointCountEl.textContent =
        checkpoints.filter(
          c => c.visited
        ).length;

      fullRedraw();
    }
  });

  const allVisited =
    checkpoints.every(
      cp => cp.visited
    );

  if (
    lastRow === end.row &&
    lastCol === end.col &&
    allVisited
  ) {

    endGame(
      true,
      "🎉 ¡Nivel completado!"
    );
  }
}

function stopDrawing() {

  if (
    !won &&
    !gameOver
  ) {

    endGame(
      false,
      "❌ No puedes soltar el trazo"
    );
  }

  drawing = false;
}

function endGame(
  success,
  text
) {

  clearInterval(
    timerInterval
  );

  stopPulse();
  drawing = false;

  if (success) {
    won = true;

    messageEl.className =
      "message success";

    messageEl.textContent =
      text;

    if (
      currentLevelIndex + 1 <
      LEVELS.length
    ) {

      setTimeout(
        () => nextLevel(),
        1500
      );
    }

  } else {

    gameOver = true;

    messageEl.className =
      "message error";

    messageEl.textContent =
      text;
  }

  fullRedraw();
}

function nextLevel() {
  stopPulse();

  clearInterval(
    timerInterval
  );

  currentLevelIndex++;

  loadLevel(
    currentLevelIndex
  );

  startTimer();
  startPulse();
}

function restartGame() {

  stopPulse();

  clearInterval(
    timerInterval
  );

  currentLevelIndex = 0;
  loadLevel(0);
  startTimer();
  startPulse();
}

canvas.addEventListener(
  "pointerdown",
  startDrawing
);

canvas.addEventListener(
  "pointermove",
  draw
);

canvas.addEventListener(
  "pointerup",
  stopDrawing
);

canvas.addEventListener(
  "pointerleave",
  stopDrawing
);

loadLevel(0);
startTimer();
startPulse();