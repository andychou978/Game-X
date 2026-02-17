import pygame
import sys
# 匯入你農出的 5 大模組 (假設檔案都在同一個目錄)
from physics import GameXPhysics
from world_gen import GameXWorldGen
from visuals import GameXVisuals
from interaction import GameXInteraction
from system import GameXSystem

class GameXMain:
    def __init__(self):
        # 1. 系統初始化 (System Initialization)
        self.w, self.h = 1024, 768
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)
        
        # 2. 實例化所有模組 [功能 41-50]
        self.system = GameXSystem(self)
        self.physics = GameXPhysics()
        self.world_gen = GameXWorldGen(seed=888)
        self.visuals = GameXVisuals(self.w, self.h)
        self.interaction = GameXInteraction()
        
        # 3. 遊戲狀態
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.world_map = {}
        
        # 4. 啟動 Logo [功能 46]
        self.system.show_splash_screen(self.screen, "logo.png")

    def run(self):
        # 初始化地圖
        cx, cz = 0, 0
        self.world_map = self.world_gen.request_chunk(cx, cz)
        
        while self.is_running:
            # A. 事件處理 (Event Handling)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                
                # 滑鼠點擊 [功能 31, 32]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    res = self.interaction.raycast(
                        self.physics.pos, self.physics.look_x, 
                        self.physics.look_y, self.world_map, event.button
                    )
                    # 如果挖掘，產生粒子 [功能 27]
                    if res and res["action"] == "break":
                        # 這裡可以呼叫 visuals 產生粒子
                        pass

                # 快速鍵切換 [功能 35]
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F2: # 截圖 [功能 47]
                        self.system.take_screenshot(self.screen)
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        self.interaction.change_selection(event.key - pygame.K_1)

            # B. 物理與控制更新 [功能 1-10]
            keys = pygame.key.get_pressed()
            rel_x, rel_y = pygame.mouse.get_rel()
            self.physics.apply_mouse_movement(rel_x, rel_y)
            self.physics.update(keys, self.world_map)
            
            # C. 動態地圖更新 [功能 11, 44]
            new_cx = int(self.physics.pos[0] // 8)
            new_cz = int(self.physics.pos[2] // 8)
            # 背景讀取新區塊
            self.system.load_data_async(self.world_gen.request_chunk, new_cx, new_cz)

            # D. 渲染管線 (Rendering Pipeline) [功能 21-30]
            sky_data = self.world_gen.get_environment_state(pygame.time.get_ticks() / 1000)
            self.screen.fill(sky_data["sky_color"])
            
            # 這裡執行方塊渲染 (結合 Visuals 的光影與霧氣)
            # 1. 取得玩家周邊方塊
            # 2. 進行面剔除 [功能 42, 43]
            # 3. 繪製方塊與外框 [功能 26]
            
            # E. 介面渲染 [功能 36, 37]
            self.interaction.draw_crosshair(self.screen)
            self.interaction.draw_hud(self.screen)

            pygame.display.flip()
            self.clock.tick(self.system.fps_cap)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameXMain()
    game.run()