from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

try:
    import pygame
except Exception:
    print("This game requires pygame.")
    print("Install with: python3 -m pip install pygame")
    sys.exit(1)


WIDTH, HEIGHT = 1360, 820
FPS = 60

# Colors
WHITE = (242, 246, 255)
MUTED = (152, 170, 198)
BG = (7, 12, 24)
PANEL = (18, 28, 48)
PANEL_ALT = (26, 40, 66)
ACCENT = (246, 194, 60)
GOOD = (62, 204, 126)
BAD = (228, 97, 97)
PITCH = (24, 128, 70)
PITCH_DARK = (17, 95, 53)
SKY_TOP = (22, 44, 90)
SKY_BOTTOM = (8, 12, 24)

ROLE_WEIGHT = {"GK": 1, "RB": 2, "LB": 2, "CB": 2, "CDM": 3, "CM": 4, "CAM": 5, "RW": 6, "LW": 6, "ST": 7}
XI_SLOTS = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "LW", "ST", "RW"]
LALIGA_TEAMS = [
    "Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Club", "Real Sociedad", "Real Betis", "Sevilla", "Valencia", "Villarreal", "Getafe",
    "Celta Vigo", "Osasuna", "Rayo Vallecano", "Mallorca", "Girona", "Las Palmas", "Alaves", "Espanyol", "Leganes", "Valladolid",
]


@dataclass
class Player:
    name: str
    pos: str
    ovr: int
    pace: int
    shooting: int
    passing: int
    defending: int
    dribbling: int
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
class PlayerSeasonStats:
    goals: int = 0
    assists: int = 0
    clean_sheets: int = 0


@dataclass
class CareerState:
    season: int = 1
    matchday: int = 1
    budget: int = 220_000_000
    chemistry: int = 82
    board_confidence: int = 70
    tactics: str = "Balanced"
    dev_points: int = 5
    squad: List[Player] = field(default_factory=list)
    bench: List[Player] = field(default_factory=list)
    market: List[Player] = field(default_factory=list)
    table: Dict[str, TeamRow] = field(default_factory=dict)
    golden_boot: Dict[Tuple[str, str], int] = field(default_factory=dict)
    player_stats: Dict[str, PlayerSeasonStats] = field(default_factory=dict)


@dataclass
class MatchActor:
    player: Player
    team: str
    x: float
    y: float
    role: str
    control: bool = False
    vx: float = 0.0
    vy: float = 0.0
    stamina_live: float = 100.0


