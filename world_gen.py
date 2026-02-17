import math
import random

# --- 地圖生成常數 (Generation Constants) ---
CHUNK_SIZE = 8          # [功能 11] 區塊大小
SEA_LEVEL = 0           # [功能 20] 水面高度
CAVE_THRESHOLD = 0.1    # [功能 16] 洞穴生成閾值

class GameXWorldGen:
    def __init__(self, seed=12345):
        # [功能 14] 隨機種子系統
        self.seed = seed
        self.random_gen = random.Random(seed)
        
        # 儲存已生成的區塊數據
        self.chunks = {} 
        self.biomes = ["forest", "desert", "mountains"] # [功能 13] 生物群系

    # --- [功能 12] 簡易雜訊演算法 (Simulated Perlin Noise) ---
    def get_noise_height(self, x, z):
        """根據座標計算地形高度，確保平滑過渡"""
        # 使用多個正弦波疊加來模擬複雜地形
        h = math.sin(x * 0.1 + self.seed) * 2
        h += math.cos(z * 0.15 + self.seed) * 2
        h += math.sin((x + z) * 0.05) * 4  # 大規模起伏
        return int(h)

    # --- [功能 11] 區塊管理 API ---
    def request_chunk(self, cx, cz):
        """當玩家靠近時，動態生成區塊資料"""
        chunk_key = (cx, cz)
        if chunk_key in self.chunks:
            return self.chunks[chunk_key]
        
        # 如果沒生成過，就「農」出一個新的
        return self.generate_chunk(cx, cz)

    def generate_chunk(self, cx, cz):
        """[功能 11, 12, 13, 15, 16, 19] 核心生成邏輯"""
        new_chunk_data = {}
        
        # 決定這個區塊的群系 [功能 13]
        biome = self.random_gen.choice(self.biomes)

        for x in range(cx * CHUNK_SIZE, (cx + 1) * CHUNK_SIZE):
            for z in range(cz * CHUNK_SIZE, (cz + 1) * CHUNK_SIZE):
                # 1. 獲取地表高度 [功能 12]
                base_h = self.get_noise_height(x, z)
                
                # 2. 填充方塊層次 [功能 19]
                for y in range(base_h - 10, base_h + 1):
                    # [功能 16] 洞穴系統：使用隨機機率在地底挖空
                    if y < base_h - 2 and self.random_gen.random() < CAVE_THRESHOLD:
                        continue # 留空，形成洞穴
                    
                    # 決定方塊類型
                    if y == base_h:
                        block_type = "grass" if biome == "forest" else "sand"
                    elif y > base_h - 3:
                        block_type = "dirt"
                    else:
                        block_type = "stone" # 深處是石頭 [功能 19]
                        
                    new_chunk_data[(x, y, z)] = block_type

                # 3. 自動種樹 [功能 15]
                if biome == "forest" and self.random_gen.random() < 0.01:
                    self.add_tree(new_chunk_data, x, base_h + 1, z)

        self.chunks[(cx, cz)] = new_chunk_data
        return new_chunk_data

    # --- [功能 15] 樹木生成演算法 ---
    def add_tree(self, chunk_data, x, y, z):
        """在指定座標種下一棵由木頭與葉子組成的樹"""
        # 樹幹 (Trunk)
        for i in range(3):
            chunk_data[(x, y + i, z)] = "wood"
        # 樹葉 (Leaves)
        for lx in range(-1, 2):
            for lz in range(-1, 2):
                chunk_data[(x + lx, y + 3, z + lz)] = "leaves"

    # --- [功能 17, 18] 環境數據 API ---
    def get_environment_state(self, game_time):
        """回傳當前時間的天空顏色與雲朵位置"""
        # 這裡可以根據時間計算晝夜顏色
        day_progress = (game_time % 60) / 60
        return {
            "sky_color": self.calculate_sky(day_progress),
            "cloud_offset": game_time * 0.5 # [功能 18] 雲朵移動速度
        }

    def calculate_sky(self, progress):
        # 簡易的晝夜轉色邏輯
        if 0.25 < progress < 0.75: return (135, 206, 235) # 白天
        return (20, 20, 40) # 晚上