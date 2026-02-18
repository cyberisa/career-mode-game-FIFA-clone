from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict, List, Tuple


ROLE_WEIGHT = {
    "GK": 1,
    "RB": 2,
    "LB": 2,
    "CB": 2,
    "CDM": 3,
    "CM": 4,
    "CAM": 5,
    "RW": 6,
    "LW": 6,
    "ST": 7,
}

LALIGA_TEAMS = [
    "Real Madrid",
    "Barcelona",
    "Atletico Madrid",
    "Athletic Club",
    "Real Sociedad",
    "Real Betis",
    "Sevilla",
    "Valencia",
    "Villarreal",
    "Getafe",
    "Celta Vigo",
    "Osasuna",
    "Rayo Vallecano",
    "Mallorca",
    "Girona",
    "Las Palmas",
    "Alaves",
    "Espanyol",
    "Leganes",
    "Valladolid",
]

XI_SLOTS = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "LW", "ST", "RW"]


@dataclass
class Player:
    name: str
    position: str
    rating: int
    stamina: int = 88
    morale: int = 82
    price: int = 0


@dataclass
class TeamTableRow:
    team: str
    pts: int = 0
    p: int = 0
    w: int = 0
    d: int = 0
    l: int = 0
    gf: int = 0
    ga: int = 0

    @property
    def gd(self) -> int:
        return self.gf - self.ga


@dataclass
class PlayerStats:
    goals: int = 0
    assists: int = 0
    clean_sheets: int = 0
    apps: int = 0


