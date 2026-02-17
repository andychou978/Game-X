import pygame
import time
import threading
import os

class GameXSystem:
    def __init__(self, engine):
        self.engine = engine
        
        # --- [功能 48] 性能設置 ---
        self.fps_cap = 60
        self.is_loading = False
        self.last_error = None
        
        # --- [功能 45] 指令台系統 ---
        self.console_active = False
        self.command_history = []
        
        # --- [功能 49] 日誌路徑 ---
        self.log_file = "game_x_log.txt"
    
    # --- [功能 46] 自定義啟動畫面 (取代 Pygame Logo) ---
    def show_splash_screen(self, screen, logo_path="logo.png"):
        """
        顯示你的專屬 Logo。改為純白色背景，並修正變數未定義問題。
        """
        screen_w, screen_h = screen.get_size()
        logo_exists = os.path.exists(logo_path) # ✅ 先定義變數
        
        if logo_exists:
            logo = pygame.image.load(logo_path).convert_alpha()
            # 自動縮放 Logo 以適應螢幕 (假設你想要 400x400)
            logo = pygame.transform.smoothscale(logo, (400, 400))
            rect = logo.get_rect(center=(screen_w // 2, screen_h // 2))
            
            # 淡入效果 (Fade In)
            for alpha in range(0, 255, 4):
                screen.fill((255, 255, 255)) # ✅ 背景改為白色
                logo.set_alpha(alpha)
                screen.blit(logo, rect)
                pygame.display.flip()
                pygame.time.delay(10)
            time.sleep(1.2) # 展示時間
        else:
            # ✅ 如果沒有 Logo，在白色背景上顯示黑色文字提示
            font = pygame.font.SysFont("Arial", 32)
            text = font.render("GAME X ENGINE STARTING...", True, (50, 50, 50))
            screen.fill((255, 255, 255)) # ✅ 背景改為白色
            screen.blit(text, (screen_w//2 - 180, screen_h//2))
            pygame.display.flip()
            time.sleep(1)

    # --- [功能 42 & 43] 核心渲染優化 (Culling) ---
    def check_occlusion(self, world_map, pos, direction):
        """
        遮擋剔除：如果方塊的面被鄰居擋住，則回傳 False (不渲染)。
        direction: (dx, dy, dz)
        """
        neighbor = (pos[0] + direction[0], pos[1] + direction[1], pos[2] + direction[2])
        # 如果鄰居存在，則當前的面被遮擋
        return neighbor not in world_map

    # --- [功能 44] 多執行緒異步載入 API ---
    def load_data_async(self, target_func, *args):
        """
        在後台執行繁重的任務（如生成大地圖），不卡住主線程。
        """
        if not self.is_loading:
            self.is_loading = True
            t = threading.Thread(target=self._wrapper, args=(target_func, *args))
            t.daemon = True # 隨主程式一起關閉
            t.start()

    def _wrapper(self, func, *args):
        try:
            func(*args)
        except Exception as e:
            self.log_error(f"Async Error: {e}")
        finally:
            self.is_loading = False

    # --- [功能 45] 開發者指令執行器 ---
    def run_command(self, cmd_string):
        """
        支援 /tp, /set_time, /give 等普及化指令
        """
        parts = cmd_string.split()
        if not parts: return
        
        cmd = parts[0].lower()
        try:
            if cmd == "/tp" and len(parts) >= 4:
                # 傳送玩家: /tp x y z
                self.engine.physics.pos = [float(parts[1]), float(parts[2]), float(parts[3])]
                self.log_error(f"Teleported to {parts[1:]}")
            elif cmd == "/screenshot":
                self.save_screenshot(self.engine.screen)
        except ValueError:
            self.log_error("Invalid command arguments.")

    # --- [功能 47] 截圖功能 ---
    def save_screenshot(self, screen):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"capture_{timestamp}.png"
        pygame.image.save(screen, filename)
        print(f"Screenshot saved as {filename}")

    # --- [功能 49] 錯誤紀錄與日誌 ---
    def log_error(self, message):
        self.last_error = message
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.ctime()}] {message}\n")

    # --- [功能 50] 插件 Mod API 接口 ---
    def register_mod(self, mod_func):
        """
        開放給外部 Python 腳本的掛鉤 (Hook)
        """
        print(f"Mod System: Registering {mod_func.__name__}")
        # 在這裡可以把 mod 函數加入執行列表