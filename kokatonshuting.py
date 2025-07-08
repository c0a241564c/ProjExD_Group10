import pygame
import  os
import sys
import random

# 色の定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 40, 0)

if "__file__" in globals():                 # ← 対話モード対策
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    BASE_DIR = os.getcwd()                  # それでも動かす場合

IMG_DIR = os.path.join(BASE_DIR, "ex5", "fig")

def load_img(filename, alpha=True):
    """IMG_DIR から (アルファ付きで) 読み込むユーティリティ"""
    path = os.path.join(IMG_DIR, filename)
    img  = pygame.image.load(path)
    return img.convert_alpha() if alpha else img.convert()


# プレイヤークラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("ex5/fig/4.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (400, 550)
        self.speed = 5
        self.invincible = False
        self.invincible_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

# エイリアンクラス
class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, all_sprites, alien_bullets):
        super().__init__()
        self.image = pygame.image.load("ex5/fig/alien1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2
        self.all_sprites = all_sprites
        self.alien_bullets = alien_bullets

    def update(self):
        self.rect.x += self.speed
        if self.rect.right >= 800 or self.rect.left <= 0:
            self.speed = -self.speed
            self.rect.y += 40
        if random.randint(1, 300) == 1:
            bullet = AlienBullet(self.rect.centerx, self.rect.bottom)
            self.all_sprites.add(bullet)
            self.alien_bullets.add(bullet)

# 弾クラス（プレイヤー用）
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("ex5/fig/beam.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# エイリアンの弾クラス
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()

# 無敵アイテム（黄色い〇）
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        radius = 15
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()

# メインゲーム関数
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Space Invaders")
    font = pygame.font.SysFont(None, 55)

    all_sprites = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    alien_bullets = pygame.sprite.Group()
    items = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    score = 0
    game_over = False
    game_clear = False
    game_started = False
    running = True

    # エイリアンを配置
    for i in range(10):
        for j in range(3):
            alien = Alien(50 + i * 50, 70 + j * 80, all_sprites, alien_bullets)
            all_sprites.add(alien)
            aliens.add(alien)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                if event.key == pygame.K_s:
                    game_started = True
                if game_over and event.key == pygame.K_r:
                    main()

        if not game_over and game_started:
            all_sprites.update()

            # 弾とエイリアンの衝突
            hits = pygame.sprite.groupcollide(bullets, aliens, True, True)
            for hit in hits:
                score += 10
                if random.randint(1, 5) == 1:  # 20%の確率でアイテム出現
                    item = Item(hit.rect.centerx, hit.rect.centery)
                    all_sprites.add(item)
                    items.add(item)

            # アイテム取得処理
            item_hits = pygame.sprite.spritecollide(player, items, True)
            if item_hits:
                player.invincible = True
                player.invincible_timer = 300  # 約5秒（60FPS）

            # 弾がプレイヤーに当たったか（無敵中は無効）
            if not player.invincible:
                player_hits = pygame.sprite.spritecollide(player, alien_bullets, True)
                if player_hits:
                    game_over = True

            # エイリアンが下に到達したらゲームオーバー
            for alien in aliens:
                if alien.rect.bottom >= player.rect.top:
                    game_over = True

            # 全滅でゲームクリア
            if not aliens:
                game_clear = True

        # 描画処理
        screen.fill(DARK_GREEN)

        # プレイヤー以外を描画
        for sprite in all_sprites:
            if sprite != player:
                screen.blit(sprite.image, sprite.rect)

        # プレイヤーを描画（無敵中は点滅）
        if player.invincible:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                screen.blit(player.image, player.rect)
        else:
            screen.blit(player.image, player.rect)

        # スコア表示
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # ゲームオーバー・クリア表示
        if game_over:
            game_over_text = font.render("GAME OVER - Press 'R' to Restart", True, WHITE)
            screen.blit(game_over_text, (150, 250))
            all_sprites.empty()
            aliens.empty()
            bullets.empty()
            alien_bullets.empty()
            items.empty()

        if game_clear:
            game_clear_text = font.render("GAME CLEAR", True, WHITE)
            screen.blit(game_clear_text, (300, 250))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