@dataclass
class CareerGame:
    season: int = 1
    matchday: int = 1
    budget: int = 220_000_000
    chemistry: int = 82
    tactic: str = "balanced"
    squad: List[Player] = field(default_factory=list)
    bench: List[Player] = field(default_factory=list)
    market: List[Player] = field(default_factory=list)
    table: Dict[str, TeamTableRow] = field(default_factory=dict)
    player_stats: Dict[str, PlayerStats] = field(default_factory=dict)
    league_scorers: Dict[Tuple[str, str], int] = field(default_factory=dict)
    team_rosters: Dict[str, List[Player]] = field(default_factory=dict)

    @staticmethod
    def _p(name: str, pos: str, rating: int, price: int = 0) -> Player:
        return Player(name=name, position=pos, rating=rating, price=price)

    def __post_init__(self) -> None:
        self.squad = [
            self._p("Thibaut Courtois", "GK", 90),
            self._p("Ferland Mendy", "LB", 83),
            self._p("Antonio Rudiger", "CB", 86),
            self._p("Eder Militao", "CB", 85),
            self._p("Dani Carvajal", "RB", 84),
            self._p("Jude Bellingham", "CM", 88),
            self._p("Federico Valverde", "CM", 87),
            self._p("Eduardo Camavinga", "CM", 84),
            self._p("Vinicius Jr", "LW", 89),
            self._p("Kylian Mbappe", "ST", 91),
            self._p("Rodrygo", "RW", 86),
        ]
        self.bench = [
            self._p("Andriy Lunin", "GK", 81),
            self._p("Fran Garcia", "LB", 80),
            self._p("David Alaba", "CB", 84),
            self._p("Lucas Vazquez", "RB", 81),
            self._p("Aurelien Tchouameni", "CDM", 86),
            self._p("Arda Guler", "CAM", 82),
            self._p("Brahim Diaz", "RW", 83),
            self._p("Endrick", "ST", 79),
            self._p("Dani Ceballos", "CM", 80),
        ]
        self.market = [
            self._p("Erling Haaland", "ST", 91, 190_000_000),
            self._p("Lautaro Martinez", "ST", 89, 132_000_000),
            self._p("Victor Osimhen", "ST", 89, 146_000_000),
            self._p("Mohamed Salah", "RW", 89, 98_000_000),
            self._p("Bukayo Saka", "RW", 89, 145_000_000),
            self._p("Phil Foden", "RW", 89, 150_000_000),
            self._p("Jamal Musiala", "CAM", 88, 134_000_000),
            self._p("Florian Wirtz", "CAM", 88, 126_000_000),
            self._p("Pedri", "CM", 88, 143_000_000),
            self._p("Declan Rice", "CDM", 88, 140_000_000),
            self._p("Khvicha Kvaratskhelia", "LW", 86, 99_000_000),
            self._p("Theo Hernandez", "LB", 87, 90_000_000),
            self._p("Achraf Hakimi", "RB", 86, 84_000_000),
            self._p("William Saliba", "CB", 87, 104_000_000),
            self._p("Ruben Dias", "CB", 89, 121_000_000),
            self._p("Mike Maignan", "GK", 88, 94_000_000),
        ]
        self._build_table()
        self._build_ai_rosters()
        self._ensure_stats()

    def _build_table(self) -> None:
        self.table = {team: TeamTableRow(team=team) for team in LALIGA_TEAMS}

    def _build_ai_rosters(self) -> None:
        self.team_rosters = {}
        for team in LALIGA_TEAMS:
            if team == "Real Madrid":
                self.team_rosters[team] = list(self.squad) + list(self.bench)
                continue
            roster = []
            for i in range(15):
                pos = ["GK", "RB", "LB", "CB", "CB", "CM", "CM", "CDM", "RW", "LW", "ST", "CAM", "RB", "CB", "ST"][i]
                roster.append(self._p(f"{team.split()[0]} Player {i+1}", pos, 74 + (i % 8)))
            self.team_rosters[team] = roster

    def _ensure_stats(self) -> None:
        for p in self.squad + self.bench:
            if p.name not in self.player_stats:
                self.player_stats[p.name] = PlayerStats()

    def average_rating(self) -> int:
        return round(sum(p.rating for p in self.squad) / len(self.squad))

    def next_opponent(self) -> str:
        opp = [t for t in LALIGA_TEAMS if t != "Real Madrid"]
        return opp[(self.matchday - 1) % len(opp)]

    def sorted_table(self) -> List[TeamTableRow]:
        return sorted(self.table.values(), key=lambda r: (r.pts, r.gd, r.gf), reverse=True)

    def position(self) -> int:
        return next(i for i, r in enumerate(self.sorted_table(), start=1) if r.team == "Real Madrid")

    def restore_stamina(self) -> int:
        days = random.randint(2, 4)
        gain = days * 6
        for p in self.squad:
            p.stamina = min(100, p.stamina + gain)
        return days

    def _weighted_scorer(self, team: str) -> Player:
        roster = self.squad if team == "Real Madrid" else self.team_rosters[team]
        pool: List[Player] = []
        for p in roster:
            pool.extend([p] * ROLE_WEIGHT.get(p.position, 2))
        return random.choice(pool)

    def _simulate_goals(self, power: int) -> int:
        xg = max(0.25, (power - 72) / 13 + random.random() * 1.5)
        base = int(xg)
        return min(6, max(0, base + (1 if random.random() < (xg - base) else 0)))

    def _add_league_goal(self, team: str, player: str) -> None:
        key = (team, player)
        self.league_scorers[key] = self.league_scorers.get(key, 0) + 1

    def _update_table(self, home: str, away: str, hg: int, ag: int) -> None:
        h, a = self.table[home], self.table[away]
        h.p += 1
        a.p += 1
        h.gf += hg
        h.ga += ag
        a.gf += ag
        a.ga += hg
        if hg > ag:
            h.w += 1
            h.pts += 3
            a.l += 1
        elif ag > hg:
            a.w += 1
            a.pts += 3
            h.l += 1
        else:
            h.d += 1
            a.d += 1
            h.pts += 1
            a.pts += 1

    def _simulate_other_fixture(self, home: str, away: str) -> None:
        hg = self._simulate_goals(79 + random.randint(0, 10))
        ag = self._simulate_goals(79 + random.randint(0, 10))
        self._update_table(home, away, hg, ag)
        for _ in range(hg):
            self._add_league_goal(home, self._weighted_scorer(home).name)
        for _ in range(ag):
            self._add_league_goal(away, self._weighted_scorer(away).name)

    def _register_rm_events(self, goals: int, conceded: int) -> List[Tuple[int, str, str]]:
        for p in self.squad:
            self.player_stats[p.name].apps += 1
        events: List[Tuple[int, str, str]] = []
        for _ in range(goals):
            scorer = self._weighted_scorer("Real Madrid")
            assister = self._weighted_scorer("Real Madrid")
            self.player_stats[scorer.name].goals += 1
            self.player_stats[assister.name].assists += 1
            self._add_league_goal("Real Madrid", scorer.name)
            events.append((random.randint(5, 90), scorer.name, assister.name))
        if conceded == 0:
            self.player_stats[self.squad[0].name].clean_sheets += 1
        events.sort(key=lambda x: x[0])
        return events

    def play_matchday(self) -> str:
        rest_days = self.restore_stamina()
        opponent = self.next_opponent()
        tactic_boost = {"balanced": 0, "high-press": 2, "counter": 1, "possession": 1}[self.tactic]
        stamina = round(sum(p.stamina for p in self.squad) / len(self.squad) / 12)
        morale = round(sum(p.morale for p in self.squad) / len(self.squad) / 20)
        rm_power = self.average_rating() + tactic_boost + stamina + morale + round(self.chemistry / 24)
        opp_power = 80 + random.randint(0, 12)

        rm_goals = self._simulate_goals(rm_power)
        opp_goals = self._simulate_goals(opp_power)
        self._update_table("Real Madrid", opponent, rm_goals, opp_goals)

        events = self._register_rm_events(rm_goals, opp_goals)
        for _ in range(opp_goals):
            self._add_league_goal(opponent, self._weighted_scorer(opponent).name)

        others = [t for t in LALIGA_TEAMS if t not in {"Real Madrid", opponent}]
        for i in range(0, len(others), 2):
            self._simulate_other_fixture(others[i], others[i + 1])

        for p in self.squad:
            p.stamina = max(46, p.stamina - (9 if self.tactic == "high-press" else 6))
            p.morale = max(58, min(99, p.morale + (2 if rm_goals > opp_goals else -2 if rm_goals < opp_goals else 0)))

        if rm_goals > opp_goals:
            self.budget += 5_000_000
            self.chemistry = min(99, self.chemistry + 1)
        elif rm_goals == opp_goals:
            self.budget += 2_000_000
        else:
            self.chemistry = max(65, self.chemistry - 2)

        event_lines = [f"  {m}' {s} (assist: {a})" for m, s, a in events] if events else ["  No RM goals"]
        summary = [
            f"MD{self.matchday}: Real Madrid {rm_goals}-{opp_goals} {opponent} (rest {rest_days} days)",
            *event_lines,
        ]

        self.matchday += 1
        if self.matchday > 38:
            pos = self.position()
            summary.append(f"Season {self.season} finished in position #{pos}. New season begins.")
            self.season += 1
            self.matchday = 1
            self._build_table()

        return "\n".join(summary)

    def upgrade_player(self, index: int) -> str:
        p = self.squad[index]
        cost = 1_800_000 + max(0, p.rating - 84) * 1_200_000
        chance = max(0.12, 0.92 - (p.rating - 75) * 0.04)
        if p.rating >= 99:
            return f"{p.name} is already 99 OVR."
        if self.budget < cost:
            return "Not enough budget for targeted training."
        self.budget -= cost
        p.stamina = max(55, p.stamina - 3)
        if random.random() <= chance:
            p.rating = min(99, p.rating + 1)
            return f"Training success! {p.name} is now {p.rating} OVR."
        return f"Training complete, but no OVR gain for {p.name}."

    def swap_bench(self, bench_index: int, starter_index: int) -> str:
        in_player = self.bench[bench_index]
        out_player = self.squad[starter_index]
        self.squad[starter_index] = Player(
            name=in_player.name,
            position=XI_SLOTS[starter_index],
            rating=in_player.rating,
            stamina=in_player.stamina,
            morale=in_player.morale,
            price=in_player.price,
        )
        self.bench[bench_index] = out_player
        self.chemistry = max(68, self.chemistry - 1)
        self._ensure_stats()
        return f"Swap done: {in_player.name} starts, {out_player.name} goes to bench."

    def buy_player(self, market_index: int) -> str:
        target = self.market[market_index]
        if self.budget < target.price:
            return f"Cannot afford {target.name}."
        compatible = next(
            (
                i
                for i, slot in enumerate(XI_SLOTS)
                if slot == target.position
                or (slot in {"CM", "CDM", "CAM"} and target.position in {"CM", "CDM", "CAM"})
            ),
            10,
        )
        moved = self.squad[compatible]
        self.budget -= target.price
        self.squad[compatible] = Player(
            name=target.name,
            position=XI_SLOTS[compatible],
            rating=target.rating,
            stamina=target.stamina,
            morale=target.morale,
            price=target.price,
        )
        self.bench.insert(0, moved)
        self.market.pop(market_index)
        self._ensure_stats()
        return f"Signed {target.name}. {moved.name} moved to bench."

    def top_rm_scorers(self) -> List[Tuple[str, int]]:
        return sorted(((n, s.goals) for n, s in self.player_stats.items()), key=lambda x: x[1], reverse=True)[:5]

    def top_laliga_scorers(self) -> List[Tuple[str, str, int]]:
        rows = sorted(self.league_scorers.items(), key=lambda kv: kv[1], reverse=True)[:10]
        return [(team, player, goals) for (team, player), goals in rows]


