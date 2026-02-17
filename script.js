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

const toImage = (name, dark = false) =>
  `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=${dark ? "0D1117" : "FFFFFF"}&color=${dark ? "fff" : "111"}&size=128`;

const createPlayer = (name, position, rating, price = 0, dark = false) => ({
  name,
  position,
  rating,
  price,
  stamina: 86,
  morale: 82,
  image: toImage(name, dark),
});

class CareerGame {
  constructor() {
    this.money = new Intl.NumberFormat("en", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
    this.state = {
      season: 1,
      matchday: 1,
      budget: 230000000,
      chemistry: 82,
      squad: [
        createPlayer("Thibaut Courtois", "GK", 90), createPlayer("Ferland Mendy", "LB", 83), createPlayer("Antonio Rudiger", "CB", 86),
        createPlayer("Eder Militao", "CB", 85), createPlayer("Dani Carvajal", "RB", 84), createPlayer("Jude Bellingham", "CM", 88),
        createPlayer("Federico Valverde", "CM", 87), createPlayer("Eduardo Camavinga", "CM", 84), createPlayer("Vinicius Jr", "LW", 89),
        createPlayer("Kylian Mbappe", "ST", 91), createPlayer("Rodrygo", "RW", 86),
      ],
      market: this.createMarket(),
      table: {},
      lastReport: null,
      playerStats: {},
    };

    this.el = {
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
      scoreSheet: document.getElementById("score-sheet"),
      leaders: document.getElementById("leaders"),
    };

    this.createTable();
    this.ensureStatsForSquad();
    this.bindEvents();
    this.render();
    this.setLog("Welcome manager. Build your squad, play matches, and track season awards.");
  }

  createMarket() {
    const rows = [
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
    ];
    return rows.map(([name, pos, rat, price]) => createPlayer(name, pos, rat, price, true));
  }

  createTable() {
    this.state.table = Object.fromEntries(
      laLigaTeams.map((name) => [name, { team: name, pts: 0, p: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0 }]),
    );
  }

  ensureStatsForSquad() {
    this.state.squad.forEach((p) => {
      if (!this.state.playerStats[p.name]) {
        this.state.playerStats[p.name] = { goals: 0, assists: 0, cleanSheets: 0, appearances: 0 };
      }
    });
  }

  averageRating() {
    return Math.round(this.state.squad.reduce((sum, p) => sum + p.rating, 0) / this.state.squad.length);
  }

  nextOpponentName() {
    const opponents = laLigaTeams.filter((t) => t !== "Real Madrid");
    return opponents[(this.state.matchday - 1) % opponents.length];
  }

  tableSorted() {
    return Object.values(this.state.table).sort((a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf);
  }

  yourPosition() {
    return this.tableSorted().findIndex((row) => row.team === "Real Madrid") + 1;
  }

  filteredMarket() {
    const q = this.el.search.value.trim().toLowerCase();
    if (!q) return this.state.market;
    return this.state.market.filter((p) => p.name.toLowerCase().includes(q) || p.position.toLowerCase().includes(q));
  }

  weightedAttackingPool() {
    const indexes = [8, 9, 10, 5, 6, 7];
    return indexes.flatMap((idx) => {
      const p = this.state.squad[idx];
      const weight = Math.max(1, Math.round((p.rating + p.morale / 2) / 18));
      return Array.from({ length: weight }, () => p);
    });
  }

  chooseScorer(excludeName = null) {
    const pool = this.weightedAttackingPool().filter((p) => p.name !== excludeName);
    return pool[Math.floor(Math.random() * pool.length)] || this.state.squad[9];
  }

  simulateGoals(power, baseline = 76) {
    const xg = Math.max(0.2, (power - baseline) / 12 + Math.random() * 1.6);
    return Math.min(6, Math.max(0, Math.floor(xg)) + (Math.random() < xg % 1 ? 1 : 0));
  }

  updateTable(home, away, hg, ag) {
    const h = this.state.table[home];
    const a = this.state.table[away];
    h.p += 1;
    a.p += 1;
    h.gf += hg;
    h.ga += ag;
    h.gd = h.gf - h.ga;
    a.gf += ag;
    a.ga += hg;
    a.gd = a.gf - a.ga;
    if (hg > ag) {
      h.w += 1;
      h.pts += 3;
      a.l += 1;
    } else if (hg < ag) {
      a.w += 1;
      a.pts += 3;
      h.l += 1;
    } else {
      h.d += 1;
      a.d += 1;
      h.pts += 1;
      a.pts += 1;
    }
  }

  simulateOtherFixture(home, away) {
    const hg = this.simulateGoals(80 + Math.floor(Math.random() * 11));
    const ag = this.simulateGoals(80 + Math.floor(Math.random() * 11));
    this.updateTable(home, away, hg, ag);
  }

  registerPlayerContribution(goals, conceded) {
    this.state.squad.forEach((p) => {
      this.state.playerStats[p.name].appearances += 1;
    });

    const events = [];
    for (let i = 0; i < goals; i += 1) {
      const scorer = this.chooseScorer();
      const assister = this.chooseScorer(scorer.name);
      this.state.playerStats[scorer.name].goals += 1;
      this.state.playerStats[assister.name].assists += 1;
      events.push({
        minute: 5 + Math.floor(Math.random() * 86),
        scorer: scorer.name,
        assister: assister.name,
      });
    }

    if (conceded === 0) {
      const gk = this.state.squad[0];
      this.state.playerStats[gk.name].cleanSheets += 1;
    }

    events.sort((a, b) => a.minute - b.minute);
    return events;
  }

  playMatchday() {
    const opponent = this.nextOpponentName();
    const tacticBoost = { balanced: 0, "high-press": 2, counter: 1, possession: 1 }[this.el.tactic.value];
    const staminaScore = Math.round(this.state.squad.reduce((s, p) => s + p.stamina, 0) / this.state.squad.length / 12);
    const moraleScore = Math.round(this.state.squad.reduce((s, p) => s + p.morale, 0) / this.state.squad.length / 21);
    const rmPower = this.averageRating() + tacticBoost + staminaScore + moraleScore + Math.round(this.state.chemistry / 25);
    const oppPower = 81 + Math.floor(Math.random() * 13);

    const rmGoals = this.simulateGoals(rmPower);
    const oppGoals = this.simulateGoals(oppPower);
    this.updateTable("Real Madrid", opponent, rmGoals, oppGoals);

    const others = laLigaTeams.filter((t) => !["Real Madrid", opponent].includes(t));
    for (let i = 0; i < others.length; i += 2) {
      this.simulateOtherFixture(others[i], others[i + 1]);
    }

    const scoringEvents = this.registerPlayerContribution(rmGoals, oppGoals);
    this.state.lastReport = {
      matchday: this.state.matchday,
      opponent,
      result: `Real Madrid ${rmGoals}-${oppGoals} ${opponent}`,
      events: scoringEvents,
    };

    if (rmGoals > oppGoals) {
      this.state.budget += 5000000;
      this.state.chemistry = Math.min(99, this.state.chemistry + 1);
    } else if (rmGoals === oppGoals) {
      this.state.budget += 2000000;
    } else {
      this.state.chemistry = Math.max(65, this.state.chemistry - 2);
    }

    this.state.squad.forEach((p) => {
      p.stamina = Math.max(50, p.stamina - (this.el.tactic.value === "high-press" ? 8 : 5));
      p.morale = Math.max(60, Math.min(99, p.morale + (rmGoals > oppGoals ? 2 : rmGoals < oppGoals ? -2 : 0)));
    });

    this.setLog(
      `MD${this.state.matchday}: Real Madrid ${rmGoals}-${oppGoals} ${opponent}. Power ${rmPower} vs ${oppPower}.`,
      rmGoals >= oppGoals,
    );

    this.state.matchday += 1;
    if (this.state.matchday > 38) {
      const pos = this.yourPosition();
      this.setLog(`Season ${this.state.season} finished in #${pos}. New season begins.`, pos <= 4);
      this.state.season += 1;
      this.state.matchday = 1;
      this.createTable();
    }

    this.render();
  }

  upgrade(index) {
    const player = this.state.squad[index];
    const cost = 1800000;
    if (this.state.budget < cost) return this.setLog("Not enough budget for upgrade.", false);
    if (player.rating >= 99) return this.setLog(`${player.name} has reached max rating 99.`, false);
    this.state.budget -= cost;
    player.rating = Math.min(99, player.rating + 1);
    player.stamina = Math.max(55, player.stamina - 2);
    player.morale = Math.min(99, player.morale + 1);
    this.state.chemistry = Math.min(99, this.state.chemistry + 1);
    this.setLog(`${player.name} improved to ${player.rating} OVR.`);
    this.render();
  }

  recover(index) {
    const player = this.state.squad[index];
    player.stamina = Math.min(100, player.stamina + 10);
    player.morale = Math.min(99, player.morale + 1);
    this.setLog(`${player.name} is recovered and ready.`);
    this.render();
  }

  buy(marketIndex) {
    const target = this.filteredMarket()[marketIndex];
    if (!target) return;
    if (this.state.budget < target.price) return this.setLog(`Budget too low for ${target.name}.`, false);

    const compatibleIndex = this.state.squad.findIndex((player, idx) => {
      const role = formation[idx].role;
      return role === target.position || (["CM", "CDM", "CAM"].includes(role) && ["CM", "CDM", "CAM"].includes(target.position));
    });
    const idx = compatibleIndex >= 0 ? compatibleIndex : Math.floor(Math.random() * this.state.squad.length);
    const replaced = this.state.squad[idx];

    this.state.budget -= target.price;
    this.state.squad[idx] = {
      ...target,
      position: formation[idx].role,
      morale: 82,
      stamina: target.stamina,
    };

    if (!this.state.playerStats[target.name]) {
      this.state.playerStats[target.name] = { goals: 0, assists: 0, cleanSheets: 0, appearances: 0 };
    }

    this.state.market = this.state.market.filter((p) => p.name !== target.name);
    this.state.chemistry = Math.max(70, Math.min(99, this.state.chemistry + (target.rating > replaced.rating ? 2 : -1)));
    this.setLog(`${target.name} signed for ${this.money.format(target.price)}. ${replaced.name} moved out of XI.`);
    this.render();
  }

  setLog(message, good = true) {
    this.el.log.innerHTML = `<span class="${good ? "good" : "bad"}">${message}</span>`;
  }

  renderOverview() {
    this.el.budget.textContent = this.money.format(this.state.budget);
    this.el.clubRating.textContent = `${this.averageRating()}`;
    this.el.chemistry.textContent = `${this.state.chemistry}`;
    this.el.position.textContent = `${this.yourPosition()}/20`;
    this.el.matchday.textContent = `${this.state.matchday}`;
    this.el.nextOpponent.textContent = this.nextOpponentName();
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
      node.innerHTML = `
        <img src="${p.image}" alt="${p.name}" />
        <div class="name">${p.name}</div>
        <div class="meta">${slot.role} • OVR ${p.rating}</div>
      `;
      this.el.pitch.appendChild(node);
    });
  }

