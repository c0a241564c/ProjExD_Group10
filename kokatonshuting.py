import os
import pygame
import sys
import random
import os


# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 40, 0)

if "__file__" in globals():                 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    BASE_DIR = os.getcwd()                  
IMG_DIR = os.path.join(BASE_DIR, "fig")  # ← "ex5" を入れない！

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


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed

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
        if random.randint(1, 300) == 1:  # 1/300の確率で弾を発射
            bullet = AlienBullet(self.rect.centerx, self.rect.bottom)
            self.all_sprites.add(bullet)
            self.alien_bullets.add(bullet)

# 弾クラス
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("ex5/fig/beam.png").convert_alpha()  # ← 画像に変更
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
  
            
# スコアに基づいてランクを取得する関数
def get_rank(score):
     
    """
    # スコアに基づいてランクを取得する関数
    """

    if score >= 300:
        return "S"
    elif score >= 2500:
        return "A"
    elif score >= 200:
        return "B"
    elif score >= 150:
        return "C"
    elif score >= 100:
        return "D"
    else:
        return "E"
    


      # ランキングをファイルに保存
def save_score(score):  # ランキングをファイルに保存する関数
    """
    # ランキングをファイルに保存する関数
    """
    scores = []  # スコアを保存するリスト
    if os.path.exists("ranking.txt"):  # ファイルが存在する場合
        with open("ranking.txt", "r") as f:  # ファイルを読み込む
            scores = [int(line.strip()) for line in f.readlines()]  # 各行を整数に変換してリストに格納
    scores.append(score)  # 新しいスコアを追加
    scores = sorted(scores, reverse=True)[:5]  # 上位5つのスコアを保持
    with open("ranking.txt", "w") as f:  # ファイルに書き込む
        for s in scores:  # 各スコアをファイルに書き込む
            f.write(f"{s}\n")  # ランキングをファイルに保存する


# ランキングを読み込んで上位5位を返す
def load_ranking():  # ランキングを読み込む関数
    """
    # ランキングを読み込む関数
    """
    if not os.path.exists("ranking.txt"):  # ファイルが存在しない場合
        return []  # 空のリストを返す
    with open("ranking.txt", "r") as f:  # ファイルを読み込む
        scores = [int(line.strip()) for line in f.readlines()]  # 各行を整数に変換してリストに格納
    scores.sort(reverse=True)  # スコアを降順にソート
    return scores[:5]  # 上位5つのスコアを返す

# ライフクラス            
class Heart:
    def __init__(self, max_life, filename, pos=(10, 50)):
        """
        ライフの基本設定
        """
        self.max_life = max_life
        self.current_life = max_life
        self.image = load_img(filename)  
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.pos = pos
    def draw(self, screen):
        """
        ライフの描画を行う
        for文を用いてライフの数だけライフの隣に描画していく
        """
        x, y = self.pos
        for i in range(self.current_life):
            screen.blit(self.image, (x + i * 35, y))

    def decrease(self):
        """
        敵の攻撃に当たってしまった場合のライフの処理
        敵の弾に当たるとライフ-1
        ライフが0になるとゲームオーバー
        """
        if self.current_life > 0:
            self.current_life -= 1

    def is_empty(self):
        return self.current_life <= 0

# メインループ
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Space Invaders")
    font = pygame.font.SysFont(None, 55)
    heart = Heart(3, "heart.jpg") # ここでライフクラスを呼ぶ
    all_sprites = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    alien_bullets = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

   

    score = 0
    game_over = False
    game_clear = False
    game_started = False
    score_saved = False

    for i in range(10):
        for j in range(3):
            alien = Alien(50 + i * 50, 70 + j * 80, all_sprites, alien_bullets)
            all_sprites.add(alien)
            aliens.add(alien)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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
            hits = pygame.sprite.groupcollide(bullets, aliens, True, True)
            if hits:
                score += 10
            player_hits = pygame.sprite.spritecollide(player, alien_bullets, True)
            if player_hits:
                heart.decrease()
            if heart.is_empty():
                game_over = True

            for alien in aliens:
                if alien.rect.bottom >= player.rect.top:
                    game_over = True
            if not aliens:
                game_clear = True

        screen.fill(DARK_GREEN)
        all_sprites.draw(screen)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        heart.draw(screen) # ライフを画面に描画

        if (game_over or game_clear) and not score_saved:
            save_score(score)
            score_saved = True

        if game_over:
            game_over_text = font.render("GAME OVER - Press 'R' to Restart", True, WHITE)  # ゲームオーバーテキスト
            screen.blit(game_over_text, (100, 220))
            ranking = load_ranking()  # ランキングを読み込む
            y = 320  # ランキングの表示位置
            screen.blit(font.render("Ranking", True, WHITE), (310, y))  # ランキングタイトル
            for i, s in enumerate(ranking):  # 上位5つのスコアを表示
                y += 40  # ランキングの行間隔
                screen.blit(font.render(f"{i+1}. {s} pts", True, WHITE), (310, y))  # ランキングのスコアを表示

           
            game_over_text = font.render("GAME OVER - Press 'R' to Restart", True, WHITE)
            screen.blit(game_over_text, (150, 250))
            all_sprites.empty()
            aliens.empty()
            bullets.empty()
            alien_bullets.empty()

        if game_clear:
            rank = get_rank(score)  # スコアに基づいてランクを取得
            game_clear_text = font.render("GAME CLEAR", True, WHITE)  # ゲームクリアテキスト
            rank_text = font.render(f"Rank: {rank}", True, WHITE)  # ランクテキスト
            screen.blit(game_clear_text, (300, 250))  # ゲームクリアテキストを画面に描画
            screen.blit(rank_text, (330, 320))  # ランクテキストを画面に描画
            ranking = load_ranking()  # ランキングを読み込む
            y = 360
            screen.blit(font.render("Ranking", True, WHITE), (310, y))  # ランキングタイトル
            for i, s in enumerate(ranking):  # 上位5つのスコアを表示
                y += 40  # ランキングの行間隔
                screen.blit(font.render(f"{i+1}. {s} pts", True, WHITE), (310, y))  # ランキングのスコアを表示



        pygame.display.flip()
        pygame.time.Clock().tick(60)
    if game_over and event.key == pygame.K_r:  # ゲームオーバー時にRキーが押されたら再起動
        pygame.quit()  # Pygameを終了
        os.execl(sys.executable, sys.executable, *sys.argv)  # スクリプトを再起動

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()