from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

try:
    import pygame
except Exception:
    print("This game requires pygame.")
    print("Install with: python3 -m pip install pygame")
    sys.exit(1)

WIDTH, HEIGHT = 1280, 780
FPS = 60

WHITE = (240, 246, 255)
MUTED = (160, 176, 203)
BG = (8, 13, 24)
PANEL = (18, 28, 45)
PANEL2 = (26, 40, 65)
ACCENT = (247, 194, 60)
GREEN = (34, 190, 104)
RED = (225, 90, 90)
PITCH = (21, 122, 68)
PITCH_DARK = (15, 92, 51)

ROLE_WEIGHT = {"GK": 1, "RB": 2, "LB": 2, "CB": 2, "CDM": 3, "CM": 4, "CAM": 5, "RW": 6, "LW": 6, "ST": 7}
LALIGA_TEAMS = [
    "Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Club", "Real Sociedad", "Real Betis", "Sevilla", "Valencia", "Villarreal", "Getafe",
    "Celta Vigo", "Osasuna", "Rayo Vallecano", "Mallorca", "Girona", "Las Palmas", "Alaves", "Espanyol", "Leganes", "Valladolid",
]
XI_SLOTS = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "LW", "ST", "RW"]
FORMATION_POINTS = [(580, 640), (330, 520), (485, 535), (675, 535), (835, 520), (360, 365), (575, 340), (790, 365), (350, 190), (575, 150), (800, 190)]


@dataclass
class Player:
    name: str
    pos: str
    ovr: int
    stamina: float = 88.0
    morale: float = 82.0
    price: int = 0


@dataclass
class TeamRow:
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
class MatchEvent:
    minute: int
    text: str


@dataclass
class CareerState:
    season: int = 1
    matchday: int = 1
    budget: int = 220_000_000
    chemistry: int = 82
    tactics: str = "Balanced"
    squad: List[Player] = field(default_factory=list)
    bench: List[Player] = field(default_factory=list)
    market: List[Player] = field(default_factory=list)
    table: Dict[str, TeamRow] = field(default_factory=dict)
    golden_boot: Dict[Tuple[str, str], int] = field(default_factory=dict)


