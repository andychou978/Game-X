import pygame
import math
import random

# --- 視覺常數 ---
FOG_MAX_DIST = 18    # [功能 22] 霧氣完全遮蔽距離
WATER_ALPHA = 160    # [功能 23] 水的透明度 (0-255)

class GameXVisuals:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        # [功能 30] FOV 視野調整 API
        self.fov = 600
        
        # [功能 28] 初始化星空數據
        self.stars = [(random.randint(0, self.w), random.randint(0, self.h)) for _ in range(150)]

    # --- [功能 21] 動態光影 API (Directional Lighting) ---
    def get_shaded_color(self, base_color, normal, sun_pos):
        """根據面法線與太陽位置計算亮度"""
        # 簡單的點積模擬：太陽在正上方時頂部最亮
        dot = max(0.4, normal[0]*sun_pos[0] + normal[1]*sun_pos[1] + normal[2]*sun_pos[2])
        return [int(c * dot) for c in base_color]

    # --- [功能 22] 距離起霧 API (Distance Fog) ---
    def apply_fog(self, color, distance, sky_color):
        """將方塊顏色與背景色依距離混合"""
        factor = min(1.0, distance / FOG_MAX_DIST)
        return [int(color[i] * (1 - factor) + sky_color[i] * factor) for i in range(3)]

    # --- [功能 25] 動態水波 API (Water Waving) ---
    def get_water_offset(self, t, x, z):
        """讓水面方塊產生 Sine 波起伏"""
        return math.sin(t * 2 + x * 0.5 + z * 0.5) * 0.15

    # --- [功能 27] 粒子特效系統 (Particle System) ---
    def create_block_particles(self, pos, color):
        """方塊破碎時產生小碎片"""
        particles = []
        for _ in range(8):
            particles.append({
                "pos": list(pos),
                "vel": [random.uniform(-0.1, 0.1), random.uniform(0.1, 0.2), random.uniform(-0.1, 0.1)],
                "life": 1.0,
                "color": color
            })
        return particles

    # --- [功能 26] 選取外框 API (Block Outline) ---
    def draw_selection_outline(self, screen, pts):
        """在準星指向的方塊繪製高亮邊框"""
        if len(pts) == 4:
            pygame.draw.polygon(screen, (255, 255, 255), pts, 3)

    # --- [功能 28] 星空與天體 API ---
    def draw_celestial(self, screen, sky_color, sun_y):
        # 畫星星 (只有晚上畫)
        if sun_y < 0:
            for star in self.stars:
                alpha = int(abs(sun_y) * 255)
                s = pygame.Surface((2, 2))
                s.fill((255, 255, 255))
                s.set_alpha(alpha)
                screen.blit(s, star)

    # --- [功能 24] 環境光遮蔽 (AO) 模擬 ---
    def apply_ao(self, color, is_edge):
        """如果在方塊邊緣，顏色稍微加深"""
        if is_edge:
            return [int(c * 0.8) for c in color]
        return color

    # --- [功能 29] 材質貼圖支援 (預留接口) ---
    def load_texture(self, path):
        """載入圖片並轉換為方塊表面"""
        return pygame.image.load(path).convert_alpha()