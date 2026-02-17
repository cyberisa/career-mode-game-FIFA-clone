const formationSlots = [
  { slot: "GK", x: 50, y: 92 },
  { slot: "LB", x: 18, y: 72 },
  { slot: "CB", x: 39, y: 74 },
  { slot: "CB", x: 61, y: 74 },
  { slot: "RB", x: 82, y: 72 },
  { slot: "CM", x: 24, y: 52 },
  { slot: "CM", x: 50, y: 49 },
  { slot: "CM", x: 76, y: 52 },
  { slot: "LW", x: 20, y: 24 },
  { slot: "ST", x: 50, y: 20 },
  { slot: "RW", x: 80, y: 24 },
];

const state = {
  budget: 180000000,
  chemistry: 84,
  points: 0,
  wins: 0,
  week: 1,
  squad: [
    { name: "Courtois", position: "GK", rating: 90, stamina: 90 },
    { name: "Mendy", position: "LB", rating: 83, stamina: 88 },
    { name: "Rudiger", position: "CB", rating: 86, stamina: 87 },
    { name: "Militao", position: "CB", rating: 85, stamina: 85 },
    { name: "Carvajal", position: "RB", rating: 84, stamina: 83 },
    { name: "Bellingham", position: "CM", rating: 88, stamina: 91 },
    { name: "Valverde", position: "CM", rating: 87, stamina: 90 },
    { name: "Camavinga", position: "CM", rating: 84, stamina: 89 },
    { name: "Vinicius Jr", position: "LW", rating: 89, stamina: 89 },
    { name: "Mbappe", position: "ST", rating: 91, stamina: 88 },
    { name: "Rodrygo", position: "RW", rating: 86, stamina: 87 },
  ],
  market: [
    ["Haaland", "ST", 91, 190000000], ["Wirtz", "CAM", 88, 125000000], ["Musiala", "CAM", 88, 131000000],
    ["Saka", "RW", 89, 142000000], ["Saliba", "CB", 87, 102000000], ["Bastoni", "CB", 87, 98000000],
    ["Theo Hernandez", "LB", 87, 89000000], ["Hakimi", "RB", 86, 83000000], ["Pedri", "CM", 88, 145000000],
    ["Rice", "CDM", 88, 138000000], ["Alvarez", "ST", 86, 97000000], ["Leao", "LW", 87, 116000000],
    ["Kvaratskhelia", "LW", 86, 99000000], ["Osimhen", "ST", 89, 149000000], ["Lautaro", "ST", 89, 135000000],
    ["Foden", "RW", 89, 148000000], ["Grimaldo", "LB", 85, 62000000], ["Frimpong", "RB", 84, 72000000],
    ["Tonali", "CM", 85, 88000000], ["Guimaraes", "CM", 86, 94000000], ["Gavi", "CM", 84, 78000000],
    ["Araujo", "CB", 88, 136000000], ["Diogo Costa", "GK", 85, 71000000], ["Maignan", "GK", 88, 93000000],
    ["Dimarco", "LB", 84, 55000000], ["Reece James", "RB", 84, 69000000], ["Nico Williams", "LW", 84, 76000000],
    ["Palmer", "RW", 85, 85000000], ["Xavi Simons", "CAM", 85, 79000000], ["Zubimendi", "CDM", 84, 67000000],
  ].map((p) => ({ name: p[0], position: p[1], rating: p[2], stamina: 84, price: p[3] })),
};