class Button:
    def __init__(self, rect: pygame.Rect, text: str, scene: str):
        self.rect = rect
        self.text = text
        self.scene = scene

    def draw(self, surf: pygame.Surface, font: pygame.font.Font, active: bool):
        bg = (83, 122, 184) if active else (56, 86, 136)
        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, (132, 168, 220), self.rect, 2, border_radius=10)
        txt = font.render(self.text, True, WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def hit(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class CareerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("ADWBALL 2026 - Ultimate Career Mode")
        self.clock = pygame.time.Clock()

        self.font_xs = pygame.font.SysFont("arial", 14)
        self.font_sm = pygame.font.SysFont("arial", 16)
        self.font_md = pygame.font.SysFont("arial", 22)
        self.font_lg = pygame.font.SysFont("arial", 34, bold=True)
        self.font_xl = pygame.font.SysFont("arial", 52, bold=True)

        self.state = self.build_initial_state()
        self.ai_rosters = self.build_ai_rosters()

        self.scene = "hub"
        self.message = "Welcome to ADWBALL 2026. Build greatness."

        # selections
        self.selected_xi = 0
        self.selected_bench = 0
        self.selected_market = 0

        # match state
        self.match_active = False
        self.match_timer = 90.0
        self.half_announced = False
        self.rm_score = 0
        self.opp_score = 0
        self.opp_team = "Barcelona"
        self.weather = "Clear"
        self.rm_actors: List[MatchActor] = []
        self.opp_actors: List[MatchActor] = []
        self.ball = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.ball_vel = pygame.Vector2(0, 0)
        self.last_touch_rm: Optional[str] = None
        self.last_touch_rm_prev: Optional[str] = None
        self.events: List[MatchEvent] = []

        self.nav_buttons = [
            Button(pygame.Rect(18, 20, 145, 42), "Hub", "hub"),
            Button(pygame.Rect(170, 20, 145, 42), "Squad", "squad"),
            Button(pygame.Rect(322, 20, 145, 42), "Market", "market"),
            Button(pygame.Rect(474, 20, 155, 42), "Standings", "standings"),
            Button(pygame.Rect(636, 20, 185, 42), "Play Match", "match"),
        ]

    @staticmethod
    def create_player(name: str, pos: str, ovr: int, price: int = 0) -> Player:
        noise = random.randint(-4, 4)
        return Player(
            name=name,
            pos=pos,
            ovr=ovr,
            pace=max(55, min(99, ovr + noise)),
            shooting=max(50, min(99, ovr + random.randint(-6, 5))),
            passing=max(50, min(99, ovr + random.randint(-5, 6))),
            defending=max(45, min(99, ovr + random.randint(-7, 7))),
            dribbling=max(50, min(99, ovr + random.randint(-5, 6))),
            price=price,
        )

    def build_initial_state(self) -> CareerState:
        squad = [
            self.create_player("Thibaut Courtois", "GK", 90), self.create_player("Ferland Mendy", "LB", 83), self.create_player("Antonio Rudiger", "CB", 86),
            self.create_player("Eder Militao", "CB", 85), self.create_player("Dani Carvajal", "RB", 84), self.create_player("Jude Bellingham", "CM", 88),
            self.create_player("Federico Valverde", "CM", 87), self.create_player("Eduardo Camavinga", "CM", 84), self.create_player("Vinicius Jr", "LW", 89),
            self.create_player("Kylian Mbappe", "ST", 91), self.create_player("Rodrygo", "RW", 86),
        ]
        bench = [
            self.create_player("Andriy Lunin", "GK", 81), self.create_player("David Alaba", "CB", 84), self.create_player("Fran Garcia", "LB", 80),
            self.create_player("Lucas Vazquez", "RB", 81), self.create_player("Aurelien Tchouameni", "CDM", 86), self.create_player("Arda Guler", "CAM", 82),
            self.create_player("Brahim Diaz", "RW", 83), self.create_player("Endrick", "ST", 79), self.create_player("Dani Ceballos", "CM", 80),
        ]
        market = [
            self.create_player("Erling Haaland", "ST", 91, 190_000_000), self.create_player("Bukayo Saka", "RW", 89, 145_000_000),
            self.create_player("Florian Wirtz", "CAM", 88, 126_000_000), self.create_player("Theo Hernandez", "LB", 87, 90_000_000),
            self.create_player("Ruben Dias", "CB", 89, 121_000_000), self.create_player("Mike Maignan", "GK", 88, 94_000_000),
            self.create_player("Declan Rice", "CDM", 88, 140_000_000), self.create_player("Khvicha Kvaratskhelia", "LW", 86, 99_000_000),
            self.create_player("Victor Osimhen", "ST", 89, 146_000_000), self.create_player("Jamal Musiala", "CAM", 88, 134_000_000),
            self.create_player("Achraf Hakimi", "RB", 86, 84_000_000), self.create_player("Ronald Araujo", "CB", 88, 136_000_000),
            self.create_player("Rodri", "CDM", 91, 157_000_000), self.create_player("Pedri", "CM", 88, 143_000_000),
        ]
        state = CareerState(squad=squad, bench=bench, market=market)
        state.table = {team: TeamRow(team) for team in LALIGA_TEAMS}
        for p in squad + bench:
            state.player_stats[p.name] = PlayerSeasonStats()
        return state

    def build_ai_rosters(self) -> Dict[str, List[Player]]:
        rosters = {}
        for team in LALIGA_TEAMS:
            if team == "Real Madrid":
                rosters[team] = [*self.state.squad, *self.state.bench]
            else:
                players = []
                pattern = ["GK", "RB", "LB", "CB", "CB", "CM", "CM", "CDM", "RW", "LW", "ST", "CAM", "RB", "CB", "ST"]
                for i, pos in enumerate(pattern):
                    players.append(self.create_player(f"{team.split()[0]} Player {i+1}", pos, 74 + (i % 10)))
                rosters[team] = players
        return rosters

    def avg_ovr(self) -> int:
        return round(sum(p.ovr for p in self.state.squad) / len(self.state.squad))

    def next_opponent(self) -> str:
        opps = [t for t in LALIGA_TEAMS if t != "Real Madrid"]
        return opps[(self.state.matchday - 1) % len(opps)]

    def sorted_table(self) -> List[TeamRow]:
        return sorted(self.state.table.values(), key=lambda r: (r.pts, r.gd, r.gf), reverse=True)

    def league_pos(self) -> int:
        for i, row in enumerate(self.sorted_table(), start=1):
            if row.team == "Real Madrid":
                return i
        return 20

    def set_message(self, text: str):
        self.message = text

    # ---------- UI drawing ----------

    def draw_gradient_background(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(SKY_TOP[0] * (1 - t) + SKY_BOTTOM[0] * t)
            g = int(SKY_TOP[1] * (1 - t) + SKY_BOTTOM[1] * t)
            b = int(SKY_TOP[2] * (1 - t) + SKY_BOTTOM[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

    def draw_top_bar(self):
        pygame.draw.rect(self.screen, PANEL, (0, 0, WIDTH, 80))
        for b in self.nav_buttons:
            b.draw(self.screen, self.font_sm, b.scene == self.scene)

        title = self.font_md.render("ADWBALL 2026", True, WHITE)
        self.screen.blit(title, (WIDTH - 190, 17))
        sub = self.font_xs.render("Ultimate Career", True, MUTED)
        self.screen.blit(sub, (WIDTH - 188, 48))

    def draw_footer_message(self):
        pygame.draw.rect(self.screen, PANEL_ALT, (16, HEIGHT - 46, WIDTH - 32, 30), border_radius=8)
        txt = self.font_sm.render(self.message[:160], True, WHITE)
        self.screen.blit(txt, (24, HEIGHT - 40))

    def draw_hub(self):
        self.draw_gradient_background()
        self.draw_top_bar()

        self.screen.blit(self.font_xl.render("ADWBALL 2026", True, WHITE), (20, 96))
        self.screen.blit(self.font_sm.render("Massive Career Mode Overhaul", True, MUTED), (24, 152))

        stats = [
            ("Season", f"{self.state.season}"),
            ("Matchday", f"{self.state.matchday}"),
            ("Budget", f"€{self.state.budget:,}"),
            ("Chemistry", f"{self.state.chemistry}"),
            ("Club OVR", f"{self.avg_ovr()}"),
            ("Board", f"{self.state.board_confidence}"),
            ("Dev Points", f"{self.state.dev_points}"),
            ("Next Opponent", self.next_opponent()),
            ("Tactic", self.state.tactics),
            ("League Position", f"{self.league_pos()}/20"),
        ]
        for i, (k, v) in enumerate(stats):
            x = 20 + (i % 5) * 265
            y = 190 + (i // 5) * 105
            pygame.draw.rect(self.screen, PANEL, (x, y, 248, 88), border_radius=12)
            pygame.draw.rect(self.screen, PANEL_ALT, (x, y, 248, 30), border_radius=12)
            self.screen.blit(self.font_sm.render(k, True, MUTED), (x + 12, y + 8))
            self.screen.blit(self.font_md.render(v, True, WHITE), (x + 12, y + 47))

        self.screen.blit(self.font_md.render("Quick Tactic Switch (Click):", True, WHITE), (20, 435))
        for i, t in enumerate(["Balanced", "High Press", "Counter", "Possession"]):
            rect = pygame.Rect(280 + i * 180, 428, 170, 36)
            active = self.state.tactics == t
            pygame.draw.rect(self.screen, (89, 128, 188) if active else PANEL, rect, border_radius=8)
            pygame.draw.rect(self.screen, (130, 166, 216), rect, 1, border_radius=8)
            self.screen.blit(self.font_sm.render(t, True, WHITE), (rect.x + 14, rect.y + 9))

        # Board objectives
        panel = pygame.Rect(20, 500, WIDTH - 40, 260)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=12)
        self.screen.blit(self.font_md.render("Board Objectives", True, WHITE), (36, 516))
        goals = [
            f"• Finish Top 4 (current position: {self.league_pos()})",
            f"• Keep chemistry at 80+ (current: {self.state.chemistry})",
            f"• Reach €250m budget (current: €{self.state.budget:,})",
            f"• Have 2 players in Golden Boot top 10",
            "• Win rivalry matches with Barcelona & Atletico",
        ]
        for i, g in enumerate(goals):
            color = GOOD if i == 1 and self.state.chemistry >= 80 else WHITE
            self.screen.blit(self.font_sm.render(g, True, color), (40, 548 + i * 34))

        self.draw_footer_message()

    def draw_squad(self):
        self.draw_gradient_background()
        self.draw_top_bar()
        self.screen.blit(self.font_lg.render("Squad Management", True, WHITE), (20, 95))

        # pitch view
        pitch = pygame.Rect(20, 140, 830, 600)
        pygame.draw.rect(self.screen, PITCH, pitch, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, pitch, 3, border_radius=12)
        pygame.draw.line(self.screen, WHITE, (pitch.centerx, pitch.top), (pitch.centerx, pitch.bottom), 2)
        pygame.draw.circle(self.screen, WHITE, pitch.center, 72, 2)
        pygame.draw.rect(self.screen, WHITE, (pitch.x - 1, pitch.centery - 95, 34, 190), 2)
        pygame.draw.rect(self.screen, WHITE, (pitch.right - 33, pitch.centery - 95, 34, 190), 2)

        pts = [(415, 685), (210, 560), (330, 572), (500, 572), (650, 560), (250, 425), (415, 405), (590, 425), (215, 245), (415, 210), (615, 245)]
        for i, p in enumerate(self.state.squad):
            px, py = pts[i]
            color = ACCENT if i == self.selected_xi else WHITE
            pygame.draw.circle(self.screen, color, (px, py), 18)
            text = self.font_xs.render(f"{XI_SLOTS[i]} {p.name.split()[0]} ({p.ovr})", True, WHITE)
            self.screen.blit(text, (px - text.get_width() // 2, py + 22))

        # bench panel
        bench_panel = pygame.Rect(870, 140, 470, 600)
        pygame.draw.rect(self.screen, PANEL, bench_panel, border_radius=12)
        self.screen.blit(self.font_md.render("Bench (LEFT/RIGHT)", True, WHITE), (886, 156))
        self.screen.blit(self.font_xs.render("UP/DOWN choose XI | SPACE swap | T train XI", True, MUTED), (886, 183))

        for i, p in enumerate(self.state.bench[:10]):
            y = 210 + i * 50
            row = pygame.Rect(886, y, 438, 42)
            active = i == self.selected_bench
            pygame.draw.rect(self.screen, (80, 120, 176) if active else PANEL_ALT, row, border_radius=8)
            label = f"{i+1}. {p.pos} {p.name[:19]:19s} OVR {p.ovr:2d} STM {int(p.stamina):3d}"
            self.screen.blit(self.font_sm.render(label, True, WHITE), (895, y + 12))

        xi = self.state.squad[self.selected_xi]
        cost = self.training_cost(xi)
        chance = self.training_chance(xi)
        info = pygame.Rect(886, 710, 438, 30)
        pygame.draw.rect(self.screen, PANEL_ALT, info, border_radius=8)
        self.screen.blit(self.font_xs.render(f"Selected XI: {xi.name} | Upgrade cost €{cost:,} | Success {int(chance*100)}%", True, WHITE), (894, 717))

        self.draw_footer_message()

    def draw_market(self):
        self.draw_gradient_background()
        self.draw_top_bar()
        self.screen.blit(self.font_lg.render("Transfer Market + Scouting", True, WHITE), (20, 95))
        self.screen.blit(self.font_sm.render("UP/DOWN select | ENTER negotiate/sign | S scout 3 prospects", True, MUTED), (24, 132))

        for i, p in enumerate(self.state.market):
            y = 165 + i * 48
            if y > HEIGHT - 92:
                break
            row = pygame.Rect(20, y, WIDTH - 40, 40)
            pygame.draw.rect(self.screen, (80, 122, 182) if i == self.selected_market else PANEL, row, border_radius=8)
            self.screen.blit(self.font_sm.render(f"{i+1:2d}. {p.name:22s} {p.pos:3s} OVR {p.ovr:2d}", True, WHITE), (30, y + 12))
            attrs = f"PAC {p.pace} SHO {p.shooting} PAS {p.passing} DEF {p.defending} DRI {p.dribbling}"
            self.screen.blit(self.font_xs.render(attrs, True, MUTED), (430, y + 13))
            self.screen.blit(self.font_sm.render(f"€{p.price:,}", True, ACCENT), (1165, y + 12))

        self.draw_footer_message()

    def draw_standings(self):
        self.draw_gradient_background()
        self.draw_top_bar()
        self.screen.blit(self.font_lg.render("Standings + Awards", True, WHITE), (20, 95))

        # table
        rows = self.sorted_table()
        for i, r in enumerate(rows[:14], start=1):
            y = 140 + (i - 1) * 40
            row = pygame.Rect(20, y, 700, 34)
            pygame.draw.rect(self.screen, (82, 124, 188) if r.team == "Real Madrid" else PANEL, row, border_radius=6)
            text = f"{i:2d}. {r.team:16s} P{r.p:2d} W{r.w:2d} D{r.d:2d} L{r.l:2d} GF{r.gf:3d} GA{r.ga:3d} GD{r.gd:3d} PTS {r.pts:3d}"
            self.screen.blit(self.font_sm.render(text, True, WHITE), (28, y + 9))

        # golden boot
        boot = sorted(self.state.golden_boot.items(), key=lambda kv: kv[1], reverse=True)[:12]
        panel = pygame.Rect(740, 140, 600, 600)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=12)
        self.screen.blit(self.font_md.render("LaLiga Golden Boot", True, WHITE), (758, 160))
        self.screen.blit(self.font_xs.render("(All teams, not only Real Madrid)", True, MUTED), (760, 188))
        for i, ((team, player), goals) in enumerate(boot):
            y = 214 + i * 42
            self.screen.blit(self.font_sm.render(f"{i+1:2d}. {player[:22]:22s}", True, WHITE), (760, y))
            self.screen.blit(self.font_xs.render(f"{team[:18]:18s}", True, MUTED), (1015, y + 2))
            self.screen.blit(self.font_sm.render(f"{goals}", True, ACCENT), (1290, y))

        # RM awards
        rm_stats = sorted(self.state.player_stats.items(), key=lambda kv: kv[1].goals, reverse=True)[:5]
        self.screen.blit(self.font_md.render("Real Madrid Top Scorers", True, WHITE), (760, 520))
        for i, (name, st) in enumerate(rm_stats):
            self.screen.blit(self.font_sm.render(f"{i+1}. {name[:22]:22s}  {st.goals}", True, WHITE), (760, 552 + i * 30))

        self.draw_footer_message()

    # ---------- gameplay ----------

    def weather_multiplier(self) -> float:
        if self.weather == "Rain":
            return 0.88
        if self.weather == "Windy":
            return 0.94
        return 1.0

    def start_match(self):
        self.scene = "match"
        self.match_active = True
        self.match_timer = 90.0
        self.half_announced = False
        self.rm_score = 0
        self.opp_score = 0
        self.opp_team = self.next_opponent()
        self.weather = random.choice(["Clear", "Rain", "Windy"])
        self.ball = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.ball_vel = pygame.Vector2(0, 0)
        self.events = [MatchEvent(0, f"Kickoff vs {self.opp_team} - Weather: {self.weather}")]
        self.last_touch_rm = None
        self.last_touch_rm_prev = None

        rm_layout = [(220, 410, "GK"), (290, 285, "CB"), (290, 535, "CB"), (430, 220, "CM"), (430, 600, "CM"), (580, 410, "ST")]
        opp_layout = [(1140, 410, "GK"), (1070, 290, "CB"), (1070, 530, "CB"), (930, 220, "CM"), (930, 600, "CM"), (790, 410, "ST")]

        self.rm_actors = []
        self.opp_actors = []
        for i, (x, y, role) in enumerate(rm_layout):
            # map from squad by role preference
            player = self.pick_player_for_role(self.state.squad, role, fallback=i)
            self.rm_actors.append(MatchActor(player=player, team="Real Madrid", x=x, y=y, role=role, control=(i == 5), stamina_live=player.stamina))

        for i, (x, y, role) in enumerate(opp_layout):
            roster = self.ai_rosters[self.opp_team]
            player = self.pick_player_for_role(roster, role, fallback=i)
            self.opp_actors.append(MatchActor(player=player, team=self.opp_team, x=x, y=y, role=role, stamina_live=95))

        self.set_message("Live match started! Move with WASD/arrows, hold/release SPACE to shoot, Q pass, E tackle.")

    @staticmethod
    def pick_player_for_role(players: List[Player], role: str, fallback: int = 0) -> Player:
        exact = [p for p in players if p.pos == role]
        if exact:
            return max(exact, key=lambda p: p.ovr)
        mids = [p for p in players if role in {"CM", "CDM", "CAM"} and p.pos in {"CM", "CDM", "CAM"}]
        if mids:
            return max(mids, key=lambda p: p.ovr)
        return players[min(fallback, len(players) - 1)]

    def update_match(self, dt: float, keys):
        if not self.match_active:
            return

        speed_mult = self.weather_multiplier()
        controlled = next(a for a in self.rm_actors if a.control)

        # move controlled player
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1

        sprint = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        base_speed = 220 * speed_mult
        sprint_boost = 1.45 if sprint and controlled.stamina_live > 8 else 1.0

        if move.length_squared() > 0:
            step = move.normalize() * base_speed * sprint_boost * dt
            controlled.x += step.x
            controlled.y += step.y
            controlled.stamina_live = max(0, controlled.stamina_live - (18 * dt if sprint_boost > 1 else 7 * dt))
        else:
            controlled.stamina_live = min(100, controlled.stamina_live + 5 * dt)

        # keep in bounds
        controlled.x = max(75, min(WIDTH - 75, controlled.x))
        controlled.y = max(120, min(HEIGHT - 70, controlled.y))

        # teammate AI support movement
        for actor in self.rm_actors:
            if actor.control:
                continue
            self.support_move(actor, target_x=min(620, self.ball.x - 120), target_y=self.ball.y, speed=140 * speed_mult, dt=dt)

        # opposition AI
        for actor in self.opp_actors:
            if actor.role == "GK":
                self.support_move(actor, target_x=1140, target_y=self.ball.y, speed=120, dt=dt)
            else:
                chase = pygame.Vector2(self.ball.x - actor.x, self.ball.y - actor.y)
                if chase.length() < 300:
                    self.support_move(actor, target_x=self.ball.x, target_y=self.ball.y, speed=170 * speed_mult, dt=dt)
                else:
                    base = 980 if actor.role in {"CB", "GK"} else 910
                    self.support_move(actor, target_x=base, target_y=actor.y, speed=80, dt=dt)

        # ball physics
        self.ball += self.ball_vel * dt
        self.ball_vel *= 0.985 if self.weather != "Rain" else 0.975

        # touches
        self.handle_ball_touches(self.rm_actors, True, dt)
        self.handle_ball_touches(self.opp_actors, False, dt)

        # constraints
        self.ball.x = max(25, min(WIDTH - 25, self.ball.x))
        self.ball.y = max(115, min(HEIGHT - 45, self.ball.y))
        if self.ball.y in (115, HEIGHT - 45):
            self.ball_vel.y *= -0.7

        # goals
        left_goal = self.ball.x < 36 and HEIGHT // 2 - 95 < self.ball.y < HEIGHT // 2 + 95
        right_goal = self.ball.x > WIDTH - 36 and HEIGHT // 2 - 95 < self.ball.y < HEIGHT // 2 + 95
        minute = max(1, int(90 - self.match_timer))

        if left_goal:
            self.opp_score += 1
            scorer = self.pick_player_for_role(self.ai_rosters[self.opp_team], "ST").name
            self.state.golden_boot[(self.opp_team, scorer)] = self.state.golden_boot.get((self.opp_team, scorer), 0) + 1
            self.events.append(MatchEvent(minute, f"{minute}' Goal {self.opp_team} ({scorer})"))
            self.reset_kickoff()

        if right_goal:
            self.rm_score += 1
            scorer = self.last_touch_rm or "Unknown"
            self.state.golden_boot[("Real Madrid", scorer)] = self.state.golden_boot.get(("Real Madrid", scorer), 0) + 1
            if scorer in self.state.player_stats:
                self.state.player_stats[scorer].goals += 1
            if self.last_touch_rm_prev and self.last_touch_rm_prev != scorer and self.last_touch_rm_prev in self.state.player_stats:
                self.state.player_stats[self.last_touch_rm_prev].assists += 1
            self.events.append(MatchEvent(minute, f"{minute}' Goal Real Madrid ({scorer})"))
            self.reset_kickoff()

        self.events = self.events[-10:]

        # match clock
        self.match_timer -= dt * 3.4
        if not self.half_announced and self.match_timer <= 45:
            self.half_announced = True
            self.events.append(MatchEvent(45, "45' Half-time whistle"))

        if self.match_timer <= 0:
            self.finish_match()

    @staticmethod
    def support_move(actor: MatchActor, target_x: float, target_y: float, speed: float, dt: float):
        vec = pygame.Vector2(target_x - actor.x, target_y - actor.y)
        if vec.length_squared() > 4:
            step = vec.normalize() * speed * dt
            actor.x += step.x
            actor.y += step.y

    def handle_ball_touches(self, actors: List[MatchActor], is_rm: bool, dt: float):
        for actor in actors:
            d = math.hypot(self.ball.x - actor.x, self.ball.y - actor.y)
            if d < 24:
                vec = pygame.Vector2(self.ball.x - actor.x, self.ball.y - actor.y)
                if vec.length_squared() > 0:
                    push = 165 if actor.role != "GK" else 110
                    self.ball_vel += vec.normalize() * push * dt
                if is_rm:
                    self.last_touch_rm_prev = self.last_touch_rm
                    self.last_touch_rm = actor.player.name

    def reset_kickoff(self):
        self.ball.update(WIDTH / 2, HEIGHT / 2)
        self.ball_vel.update(0, 0)

    def finish_match(self):
        self.match_active = False
        rm, opp = self.rm_score, self.opp_score
        opponent = self.opp_team

        self.update_table("Real Madrid", opponent, rm, opp)
        others = [t for t in LALIGA_TEAMS if t not in {"Real Madrid", opponent}]
        for i in range(0, len(others), 2):
            self.sim_other_fixture(others[i], others[i + 1])

        # recover because of rest days
        rest_days = random.randint(2, 5)
        recovery = rest_days * 6
        for p in self.state.squad:
            p.stamina = min(100, p.stamina + recovery)
            p.morale = max(58, min(99, p.morale + (2 if rm > opp else -2 if rm < opp else 0)))

        if rm > opp:
            self.state.budget += 5_000_000
            self.state.chemistry = min(99, self.state.chemistry + 1)
            self.state.board_confidence = min(99, self.state.board_confidence + 2)
            self.state.dev_points += 2
        elif rm == opp:
            self.state.budget += 2_000_000
            self.state.board_confidence = min(99, self.state.board_confidence + 1)
            self.state.dev_points += 1
        else:
            self.state.chemistry = max(64, self.state.chemistry - 2)
            self.state.board_confidence = max(35, self.state.board_confidence - 2)

        # clean sheet bonus
        if opp == 0:
            gk = self.state.squad[0].name
            if gk in self.state.player_stats:
                self.state.player_stats[gk].clean_sheets += 1

        self.state.matchday += 1
        if self.state.matchday > 38:
            self.state.season += 1
            self.state.matchday = 1
            self.state.table = {t: TeamRow(t) for t in LALIGA_TEAMS}
            self.state.board_confidence = min(99, self.state.board_confidence + 3)
            self.events.append(MatchEvent(90, f"Season rollover: now Season {self.state.season}"))

        self.scene = "hub"
        self.set_message(f"FT Real Madrid {rm}-{opp} {opponent}. Rest gap: {rest_days} days. Dev points +{2 if rm>opp else 1 if rm==opp else 0}")

    # ---------- Career systems ----------

    def training_cost(self, p: Player) -> int:
        return 2_200_000 + max(0, p.ovr - 83) * 1_450_000

    def training_chance(self, p: Player) -> float:
        return max(0.1, 0.9 - (p.ovr - 74) * 0.045)

    def train_selected(self):
        p = self.state.squad[self.selected_xi]
        if p.ovr >= 99:
            self.set_message(f"{p.name} is already maxed at 99.")
            return
        cost = self.training_cost(p)
        chance = self.training_chance(p)
        if self.state.budget < cost:
            self.set_message("Insufficient budget for focused training.")
            return
        self.state.budget -= cost
        p.stamina = max(52, p.stamina - 4)
        if random.random() <= chance:
            p.ovr += 1
            p.pace = min(99, p.pace + random.randint(0, 1))
            p.shooting = min(99, p.shooting + random.randint(0, 1))
            p.passing = min(99, p.passing + random.randint(0, 1))
            p.defending = min(99, p.defending + random.randint(0, 1))
            p.dribbling = min(99, p.dribbling + random.randint(0, 1))
            self.state.dev_points += 1
            self.set_message(f"Training success: {p.name} reached {p.ovr} OVR.")
        else:
            self.set_message(f"Training complete. {p.name} had no OVR gain this cycle.")

    def swap_selected(self):
        if not self.state.bench:
            return
        starter = self.state.squad[self.selected_xi]
        bench = self.state.bench[self.selected_bench]
        self.state.squad[self.selected_xi] = Player(
            name=bench.name,
            pos=XI_SLOTS[self.selected_xi],
            ovr=bench.ovr,
            pace=bench.pace,
            shooting=bench.shooting,
            passing=bench.passing,
            defending=bench.defending,
            dribbling=bench.dribbling,
            stamina=bench.stamina,
            morale=bench.morale,
            price=bench.price,
        )
        self.state.bench[self.selected_bench] = starter
        self.state.chemistry = max(68, self.state.chemistry - 1)
        if bench.name not in self.state.player_stats:
            self.state.player_stats[bench.name] = PlayerSeasonStats()
        self.set_message(f"Swap complete: {bench.name} starts, {starter.name} to bench.")

    def negotiate_and_buy_selected(self):
        if not self.state.market:
            return
        p = self.state.market[self.selected_market]
        if self.state.budget < p.price:
            self.set_message(f"Cannot afford {p.name}.")
            return

        fee_factor = max(0, min(1.0, (self.state.budget - p.price) / max(1, p.price)))
        confidence_factor = self.state.board_confidence / 100
        chance = 0.45 + 0.25 * fee_factor + 0.2 * confidence_factor

        if random.random() > chance:
            self.set_message(f"{p.name} rejected negotiations. Improve finances and board confidence.")
            return

        # find compatible slot
        slot = next(
            (
                i for i, role in enumerate(XI_SLOTS)
                if role == p.pos or (role in {"CM", "CDM", "CAM"} and p.pos in {"CM", "CDM", "CAM"})
            ),
            len(self.state.squad) - 1,
        )

        moved = self.state.squad[slot]
        self.state.squad[slot] = Player(
            name=p.name,
            pos=XI_SLOTS[slot],
            ovr=p.ovr,
            pace=p.pace,
            shooting=p.shooting,
            passing=p.passing,
            defending=p.defending,
            dribbling=p.dribbling,
            stamina=p.stamina,
            morale=p.morale,
            price=p.price,
        )
        self.state.bench.insert(0, moved)
        self.state.budget -= p.price
        self.state.market.pop(self.selected_market)
        self.selected_market = max(0, min(self.selected_market, len(self.state.market) - 1))
        if p.name not in self.state.player_stats:
            self.state.player_stats[p.name] = PlayerSeasonStats()

        self.set_message(f"Deal done: {p.name} joins Real Madrid for €{p.price:,}.")

    def scout_prospects(self):
        if self.state.dev_points < 1:
            self.set_message("Need at least 1 dev point to run scouting this week.")
            return
        self.state.dev_points -= 1
        first = ["Mateo", "Leo", "Aron", "Nico", "Iker", "Sergio", "Pablo", "Rayan", "Enzo", "Tiago"]
        last = ["Silva", "Costa", "Navas", "Ruiz", "Torres", "Molina", "Duarte", "Ramos", "Reyes", "Alonso"]
        for _ in range(3):
            name = f"{random.choice(first)} {random.choice(last)}"
            pos = random.choice(["ST", "RW", "LW", "CM", "CB", "LB", "RB"])
            ovr = random.randint(72, 82)
            price = random.randint(18_000_000, 45_000_000)
            self.state.market.append(self.create_player(name, pos, ovr, price))
        self.set_message("Scouting completed: 3 new prospects added to market.")

    # ---------- Table/season simulation ----------

    def update_table(self, home: str, away: str, hg: int, ag: int):
        h = self.state.table[home]
        a = self.state.table[away]
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

    def sim_goals(self, team_power: int) -> int:
        xg = max(0.2, (team_power - 72) / 13 + random.random() * 1.3)
        base = math.floor(xg)
        return min(6, max(0, base + (1 if random.random() < xg - base else 0)))

    def weighted_scorer(self, team: str) -> str:
        roster = self.state.squad if team == "Real Madrid" else self.ai_rosters[team]
        pool = []
        for p in roster:
            pool.extend([p.name] * ROLE_WEIGHT.get(p.pos, 2))
        return random.choice(pool)

    def sim_other_fixture(self, home: str, away: str):
        hg = self.sim_goals(80 + random.randint(0, 10))
        ag = self.sim_goals(80 + random.randint(0, 10))
        self.update_table(home, away, hg, ag)
        for _ in range(hg):
            s = self.weighted_scorer(home)
            self.state.golden_boot[(home, s)] = self.state.golden_boot.get((home, s), 0) + 1
        for _ in range(ag):
            s = self.weighted_scorer(away)
            self.state.golden_boot[(away, s)] = self.state.golden_boot.get((away, s), 0) + 1

    # ---------- Event handling ----------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for b in self.nav_buttons:
                    if b.hit(pos):
                        if b.scene == "match":
                            self.start_match()
                        else:
                            self.scene = b.scene

                if self.scene == "hub":
                    for i, t in enumerate(["Balanced", "High Press", "Counter", "Possession"]):
                        rect = pygame.Rect(280 + i * 180, 428, 170, 36)
                        if rect.collidepoint(pos):
                            self.state.tactics = t
                            self.set_message(f"Tactic set to {t}")

            if event.type == pygame.KEYDOWN:
                if self.scene == "squad":
                    if event.key == pygame.K_UP:
                        self.selected_xi = (self.selected_xi - 1) % len(self.state.squad)
                    elif event.key == pygame.K_DOWN:
                        self.selected_xi = (self.selected_xi + 1) % len(self.state.squad)
                    elif event.key == pygame.K_LEFT:
                        self.selected_bench = (self.selected_bench - 1) % len(self.state.bench)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_bench = (self.selected_bench + 1) % len(self.state.bench)
                    elif event.key == pygame.K_SPACE:
                        self.swap_selected()
                    elif event.key == pygame.K_t:
                        self.train_selected()

                elif self.scene == "market":
                    if event.key == pygame.K_UP:
                        self.selected_market = (self.selected_market - 1) % len(self.state.market)
                    elif event.key == pygame.K_DOWN:
                        self.selected_market = (self.selected_market + 1) % len(self.state.market)
                    elif event.key == pygame.K_RETURN:
                        self.negotiate_and_buy_selected()
                    elif event.key == pygame.K_s:
                        self.scout_prospects()

                elif self.scene == "match":
                    if event.key == pygame.K_q:
                        self.pass_ball()

    def pass_ball(self):
        controlled = next(a for a in self.rm_actors if a.control)
        candidates = [a for a in self.rm_actors if not a.control]
        if not candidates:
            return
        target = min(candidates, key=lambda a: math.hypot(a.x - controlled.x, a.y - controlled.y))
        direction = pygame.Vector2(target.x - self.ball.x, target.y - self.ball.y)
        if direction.length_squared() > 0:
            self.ball_vel = direction.normalize() * 420
            self.last_touch_rm_prev = self.last_touch_rm
            self.last_touch_rm = controlled.player.name
            self.set_message(f"Quick pass by {controlled.player.name}.")

    # ---------- Match rendering ----------

    def draw_match(self):
        self.draw_gradient_background()
        self.draw_top_bar()

        field = pygame.Rect(20, 92, WIDTH - 40, HEIGHT - 170)

        # crowd + stadium vibes
        pygame.draw.rect(self.screen, (40, 58, 96), (20, 92, WIDTH - 40, 45), border_radius=8)
        for i in range(40):
            cx = 30 + i * 33
            pygame.draw.circle(self.screen, (random.randint(130, 230), random.randint(80, 180), random.randint(80, 200)), (cx, 114), 3)

        pygame.draw.rect(self.screen, PITCH, field, border_radius=12)
        for i in range(10):
            band = pygame.Rect(field.x, field.y + i * (field.height // 10), field.width, field.height // 10)
            pygame.draw.rect(self.screen, PITCH if i % 2 == 0 else PITCH_DARK, band)

        pygame.draw.rect(self.screen, WHITE, field, 3, border_radius=12)
        pygame.draw.line(self.screen, WHITE, (field.centerx, field.top), (field.centerx, field.bottom), 2)
        pygame.draw.circle(self.screen, WHITE, field.center, 72, 2)
        pygame.draw.rect(self.screen, WHITE, (field.x - 1, field.centery - 95, 34, 190), 2)
        pygame.draw.rect(self.screen, WHITE, (field.right - 33, field.centery - 95, 34, 190), 2)

        # players
        for a in self.rm_actors:
            color = ACCENT if a.control else (250, 233, 120)
            pygame.draw.circle(self.screen, color, (int(a.x), int(a.y)), 16)
            pygame.draw.circle(self.screen, (20, 20, 20), (int(a.x), int(a.y)), 16, 1)
        for a in self.opp_actors:
            pygame.draw.circle(self.screen, (225, 92, 96), (int(a.x), int(a.y)), 16)
            pygame.draw.circle(self.screen, (20, 20, 20), (int(a.x), int(a.y)), 16, 1)

        # ball + shadow
        pygame.draw.circle(self.screen, (0, 0, 0, 60), (int(self.ball.x), int(self.ball.y + 8)), 10)
        pygame.draw.circle(self.screen, WHITE, (int(self.ball.x), int(self.ball.y)), 9)

        # scoreboard
        score = self.font_lg.render(f"Real Madrid {self.rm_score} - {self.opp_score} {self.opp_team}", True, WHITE)
        self.screen.blit(score, score.get_rect(center=(WIDTH // 2, 40)))
        minute = max(0, int(90 - self.match_timer))
        ttxt = self.font_md.render(f"{minute}'", True, ACCENT)
        self.screen.blit(ttxt, (WIDTH // 2 - 18, 65))
        weather = self.font_sm.render(f"Weather: {self.weather}", True, MUTED)
        self.screen.blit(weather, (25, 64))

        # minimap
        mini = pygame.Rect(WIDTH - 220, 92, 190, 120)
        pygame.draw.rect(self.screen, PANEL, mini, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, mini, 1, border_radius=8)
        for a in self.rm_actors:
            mx = mini.x + int((a.x / WIDTH) * mini.width)
            my = mini.y + int((a.y / HEIGHT) * mini.height)
            pygame.draw.circle(self.screen, ACCENT, (mx, my), 3)
        for a in self.opp_actors:
            mx = mini.x + int((a.x / WIDTH) * mini.width)
            my = mini.y + int((a.y / HEIGHT) * mini.height)
            pygame.draw.circle(self.screen, BAD, (mx, my), 3)
        bx = mini.x + int((self.ball.x / WIDTH) * mini.width)
        by = mini.y + int((self.ball.y / HEIGHT) * mini.height)
        pygame.draw.circle(self.screen, WHITE, (bx, by), 3)

        # controls tips
        tips = self.font_xs.render("WASD move | SHIFT sprint | hold/release SPACE shoot | Q pass | E tackle", True, WHITE)
        self.screen.blit(tips, (28, HEIGHT - 102))

        # recent events
        panel = pygame.Rect(20, HEIGHT - 78, WIDTH - 40, 56)
        pygame.draw.rect(self.screen, PANEL_ALT, panel, border_radius=8)
        ev = " | ".join(e.text for e in self.events[-2:]) if self.events else "Kickoff"
        self.screen.blit(self.font_sm.render(ev[:170], True, WHITE), (30, HEIGHT - 58))

    def update_live_inputs(self, keys):
        # shoot charging by hold/release
        controlled = next(a for a in self.rm_actors if a.control)
        if not hasattr(self, "shot_charge"):
            self.shot_charge = 0.0
            self.space_was_down = False

        space_now = keys[pygame.K_SPACE]
        if space_now:
            self.shot_charge = min(1.0, self.shot_charge + 0.035)
        if self.space_was_down and not space_now:
            if math.hypot(self.ball.x - controlled.x, self.ball.y - controlled.y) < 52:
                direction = pygame.Vector2(1.0, random.uniform(-0.2, 0.2))
                shot_power = 360 + 360 * self.shot_charge
                if self.weather == "Windy":
                    direction.y += random.uniform(-0.15, 0.15)
                self.ball_vel += direction.normalize() * shot_power
                self.last_touch_rm_prev = self.last_touch_rm
                self.last_touch_rm = controlled.player.name
                self.events.append(MatchEvent(max(1, int(90 - self.match_timer)), f"{controlled.player.name} shoots!"))
            self.shot_charge = 0.0
        self.space_was_down = space_now

        # tackle
        if keys[pygame.K_e]:
            for opp in self.opp_actors:
                d = math.hypot(opp.x - controlled.x, opp.y - controlled.y)
                if d < 36 and math.hypot(self.ball.x - opp.x, self.ball.y - opp.y) < 32:
                    vec = pygame.Vector2(self.ball.x - opp.x, self.ball.y - opp.y)
                    if vec.length_squared() > 0:
                        self.ball_vel += vec.normalize() * 330
                        self.events.append(MatchEvent(max(1, int(90 - self.match_timer)), f"{controlled.player.name} wins tackle"))
                        break

    # ---------- main loop ----------

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
                self.update_live_inputs(keys)
                self.update_match(dt, keys)
                self.draw_match()

            self.draw_footer_message() if self.scene != "match" else None
            pygame.display.flip()


if __name__ == "__main__":
    CareerGame().run()
