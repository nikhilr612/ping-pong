# game/paddle.py
import pygame

class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.speed = 7

    def move(self, dy: int, screen_height: int) -> None:
        """Move by dy pixels, clamped to the screen."""
        self.y += dy
        self.y = max(0, min(self.y, screen_height - self.height))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, int(self.y), self.width, self.height)

    def auto_track(self, ball, screen_height) -> None:
        """
        Simple AI: move towards the ball center using limited speed.
        This is smoother and prevents jitter at edges.
        """
        ball_center = ball.y + ball.height / 2
        paddle_center = self.y + self.height / 2
        # only move if center is noticeably off
        diff = ball_center - paddle_center
        if abs(diff) > 8:
            # proportional movement but capped by speed
            move_amount = max(-self.speed, min(self.speed, diff * 0.15))
            self.move(move_amount, screen_height)
