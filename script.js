const state = {
  budget: 95000000,
  chemistry: 74,
  points: 0,
  week: 1,
  squad: [
    { name: "Bellingham", position: "CM", rating: 88, stamina: 92, morale: 84, value: 130000000 },
    { name: "Vinicius Jr", position: "LW", rating: 89, stamina: 90, morale: 82, value: 150000000 },
    { name: "Rodrygo", position: "RW", rating: 86, stamina: 88, morale: 80, value: 95000000 },
    { name: "Camavinga", position: "CM", rating: 84, stamina: 91, morale: 78, value: 85000000 },
    { name: "Militao", position: "CB", rating: 85, stamina: 86, morale: 79, value: 70000000 },
  ],
  market: [
    { name: "Wirtz", position: "CAM", rating: 88, stamina: 85, morale: 80, price: 125000000 },
    { name: "Davies", position: "LB", rating: 86, stamina: 92, morale: 79, price: 78000000 },
    { name: "Haaland", position: "ST", rating: 91, stamina: 84, morale: 81, price: 165000000 },
    { name: "Saliba", position: "CB", rating: 87, stamina: 88, morale: 82, price: 98000000 },
  ],
};

const clubs = ["Barcelona", "Atletico", "Sevilla", "Valencia", "Real Sociedad", "Villarreal"];