def print_menu() -> None:
    print("\n=== ADWBALL 2026 (Terminal Edition) ===")
    print("1) Club dashboard")
    print("2) Play matchday")
    print("3) Set tactic (balanced/high-press/counter/possession)")
    print("4) Train player")
    print("5) Swap bench player into XI")
    print("6) Buy from transfer market")
    print("7) Show standings")
    print("8) Show top scorers")
    print("9) Exit")


def show_dashboard(game: CareerGame) -> None:
    print(f"\nSeason {game.season} | Matchday {game.matchday} | Next: {game.next_opponent()}")
    print(f"Budget: €{game.budget:,} | Chemistry: {game.chemistry} | XI OVR: {game.average_rating()} | Position: {game.position()}/20")
    print("\nStarting XI")
    for i, p in enumerate(game.squad):
        print(f"{i:2d}. {XI_SLOTS[i]:3s} {p.name:22s} OVR {p.rating:2d}  STM {p.stamina:3d} MOR {p.morale:3d}")
    print("\nBench")
    for i, p in enumerate(game.bench):
        print(f"{i:2d}. {p.position:3s} {p.name:22s} OVR {p.rating:2d}  STM {p.stamina:3d}")


def show_standings(game: CareerGame) -> None:
    print("\n--- LaLiga Standings ---")
    for i, row in enumerate(game.sorted_table(), start=1):
        mark = "*" if row.team == "Real Madrid" else " "
        print(f"{mark}{i:2d}. {row.team:16s} P {row.p:2d}  W {row.w:2d} D {row.d:2d} L {row.l:2d} GD {row.gd:3d} Pts {row.pts:3d}")


