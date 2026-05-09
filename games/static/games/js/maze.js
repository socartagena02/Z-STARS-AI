const canvas = document.getElementById("mazeCanvas");
const ctx = canvas.getContext("2d");
const timerEl = document.getElementById("timer");
const messageEl = document.getElementById("message");
const checkpointCountEl = document.getElementById("CheckpointCount");
const CELL_SIZE = 80;

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

canvas.width = COLS * CELL_SIZE;
canvas.height = ROWS * CELL_SIZE;

const start = {
    row: 1,
    col: 1
};

const end = {
    row: 5,
    col: 5
};

const checkpoints = [
    { row: 1, col: 3, visited: false },
    { row: 5, col: 2, visited: false }
];

let drawing = false;
let gameOver = false;
let won = false;

let timeLeft = 60;
let timerInterval;

let trail = [];

function drawMaze() {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let row = 0; row < ROWS; row++) {

        for (let col = 0; col < COLS; col++) {

            const x = col * CELL_SIZE;
            const y = row * CELL_SIZE;

            if (maze[row][col] === 1) {
                ctx.fillStyle = "#1f2937";
            } else {
                ctx.fillStyle = "#e5e7eb";
            }

            ctx.fillRect(
                x,
                y,
                CELL_SIZE,
                CELL_SIZE
            );

            ctx.strokeStyle = "#d1d5db";

            ctx.strokeRect(
                x,
                y,
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
        "#ef4444"
    );

    checkpoints.forEach(cp => {

        drawCircle(
            cp.col,
            cp.row,
            cp.visited
                ? "#10b981"
                : "#f59e0b",
            12
        );
    });
}

function drawCircle(col, row, color, radius = 18) {

    ctx.beginPath();

    ctx.fillStyle = color;

    ctx.arc(
        col * CELL_SIZE + CELL_SIZE / 2,
        row * CELL_SIZE + CELL_SIZE / 2,
        radius,
        0,
        Math.PI * 2
    );

    ctx.fill();
}

function redrawTrail() {

    if (trail.length < 2) return;

    ctx.beginPath();

    ctx.moveTo(
        trail[0].x,
        trail[0].y
    );

    ctx.strokeStyle = "#537fc6";
    ctx.lineWidth = 14;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    for (let i = 1; i < trail.length; i++) {

        ctx.lineTo(
            trail[i].x,
            trail[i].y
        );
    }

    ctx.stroke();
}

function startTimer() {

    clearInterval(timerInterval);

    timerInterval = setInterval(() => {

        timeLeft--;

        timerEl.textContent = timeLeft;

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

    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

function startDrawing(e) {

    if (gameOver || won) return;

    drawing = true;
    trail = [];

    const { x, y } =
        getPosition(e);

    trail.push({ x, y });

    ctx.beginPath();

    ctx.moveTo(x, y);

    ctx.strokeStyle = "#537fc6";
    ctx.lineWidth = 14;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
}

function draw(e) {

    if (!drawing || gameOver || won)
        return;

    const { x, y } =
        getPosition(e);

    const row =
        Math.floor(y / CELL_SIZE);

    const col =
        Math.floor(x / CELL_SIZE);

    // OUTSIDE
    if (
        row < 0 ||
        col < 0 ||
        row >= ROWS ||
        col >= COLS
    ) {
        return;
    }

    if (maze[row][col] === 1) {

        endGame(
            false,
            "❌ Tocaste una pared"
        );

        return;
    }

    ctx.lineTo(x, y);
    ctx.stroke();

    trail.push({ x, y });

    checkpoints.forEach(cp => {

        if (
            row === cp.row &&
            col === cp.col &&
            !cp.visited
        ) {

            cp.visited = true;

            checkpointCountEl.textContent =
                checkpoints.filter(
                    c => c.visited
                ).length;

            drawMaze();
            redrawTrail();
        }
    });

    const allVisited =
        checkpoints.every(
            cp => cp.visited
        );

    if (
        row === end.row &&
        col === end.col &&
        allVisited
    ) {

        endGame(
            true,
            "🎉 ¡Nivel completado!"
        );
    }
}

function stopDrawing() {

    drawing = false;
}

function endGame(success, text) {

    clearInterval(timerInterval);

    drawing = false;

    if (success) {

        won = true;

        messageEl.className =
            "message success";

    } else {

        gameOver = true;

        messageEl.className =
            "message error";
    }

    messageEl.textContent = text;
}

function restartGame() {

    clearInterval(timerInterval);

    drawing = false;
    gameOver = false;
    won = false;

    timeLeft = 60;

    timerEl.textContent =
        timeLeft;

    messageEl.textContent = "";
    trail = [];

    checkpoints.forEach(cp => {

        cp.visited = false;
    });

    checkpointCountEl.textContent = "0";

    drawMaze();

    startTimer();
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

drawMaze();
startTimer();