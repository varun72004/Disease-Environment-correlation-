import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Animated Chest", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>3D Chest</title>
<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  transform-style: preserve-3d;
}

:root {
  --bg: hsl(210, 32%, 80%);
  --height: 30;
  --width: 20;
  --depth: 15;
  --frame: 1;
  --drawer-one: hsl(0, 0%, 98%);
  --drawer-two: hsl(0, 0%, 90%);
  --drawer-three: hsl(0, 0%, 95%);
  --unit-two: hsl(10, 0%, 40%);
  --unit-three: hsl(10, 0%, 20%);
  --unit-four: hsl(10, 0%, 15%);
  --transition: 0.4s ease;
}

body {
  background: var(--bg);
  display: grid;
  place-items: center;
  min-height: 100vh;
  perspective: 200vmin;
  transform: scale(1.5);
}

.chest {
  height: calc(var(--height) * 1vmin);
  width: calc(var(--width) * 1vmin);
  position: relative;
  transform: translate3d(0, 0, 50vmin) rotateX(-32deg) rotateY(40deg);
}

/* Panels */
.chest__panel {
  position: absolute;
}
.chest__panel--front, .chest__panel--back {
  height: 100%;
  width: 100%;
  background: var(--unit-two);
  transform: translate3d(0, 0, calc(var(--depth) * var(--coef)));
}
.chest__panel--front { --coef: 0.5vmin; }
.chest__panel--back { --coef: -0.5vmin; }
.chest__panel--left, .chest__panel--right {
  height: 100%;
  width: calc(var(--depth) * 1vmin);
  background: var(--unit-three);
  left: 50%;
  transform: translate(-50%, 0) rotateY(90deg) translate3d(0, 0, calc(var(--width) * var(--coef)));
}
.chest__panel--right { --coef: 0.5vmin; }
.chest__panel--left { --coef: -0.5vmin; }
.chest__panel--top, .chest__panel--bottom {
  width: calc(var(--width) * 1vmin);
  background: var(--unit-two);
}
.chest__panel--top {
  height: calc(var(--depth) * 1vmin);
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%) rotateX(-90deg);
}
.chest__panel--bottom {
  height: calc(var(--depth) * 1vmin);
  bottom: 0;
  transform: translate(0, 50%) rotateX(-90deg);
}

/* Drawers */
.chest__drawer {
  --drawer-height: calc((var(--height) - (5 * var(--frame))) / 3);
  position: absolute;
  left: 50%;
  height: calc(var(--drawer-height) * 1vmin);
  width: calc((var(--width) - (2 * var(--frame))) * 1vmin);
  transform: translate3d(-50%, 0, calc(var(--depth) * 0.5vmin));
}
.chest__drawer[data-position="1"] { top: calc(var(--frame) * 1vmin); }
.chest__drawer[data-position="2"] { top: calc(((2 * var(--frame)) + var(--drawer-height)) * 1vmin); }
.chest__drawer[data-position="3"] { top: calc(((3 * var(--frame)) + (2 * var(--drawer-height))) * 1vmin); }

.drawer__structure {
  height: 100%;
  width: 100%;
  position: absolute;
  transition: transform var(--transition);
}
.drawer__structure.open {
  transform: translate3d(0, 0, calc(var(--depth) * 1vmin));
}

/* Drawer panels */
.drawer__panel {
  position: absolute;
}
.drawer__panel--left, .drawer__panel--right {
  width: calc(var(--depth) * 1vmin);
  height: 100%;
  background: var(--drawer-two);
}
.drawer__panel--left {
  left: 0;
  transform-origin: 0 50%;
  transform: rotateY(90deg);
}
.drawer__panel--right {
  right: 0;
  transform-origin: 100% 50%;
  transform: rotateY(-90deg);
}
.drawer__panel--front {
  width: 100%;
  height: 100%;
  background: var(--unit-four);
  position: relative;
}
.drawer__panel--bottom {
  position: absolute;
  height: calc(var(--depth) * 1vmin);
  width: 100%;
  background: var(--drawer-three);
  bottom: 0;
  left: 50%;
  transform-origin: top center;
  /* Drop inside drawer and push back behind front face */
  transform: translate3d(-50%, 100%,calc(var(--depth) * -1vmin)) rotateX(90deg) translateZ(1vmin) ;
  z-index: 1; /* keep behind text & front panel */
}