  renderSquadActions() {
    this.el.squadList.innerHTML = "";
    this.state.squad.forEach((p, i) => {
      const stats = this.state.playerStats[p.name];
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="row">
          <div class="row"><img src="${p.image}" alt="${p.name}" /><strong>${formation[i].role} • ${p.name}</strong></div>
          <strong>${p.rating}</strong>
        </div>
        <div class="meta">STM ${p.stamina} • MOR ${p.morale} • G ${stats.goals} • A ${stats.assists} • Upgrade ${this.money.format(1800000)}</div>
        <div class="row">
          <button data-action="upgrade" data-index="${i}">Upgrade +1</button>
          <button data-action="recover" data-index="${i}">Recover</button>
        </div>
      `;
      this.el.squadList.appendChild(card);
    });
  }

  renderMarket() {
    this.el.marketList.innerHTML = "";
    this.filteredMarket().forEach((p, i) => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="row">
          <div class="row"><img src="${p.image}" alt="${p.name}" /><strong>${p.name}</strong></div>
          <strong>${p.rating}</strong>
        </div>
        <div class="meta">${p.position} • ${this.money.format(p.price)}</div>
        <button data-action="buy" data-index="${i}">Sign Player</button>
      `;
      this.el.marketList.appendChild(card);
    });
  }

