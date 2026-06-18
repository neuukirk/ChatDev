/* BEATGRID front-end: Web Audio synthesis + a 4-lane falling-note rhythm game.
 * The same track data (BPM + 16-step patterns) drives both the audio and the
 * note chart, so music and gameplay stay locked together. No audio files. */

const BEATGRID = (function () {
  let ctx = null;
  function audio() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    return ctx;
  }

  // ---- noise helper ----
  let noiseBuf = null;
  function noise() {
    const ac = audio();
    if (!noiseBuf) {
      noiseBuf = ac.createBuffer(1, ac.sampleRate * 1, ac.sampleRate);
      const d = noiseBuf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    }
    const src = ac.createBufferSource();
    src.buffer = noiseBuf;
    return src;
  }

  // ---- voices ----
  function kick(t) {
    const ac = audio();
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.setValueAtTime(150, t);
    o.frequency.exponentialRampToValueAtTime(50, t + 0.12);
    g.gain.setValueAtTime(0.9, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
    o.connect(g).connect(ac.destination);
    o.start(t); o.stop(t + 0.2);
  }
  function snare(t) {
    const ac = audio();
    const n = noise(), hp = ac.createBiquadFilter(), g = ac.createGain();
    hp.type = "highpass"; hp.frequency.value = 1200;
    g.gain.setValueAtTime(0.6, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
    n.connect(hp).connect(g).connect(ac.destination);
    n.start(t); n.stop(t + 0.16);
    const o = ac.createOscillator(), g2 = ac.createGain();
    o.type = "triangle"; o.frequency.value = 180;
    g2.gain.setValueAtTime(0.3, t);
    g2.gain.exponentialRampToValueAtTime(0.001, t + 0.1);
    o.connect(g2).connect(ac.destination);
    o.start(t); o.stop(t + 0.1);
  }
  function hat(t) {
    const ac = audio();
    const n = noise(), hp = ac.createBiquadFilter(), g = ac.createGain();
    hp.type = "highpass"; hp.frequency.value = 7000;
    g.gain.setValueAtTime(0.3, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
    n.connect(hp).connect(g).connect(ac.destination);
    n.start(t); n.stop(t + 0.06);
  }
  function bass(t, semi, dur, rootHz) {
    const ac = audio();
    const o = ac.createOscillator(), lp = ac.createBiquadFilter(), g = ac.createGain();
    o.type = "sawtooth";
    o.frequency.value = rootHz * Math.pow(2, semi / 12) * 2; // up an octave to sit in the mix
    lp.type = "lowpass"; lp.frequency.value = 900;
    const d = Math.min(dur, 0.26);
    g.gain.setValueAtTime(0.5, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + d);
    o.connect(lp).connect(g).connect(ac.destination);
    o.start(t); o.stop(t + d + 0.02);
  }

  function stepDur(bpm) { return (60 / bpm) / 4; } // 16th note

  // lane 0 kick, 1 snare, 2 bass, 3 hat
  function buildEvents(d) {
    const sd = stepDur(d.bpm);
    const p = d.patterns;
    const events = [];
    for (let bar = 0; bar < d.bars; bar++) {
      for (let s = 0; s < d.steps; s++) {
        const t = (bar * d.steps + s) * sd;
        if (p.kick[s] === 1) events.push({ time: t, lane: 0 });
        if (p.snare[s] === 1) events.push({ time: t, lane: 1 });
        if (p.bass[s] !== -1) events.push({ time: t, lane: 2, semi: p.bass[s] });
        if (p.hat[s] === 1) events.push({ time: t, lane: 3 });
      }
    }
    events.sort((a, b) => a.time - b.time);
    const duration = d.bars * d.steps * sd;
    return { events, duration, sd };
  }

  function scheduleAudio(startT, events, rootHz, sd) {
    for (const e of events) {
      const t = startT + e.time;
      if (e.lane === 0) kick(t);
      else if (e.lane === 1) snare(t);
      else if (e.lane === 2) bass(t, e.semi, sd * 2, rootHz);
      else hat(t);
    }
  }

  const LANE_KEYS = { KeyD: 0, KeyF: 1, KeyJ: 2, KeyK: 3 };
  const LANE_COLORS = ["#00eaff", "#ff2db5", "#39ff88", "#ffd23f"];
  const LANE_LABELS = ["D", "F", "J", "K"];
  const TRAVEL = 1.9; // seconds a note is visible before the hit line

  function initGame(d, mountId) {
    const mount = document.getElementById(mountId);
    mount.innerHTML = "";
    const meta = document.getElementById("track-meta");
    if (meta) meta.textContent =
      `${d.track_name} · ${d.bpm} BPM · from "${d.pack_name}"`;

    const cs = document.getElementById("crosssell");
    if (cs) cs.innerHTML =
      `Like this beat? <a href="/shop/${d.pack_id}">Get “${d.pack_name}” in the Sound Shop →</a>`;

    const start = document.createElement("button");
    start.className = "btn big";
    start.textContent = d.ranked === false ? `▶ Play ${d.track_name}` : "▶ Play today's beat";
    mount.appendChild(start);

    const help = document.createElement("p");
    help.className = "help";
    help.textContent = "Hit D F J K (or tap the lanes) when notes reach the line.";
    mount.appendChild(help);

    start.addEventListener("click", () => run(d, mount));
  }

  function run(d, mount) {
    mount.innerHTML = "";
    const canvas = document.createElement("canvas");
    const W = Math.min(mount.clientWidth || 480, 480), H = 560;
    canvas.width = W; canvas.height = H;
    canvas.className = "stage";
    mount.appendChild(canvas);
    const g = canvas.getContext("2d");
    const laneW = W / 4, hitY = H - 90;

    const { events, duration, sd } = buildEvents(d);
    events.forEach(e => { e.judged = false; });

    let score = 0, combo = 0, maxCombo = 0;
    const counts = { Perfect: 0, Good: 0, Ok: 0, Miss: 0 };
    const flashes = [0, 0, 0, 0];
    const judgements = [];

    const ac = audio();
    const startAt = ac.currentTime + 1.2; // lead-in
    scheduleAudio(startAt, events, d.root_hz, sd);

    function songTime() { return ac.currentTime - startAt; }

    function judge(lane) {
      const now = songTime();
      let best = null, bestDiff = 1e9;
      for (const e of events) {
        if (e.lane !== lane || e.judged) continue;
        const diff = Math.abs(e.time - now);
        if (diff < bestDiff) { bestDiff = diff; best = e; }
      }
      if (!best || bestDiff > 0.18) return;
      best.judged = true;
      let label;
      if (bestDiff <= 0.06) { score += 100; combo++; counts.Perfect++; label = "Perfect"; }
      else if (bestDiff <= 0.12) { score += 60; combo++; counts.Good++; label = "Good"; }
      else { score += 30; combo++; counts.Ok++; label = "Ok"; }
      maxCombo = Math.max(maxCombo, combo);
      judgements.push(label);
      flashes[lane] = 1;
    }

    function hitLane(lane) { flashes[lane] = Math.max(flashes[lane], 0.6); judge(lane); }

    function onKey(ev) {
      if (ev.code in LANE_KEYS) { ev.preventDefault(); hitLane(LANE_KEYS[ev.code]); }
    }
    window.addEventListener("keydown", onKey);
    canvas.addEventListener("pointerdown", (ev) => {
      const r = canvas.getBoundingClientRect();
      const x = (ev.clientX - r.left) * (W / r.width);
      hitLane(Math.max(0, Math.min(3, Math.floor(x / laneW))));
    });

    let done = false;
    function frame() {
      const now = songTime();
      // expire missed notes
      for (const e of events) {
        if (!e.judged && e.time < now - 0.18) {
          e.judged = true; counts.Miss++; combo = 0;
          judgements.push("Miss");
        }
      }
      // draw
      g.fillStyle = "#0b0420"; g.fillRect(0, 0, W, H);
      for (let l = 0; l < 4; l++) {
        g.fillStyle = l % 2 ? "rgba(255,255,255,0.02)" : "rgba(255,255,255,0.04)";
        g.fillRect(l * laneW, 0, laneW, H);
      }
      // hit line
      g.fillStyle = "rgba(255,255,255,0.25)";
      g.fillRect(0, hitY, W, 3);
      for (let l = 0; l < 4; l++) {
        if (flashes[l] > 0) {
          g.fillStyle = LANE_COLORS[l];
          g.globalAlpha = flashes[l];
          g.fillRect(l * laneW + 4, hitY - 6, laneW - 8, 14);
          g.globalAlpha = 1;
          flashes[l] = Math.max(0, flashes[l] - 0.08);
        }
        g.fillStyle = "rgba(255,255,255,0.5)";
        g.font = "bold 18px monospace";
        g.textAlign = "center";
        g.fillText(LANE_LABELS[l], l * laneW + laneW / 2, H - 30);
      }
      // notes
      for (const e of events) {
        if (e.judged) continue;
        const dt = e.time - now;
        if (dt > TRAVEL || dt < -0.2) continue;
        const y = hitY - (dt / TRAVEL) * hitY;
        g.fillStyle = LANE_COLORS[e.lane];
        const x = e.lane * laneW + 8;
        g.fillRect(x, y - 9, laneW - 16, 18);
      }
      // hud
      g.fillStyle = "#f3e9ff";
      g.font = "bold 20px monospace";
      g.textAlign = "left";
      g.fillText("SCORE " + score, 12, 28);
      g.textAlign = "right";
      g.fillText("COMBO " + combo, W - 12, 28);

      if (now > duration + 1) {
        if (!done) { done = true; window.removeEventListener("keydown", onKey); end(); }
        return;
      }
      requestAnimationFrame(frame);
    }

    function end() {
      const total = events.length;
      const acc = total ? Math.round((score / (total * 100)) * 100) : 0;
      const grade = acc >= 95 ? "S" : acc >= 85 ? "A" : acc >= 70 ? "B" : acc >= 50 ? "C" : "D";
      const share = shareText(d, score, acc, maxCombo, grade, judgements);
      const ranked = d.ranked !== false;
      const saved = (localStorage.getItem("bg_initials") || "AAA").toUpperCase();
      const qs = `grade=${grade}&score=${score}&acc=${acc}&combo=${maxCombo}` +
        `&initials=${encodeURIComponent(saved)}&day=${d.day}` +
        `&track=${encodeURIComponent(d.track_name)}`;
      const cardUrl = `/share-card.png?${qs}`;
      const resultUrl = `${location.origin}/result?${qs}`;
      const rankedBlock = ranked ? `
          <div class="submit-row">
            <input id="initials" maxlength="3" value="${saved}" placeholder="AAA">
            <button class="btn" id="submit">Submit score</button>
          </div>
          <div id="board"></div>` : `<p class="counts">Free play — not ranked.</p>`;
      mount.innerHTML = `
        <div class="result">
          <div class="grade grade-${grade}">${grade}</div>
          <h2>${acc}% accuracy</h2>
          <p class="sub">Score ${score} · Max combo ${maxCombo}</p>
          <p class="counts">Perfect ${counts.Perfect} · Good ${counts.Good} · Ok ${counts.Ok} · Miss ${counts.Miss}</p>
          ${rankedBlock}
          <pre class="share" id="share">${share}</pre>
          <div class="actions">
            <button class="btn" id="copylink">Copy share link</button>
            <a class="btn ghost" href="${cardUrl}" download="beatgrid-${d.day}.png">Download card</a>
            <button class="btn ghost" id="again">Play again</button>
            <a class="btn ghost" href="/shop/${d.pack_id}">Get the pack</a>
          </div>
        </div>`;

      document.getElementById("again").onclick = () => run(d, mount);
      document.getElementById("copylink").onclick = () => {
        navigator.clipboard && navigator.clipboard.writeText(resultUrl);
        document.getElementById("copylink").textContent = "Link copied!";
      };
      if (ranked) {
        const initEl = document.getElementById("initials");
        initEl.addEventListener("input", () => {
          initEl.value = initEl.value.replace(/[^A-Za-z]/g, "").toUpperCase().slice(0, 3);
        });
        document.getElementById("submit").onclick = async () => {
          const initials = (initEl.value || "AAA").toUpperCase();
          localStorage.setItem("bg_initials", initials);
          try {
            const res = await fetch("/api/score", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ initials, score, accuracy: acc, combo: maxCombo, grade }),
            });
            const data = await res.json();
            renderBoard(data.leaderboard, data.rank, data.players);
          } catch (e) { /* offline: leave board empty */ }
        };
        loadBoard();
      }
    }

    async function loadBoard() {
      try {
        const res = await fetch("/api/leaderboard");
        const data = await res.json();
        renderBoard(data.leaderboard, null, data.players);
      } catch (e) { /* ignore */ }
    }

    function renderBoard(list, rank, players) {
      const board = document.getElementById("board");
      if (!board) return;
      if (!list || !list.length) {
        board.innerHTML = `<p class="counts">Be the first on today's board.</p>`;
        return;
      }
      const rows = list.map((r, i) =>
        `<li><span class="pos">${i + 1}</span><span class="ini">${r.initials}</span>` +
        `<span class="sc">${r.score}</span><span class="gr grade-${r.grade}">${r.grade}</span></li>`
      ).join("");
      board.innerHTML =
        `<h3 class="board-title">Today's Top Players${players ? " · " + players + " played" : ""}</h3>` +
        `<ol class="board">${rows}</ol>` +
        (rank ? `<p class="rank">Your rank: #${rank}</p>` : "");
    }

    requestAnimationFrame(frame);
  }

  function shareText(d, score, acc, maxCombo, grade, judgements) {
    const emoji = { Perfect: "🟪", Good: "🟦", Ok: "🟨", Miss: "⬛" };
    let bar = "";
    const stepN = Math.max(1, Math.floor(judgements.length / 16));
    for (let i = 0; i < judgements.length && bar.length < 16; i += stepN) {
      bar += emoji[judgements[i]] || "⬛";
    }
    return `BEATGRID #${d.day} — ${d.track_name}\n` +
      `${grade}  ${acc}%  combo ${maxCombo}\n${bar}\nbeatgrid.play`;
  }

  // ---- shop preview ----
  let previewNodes = [];
  function initPackPreview() {
    const pack = window.BEATGRID_PACK;
    if (!pack) return;
    document.querySelectorAll(".play-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const t = pack.tracks[parseInt(btn.dataset.track, 10)];
        const d = {
          bpm: t.bpm, bars: 4, steps: 16, root_hz: 55,
          patterns: { kick: t.kick, snare: t.snare, hat: t.hat, bass: t.bass },
        };
        const { events, sd } = buildEvents(d);
        const ac = audio();
        scheduleAudio(ac.currentTime + 0.1, events, d.root_hz, sd);
        btn.textContent = "♪";
        setTimeout(() => { btn.textContent = "▶"; }, d.bars * 16 * sd * 1000);
      });
    });
  }

  function initArcade() {
    const cat = window.BEATGRID_CATALOG;
    if (!cat) return;
    document.querySelectorAll(".arcade-play").forEach((btn) => {
      btn.addEventListener("click", () => {
        const pack = cat.packs.find((p) => p.id === btn.dataset.pack);
        if (!pack) return;
        const t = pack.tracks[parseInt(btn.dataset.track, 10)];
        const d = {
          track_name: t.name, pack_id: pack.id, pack_name: pack.name,
          bpm: t.bpm, bars: t.bars, steps: cat.steps, root_hz: cat.root_hz,
          day: 0, ranked: false,
          patterns: { kick: t.kick, snare: t.snare, hat: t.hat, bass: t.bass },
        };
        initGame(d, "game");
        document.getElementById("game").scrollIntoView({ behavior: "smooth" });
      });
    });
  }

  return { initPackPreview, initGame, initArcade };
})();

if (window.BEATGRID_DAILY) {
  BEATGRID.initGame(window.BEATGRID_DAILY, "game");
}