/* Text panel without animation delay */
.drawer__panel--back {
  position: absolute;
  height: 100%;
  width: 100%;
  color: red; 
  background: var(--drawer-one);
  bottom: 0;
  left: 50%;
  transform: translate3d(-50%, 0, calc(var(--depth) * -1vmin));
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 0.5vmin;
  font-size: 3vmin;
  font-family: sans-serif;
  font-weight: bold;
  z-index: 6; /* Ensure text always on top */
transform: translate3d(-50%, 0, -15vmin);
}

/* Drawer handles */
.drawer__handle {
  position: absolute;
  top: 35%;
  left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 8%;
  background: hsl(0, 0%, 80%);
  border-radius: 2px;
}

/* Letters animation */
.letter {
  display: inline-block;
  animation: wave 1s infinite ease-in-out;
}
/* Rainbow colors for Awesome */
.letter:nth-of-type(1) { color: hsl(15, 80%, 50%); }
.letter:nth-of-type(2) { color: hsl(35, 80%, 50%); }
.letter:nth-of-type(3) { color: hsl(45, 80%, 50%); }
.letter:nth-of-type(4) { color: hsl(90, 80%, 50%); }
.letter:nth-of-type(5) { color: hsl(180, 80%, 50%); }
.letter:nth-of-type(6) { color: hsl(260, 80%, 50%); }
.letter:nth-of-type(7) { color: hsl(320, 80%, 50%); }

@keyframes wave {
  0%, 100% { transform: translateY(10%); }
  50% { transform: translateY(-10%); }
}
</style>
</head>
<body>
<div class="chest">
  <div class="chest__panel chest__panel--back"></div>
  <div class="chest__panel chest__panel--top"></div>
  <div class="chest__panel chest__panel--bottom"></div>
  <div class="chest__panel chest__panel--right"></div>
  <div class="chest__panel chest__panel--front"></div>
  <div class="chest__panel chest__panel--left"></div>

  <!-- Drawer 1 -->
  <div class="chest__drawer" data-position="1">
    <div class="drawer__structure">
      <div class="drawer__panel drawer__panel--back">Isn't</div>
      <div class="drawer__panel drawer__panel--bottom"></div>
      <div class="drawer__panel drawer__panel--right"></div>
      <div class="drawer__panel drawer__panel--left"></div>
      <div class="drawer__panel drawer__panel--front">
        <div class="drawer__handle"></div>
      </div>
    </div>
  </div>

  <!-- Drawer 2 -->
  <div class="chest__drawer" data-position="2">
    <div class="drawer__structure">
      <div class="drawer__panel drawer__panel--back">It</div>
      <div class="drawer__panel drawer__panel--bottom"></div>
      <div class="drawer__panel drawer__panel--right"></div>
      <div class="drawer__panel drawer__panel--left"></div>
      <div class="drawer__panel drawer__panel--front">
        <div class="drawer__handle"></div>
      </div>
    </div>
  </div>

  <!-- Drawer 3 -->
  <div class="chest__drawer" data-position="3">
    <div class="drawer__structure">
      <div class="drawer__panel drawer__panel--back">
        <span class="letter">A</span>
        <span class="letter">w</span>
        <span class="letter">e</span>
        <span class="letter">s</span>
        <span class="letter">o</span>
        <span class="letter">m</span>
        <span class="letter">e</span>
      </div>
      <div class="drawer__panel drawer__panel--bottom"></div>
      <div class="drawer__panel drawer__panel--right"></div>
      <div class="drawer__panel drawer__panel--left"></div>
      <div class="drawer__panel drawer__panel--front">
        <div class="drawer__handle"></div>
      </div>
    </div>
  </div>
</div>

<script>
document.querySelectorAll(".chest__drawer").forEach(drawer => {
  drawer.addEventListener("click", () => {
    drawer.querySelector(".drawer__structure").classList.toggle("open");
  });
});
</script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