  renderStandings() {
    const rows = this.tableSorted();
    this.el.standings.innerHTML = `
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
  }

  renderScoreSheet() {
    const report = this.state.lastReport;
    if (!report) {
      this.el.scoreSheet.innerHTML = '<p class="meta">No match played yet. Play matchday to generate score events.</p>';
      return;
    }

    const lines = report.events.length
      ? report.events
          .map((e) => `<div class="score-line"><span>${e.minute}' ${e.scorer}</span><span>Assist: ${e.assister}</span></div>`)
          .join("")
      : '<div class="score-line"><span>No Real Madrid goals this match.</span><span>—</span></div>';

    this.el.scoreSheet.innerHTML = `
      <div class="row"><strong>MD${report.matchday}</strong><strong>${report.result}</strong></div>
      ${lines}
    `;
  }

  topBy(metric) {
    return Object.entries(this.state.playerStats)
      .filter(([, v]) => v.appearances > 0)
      .sort((a, b) => b[1][metric] - a[1][metric])
      .slice(0, 5);
  }

  renderLeaders() {
    const goals = this.topBy("goals");
    const assists = this.topBy("assists");
    const cleanSheets = this.topBy("cleanSheets");

    const buildList = (items, key) =>
      items.length
        ? `<ol class="leader-list">${items.map(([name, s]) => `<li>${name} — ${s[key]}</li>`).join("")}</ol>`
        : '<p class="meta">No data yet.</p>';

    this.el.leaders.innerHTML = `
      <div class="leader-card"><h3>Top Scorers</h3>${buildList(goals, "goals")}</div>
      <div class="leader-card"><h3>Top Assisters</h3>${buildList(assists, "assists")}</div>
      <div class="leader-card"><h3>Clean Sheets</h3>${buildList(cleanSheets, "cleanSheets")}</div>
    `;
  }

  bindEvents() {
    document.body.addEventListener("click", (event) => {
      if (!(event.target instanceof HTMLElement)) return;
      const action = event.target.dataset.action;
      const index = Number(event.target.dataset.index);
      if (!action || Number.isNaN(index)) return;
      if (action === "upgrade") this.upgrade(index);
      if (action === "recover") this.recover(index);
      if (action === "buy") this.buy(index);
    });

    this.el.search.addEventListener("input", () => this.renderMarket());
    this.el.playButton.addEventListener("click", () => this.playMatchday());
  }

  render() {
    this.renderOverview();
    this.renderPitch();
    this.renderSquadActions();
    this.renderMarket();
    this.renderStandings();
    this.renderScoreSheet();
    this.renderLeaders();
  }
}

new CareerGame();
