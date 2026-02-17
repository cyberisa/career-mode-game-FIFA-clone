const formation = [
  { role: "GK", x: 50, y: 91 },
  { role: "LB", x: 18, y: 73 },
  { role: "CB", x: 38, y: 75 },
  { role: "CB", x: 62, y: 75 },
  { role: "RB", x: 82, y: 73 },
  { role: "CM", x: 22, y: 52 },
  { role: "CM", x: 50, y: 48 },
  { role: "CM", x: 78, y: 52 },
  { role: "LW", x: 20, y: 24 },
  { role: "ST", x: 50, y: 20 },
  { role: "RW", x: 80, y: 24 },
];

const laLigaTeams = [
  "Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Club", "Real Sociedad", "Real Betis", "Sevilla", "Valencia",
  "Villarreal", "Getafe", "Celta Vigo", "Osasuna", "Rayo Vallecano", "Mallorca", "Girona", "Las Palmas", "Alaves",
  "Espanyol", "Leganes", "Valladolid",
];

const playerPool = [
  ["Erling Haaland", "ST", 91, 190000000], ["Lautaro Martinez", "ST", 89, 132000000], ["Victor Osimhen", "ST", 89, 146000000],
  ["Julian Alvarez", "ST", 86, 98000000], ["Mohamed Salah", "RW", 89, 98000000], ["Bukayo Saka", "RW", 89, 145000000],
  ["Phil Foden", "RW", 89, 150000000], ["Jamal Musiala", "CAM", 88, 134000000], ["Florian Wirtz", "CAM", 88, 126000000],
  ["Pedri", "CM", 88, 143000000], ["Gavi", "CM", 84, 79000000], ["Bruno Guimaraes", "CM", 86, 95000000],
  ["Sandro Tonali", "CM", 85, 88000000], ["Declan Rice", "CDM", 88, 140000000], ["Martin Zubimendi", "CDM", 84, 68000000],
  ["Khvicha Kvaratskhelia", "LW", 86, 99000000], ["Rafael Leao", "LW", 87, 118000000], ["Nico Williams", "LW", 84, 77000000],
  ["Theo Hernandez", "LB", 87, 90000000], ["Federico Dimarco", "LB", 84, 56000000], ["Alphonso Davies", "LB", 86, 87000000],
  ["Achraf Hakimi", "RB", 86, 84000000], ["Jeremie Frimpong", "RB", 84, 73000000], ["Reece James", "RB", 84, 70000000],
  ["William Saliba", "CB", 87, 104000000], ["Ronald Araujo", "CB", 88, 136000000], ["Alessandro Bastoni", "CB", 87, 98000000],
  ["Ruben Dias", "CB", 89, 121000000], ["Mike Maignan", "GK", 88, 94000000], ["Diogo Costa", "GK", 85, 72000000],
  ["Gregor Kobel", "GK", 85, 69000000], ["Cole Palmer", "RW", 85, 86000000], ["Xavi Simons", "CAM", 85, 81000000],
  ["Gabriel Martinelli", "LW", 85, 88000000], ["Gabriel Jesus", "ST", 84, 70000000], ["Rodri", "CDM", 91, 157000000],
  ["Valentin Barco", "LB", 80, 39000000], ["Jules Kounde", "CB", 85, 86000000], ["Joao Neves", "CM", 82, 56000000],
].map(([name, position, rating, price]) => ({
  name,
  position,
  rating,
  price,
  stamina: 84,
  image: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=0D1117&color=fff&size=128`,
}));

const state = {
  season: 1,
  matchday: 1,
  budget: 230000000,
  chemistry: 82,
  squad: [
    ["Thibaut Courtois", "GK", 90], ["Ferland Mendy", "LB", 83], ["Antonio Rudiger", "CB", 86], ["Eder Militao", "CB", 85],
    ["Dani Carvajal", "RB", 84], ["Jude Bellingham", "CM", 88], ["Federico Valverde", "CM", 87], ["Eduardo Camavinga", "CM", 84],
    ["Vinicius Jr", "LW", 89], ["Kylian Mbappe", "ST", 91], ["Rodrygo", "RW", 86],
  ].map(([name, position, rating]) => ({
    name,
    position,
    rating,
    stamina: 88,
    morale: 82,
    image: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=fff&color=111&size=128`,
  })),
  market: playerPool,
  table: {},
};

const el = {
  budget: document.getElementById("budget"),
  clubRating: document.getElementById("club-rating"),
  chemistry: document.getElementById("chemistry"),
  position: document.getElementById("table-position"),
  matchday: document.getElementById("matchday"),
  nextOpponent: document.getElementById("next-opponent"),
  seasonChip: document.getElementById("season-chip"),
  pitch: document.getElementById("pitch"),
  squadList: document.getElementById("squad-list"),
  marketList: document.getElementById("market-list"),
  search: document.getElementById("market-search"),
  tactic: document.getElementById("tactic"),
  playButton: document.getElementById("play-match"),
  log: document.getElementById("match-log"),
  standings: document.getElementById("standings"),
};