def show_scorers(game: CareerGame) -> None:
    print("\n--- Real Madrid Top Scorers ---")
    for name, goals in game.top_rm_scorers():
        print(f"{name:24s} {goals}")
    print("\n--- LaLiga Golden Boot Race ---")
    for team, player, goals in game.top_laliga_scorers():
        print(f"{player:24s} {team:16s} {goals}")


def run() -> None:
    game = CareerGame()
    while True:
        print_menu()
        choice = input("Choose action: ").strip()

        if choice == "1":
            show_dashboard(game)
        elif choice == "2":
            print("\n" + game.play_matchday())
        elif choice == "3":
            tactic = input("Enter tactic: ").strip().lower()
            if tactic in {"balanced", "high-press", "counter", "possession"}:
                game.tactic = tactic
                print(f"Tactic set to {tactic}.")
            else:
                print("Invalid tactic.")
        elif choice == "4":
            show_dashboard(game)
            idx = int(input("Train which XI index? ").strip())
            if 0 <= idx < len(game.squad):
                print(game.upgrade_player(idx))
            else:
                print("Invalid index.")
        elif choice == "5":
            show_dashboard(game)
            b_idx = int(input("Bench index to bring in: ").strip())
            s_idx = int(input("XI index to replace: ").strip())
            if 0 <= b_idx < len(game.bench) and 0 <= s_idx < len(game.squad):
                print(game.swap_bench(b_idx, s_idx))
            else:
                print("Invalid indexes.")
        elif choice == "6":
            print("\nTransfer Market")
            for i, p in enumerate(game.market):
                print(f"{i:2d}. {p.name:24s} {p.position:3s} OVR {p.rating:2d}  €{p.price:,}")
            idx = int(input("Market index to sign: ").strip())
            if 0 <= idx < len(game.market):
                print(game.buy_player(idx))
            else:
                print("Invalid index.")
        elif choice == "7":
            show_standings(game)
        elif choice == "8":
            show_scorers(game)
        elif choice == "9":
            print("Good luck, manager.")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    run()
