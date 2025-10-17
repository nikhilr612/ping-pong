# game/game_engine.py
import pygame
from .paddle import Paddle
from .ball import Ball
import os

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameEngine:
    def __init__(self, width: int, height: int, winning_score: int = 5) -> None:
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        # Create paddles and ball
        self.player = Paddle(10, height // 2 - self.paddle_height // 2,
                             self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - self.paddle_height // 2,
                         self.paddle_width, self.paddle_height)
        # ball width/height small square
        self.ball = Ball(width // 2 - 7, height // 2 - 7, 14, 14, width, height)

        # Scores and fonts
        self.player_score = 0
        self.ai_score = 0
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 22)

        # Game rules
        self.winning_score = winning_score
        self.game_over = False
        self.winner = None

        # Sound placeholders
        self.sound_paddle = None
        self.sound_wall = None
        self.sound_score = None
        self._init_sounds()

        # which side serves next (True -> to right/player)
        self.serve_to_right = True

    def _init_sounds(self) -> None:
        """Try to initialize pygame.mixer and load sound files if available.
        If assets are missing, just skip sounds (no crash)."""
        try:
            pygame.mixer.init()
            base = os.path.join(os.getcwd(), "assets")
            paddle_path = os.path.join(base, "paddle.wav")
            wall_path = os.path.join(base, "wall.wav")
            score_path = os.path.join(base, "score.wav")
            if os.path.isfile(paddle_path):
                self.sound_paddle = pygame.mixer.Sound(paddle_path)
            if os.path.isfile(wall_path):
                self.sound_wall = pygame.mixer.Sound(wall_path)
            if os.path.isfile(score_path):
                self.sound_score = pygame.mixer.Sound(score_path)
        except Exception:
            # If mixer initialization fails, keep sounds None and continue
            self.sound_paddle = None
            self.sound_wall = None
            self.sound_score = None

    def play_sound(self, sound: pygame.mixer.Sound) -> None:
        try:
            if sound:
                sound.play()
        except Exception:
            pass

    def handle_input(self) -> None:
        """Realtime keyboard (W/S for player)."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-self.player.speed, self.height)
        if keys[pygame.K_s]:
            self.player.move(self.player.speed, self.height)

    def handle_event(self, event) -> None:
        """
        Handle discrete events (used for replay menu). Should be called for each event
        in the main loop.
        """
        if event.type == pygame.KEYDOWN and self.game_over:
            if event.key == pygame.K_3:
                self._start_new_match(best_of=3)
            elif event.key == pygame.K_5:
                self._start_new_match(best_of=5)
            elif event.key == pygame.K_7:
                self._start_new_match(best_of=7)
            elif event.key == pygame.K_ESCAPE:
                # signal to caller (main) to quit by setting a flag; here we set winner to 'exit'
                self.winner = 'exit'

    def _start_new_match(self, best_of=5) -> None:
        """Set a new target winning score (best_of -> majority). Reset scores and ball."""
        target = (best_of // 2) + 1
        self.winning_score = target
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = None
        self.serve_to_right = True
        self.ball.reset(serve_right=self.serve_to_right)

    def update(self) -> None:
        """Update game state (only when not game_over)."""
        if self.game_over:
            return

        # Move ball with collision checks
        events = self.ball.move(paddles=[self.player, self.ai])

        # play sounds
        if events.get('wall_hit') and self.sound_wall is not None:
            self.play_sound(sound=self.sound_wall)
        if events.get('paddle_hit') and self.sound_paddle is not None:
            self.play_sound(sound=self.sound_paddle)

        # scoring
        if events.get('score') == 'player':
            self.player_score += 1
            if self.sound_score is not None:
                self.play_sound(sound=self.sound_score)
            # next serve goes to AI (ball moves toward AI when we reset?) - flip serve
            self.serve_to_right = False
            # check for game over
            if self.player_score >= self.winning_score:
                self.game_over = True
                self.winner = 'Player'
            else:
                self.ball.reset(serve_right=self.serve_to_right)
        elif events.get('score') == 'ai':
            self.ai_score += 1
            if self.sound_score is not None:
                self.play_sound(sound=self.sound_score)
            self.serve_to_right = True
            if self.ai_score >= self.winning_score:
                self.game_over = True
                self.winner = 'AI'
            else:
                self.ball.reset(serve_right=self.serve_to_right)

        # AI paddle movement (simple tracking)
        self.ai.auto_track(self.ball, self.height)

    def render(self, screen):
        # Clear previously done by main; here draw game objects
        # Draw center line
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        # draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        self.ball.draw(screen)

        # Draw scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4 - player_text.get_width() // 2, 20))
        screen.blit(ai_text, (self.width * 3 // 4 - ai_text.get_width() // 2, 20))

        # Show small hint
        hint = self.small_font.render("W/S to move - After game, press 3/5/7 to play again or ESC to exit", True, WHITE)
        screen.blit(hint, (10, self.height - 30))

        # If game over, overlay Game Over screen and options
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))  # translucent dark overlay
            screen.blit(overlay, (0, 0))

            # Winner text
            winner_text = self.font.render(f"{self.winner} Wins!", True, WHITE)
            screen.blit(winner_text, (self.width // 2 - winner_text.get_width() // 2, self.height // 2 - 80))

            # Replay options
            opt_text = self.small_font.render("Press 3 (Best of 3)  5 (Best of 5)  7 (Best of 7)  ESC (Exit)", True, WHITE)
            screen.blit(opt_text, (self.width // 2 - opt_text.get_width() // 2, self.height // 2))

            # Show final score
            score_text = self.small_font.render(f"Final Score — Player {self.player_score} : {self.ai_score} AI", True, WHITE)
            screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, self.height // 2 + 40))
