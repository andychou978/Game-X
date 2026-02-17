import pygame
import math

# 物理常數設定 (Physics Constants)
GRAVITY = -0.012          # [功能 2] 重力
TERMINAL_VELOCITY = -0.5  # 終端速度
WALK_SPEED = 0.15         # 步行速度
SPRINT_SPEED = 0.25       # [功能 10] 衝刺/慣性基準
JUMP_FORCE = 0.22         # [功能 3] 跳躍力
WATER_DRAG = 0.4          # [功能 8] 水中阻力係數

class GameXPhysics:
    def __init__(self):
        # 玩家狀態 [功能 1]
        self.pos = [0, 10, 0]    # 座標 (x, y, z)
        self.vel = [0, 0, 0]     # 速度向量 (vx, vy, vz)
        self.look_x = 0          # 抬頭角度
        self.look_y = 0          # 轉身角度
        
        self.is_grounded = False # 是否在地面 [功能 4]
        self.is_flying = False   # [功能 7] 飛行模式
        self.in_water = False    # [功能 8] 是否在水中
        
        # 慣性緩衝 [功能 10]
        self.friction = 0.85

    # --- [功能 1] 第一人稱視角控制 API ---
    def apply_mouse_movement(self, dx, dy, sensitivity=0.2):
        self.look_y += dx * sensitivity
        self.look_x = max(-89, min(89, self.look_x + dy * sensitivity))

    # --- [功能 4] AABB 碰撞偵測核心 ---
    def check_collision(self, next_pos, world_map):
        """簡單的點對方塊碰撞偵測"""
        # 檢查腳下、頭頂與身體四周是否有固體方塊
        bx, by, bz = round(next_pos[0]), round(next_pos[1]), round(next_pos[2])
        # 這裡假設 world_map 儲存了固體方塊的座標
        if (bx, by, bz) in world_map:
            return True
        return False

    # --- [功能 2, 3, 7, 8, 9, 10] 綜合運動更新 ---
    def update(self, keys, world_map):
        dt_speed = SPRINT_SPEED if keys[pygame.K_LSHIFT] else WALK_SPEED
        
        # 1. 處理水中阻力 [功能 8]
        if self.in_water:
            dt_speed *= WATER_DRAG
            self.vel[1] *= 0.8 # 水中緩慢下沉

        # 2. 處理移動輸入 (WASD) [功能 1, 10]
        rad = math.radians(self.look_y)
        move_vec = [0, 0]
        if keys[pygame.K_w]: move_vec[0] += math.sin(rad); move_vec[1] += math.cos(rad)
        if keys[pygame.K_s]: move_vec[0] -= math.sin(rad); move_vec[1] -= math.cos(rad)
        if keys[pygame.K_a]: move_vec[0] -= math.cos(rad); move_vec[1] += math.sin(rad)
        if keys[pygame.K_d]: move_vec[0] += math.cos(rad); move_vec[1] -= math.sin(rad)

        # 應用移動速度與慣性 [功能 10]
        self.vel[0] = move_vec[0] * dt_speed + self.vel[0] * self.friction
        self.vel[2] = move_vec[1] * dt_speed + self.vel[2] * self.friction

        # 3. 處理重力與跳躍 [功能 2, 3, 7, 9]
        if not self.is_flying:
            if self.in_water and keys[pygame.K_SPACE]: # [功能 9] 游泳
                self.vel[1] = 0.05
            elif self.is_grounded and keys[pygame.K_SPACE]: # [功能 3] 跳躍
                self.vel[1] = JUMP_FORCE
                self.is_grounded = False
            
            # 應用重力 [功能 2]
            self.vel[1] = max(TERMINAL_VELOCITY, self.vel[1] + GRAVITY)
        else:
            # 飛行模式下的垂直移動 [功能 7]
            if keys[pygame.K_SPACE]: self.vel[1] = 0.2
            elif keys[pygame.K_LCTRL]: self.vel[1] = -0.2
            else: self.vel[1] *= 0.5

        # 4. 最終位置計算與碰撞偵測 [功能 4]
        next_x = self.pos[0] + self.vel[0]
        next_y = self.pos[1] + self.vel[1]
        next_z = self.pos[2] + self.vel[2]

        # 簡單的 Y 軸地板檢查 (防止掉出世界)
        if next_y < 1: # 假設 1 是地平線
            next_y = 1
            self.vel[1] = 0
            self.is_grounded = True
            # [功能 6] 這裡可以計算跌落傷害，如果速度過快
            if self.vel[1] < -0.4: print("Ouch! Fall Damage!") 

        self.pos = [next_x, next_y, next_z]

    # --- [功能 5] 腳步聲觸發 API ---
    def get_step_trigger(self):
        """當玩家在地面且有速度時，回傳 True 以觸發音效"""
        return self.is_grounded and (abs(self.vel[0]) > 0.05 or abs(self.vel[2]) > 0.05)