const currency = new Intl.NumberFormat("en", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

const budgetEl = document.getElementById("budget");
const chemistryEl = document.getElementById("chemistry");
const ratingEl = document.getElementById("squad-rating");
const pointsEl = document.getElementById("points");
const weekEl = document.getElementById("week");
const squadListEl = document.getElementById("squad-list");
const marketListEl = document.getElementById("market-list");
const tacticEl = document.getElementById("tactic");
const playMatchBtn = document.getElementById("play-match");
const matchLogEl = document.getElementById("match-log");

function averageRating() {
  const total = state.squad.reduce((sum, p) => sum + p.rating, 0);
  return Math.round(total / state.squad.length);
}

function updateObjectiveStatus() {
  document.getElementById("obj-rating").className = averageRating() >= 86 ? "good" : "";
  document.getElementById("obj-points").className = state.points >= 20 && state.week <= 11 ? "good" : "";
  document.getElementById("obj-budget").className = state.budget >= 120000000 && state.week > 10 ? "good" : "";
}

function renderOverview() {
  budgetEl.textContent = currency.format(state.budget);
  chemistryEl.textContent = `${state.chemistry}`;
  ratingEl.textContent = `${averageRating()}`;
  pointsEl.textContent = `${state.points}`;
  weekEl.textContent = `${state.week}/10`;
  updateObjectiveStatus();
}

function trainPlayer(index) {
  const player = state.squad[index];
  if (player.stamina < 60) {
    setLog(`${player.name} is too tired to train. Rest or rotate squad.`);
    return;
  }
  player.rating += 1;
  player.stamina -= 9;
  player.morale += 2;
  state.chemistry = Math.min(99, state.chemistry + 1);
  setLog(`${player.name} completed an intense session: +1 rating, stamina now ${player.stamina}.`);
  render();
}

function restPlayer(index) {
  const player = state.squad[index];
  player.stamina = Math.min(100, player.stamina + 12);
  player.morale = Math.min(99, player.morale + 1);
  setLog(`${player.name} rested and recovered fitness.`);
  render();
}

function sellPlayer(index) {
  if (state.squad.length <= 3) {
    setLog("You need at least 3 players in the squad.");
    return;
  }
  const [player] = state.squad.splice(index, 1);
  const fee = Math.round(player.value * 0.55);
  state.budget += fee;
  state.chemistry = Math.max(50, state.chemistry - 3);
  setLog(`${player.name} sold for ${currency.format(fee)}.`);
  render();
}

function buyPlayer(index) {
  const target = state.market[index];
  if (state.budget < target.price) {
    setLog(`Not enough budget to sign ${target.name}.`);
    return;
  }
  state.budget -= target.price;
  state.squad.push({
    name: target.name,
    position: target.position,
    rating: target.rating,
    stamina: target.stamina,
    morale: target.morale,
    value: Math.round(target.price * 1.15),
  });
  state.market.splice(index, 1);
  state.chemistry = Math.min(99, state.chemistry + 2);
  setLog(`${target.name} joined Real Madrid for ${currency.format(target.price)}.`);
  render();
}

function setLog(message, good = true) {
  matchLogEl.innerHTML = `<span class="${good ? "good" : "bad"}">${message}</span>`;
}

function playMatch() {
  if (state.week > 10) {
    setLog("Season complete! Restart page to begin a new rebuild.");
    return;
  }

  const opponent = clubs[Math.floor(Math.random() * clubs.length)];
  const tacticBoosts = {
    balanced: 0,
    "high-press": 2,
    counter: 1,
    possession: 1,
  };

  const chosenTactic = tacticEl.value;
  const staminaFactor = Math.round(state.squad.reduce((sum, p) => sum + p.stamina, 0) / state.squad.length / 14);
  const moraleFactor = Math.round(state.squad.reduce((sum, p) => sum + p.morale, 0) / state.squad.length / 20);
  const power = averageRating() + tacticBoosts[chosenTactic] + moraleFactor + staminaFactor + Math.round(state.chemistry / 25);
  const rivalPower = 80 + Math.floor(Math.random() * 12);

  let result;
  if (power >= rivalPower + 4) {
    state.points += 3;
    state.budget += 5000000;
    result = `Win vs ${opponent}! Bonus prize money earned.`;
  } else if (power >= rivalPower - 2) {
    state.points += 1;
    state.budget += 1500000;
    result = `Draw vs ${opponent}. Solid but not enough.`;
  } else {
    state.chemistry = Math.max(50, state.chemistry - 2);
    result = `Loss vs ${opponent}. Fans demand better performances.`;
  }

  state.squad.forEach((p) => {
    p.stamina = Math.max(45, p.stamina - (chosenTactic === "high-press" ? 9 : 6));
    p.morale = Math.max(55, p.morale + (result.startsWith("Win") ? 2 : result.startsWith("Loss") ? -2 : 0));
  });

  state.week += 1;
  setLog(`${result} (${chosenTactic} tactic, team power ${power} vs ${rivalPower})`, !result.startsWith("Loss"));
  render();
}

function renderSquad() {
  squadListEl.innerHTML = "";
  state.squad.forEach((player, index) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="name">${player.name} (${player.position})</div>
      <div class="meta">Rating ${player.rating} | Stamina ${player.stamina} | Morale ${player.morale}</div>
      <div>
        <button data-action="train" data-index="${index}">Train</button>
        <button data-action="rest" data-index="${index}">Rest</button>
        <button data-action="sell" data-index="${index}">Sell</button>
      </div>
    `;
    squadListEl.appendChild(card);
  });
}

function renderMarket() {
  marketListEl.innerHTML = "";
  state.market.forEach((player, index) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="name">${player.name} (${player.position})</div>
      <div class="meta">Overall ${player.rating} | Price ${currency.format(player.price)}</div>
      <button data-action="buy" data-index="${index}">Buy</button>
    `;
    marketListEl.appendChild(card);
  });
}

function render() {
  renderOverview();
  renderSquad();
  renderMarket();
}

document.body.addEventListener("click", (event) => {
  if (!(event.target instanceof HTMLElement)) return;

  const action = event.target.dataset.action;
  const index = Number(event.target.dataset.index);
  if (!action || Number.isNaN(index)) return;

  if (action === "train") trainPlayer(index);
  if (action === "rest") restPlayer(index);
  if (action === "sell") sellPlayer(index);
  if (action === "buy") buyPlayer(index);
});

playMatchBtn.addEventListener("click", playMatch);
render();
setLog("Welcome, manager. Start by tuning your squad and playing week 1.");