const clubs = ["Barcelona", "Atletico", "Sevilla", "Valencia", "Real Sociedad", "Villarreal", "Athletic", "Betis"];
const currency = new Intl.NumberFormat("en", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

const els = {
  budget: document.getElementById("budget"), chemistry: document.getElementById("chemistry"), rating: document.getElementById("squad-rating"),
  points: document.getElementById("points"), wins: document.getElementById("wins"), week: document.getElementById("week"),
  pitch: document.getElementById("pitch"), squadList: document.getElementById("squad-list"), marketList: document.getElementById("market-list"),
  tactic: document.getElementById("tactic"), playBtn: document.getElementById("play-match"), log: document.getElementById("match-log"),
  search: document.getElementById("market-search"),
};

function avgRating() {
  return Math.round(state.squad.reduce((sum, p) => sum + p.rating, 0) / state.squad.length);
}

function renderOverview() {
  els.budget.textContent = currency.format(state.budget);
  els.chemistry.textContent = `${state.chemistry}`;
  els.rating.textContent = `${avgRating()}`;
  els.points.textContent = `${state.points}`;
  els.wins.textContent = `${state.wins}`;
  els.week.textContent = `${state.week}/20`;
}

function renderPitch() {
  els.pitch.innerHTML = "";
  formationSlots.forEach((slot, idx) => {
    const player = state.squad[idx];
    const node = document.createElement("div");
    node.className = "pitch-player";
    node.style.left = `${slot.x}%`;
    node.style.top = `${slot.y}%`;
    node.innerHTML = `
      <div class="badge">${player.rating}</div>
      <div class="name">${player.name}</div>
      <div class="meta">${player.position} • STM ${player.stamina}</div>
    `;
    els.pitch.appendChild(node);
  });
}

function upgradePlayer(index) {
  const player = state.squad[index];
  const cost = 2500000;
  if (state.budget < cost) return setLog("Not enough budget for this upgrade.", false);
  if (player.rating >= 99) return setLog(`${player.name} is already maxed at 99.`, false);

  state.budget -= cost;
  player.rating = Math.min(99, player.rating + 2);
  player.stamina = Math.max(50, player.stamina - 4);
  state.chemistry = Math.min(99, state.chemistry + 1);
  setLog(`${player.name} upgraded quickly to ${player.rating} OVR (max 99).`);
  render();
}

function recoverPlayer(index) {
  const player = state.squad[index];
  player.stamina = Math.min(100, player.stamina + 12);
  setLog(`${player.name} recovered and is ready for the next match.`);
  render();
}

function buyPlayer(index) {
  const target = filteredMarket()[index];
  if (!target) return;
  if (state.budget < target.price) return setLog(`You cannot afford ${target.name}.`, false);

  const replaceIndex = state.squad.findIndex((p) => p.position === target.position || (target.position === "CAM" && p.position === "CM") || (target.position === "CDM" && p.position === "CM"));
  const idx = replaceIndex >= 0 ? replaceIndex : Math.floor(Math.random() * state.squad.length);
  const replaced = state.squad[idx];

  state.budget -= target.price;
  state.squad[idx] = { name: target.name, position: formationSlots[idx].slot, rating: target.rating, stamina: target.stamina };
  state.market = state.market.filter((p) => p.name !== target.name);
  state.chemistry = Math.min(99, state.chemistry + 2);

  setLog(`${target.name} signed for ${currency.format(target.price)}. ${replaced.name} loses spot in the XI.`);
  render();
}

function filteredMarket() {
  const q = els.search.value.trim().toLowerCase();
  if (!q) return state.market;
  return state.market.filter((p) => p.name.toLowerCase().includes(q) || p.position.toLowerCase().includes(q));
}

function renderSquad() {
  els.squadList.innerHTML = "";
  state.squad.forEach((p, index) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="row"><strong>${formationSlots[index].slot} • ${p.name}</strong><strong>${p.rating}</strong></div>
      <div class="meta">Stamina ${p.stamina} | Upgrade cost ${currency.format(2500000)}</div>
      <div class="row">
        <button data-action="upgrade" data-index="${index}">Quick Upgrade +2</button>
        <button data-action="recover" data-index="${index}">Recover</button>
      </div>
    `;
    els.squadList.appendChild(card);
  });
}

function renderMarket() {
  els.marketList.innerHTML = "";
  const players = filteredMarket();

  players.forEach((p, index) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="row"><strong>${p.name} (${p.position})</strong><strong>${p.rating}</strong></div>
      <div class="meta">Price ${currency.format(p.price)}</div>
      <button data-action="buy" data-index="${index}">Sign Player</button>
    `;
    els.marketList.appendChild(card);
  });
}

function playMatch() {
  if (state.week > 20) return setLog("Season ended. Refresh to start again.");

  const boost = { balanced: 0, "high-press": 2, counter: 1, possession: 2 }[els.tactic.value];
  const staminaFactor = Math.round(state.squad.reduce((s, p) => s + p.stamina, 0) / 16 / state.squad.length * 11);
  const power = avgRating() + boost + Math.round(state.chemistry / 20) + staminaFactor;
  const opponent = clubs[Math.floor(Math.random() * clubs.length)];
  const rival = 83 + Math.floor(Math.random() * 14);

  let result = "";
  if (power >= rival + 3) {
    result = `Huge win against ${opponent}!`;
    state.points += 3;
    state.wins += 1;
    state.budget += 6000000;
  } else if (power >= rival - 2) {
    result = `Draw against ${opponent}.`;
    state.points += 1;
    state.budget += 2200000;
  } else {
    result = `Loss against ${opponent}.`;
    state.chemistry = Math.max(60, state.chemistry - 2);
  }

  state.squad.forEach((p) => {
    p.stamina = Math.max(48, p.stamina - (els.tactic.value === "high-press" ? 8 : 5));
  });
  state.week += 1;

  setLog(`${result} Team power ${power} vs ${rival}.`, !result.startsWith("Loss"));
  render();
}

function setLog(msg, good = true) {
  els.log.innerHTML = `<span class="${good ? "good" : "bad"}">${msg}</span>`;
}

function render() {
  renderOverview();
  renderPitch();
  renderSquad();
  renderMarket();
}

document.body.addEventListener("click", (e) => {
  if (!(e.target instanceof HTMLElement)) return;
  const action = e.target.dataset.action;
  const index = Number(e.target.dataset.index);
  if (!action || Number.isNaN(index)) return;

  if (action === "upgrade") upgradePlayer(index);
  if (action === "recover") recoverPlayer(index);
  if (action === "buy") buyPlayer(index);
});

els.search.addEventListener("input", renderMarket);
els.playBtn.addEventListener("click", playMatch);

render();
setLog("Manager mode ready: build your elite XI and go win everything.");