const money = new Intl.NumberFormat("en", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

function createTable() {
  state.table = Object.fromEntries(
    laLigaTeams.map((name) => [name, { team: name, pts: 0, p: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0 }]),
  );
}

function averageRating() {
  return Math.round(state.squad.reduce((sum, p) => sum + p.rating, 0) / state.squad.length);
}

function nextOpponentName() {
  const opponents = laLigaTeams.filter((t) => t !== "Real Madrid");
  return opponents[(state.matchday - 1) % opponents.length];
}

function tableSorted() {
  return Object.values(state.table).sort((a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf);
}

function yourPosition() {
  return tableSorted().findIndex((row) => row.team === "Real Madrid") + 1;
}

function updateOverview() {
  el.budget.textContent = money.format(state.budget);
  el.clubRating.textContent = `${averageRating()}`;
  el.chemistry.textContent = `${state.chemistry}`;
  el.position.textContent = `${yourPosition()}/20`;
  el.matchday.textContent = `${state.matchday}`;
  el.nextOpponent.textContent = nextOpponentName();
  el.seasonChip.textContent = `Season ${state.season}`;
}

function renderPitch() {
  el.pitch.innerHTML = "";
  formation.forEach((slot, i) => {
    const p = state.squad[i];
    const node = document.createElement("div");
    node.className = "pitch-player";
    node.style.left = `${slot.x}%`;
    node.style.top = `${slot.y}%`;
    node.innerHTML = `
      <img src="${p.image}" alt="${p.name}" />
      <div class="name">${p.name}</div>
      <div class="meta">${slot.role} • OVR ${p.rating}</div>
    `;
    el.pitch.appendChild(node);
  });
}

function upgrade(index) {
  const player = state.squad[index];
  const cost = 1800000;
  if (state.budget < cost) return setLog("Not enough budget for upgrade.", false);
  if (player.rating >= 99) return setLog(`${player.name} has reached max rating 99.`, false);
  state.budget -= cost;
  player.rating = Math.min(99, player.rating + 1);
  player.stamina = Math.max(55, player.stamina - 2);
  player.morale = Math.min(99, player.morale + 1);
  state.chemistry = Math.min(99, state.chemistry + 1);
  setLog(`${player.name} improved to ${player.rating} OVR.`);
  renderAll();
}

function recover(index) {
  const player = state.squad[index];
  player.stamina = Math.min(100, player.stamina + 10);
  player.morale = Math.min(99, player.morale + 1);
  setLog(`${player.name} is recovered and fresh.`);
  renderAll();
}

function filteredMarket() {
  const q = el.search.value.trim().toLowerCase();
  if (!q) return state.market;
  return state.market.filter((p) => p.name.toLowerCase().includes(q) || p.position.toLowerCase().includes(q));
}

function buy(marketIndex) {
  const target = filteredMarket()[marketIndex];
  if (!target) return;
  if (state.budget < target.price) return setLog(`Budget too low for ${target.name}.`, false);

  const compatible = state.squad.findIndex((p, idx) => {
    const role = formation[idx].role;
    return role === target.position || (["CM", "CDM", "CAM"].includes(role) && ["CM", "CDM", "CAM"].includes(target.position));
  });
  const idx = compatible >= 0 ? compatible : Math.floor(Math.random() * state.squad.length);
  const removed = state.squad[idx];

  state.budget -= target.price;
  state.squad[idx] = {
    name: target.name,
    position: formation[idx].role,
    rating: target.rating,
    stamina: target.stamina,
    morale: 82,
    image: target.image,
  };
  state.market = state.market.filter((p) => p.name !== target.name);
  state.chemistry = Math.max(70, Math.min(99, state.chemistry + (target.rating > removed.rating ? 2 : -1)));

  setLog(`${target.name} signed for ${money.format(target.price)}. ${removed.name} replaced in XI.`);
  renderAll();
}

function renderSquadActions() {
  el.squadList.innerHTML = "";
  state.squad.forEach((p, i) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="row">
        <div class="row"><img src="${p.image}" alt="${p.name}" /><strong>${formation[i].role} • ${p.name}</strong></div>
        <strong>${p.rating}</strong>
      </div>
      <div class="meta">Stamina ${p.stamina} • Morale ${p.morale} • Upgrade ${money.format(1800000)}</div>
      <div class="row">
        <button data-action="upgrade" data-index="${i}">Upgrade +1</button>
        <button data-action="recover" data-index="${i}">Recover</button>
      </div>
    `;
    el.squadList.appendChild(card);
  });
}

function renderMarket() {
  el.marketList.innerHTML = "";
  filteredMarket().forEach((p, i) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="row">
        <div class="row"><img src="${p.image}" alt="${p.name}" /><strong>${p.name}</strong></div>
        <strong>${p.rating}</strong>
      </div>
      <div class="meta">${p.position} • ${money.format(p.price)}</div>
      <button data-action="buy" data-index="${i}">Sign Player</button>
    `;
    el.marketList.appendChild(card);
  });
}

function simulateOtherFixture(home, away) {
  const hPower = 78 + Math.floor(Math.random() * 16);
  const aPower = 78 + Math.floor(Math.random() * 16);
  const hGoals = Math.max(0, Math.floor((hPower - 70) / 9) + Math.floor(Math.random() * 3));
  const aGoals = Math.max(0, Math.floor((aPower - 70) / 9) + Math.floor(Math.random() * 3));
  updateTable(home, away, hGoals, aGoals);
}

function updateTable(home, away, hg, ag) {
  const h = state.table[home];
  const a = state.table[away];
  h.p += 1; a.p += 1;
  h.gf += hg; h.ga += ag; h.gd = h.gf - h.ga;
  a.gf += ag; a.ga += hg; a.gd = a.gf - a.ga;
  if (hg > ag) { h.w += 1; h.pts += 3; a.l += 1; }
  else if (hg < ag) { a.w += 1; a.pts += 3; h.l += 1; }
  else { h.d += 1; a.d += 1; h.pts += 1; a.pts += 1; }
}

function playMatchday() {
  const opponent = nextOpponentName();
  const tacticBoost = { balanced: 0, "high-press": 2, counter: 1, possession: 1 }[el.tactic.value];
  const staminaScore = Math.round(state.squad.reduce((s, p) => s + p.stamina, 0) / state.squad.length / 12);
  const moraleScore = Math.round(state.squad.reduce((s, p) => s + p.morale, 0) / state.squad.length / 20);
  const rmPower = averageRating() + tacticBoost + staminaScore + moraleScore + Math.round(state.chemistry / 25);
  const oppPower = 81 + Math.floor(Math.random() * 14);

  const rmGoals = Math.max(0, Math.floor((rmPower - 75) / 8) + Math.floor(Math.random() * 3));
  const oppGoals = Math.max(0, Math.floor((oppPower - 75) / 8) + Math.floor(Math.random() * 3));

  updateTable("Real Madrid", opponent, rmGoals, oppGoals);

  const others = laLigaTeams.filter((t) => !["Real Madrid", opponent].includes(t));
  for (let i = 0; i < others.length; i += 2) {
    simulateOtherFixture(others[i], others[i + 1]);
  }

  if (rmGoals > oppGoals) {
    state.budget += 5000000;
    state.chemistry = Math.min(99, state.chemistry + 1);
  } else if (rmGoals === oppGoals) {
    state.budget += 2000000;
  } else {
    state.chemistry = Math.max(65, state.chemistry - 2);
  }

  state.squad.forEach((p) => {
    p.stamina = Math.max(50, p.stamina - (el.tactic.value === "high-press" ? 8 : 5));
    p.morale = Math.max(60, Math.min(99, p.morale + (rmGoals > oppGoals ? 2 : rmGoals < oppGoals ? -2 : 0)));
  });

  setLog(
    `MD${state.matchday}: Real Madrid ${rmGoals}-${oppGoals} ${opponent}. Power ${rmPower} vs ${oppPower}.`,
    rmGoals >= oppGoals,
  );

  state.matchday += 1;
  if (state.matchday > 38) {
    const pos = yourPosition();
    setLog(`Season ${state.season} complete! Finished #${pos}. New season starts now.`, pos <= 4);
    state.season += 1;
    state.matchday = 1;
    createTable();
  }

  renderAll();
}

function renderStandings() {
  const rows = tableSorted();
  const html = `
    <table>
      <thead>
        <tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (r, i) => `<tr class="${r.team === "Real Madrid" ? "you-row" : ""}">
              <td>${i + 1}</td><td>${r.team}</td><td>${r.p}</td><td>${r.w}</td><td>${r.d}</td><td>${r.l}</td><td>${r.gd}</td><td>${r.pts}</td>
            </tr>`,
          )
          .join("")}
      </tbody>
    </table>
  `;
  el.standings.innerHTML = html;
}

function setLog(message, good = true) {
  el.log.innerHTML = `<span class="${good ? "good" : "bad"}">${message}</span>`;
}

function renderAll() {
  updateOverview();
  renderPitch();
  renderSquadActions();
  renderMarket();
  renderStandings();
}

document.body.addEventListener("click", (event) => {
  if (!(event.target instanceof HTMLElement)) return;
  const action = event.target.dataset.action;
  const index = Number(event.target.dataset.index);
  if (!action || Number.isNaN(index)) return;
  if (action === "upgrade") upgrade(index);
  if (action === "recover") recover(index);
  if (action === "buy") buy(index);
});

el.search.addEventListener("input", renderMarket);
el.playButton.addEventListener("click", playMatchday);

createTable();
renderAll();
setLog("Welcome manager. Build your squad and play through endless LaLiga seasons.");
