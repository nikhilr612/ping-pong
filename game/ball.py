# game/ball.py
import pygame
import random

class Ball:
    """
    Ball takes (x, y, width, height, screen_width, screen_height)
    width/height describe the ball's bounding box (keeps compatibility with your UI).
    """

    def __init__(self, x: float, y: float, width: float, height: float, screen_width: float, screen_height: float) -> None:
        self.original_x = x
        self.original_y = y
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def reset(self, serve_right=True) -> None:
        """Reset ball to center; flip horizontal direction if serve_right False."""
        self.x = float(self.original_x)
        self.y = float(self.original_y)
        # serve in opposite direction of last serve if requested
        self.velocity_x = 5 if serve_right else -5
        self.velocity_y = random.choice([-3, -2, 2, 3])

    def move(self, paddles) -> dict[str, object]:
        """
        Move the ball using substeps to avoid tunneling.
        `paddles` is a list of paddle objects with .rect() method.
        Returns events dict with flags:
          {'paddle_hit': bool, 'wall_hit': bool, 'score': None|'player'|'ai'}
        """
        events = {'paddle_hit': False, 'wall_hit': False, 'score': None}

        # Determine number of sub-steps based on speed; ensure at least 1
        max_speed = max(abs(self.velocity_x), abs(self.velocity_y), 1)
        n_steps = int(max_speed) + 1

        step_x = self.velocity_x / n_steps
        step_y = self.velocity_y / n_steps

        for _ in range(n_steps):
            self.x += step_x
            self.y += step_y

            # Top / bottom wall collision
            if self.y <= 0:
                self.y = 0
                self.velocity_y = -self.velocity_y
                events['wall_hit'] = True
                step_y = self.velocity_y / n_steps
            elif self.y + self.height >= self.screen_height:
                self.y = self.screen_height - self.height
                self.velocity_y = -self.velocity_y
                events['wall_hit'] = True
                step_y = self.velocity_y / n_steps

            # Paddle collisions
            ball_rect = self.rect()
            for paddle in paddles:
                if ball_rect.colliderect(paddle.rect()):
                    # Mark event
                    events['paddle_hit'] = True

                    # Bounce horizontally
                    # If ball coming from right (velocity_x > 0) collided with right paddle,
                    # or from left, place it just outside paddle to avoid sticking.
                    if self.velocity_x > 0:
                        # hit right paddle -> move left of it
                        self.x = paddle.x - self.width
                    else:
                        # hit left paddle -> move right of it
                        self.x = paddle.x + paddle.width

                    # Reverse X velocity
                    self.velocity_x = -self.velocity_x

                    # Add some Y variation depending on where it hit the paddle (spin)
                    # Compute relative hit position (-1 .. 1)
                    paddle_center = paddle.y + paddle.height / 2
                    relative_hit = ((self.y + self.height / 2) - paddle_center) / (paddle.height / 2)
                    # Tweak velocity_y slightly
                    self.velocity_y += relative_hit * 1.5
                    # clamp vertical speed to avoid extreme angles
                    max_vy = 8
                    if self.velocity_y > max_vy:
                        self.velocity_y = max_vy
                    elif self.velocity_y < -max_vy:
                        self.velocity_y = -max_vy

                    # Recompute step_x for remaining micro-steps
                    step_x = self.velocity_x / n_steps

                    # break from checking other paddles
                    break

            # Scoring: if ball goes fully off-screen horizontally
            if self.x + self.width < 0:
                events['score'] = 'ai'  # AI scored (player missed)
                break
            elif self.x > self.screen_width:
                events['score'] = 'player'  # Player scored (AI missed)
                break

        return events

    def draw(self, surface) -> None:
        pygame.draw.ellipse(surface, (255, 255, 255), self.rect())
