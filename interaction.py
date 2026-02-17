import pygame
import math
import json

class GameXInteraction:
    def __init__(self):
        # [功能 33] 物品欄系統：存儲方塊 ID
        self.inventory = ["grass", "dirt", "stone", "wood", "leaves"]
        self.selected_index = 0  # [功能 35] 快捷列選中索引
        
        # [功能 37] HUD 狀態
        self.hp = 20
        self.max_hp = 20

    # --- [功能 31 & 32] 挖掘與放置核心 API (Raycasting) ---
    def raycast(self, pos, look_x, look_y, world_map, button):
        """從玩家視角發射射線，偵測前方 5 格內的方塊"""
        ry, rx = math.radians(look_y), math.radians(look_x)
        dx = math.sin(ry) * math.cos(rx)
        dy = math.sin(rx)
        dz = math.cos(ry) * math.cos(rx)

        # 以 0.1 格為步長進行掃描
        for i in range(1, 50):
            d = i * 0.1
            tx, ty, tz = pos[0] + dx * d, pos[1] + dy * d, pos[2] + dz * d
            bx, by, bz = round(tx), round(ty), round(tz)

            if (bx, by, bz) in world_map:
                if button == 1: # 左鍵：[功能 31] 挖掘
                    target_block = world_map[(bx, by, bz)]
                    del world_map[(bx, by, bz)]
                    return {"action": "break", "pos": (bx, by, bz), "type": target_block}
                
                if button == 3: # 右鍵：[功能 32] 放置
                    # 往回推一格，找到放置的位置
                    px, py, pz = round(tx - dx*0.1), round(ty - dy*0.1), round(tz - dz*0.1)
                    block_type = self.inventory[self.selected_index]
                    world_map[(px, py, pz)] = block_type
                    return {"action": "place", "pos": (px, py, pz), "type": block_type}
                break
        return None

    # --- [功能 36] 十字準星渲染 API ---
    def draw_crosshair(self, screen):
        w, h = screen.get_size()
        color = (255, 255, 255)
        pygame.draw.line(screen, color, (w//2 - 10, h//2), (w//2 + 10, h//2), 2)
        pygame.draw.line(screen, color, (w//2, h//2 - 10), (w//2, h//2 + 10), 2)

    # --- [功能 37] HUD 狀態列渲染 ---
    def draw_hud(self, screen):
        # 繪製血條
        pygame.draw.rect(screen, (50, 0, 0), (20, 20, 200, 20)) # 背景
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, self.hp * 10, 20)) # 血量

    # --- [功能 35] 快捷列 API ---
    def change_selection(self, slot_index):
        if 0 <= slot_index < len(self.inventory):
            self.selected_index = slot_index

    # --- [功能 40] 存檔與讀取系統 API (Save/Load) ---
    def save_world(self, world_map, filename="world.json"):
        # 將元組鍵轉換為字串以符合 JSON 格式
        data = {f"{k[0]},{k[1]},{k[2]}": v for k, v in world_map.items()}
        with open(filename, "w") as f:
            json.dump(data, f)
        print("World Saved!")

    def load_world(self, filename="world.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            # 還原為元組鍵
            new_map = {}
            for k, v in data.items():
                coords = tuple(map(int, k.split(',')))
                new_map[coords] = v
            return new_map
        except FileNotFoundError:
            return {}