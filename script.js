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

const roleWeight = { GK: 1, RB: 2, LB: 2, CB: 2, CDM: 3, CM: 4, CAM: 5, RW: 6, LW: 6, ST: 7 };
const initials = (name) => name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
const hash = (str) => [...str].reduce((acc, c) => acc + c.charCodeAt(0), 0);

function avatarSvg(name) {
  const h = hash(name);
  const skin = ["#f5d0a5", "#e0ac69", "#d39c73"][h % 3];
  const shirt = ["#1f3a8a", "#6d28d9", "#0f766e", "#b45309"][h % 4];
  const hair = ["#111827", "#3f3f46", "#78350f"][h % 3];
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='128' height='128'>
    <rect width='100%' height='100%' fill='${shirt}'/>
    <circle cx='64' cy='52' r='26' fill='${skin}'/>
    <ellipse cx='64' cy='39' rx='27' ry='14' fill='${hair}'/>
    <rect x='28' y='84' width='72' height='36' rx='18' fill='${skin}'/>
  </svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

function badgeSvg(team) {
  const text = initials(team);
  const color = ["#1d4ed8", "#7c3aed", "#0f766e", "#b91c1c", "#a16207"][hash(team) % 5];
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'>
    <circle cx='32' cy='32' r='31' fill='${color}' stroke='white' stroke-width='2'/>
    <text x='32' y='38' text-anchor='middle' font-size='18' font-family='Arial' fill='white' font-weight='700'>${text}</text>
  </svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

const mkPlayer = (name, pos, rating, price = 0) => ({
  name,
  position: pos,
  rating,
  price,
  stamina: 88,
  morale: 82,
  image: avatarSvg(name),
});

class CareerGame {
  constructor() {
    this.money = new Intl.NumberFormat("en", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
    this.state = {
      season: 1,
      matchday: 1,
      budget: 220000000,
      chemistry: 82,
      squad: [
        mkPlayer("Thibaut Courtois", "GK", 90), mkPlayer("Ferland Mendy", "LB", 83), mkPlayer("Antonio Rudiger", "CB", 86),
        mkPlayer("Eder Militao", "CB", 85), mkPlayer("Dani Carvajal", "RB", 84), mkPlayer("Jude Bellingham", "CM", 88),
        mkPlayer("Federico Valverde", "CM", 87), mkPlayer("Eduardo Camavinga", "CM", 84), mkPlayer("Vinicius Jr", "LW", 89),
        mkPlayer("Kylian Mbappe", "ST", 91), mkPlayer("Rodrygo", "RW", 86),
      ],
      bench: [
        mkPlayer("Andriy Lunin", "GK", 81), mkPlayer("Fran Garcia", "LB", 80), mkPlayer("David Alaba", "CB", 84),
        mkPlayer("Lucas Vazquez", "RB", 81), mkPlayer("Aurelien Tchouameni", "CDM", 86), mkPlayer("Arda Guler", "CAM", 82),
        mkPlayer("Brahim Diaz", "RW", 83), mkPlayer("Endrick", "ST", 79), mkPlayer("Dani Ceballos", "CM", 80),
      ],
      market: this.createMarket(),
      table: {},
      lastReport: null,
      playerStats: {},
      leagueScorers: {},
      teamRosters: {},
    };

    this.el = {
      budget: document.getElementById("budget"), clubRating: document.getElementById("club-rating"), chemistry: document.getElementById("chemistry"),
      position: document.getElementById("table-position"), matchday: document.getElementById("matchday"), nextOpponent: document.getElementById("next-opponent"),
      seasonChip: document.getElementById("season-chip"), pitch: document.getElementById("pitch"), squadList: document.getElementById("squad-list"),
      benchList: document.getElementById("bench-list"), marketList: document.getElementById("market-list"), search: document.getElementById("market-search"),
      tactic: document.getElementById("tactic"), playButton: document.getElementById("play-match"), log: document.getElementById("match-log"),
      standings: document.getElementById("standings"), scoreSheet: document.getElementById("score-sheet"), leaders: document.getElementById("leaders"),
    };

    this.createTable();
    this.createTeamRosters();
    this.ensureStats();
    this.bindEvents();
    this.render();
    this.setLog("Ready. Stamina auto-recovers between games and you can swap bench into XI.");
  }

  createMarket() {
    const raw = [
      ["Erling Haaland", "ST", 91, 190000000], ["Lautaro Martinez", "ST", 89, 132000000], ["Victor Osimhen", "ST", 89, 146000000],
      ["Julian Alvarez", "ST", 86, 98000000], ["Mohamed Salah", "RW", 89, 98000000], ["Bukayo Saka", "RW", 89, 145000000],
      ["Phil Foden", "RW", 89, 150000000], ["Jamal Musiala", "CAM", 88, 134000000], ["Florian Wirtz", "CAM", 88, 126000000],
      ["Pedri", "CM", 88, 143000000], ["Gavi", "CM", 84, 79000000], ["Bruno Guimaraes", "CM", 86, 95000000],
      ["Sandro Tonali", "CM", 85, 88000000], ["Declan Rice", "CDM", 88, 140000000], ["Martin Zubimendi", "CDM", 84, 68000000],
      ["Khvicha Kvaratskhelia", "LW", 86, 99000000], ["Rafael Leao", "LW", 87, 118000000], ["Nico Williams", "LW", 84, 77000000],
      ["Theo Hernandez", "LB", 87, 90000000], ["Alphonso Davies", "LB", 86, 87000000], ["Achraf Hakimi", "RB", 86, 84000000],
      ["William Saliba", "CB", 87, 104000000], ["Ronald Araujo", "CB", 88, 136000000], ["Ruben Dias", "CB", 89, 121000000],
      ["Mike Maignan", "GK", 88, 94000000], ["Diogo Costa", "GK", 85, 72000000], ["Cole Palmer", "RW", 85, 86000000],
      ["Rodri", "CDM", 91, 157000000], ["Jules Kounde", "CB", 85, 86000000], ["Joao Neves", "CM", 82, 56000000],
    ];
    return raw.map(([n, p, r, pr]) => mkPlayer(n, p, r, pr));
  }

  createTeamRosters() {
    laLigaTeams.forEach((team) => {
      if (team === "Real Madrid") {
        this.state.teamRosters[team] = [...this.state.squad, ...this.state.bench].map((p) => ({ name: p.name, position: p.position, rating: p.rating }));
        return;
      }
      const names = Array.from({ length: 15 }, (_, i) => `${team.split(" ")[0]} Player ${i + 1}`);
      const pos = ["GK", "RB", "LB", "CB", "CB", "CM", "CM", "CDM", "RW", "LW", "ST", "CAM", "RB", "CB", "ST"];
      this.state.teamRosters[team] = names.map((name, i) => ({ name, position: pos[i], rating: 74 + (i % 8) }));
    });
  }

  ensureStats() {
    [...this.state.squad, ...this.state.bench].forEach((p) => {
      if (!this.state.playerStats[p.name]) this.state.playerStats[p.name] = { goals: 0, assists: 0, cleanSheets: 0, apps: 0 };
    });
  }

  createTable() {
    this.state.table = Object.fromEntries(laLigaTeams.map((t) => [t, { team: t, pts: 0, p: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0 }]));
  }

  avgRating() { return Math.round(this.state.squad.reduce((s, p) => s + p.rating, 0) / this.state.squad.length); }
  nextOpponent() { const opp = laLigaTeams.filter((t) => t !== "Real Madrid"); return opp[(this.state.matchday - 1) % opp.length]; }
  tableSorted() { return Object.values(this.state.table).sort((a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf); }
  yourPos() { return this.tableSorted().findIndex((r) => r.team === "Real Madrid") + 1; }

  restoreStaminaByRestDays() {
    const restDays = 2 + Math.floor(Math.random() * 3);
    const recovery = restDays * 6;
    this.state.squad.forEach((p) => { p.stamina = Math.min(100, p.stamina + recovery); });
    return restDays;
  }

  weightedScorer(teamName) {
    const roster = teamName === "Real Madrid" ? this.state.squad : this.state.teamRosters[teamName];
    const pool = roster.flatMap((p) => Array.from({ length: roleWeight[p.position] || 2 }, () => p));
    return pool[Math.floor(Math.random() * pool.length)] || roster[0];
  }

  simulateGoals(power) {
    const xg = Math.max(0.25, (power - 72) / 13 + Math.random() * 1.5);
    return Math.min(6, Math.max(0, Math.floor(xg)) + (Math.random() < xg % 1 ? 1 : 0));
  }

  addLeagueGoal(team, playerName, amount = 1) {
    const key = `${team}::${playerName}`;
    this.state.leagueScorers[key] = (this.state.leagueScorers[key] || 0) + amount;
  }

  registerRealMadridEvents(goals, conceded) {
    this.state.squad.forEach((p) => { this.state.playerStats[p.name].apps += 1; });
    const events = [];
    for (let i = 0; i < goals; i += 1) {
      const scorer = this.weightedScorer("Real Madrid");
      const assister = this.weightedScorer("Real Madrid");
      this.state.playerStats[scorer.name].goals += 1;
      this.state.playerStats[assister.name].assists += 1;
      this.addLeagueGoal("Real Madrid", scorer.name);
      events.push({ minute: 5 + Math.floor(Math.random() * 86), scorer: scorer.name, assister: assister.name });
    }
    if (conceded === 0) this.state.playerStats[this.state.squad[0].name].cleanSheets += 1;
    return events.sort((a, b) => a.minute - b.minute);
  }

  simulateOtherFixture(home, away) {
    const hg = this.simulateGoals(79 + Math.floor(Math.random() * 10));
    const ag = this.simulateGoals(79 + Math.floor(Math.random() * 10));
    this.updateTable(home, away, hg, ag);

    for (let i = 0; i < hg; i += 1) this.addLeagueGoal(home, this.weightedScorer(home).name);
    for (let i = 0; i < ag; i += 1) this.addLeagueGoal(away, this.weightedScorer(away).name);
  }

  updateTable(home, away, hg, ag) {
    const h = this.state.table[home];
    const a = this.state.table[away];
    h.p += 1; a.p += 1;
    h.gf += hg; h.ga += ag; h.gd = h.gf - h.ga;
    a.gf += ag; a.ga += hg; a.gd = a.gf - a.ga;
    if (hg > ag) { h.w += 1; h.pts += 3; a.l += 1; }
    else if (ag > hg) { a.w += 1; a.pts += 3; h.l += 1; }
    else { h.d += 1; a.d += 1; h.pts += 1; a.pts += 1; }
  }

  playMatchday() {
    const restDays = this.restoreStaminaByRestDays();
    const opponent = this.nextOpponent();
    const tacticBoost = { balanced: 0, "high-press": 2, counter: 1, possession: 1 }[this.el.tactic.value];
    const stamina = Math.round(this.state.squad.reduce((s, p) => s + p.stamina, 0) / this.state.squad.length / 12);
    const morale = Math.round(this.state.squad.reduce((s, p) => s + p.morale, 0) / this.state.squad.length / 20);
    const rmPower = this.avgRating() + tacticBoost + stamina + morale + Math.round(this.state.chemistry / 24);
    const oppPower = 80 + Math.floor(Math.random() * 13);

    const rmGoals = this.simulateGoals(rmPower);
    const oppGoals = this.simulateGoals(oppPower);
    this.updateTable("Real Madrid", opponent, rmGoals, oppGoals);

    const events = this.registerRealMadridEvents(rmGoals, oppGoals);
    for (let i = 0; i < oppGoals; i += 1) this.addLeagueGoal(opponent, this.weightedScorer(opponent).name);

    const others = laLigaTeams.filter((t) => !["Real Madrid", opponent].includes(t));
    for (let i = 0; i < others.length; i += 2) this.simulateOtherFixture(others[i], others[i + 1]);

    this.state.squad.forEach((p) => {
      p.stamina = Math.max(46, p.stamina - (this.el.tactic.value === "high-press" ? 9 : 6));
      p.morale = Math.max(58, Math.min(99, p.morale + (rmGoals > oppGoals ? 2 : rmGoals < oppGoals ? -2 : 0)));
    });

    if (rmGoals > oppGoals) { this.state.budget += 5000000; this.state.chemistry = Math.min(99, this.state.chemistry + 1); }
    else if (rmGoals === oppGoals) { this.state.budget += 2000000; }
    else { this.state.chemistry = Math.max(65, this.state.chemistry - 2); }

    this.state.lastReport = { matchday: this.state.matchday, restDays, result: `Real Madrid ${rmGoals}-${oppGoals} ${opponent}`, events };
    this.setLog(`MD${this.state.matchday}: Real Madrid ${rmGoals}-${oppGoals} ${opponent}. Rested ${restDays} days.`, rmGoals >= oppGoals);

    this.state.matchday += 1;
    if (this.state.matchday > 38) {
      const pos = this.yourPos();
      this.setLog(`Season ${this.state.season} complete (#${pos}). New season starts.`, pos <= 4);
      this.state.season += 1;
      this.state.matchday = 1;
      this.createTable();
    }

    this.render();
  }

  upgrade(index) {
    const p = this.state.squad[index];
    const cost = 1800000 + Math.max(0, p.rating - 84) * 1200000;
    const chance = Math.max(0.12, 0.92 - (p.rating - 75) * 0.04);
    if (this.state.budget < cost) return this.setLog("Not enough budget for this focused training block.", false);
    if (p.rating >= 99) return this.setLog(`${p.name} is already at 99 OVR.`, false);

    this.state.budget -= cost;
    p.stamina = Math.max(55, p.stamina - 3);
    if (Math.random() <= chance) {
      p.rating = Math.min(99, p.rating + 1);
      this.setLog(`${p.name} improved to ${p.rating} OVR (training success).`);
    } else {
      this.setLog(`${p.name} completed training but no OVR gain this time.`, false);
    }
    this.render();
  }

  swapBenchIn(benchIndex, starterIndex) {
    const benchPlayer = this.state.bench[benchIndex];
    const starter = this.state.squad[starterIndex];
    this.state.squad[starterIndex] = { ...benchPlayer, position: formation[starterIndex].role };
    this.state.bench[benchIndex] = starter;
    this.ensureStats();
    this.state.chemistry = Math.max(68, this.state.chemistry - 1);
    this.setLog(`${benchPlayer.name} is now in starting XI. ${starter.name} moves to bench.`);
    this.render();
  }

  buy(marketIndex) {
    const target = this.filteredMarket()[marketIndex];
    if (!target) return;
    if (this.state.budget < target.price) return this.setLog(`Budget too low for ${target.name}.`, false);
    const starterIndex = this.state.squad.findIndex((_, idx) => formation[idx].role === target.position || (["CM", "CDM", "CAM"].includes(formation[idx].role) && ["CM", "CDM", "CAM"].includes(target.position)));
    const idx = starterIndex >= 0 ? starterIndex : 10;
    const out = this.state.squad[idx];
    this.state.budget -= target.price;
    this.state.squad[idx] = { ...target, position: formation[idx].role };
    this.state.bench.unshift(out);
    this.state.market = this.state.market.filter((p) => p.name !== target.name);
    this.ensureStats();
    this.setLog(`${target.name} signed for ${this.money.format(target.price)}. ${out.name} moved to bench.`);
    this.render();
  }

  filteredMarket() {
    const q = this.el.search.value.trim().toLowerCase();
    if (!q) return this.state.market;
    return this.state.market.filter((p) => p.name.toLowerCase().includes(q) || p.position.toLowerCase().includes(q));
  }

  setLog(msg, good = true) { this.el.log.innerHTML = `<span class="${good ? "good" : "bad"}">${msg}</span>`; }

  renderOverview() {
    this.el.budget.textContent = this.money.format(this.state.budget);
    this.el.clubRating.textContent = `${this.avgRating()}`;
    this.el.chemistry.textContent = `${this.state.chemistry}`;
    this.el.position.textContent = `${this.yourPos()}/20`;
    this.el.matchday.textContent = `${this.state.matchday}`;
    this.el.nextOpponent.innerHTML = `<span class="club-mark">${initials(this.nextOpponent())}</span>${this.nextOpponent()}`;
    this.el.seasonChip.textContent = `Season ${this.state.season}`;
  }

  renderPitch() {
    this.el.pitch.innerHTML = "";
    formation.forEach((slot, i) => {
      const p = this.state.squad[i];
      const node = document.createElement("div");
      node.className = "pitch-player";
      node.style.left = `${slot.x}%`;
      node.style.top = `${slot.y}%`;
      node.innerHTML = `<img src="${p.image}" alt="${p.name}"/><div class="name">${p.name}</div><div class="meta">${slot.role} • OVR ${p.rating}</div>`;
      this.el.pitch.appendChild(node);
    });
  }

  renderSquad() {
    this.el.squadList.innerHTML = "";
    this.state.squad.forEach((p, i) => {
      const cost = 1800000 + Math.max(0, p.rating - 84) * 1200000;
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `<div class="row"><div class="row"><img src="${p.image}" alt="${p.name}"/><strong>${formation[i].role} • ${p.name}</strong></div><strong>${p.rating}</strong></div>
      <div class="meta">STM ${p.stamina} • MOR ${p.morale} • Upgrade cost ${this.money.format(cost)}</div>
      <button data-action="upgrade" data-index="${i}">Targeted Training</button>`;
      this.el.squadList.appendChild(card);
    });
  }

  renderBench() {
    this.el.benchList.innerHTML = "";
    this.state.bench.forEach((p, i) => {
      const opts = this.state.squad.map((s, idx) => `<option value="${idx}">${formation[idx].role} • ${s.name}</option>`).join("");
      const selectId = `swap-target-${i}`;
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `<div class="row"><div class="row"><img src="${p.image}" alt="${p.name}"/><strong>${p.name}</strong></div><strong>${p.rating}</strong></div>
      <div class="meta">${p.position} • Stamina ${p.stamina}</div>
      <div class="row"><select id="${selectId}">${opts}</select><button data-action="swap" data-bench-index="${i}" data-select-id="${selectId}">Start Player</button></div>`;
      this.el.benchList.appendChild(card);
    });
  }

  renderMarket() {
    this.el.marketList.innerHTML = "";
    this.filteredMarket().forEach((p, i) => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `<div class="row"><div class="row"><img src="${p.image}" alt="${p.name}"/><strong>${p.name}</strong></div><strong>${p.rating}</strong></div>
      <div class="meta">${p.position} • ${this.money.format(p.price)}</div><button data-action="buy" data-index="${i}">Sign Player</button>`;
      this.el.marketList.appendChild(card);
    });
  }

  renderStandings() {
    const rows = this.tableSorted();
    this.el.standings.innerHTML = `<table><thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead><tbody>
      ${rows.map((r, i) => `<tr class="${r.team === "Real Madrid" ? "you-row" : ""}"><td>${i + 1}</td><td><span class="club-mark">${initials(r.team)}</span>${r.team}</td><td>${r.p}</td><td>${r.w}</td><td>${r.d}</td><td>${r.l}</td><td>${r.gd}</td><td>${r.pts}</td></tr>`).join("")}
    </tbody></table>`;
  }

  renderScoreSheet() {
    if (!this.state.lastReport) {
      this.el.scoreSheet.innerHTML = '<p class="meta">No match played yet.</p>';
      return;
    }
    const e = this.state.lastReport.events;
    const lines = e.length ? e.map((ev) => `<div class="score-line"><span>${ev.minute}' ${ev.scorer}</span><span>Assist: ${ev.assister}</span></div>`).join("") : '<div class="score-line"><span>No Real Madrid goals</span><span>—</span></div>';
    this.el.scoreSheet.innerHTML = `<div class="row"><strong>MD${this.state.lastReport.matchday}</strong><strong>${this.state.lastReport.result}</strong></div><div class="meta">Rest gap: ${this.state.lastReport.restDays} days</div>${lines}`;
  }

  renderLeaders() {
    const rmTop = Object.entries(this.state.playerStats).sort((a, b) => b[1].goals - a[1].goals).slice(0, 5);
    const laligaTop = Object.entries(this.state.leagueScorers).sort((a, b) => b[1] - a[1]).slice(0, 8);
    const assists = Object.entries(this.state.playerStats).sort((a, b) => b[1].assists - a[1].assists).slice(0, 5);
    const cleans = Object.entries(this.state.playerStats).sort((a, b) => b[1].cleanSheets - a[1].cleanSheets).slice(0, 5);
    const list = (items, fmt) => items.length ? `<ol class="leader-list">${items.map(fmt).join("")}</ol>` : '<p class="meta">No data yet.</p>';

    this.el.leaders.innerHTML = `
      <div class="leader-card"><h3>Real Madrid Top Scorers</h3>${list(rmTop, ([n, s]) => `<li>${n} — ${s.goals}</li>`)}</div>
      <div class="leader-card"><h3>LaLiga Golden Boot Race</h3>${list(laligaTop, ([k, g]) => { const [t, p] = k.split('::'); return `<li><span class="club-mark">${initials(t)}</span>${p} (${t}) — ${g}</li>`; })}</div>
      <div class="leader-card"><h3>Top Assisters (RM)</h3>${list(assists, ([n, s]) => `<li>${n} — ${s.assists}</li>`)}</div>
      <div class="leader-card"><h3>Clean Sheets (RM)</h3>${list(cleans, ([n, s]) => `<li>${n} — ${s.cleanSheets}</li>`)}</div>
    `;
  }

  bindEvents() {
    document.body.addEventListener("click", (event) => {
      if (!(event.target instanceof HTMLElement)) return;
      const action = event.target.dataset.action;
      if (!action) return;
      if (action === "upgrade") this.upgrade(Number(event.target.dataset.index));
      if (action === "buy") this.buy(Number(event.target.dataset.index));
      if (action === "swap") {
        const benchIndex = Number(event.target.dataset.benchIndex);
        const sel = document.getElementById(event.target.dataset.selectId);
        if (sel instanceof HTMLSelectElement) this.swapBenchIn(benchIndex, Number(sel.value));
      }
    });
    this.el.search.addEventListener("input", () => this.renderMarket());
    this.el.playButton.addEventListener("click", () => this.playMatchday());
  }

  render() {
    this.renderOverview();
    this.renderPitch();
    this.renderSquad();
    this.renderBench();
    this.renderMarket();
    this.renderStandings();
    this.renderScoreSheet();
    this.renderLeaders();
  }
}

new CareerGame();