class Button:
    def __init__(self, rect: pygame.Rect, label: str):
        self.rect = rect
        self.label = label

    def draw(self, surf: pygame.Surface, font: pygame.font.Font, active: bool = False):
        color = (65, 95, 145) if not active else (90, 125, 180)
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        pygame.draw.rect(surf, (110, 140, 190), self.rect, 2, border_radius=10)
        txt = font.render(self.label, True, WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


class CareerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("ADWBALL 2026")
        self.clock = pygame.time.Clock()
        self.font_sm = pygame.font.SysFont("arial", 16)
        self.font_md = pygame.font.SysFont("arial", 22)
        self.font_lg = pygame.font.SysFont("arial", 32, bold=True)
        self.font_xl = pygame.font.SysFont("arial", 48, bold=True)

        self.state = CareerState(
            squad=[
                Player("Thibaut Courtois", "GK", 90), Player("Ferland Mendy", "LB", 83), Player("Antonio Rudiger", "CB", 86),
                Player("Eder Militao", "CB", 85), Player("Dani Carvajal", "RB", 84), Player("Jude Bellingham", "CM", 88),
                Player("Federico Valverde", "CM", 87), Player("Eduardo Camavinga", "CM", 84), Player("Vinicius Jr", "LW", 89),
                Player("Kylian Mbappe", "ST", 91), Player("Rodrygo", "RW", 86),
            ],
            bench=[
                Player("Andriy Lunin", "GK", 81), Player("David Alaba", "CB", 84), Player("Fran Garcia", "LB", 80),
                Player("Lucas Vazquez", "RB", 81), Player("Aurelien Tchouameni", "CDM", 86), Player("Arda Guler", "CAM", 82),
                Player("Brahim Diaz", "RW", 83), Player("Endrick", "ST", 79), Player("Dani Ceballos", "CM", 80),
            ],
            market=[
                Player("Erling Haaland", "ST", 91, price=190_000_000), Player("Bukayo Saka", "RW", 89, price=145_000_000),
                Player("Florian Wirtz", "CAM", 88, price=126_000_000), Player("Theo Hernandez", "LB", 87, price=90_000_000),
                Player("Ruben Dias", "CB", 89, price=121_000_000), Player("Mike Maignan", "GK", 88, price=94_000_000),
                Player("Declan Rice", "CDM", 88, price=140_000_000), Player("Khvicha Kvaratskhelia", "LW", 86, price=99_000_000),
            ],
        )

        self.state.table = {t: TeamRow(t) for t in LALIGA_TEAMS}
        self.ai_rosters = self._build_ai_rosters()

        self.scene = "hub"  # hub, squad, market, standings, match
        self.selected_xi = 0
        self.selected_bench = 0
        self.selected_market = 0
        self.message = "Welcome to ADWBALL 2026."

        # Match mini-game state
        self.match_timer = 90.0
        self.rm_score = 0
        self.opp_score = 0
        self.opp_team = "Barcelona"
        self.match_events: List[MatchEvent] = []
        self.player_pos = pygame.Vector2(420, HEIGHT // 2)
        self.ball_pos = pygame.Vector2(520, HEIGHT // 2)
        self.ball_vel = pygame.Vector2(0, 0)
        self.ai_pos = pygame.Vector2(WIDTH - 220, HEIGHT // 2)

        self.nav_buttons = [
            Button(pygame.Rect(20, 20, 130, 40), "Hub"),
            Button(pygame.Rect(160, 20, 130, 40), "Squad"),
            Button(pygame.Rect(300, 20, 130, 40), "Market"),
            Button(pygame.Rect(440, 20, 130, 40), "Standings"),
            Button(pygame.Rect(580, 20, 170, 40), "Play Match"),
        ]

    def _build_ai_rosters(self) -> Dict[str, List[Player]]:
        rosters: Dict[str, List[Player]] = {}
        for team in LALIGA_TEAMS:
            if team == "Real Madrid":
                rosters[team] = self.state.squad + self.state.bench
            else:
                names = [f"{team.split()[0]} Player {i+1}" for i in range(15)]
                pos = ["GK", "RB", "LB", "CB", "CB", "CM", "CM", "CDM", "RW", "LW", "ST", "CAM", "RB", "CB", "ST"]
                rosters[team] = [Player(names[i], pos[i], 74 + (i % 8)) for i in range(15)]
        return rosters

    def avg_ovr(self) -> int:
        return round(sum(p.ovr for p in self.state.squad) / len(self.state.squad))

    def next_opponent(self) -> str:
        teams = [t for t in LALIGA_TEAMS if t != "Real Madrid"]
        return teams[(self.state.matchday - 1) % len(teams)]

    def sorted_table(self):
        return sorted(self.state.table.values(), key=lambda r: (r.pts, r.gd, r.gf), reverse=True)

    def league_pos(self) -> int:
        for i, row in enumerate(self.sorted_table(), start=1):
            if row.team == "Real Madrid":
                return i
        return 20

    def set_message(self, text: str):
        self.message = text

    def draw_top_bar(self):
        pygame.draw.rect(self.screen, PANEL, (0, 0, WIDTH, 80))
        for i, b in enumerate(self.nav_buttons):
            active = (self.scene == ["hub", "squad", "market", "standings", "match"][i])
            b.draw(self.screen, self.font_sm, active)

    def draw_message(self):
        pygame.draw.rect(self.screen, PANEL2, (20, HEIGHT - 50, WIDTH - 40, 30), border_radius=8)
        txt = self.font_sm.render(self.message[:140], True, WHITE)
        self.screen.blit(txt, (30, HEIGHT - 44))

    def draw_hub(self):
        self.screen.fill(BG)
        self.draw_top_bar()
        title = self.font_xl.render("ADWBALL 2026", True, WHITE)
        self.screen.blit(title, (20, 95))
        subtitle = self.font_md.render("Career Hub - Real Madrid", True, MUTED)
        self.screen.blit(subtitle, (24, 150))

        stats = [
            ("Season", str(self.state.season)),
            ("Matchday", str(self.state.matchday)),
            ("Budget", f"€{self.state.budget:,}"),
            ("Chemistry", str(self.state.chemistry)),
            ("Club OVR", str(self.avg_ovr())),
            ("League Pos", f"{self.league_pos()}/20"),
            ("Next", self.next_opponent()),
            ("Tactic", self.state.tactics),
        ]
        for i, (k, v) in enumerate(stats):
            x = 20 + (i % 4) * 305
            y = 200 + (i // 4) * 90
            pygame.draw.rect(self.screen, PANEL, (x, y, 285, 72), border_radius=10)
            self.screen.blit(self.font_sm.render(k, True, MUTED), (x + 12, y + 10))
            self.screen.blit(self.font_md.render(v, True, WHITE), (x + 12, y + 34))

        # tactical controls
        y = 410
        self.screen.blit(self.font_md.render("Tactics:", True, WHITE), (20, y))
        for i, t in enumerate(["Balanced", "High Press", "Counter", "Possession"]):
            rect = pygame.Rect(110 + i * 155, y - 6, 145, 34)
            active = self.state.tactics == t
            pygame.draw.rect(self.screen, (85, 122, 188) if active else PANEL, rect, border_radius=8)
            pygame.draw.rect(self.screen, (120, 155, 210), rect, 1, border_radius=8)
            self.screen.blit(self.font_sm.render(t, True, WHITE), (rect.x + 12, rect.y + 9))

        self.draw_message()

    def draw_squad(self):
        self.screen.fill(BG)
        self.draw_top_bar()
        self.screen.blit(self.font_lg.render("Starting XI & Bench", True, WHITE), (20, 95))

        pitch_rect = pygame.Rect(20, 140, 760, 560)
        pygame.draw.rect(self.screen, PITCH, pitch_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, pitch_rect, 3, border_radius=10)
        pygame.draw.line(self.screen, WHITE, (pitch_rect.centerx, pitch_rect.top), (pitch_rect.centerx, pitch_rect.bottom), 2)
        pygame.draw.circle(self.screen, WHITE, (pitch_rect.centerx, pitch_rect.centery), 65, 2)

        for i, p in enumerate(self.state.squad):
            px, py = FORMATION_POINTS[i]
            color = ACCENT if i == self.selected_xi else WHITE
            pygame.draw.circle(self.screen, color, (px, py), 18)
            name_txt = self.font_sm.render(f"{XI_SLOTS[i]} {p.name} ({p.ovr})", True, WHITE)
            self.screen.blit(name_txt, (px - name_txt.get_width() // 2, py + 22))

        # bench panel
        panel = pygame.Rect(800, 140, 460, 560)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=10)
        self.screen.blit(self.font_md.render("Bench (Select and press SPACE to swap)", True, WHITE), (815, 155))
        for i, p in enumerate(self.state.bench[:10]):
            y = 190 + i * 48
            r = pygame.Rect(815, y, 430, 40)
            pygame.draw.rect(self.screen, (70, 105, 150) if i == self.selected_bench else PANEL2, r, border_radius=8)
            self.screen.blit(self.font_sm.render(f"{i+1}. {p.pos} {p.name} | OVR {p.ovr} | STM {int(p.stamina)}", True, WHITE), (825, y + 12))

        self.draw_message()

    def draw_market(self):
        self.screen.fill(BG)
        self.draw_top_bar()
        self.screen.blit(self.font_lg.render("Transfer Market", True, WHITE), (20, 95))
        self.screen.blit(self.font_sm.render("Use UP/DOWN, ENTER to sign selected player", True, MUTED), (20, 132))

        for i, p in enumerate(self.state.market):
            y = 160 + i * 56
            if y > HEIGHT - 80:
                break
            row = pygame.Rect(20, y, WIDTH - 40, 46)
            pygame.draw.rect(self.screen, (74, 108, 155) if i == self.selected_market else PANEL, row, border_radius=8)
            self.screen.blit(self.font_md.render(f"{p.name}", True, WHITE), (34, y + 10))
            info = f"{p.pos}  OVR {p.ovr}  Price €{p.price:,}"
            self.screen.blit(self.font_sm.render(info, True, MUTED), (520, y + 14))

        self.draw_message()

    def draw_standings(self):
        self.screen.fill(BG)
        self.draw_top_bar()
        self.screen.blit(self.font_lg.render("LaLiga Standings + Golden Boot", True, WHITE), (20, 95))

        table = self.sorted_table()
        for i, r in enumerate(table[:12], start=1):
            y = 140 + (i - 1) * 40
            row = pygame.Rect(20, y, 620, 34)
            pygame.draw.rect(self.screen, PANEL if r.team != "Real Madrid" else (86, 124, 186), row, border_radius=6)
            line = f"{i:2d}. {r.team:16s} P{r.p:2d} W{r.w:2d} D{r.d:2d} L{r.l:2d} GD{r.gd:3d} Pts {r.pts:3d}"
            self.screen.blit(self.font_sm.render(line, True, WHITE), (28, y + 9))

        scorers = sorted(self.state.golden_boot.items(), key=lambda kv: kv[1], reverse=True)[:12]
        self.screen.blit(self.font_md.render("Golden Boot", True, WHITE), (690, 140))
        for i, ((team, player), goals) in enumerate(scorers):
            y = 172 + i * 36
            self.screen.blit(self.font_sm.render(f"{i+1:2d}. {player[:17]:17s} {team[:13]:13s} {goals}", True, WHITE), (690, y))

        self.draw_message()

    def start_match(self):
        self.scene = "match"
        self.match_timer = 90.0
        self.rm_score = 0
        self.opp_score = 0
        self.opp_team = self.next_opponent()
        self.match_events.clear()
        self.player_pos = pygame.Vector2(280, HEIGHT // 2)
        self.ball_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.ball_vel = pygame.Vector2(0, 0)
        self.ai_pos = pygame.Vector2(WIDTH - 250, HEIGHT // 2)
        self.set_message("Kick-off! Move with WASD/Arrows, shoot with SPACE near ball.")

    def weighted_scorer(self, team: str) -> Player:
        roster = self.state.squad if team == "Real Madrid" else self.ai_rosters[team]
        pool: List[Player] = []
        for p in roster:
            pool.extend([p] * ROLE_WEIGHT.get(p.pos, 2))
        return random.choice(pool)

    def add_goal_event(self, team: str, minute: int):
        scorer = self.weighted_scorer(team)
        self.state.golden_boot[(team, scorer.name)] = self.state.golden_boot.get((team, scorer.name), 0) + 1
        text = f"{minute}' Goal {team}: {scorer.name}"
        self.match_events.append(MatchEvent(minute, text))
        self.match_events = self.match_events[-8:]

    def update_match(self, dt: float, keys):
        speed = 250
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1
        if move.length_squared() > 0:
            move = move.normalize() * speed * dt
            self.player_pos += move

        # clamp in pitch area
        self.player_pos.x = max(70, min(WIDTH - 70, self.player_pos.x))
        self.player_pos.y = max(120, min(HEIGHT - 70, self.player_pos.y))

        # AI chases ball
        direction = (self.ball_pos - self.ai_pos)
        if direction.length_squared() > 1:
            self.ai_pos += direction.normalize() * 170 * dt

        # ball friction
        self.ball_pos += self.ball_vel * dt
        self.ball_vel *= 0.985

        # collide with players
        if self.player_pos.distance_to(self.ball_pos) < 30:
            self.ball_vel += (self.ball_pos - self.player_pos).normalize() * 180 * dt
        if self.ai_pos.distance_to(self.ball_pos) < 28:
            self.ball_vel += (self.ball_pos - self.ai_pos).normalize() * 200 * dt

        # goal checks
        if self.ball_pos.x < 45 and HEIGHT // 2 - 80 < self.ball_pos.y < HEIGHT // 2 + 80:
            self.opp_score += 1
            self.add_goal_event(self.opp_team, max(1, int(90 - self.match_timer)))
            self.ball_pos.update(WIDTH // 2, HEIGHT // 2)
            self.ball_vel.update(0, 0)

        if self.ball_pos.x > WIDTH - 45 and HEIGHT // 2 - 80 < self.ball_pos.y < HEIGHT // 2 + 80:
            self.rm_score += 1
            self.add_goal_event("Real Madrid", max(1, int(90 - self.match_timer)))
            self.ball_pos.update(WIDTH // 2, HEIGHT // 2)
            self.ball_vel.update(0, 0)

        # boundaries
        if self.ball_pos.y < 110 or self.ball_pos.y > HEIGHT - 45:
            self.ball_vel.y *= -0.9
        if self.ball_pos.x < 25 or self.ball_pos.x > WIDTH - 25:
            self.ball_vel.x *= -0.9
        self.ball_pos.x = max(20, min(WIDTH - 20, self.ball_pos.x))
        self.ball_pos.y = max(110, min(HEIGHT - 40, self.ball_pos.y))

        self.match_timer -= dt * 3.6  # fast timeline
        if self.match_timer <= 0:
            self.finish_match()

    def finish_match(self):
        opp = self.opp_team
        rm, og = self.rm_score, self.opp_score
        self.update_table("Real Madrid", opp, rm, og)
        others = [t for t in LALIGA_TEAMS if t not in {"Real Madrid", opp}]
        for i in range(0, len(others), 2):
            self.sim_other_fixture(others[i], others[i + 1])

        rest_days = random.randint(2, 4)
        for p in self.state.squad:
            p.stamina = min(100, p.stamina + rest_days * 6)
            p.morale = max(58, min(99, p.morale + (2 if rm > og else -2 if rm < og else 0)))

        if rm > og:
            self.state.budget += 5_000_000
            self.state.chemistry = min(99, self.state.chemistry + 1)
        elif rm == og:
            self.state.budget += 2_000_000
        else:
            self.state.chemistry = max(65, self.state.chemistry - 2)

        self.state.matchday += 1
        if self.state.matchday > 38:
            self.state.season += 1
            self.state.matchday = 1
            self.state.table = {t: TeamRow(t) for t in LALIGA_TEAMS}

        self.scene = "hub"
        self.set_message(f"FT Real Madrid {rm}-{og} {opp}. Rest gap: {rest_days} days.")

    def update_table(self, home: str, away: str, hg: int, ag: int):
        h, a = self.state.table[home], self.state.table[away]
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

    def sim_other_fixture(self, home: str, away: str):
        hg = self.sim_goals(80 + random.randint(0, 10))
        ag = self.sim_goals(80 + random.randint(0, 10))
        self.update_table(home, away, hg, ag)
        for _ in range(hg):
            self.add_goal_event(home, random.randint(1, 90))
        for _ in range(ag):
            self.add_goal_event(away, random.randint(1, 90))

    @staticmethod
    def sim_goals(power: int) -> int:
        xg = max(0.2, (power - 72) / 13 + random.random() * 1.4)
        b = math.floor(xg)
        return min(6, max(0, b + (1 if random.random() < (xg - b) else 0)))

    def train_selected(self):
        p = self.state.squad[self.selected_xi]
        cost = 1_800_000 + max(0, p.ovr - 84) * 1_200_000
        chance = max(0.12, 0.92 - (p.ovr - 75) * 0.04)
        if p.ovr >= 99:
            self.set_message(f"{p.name} is already 99 OVR.")
            return
        if self.state.budget < cost:
            self.set_message("Not enough budget for targeted training.")
            return
        self.state.budget -= cost
        p.stamina = max(55, p.stamina - 3)
        if random.random() <= chance:
            p.ovr = min(99, p.ovr + 1)
            self.set_message(f"Training success: {p.name} -> {p.ovr} OVR")
        else:
            self.set_message(f"Training done: no OVR gain for {p.name}")

    def swap_selected(self):
        if not self.state.bench:
            return
        b = self.state.bench[self.selected_bench]
        s = self.state.squad[self.selected_xi]
        self.state.squad[self.selected_xi], self.state.bench[self.selected_bench] = (
            Player(b.name, XI_SLOTS[self.selected_xi], b.ovr, b.stamina, b.morale, b.price),
            s,
        )
        self.state.chemistry = max(68, self.state.chemistry - 1)
        self.set_message(f"{b.name} starts, {s.name} to bench.")

    def buy_selected(self):
        if not self.state.market:
            return
        p = self.state.market[self.selected_market]
        if self.state.budget < p.price:
            self.set_message(f"Cannot afford {p.name}")
            return
        slot = next((i for i, role in enumerate(XI_SLOTS) if role == p.pos or (role in {"CM", "CDM", "CAM"} and p.pos in {"CM", "CDM", "CAM"})), 10)
        moved = self.state.squad[slot]
        self.state.squad[slot] = Player(p.name, XI_SLOTS[slot], p.ovr, p.stamina, p.morale, p.price)
        self.state.bench.insert(0, moved)
        self.state.budget -= p.price
        self.state.market.pop(self.selected_market)
        self.selected_market = max(0, min(self.selected_market, len(self.state.market) - 1))
        self.set_message(f"Signed {p.name}. {moved.name} to bench.")

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                pos = ev.pos
                for i, b in enumerate(self.nav_buttons):
                    if b.hit(pos):
                        target = ["hub", "squad", "market", "standings", "match"][i]
                        if target == "match":
                            self.start_match()
                        else:
                            self.scene = target
                if self.scene == "hub":
                    # tactics buttons
                    for i, t in enumerate(["Balanced", "High Press", "Counter", "Possession"]):
                        rect = pygame.Rect(110 + i * 155, 404, 145, 34)
                        if rect.collidepoint(pos):
                            self.state.tactics = t
                            self.set_message(f"Tactic changed to {t}")
            if ev.type == pygame.KEYDOWN:
                if self.scene == "squad":
                    if ev.key == pygame.K_UP:
                        self.selected_xi = (self.selected_xi - 1) % len(self.state.squad)
                    if ev.key == pygame.K_DOWN:
                        self.selected_xi = (self.selected_xi + 1) % len(self.state.squad)
                    if ev.key == pygame.K_LEFT:
                        self.selected_bench = (self.selected_bench - 1) % len(self.state.bench)
                    if ev.key == pygame.K_RIGHT:
                        self.selected_bench = (self.selected_bench + 1) % len(self.state.bench)
                    if ev.key == pygame.K_t:
                        self.train_selected()
                    if ev.key == pygame.K_SPACE:
                        self.swap_selected()
                elif self.scene == "market":
                    if ev.key == pygame.K_UP:
                        self.selected_market = (self.selected_market - 1) % len(self.state.market)
                    if ev.key == pygame.K_DOWN:
                        self.selected_market = (self.selected_market + 1) % len(self.state.market)
                    if ev.key == pygame.K_RETURN:
                        self.buy_selected()
                elif self.scene == "match":
                    if ev.key == pygame.K_SPACE and self.player_pos.distance_to(self.ball_pos) < 45:
                        shoot = pygame.Vector2(1, random.uniform(-0.25, 0.25))
                        self.ball_vel += shoot.normalize() * 460

    def draw_match(self):
        self.screen.fill(BG)
        self.draw_top_bar()
        field_rect = pygame.Rect(20, 95, WIDTH - 40, HEIGHT - 180)
        pygame.draw.rect(self.screen, PITCH, field_rect, border_radius=12)
        for i in range(10):
            y = field_rect.y + i * (field_rect.height // 10)
            pygame.draw.line(self.screen, PITCH_DARK if i % 2 else PITCH, (field_rect.x, y), (field_rect.right, y), field_rect.height // 10)
        pygame.draw.rect(self.screen, WHITE, field_rect, 3, border_radius=12)
        pygame.draw.line(self.screen, WHITE, (field_rect.centerx, field_rect.top), (field_rect.centerx, field_rect.bottom), 2)
        pygame.draw.circle(self.screen, WHITE, field_rect.center, 68, 2)
        pygame.draw.rect(self.screen, WHITE, (field_rect.x - 1, field_rect.centery - 80, 26, 160), 2)
        pygame.draw.rect(self.screen, WHITE, (field_rect.right - 25, field_rect.centery - 80, 26, 160), 2)

        pygame.draw.circle(self.screen, (255, 230, 80), (int(self.player_pos.x), int(self.player_pos.y)), 16)
        pygame.draw.circle(self.screen, (230, 95, 95), (int(self.ai_pos.x), int(self.ai_pos.y)), 16)
        pygame.draw.circle(self.screen, WHITE, (int(self.ball_pos.x), int(self.ball_pos.y)), 10)

        score = self.font_lg.render(f"Real Madrid {self.rm_score} - {self.opp_score} {self.opp_team}", True, WHITE)
        self.screen.blit(score, score.get_rect(center=(WIDTH // 2, 40)))
        time = self.font_md.render(f"{max(0, int(90 - self.match_timer))}'", True, ACCENT)
        self.screen.blit(time, (WIDTH // 2 - 14, 65))

        # event log
        panel = pygame.Rect(20, HEIGHT - 78, WIDTH - 40, 56)
        pygame.draw.rect(self.screen, PANEL2, panel, border_radius=8)
        last = self.match_events[-2:]
        text = " | ".join(e.text for e in last) if last else "WASD/Arrows move, SPACE shoot"
        self.screen.blit(self.font_sm.render(text[:160], True, WHITE), (30, HEIGHT - 58))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            keys = pygame.key.get_pressed()

            if self.scene == "hub":
                self.draw_hub()
            elif self.scene == "squad":
                self.draw_squad()
            elif self.scene == "market":
                self.draw_market()
            elif self.scene == "standings":
                self.draw_standings()
            elif self.scene == "match":
                self.update_match(dt, keys)
                self.draw_match()

            pygame.display.flip()


if __name__ == "__main__":
    CareerGame().run()
