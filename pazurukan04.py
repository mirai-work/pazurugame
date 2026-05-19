import pyxel
import random
import math
import os

class FireworkPuzzleDeluxe:
    def __init__(self):
        # 画面サイズ 180x120、fps=40で超滑らかに
        pyxel.init(180, 120, title="Firework Committee -Hyper Ultra Max-", fps=40)
        pyxel.mouse(True)
        
        # --- 画像の読み込み処理 (外部ファイル不要) ---
        title_img_path = "title.png"
        ending_img_path = "ending.png"

        # 画像読み込み。Pyxel 2.xの機能を使用。
        images_loaded = False
        try:
            if os.path.exists(title_img_path) and os.path.exists(ending_img_path):
                pyxel.images[0].load(0, 0, title_img_path)
                pyxel.images[1].load(0, 0, ending_img_path)
                images_loaded = True
            else:
                missing_files = []
                if not os.path.exists(title_img_path): missing_files.append(title_img_path)
                if not os.path.exists(ending_img_path): missing_files.append(ending_img_path)
                print(f"警告: 以下の画像ファイルが見つかりません。画像なしで実行します。\n  {', '.join(missing_files)}")
        except Exception as e:
            print(f"エラー: 画像の読み込みに失敗しました: {e}")

        self.use_custom_images = images_loaded

        # 音声データのプロシージャル生成
        self.init_audio()
        
        self.flash = 0
        self.shake = 0
        self.is_gameover = False
        self.is_cleared = False
        self.current_stage_idx = 0
        self.neon_pulse = 0
        self.title_timer = 0 
        self.scene_timer = 0 
        
        self.grid_particles = []
        self.block_colors = [9, 10, 11, 12, 14, 8, 13, 15, 7]
        
        self.all_blocks = [
            [(0,0), (1,0), (0,1), (1,1)], # 1:四角
            [(0,0), (1,0), (2,0), (1,1)], # 2:T字
            [(0,0), (0,1), (0,2), (1,2)], # 3:L字
            [(0,0), (1,0), (2,0), (3,0)], # 4:I字
            [(0,0), (1,0), (3,0), (4,0)], # 5:隙間等辺I
            [(1,0), (-1,0), (0,-1)],     # 6:穴あきT
            [(2,0), (-2,0)],             # 7:長間隔
            [(-1,0), (1,0)],             # 8:短間隔
            [(-1,2), (0,2), (1,2), (-1,-2), (0,-2), (1,-2)], # 9:両柱
        ]
        
        for i, block in enumerate(self.all_blocks):
            mx = min(x for x, y in block)
            my = min(y for x, y in block)
            self.all_blocks[i] = [(x - mx, y - my) for x, y in block]
        
        self.stages = [
            [[ 0, 0, 0, 0, 0],
             [ 0, 0, 0, 0, 0],
             [ 0, 0,-2, 0, 0],
             [ 0, 0, 0, 0, 0],
             [ 0, 0, 0, 0, 0]], 
            
            [[-1, 0, 0, 0,-1],
             [ 0,-2, 0, 0, 0],
             [ 0, 0, 0, 0, 0],
             [ 0, 0, 0, 0, 0],
             [-1, 0, 0, 0,-1]], 

            [[-1,-1, 0,-1,-1],
             [-1, 0, 0, 0,-1],
             [ 0, 0,-2, 0, 0],
             [-1, 0, 0, 0,-1],
             [-1,-1, 0,-1,-1]], 

            [[ 0, 0, 0, 0, 0],
             [ 0, 0,-2, 0, 0],
             [ 0, 0, 0, 0, 0],
             [ 0, 0, 0, 0, 0],
             [ 0, 0, 0, 0, 0]], 

            [[-1,-1,-1,-2,-1,-1,-1],
             [-1,-1, 0, 0, 0,-1,-1],
             [-1,-2, 0, 0, 0,-2,-1],
             [-2, 0, 0,-2, 0, 0,-2],
             [-1,-2, 0, 0, 0,-2,-1],
             [-1,-1, 0, 0, 0,-1,-1],
             [-1,-1,-1,-2,-1,-1,-1]], 
        ]
        
        self.stage_limits = [
            [4, 0, 2, 0, 1, 0, 1, 1, 0, 0],
            [1, 2, 2, 0, 0, 2, 0, 0, 1, 0],
            [1, 1, 1, 1, 1, 2, 0, 1, 0, 0],
            [0, 1, 2, 3, 0, 0, 0, 0, 0, 0],
            [2, 2, 3, 1, 1, 1, 1, 3, 1, 0],
        ]

        self.cx, self.cy = 90, 60
        self.last_mx, self.last_my = pyxel.mouse_x, pyxel.mouse_y

        # 多重スクロール用の星空背景
        self.bg_stars = [
            [[random.randint(0, 180), random.randint(0, 120), random.uniform(0.1, 0.3), 1] for _ in range(30)], 
            [[random.randint(0, 180), random.randint(0, 120), random.uniform(0.3, 0.6), 5] for _ in range(20)], 
            [[random.randint(0, 180), random.randint(0, 120), random.uniform(0.6, 1.2), 7] for _ in range(10)]  
        ]

        self.ending_timer = 0
        self.scene = "TITLE"
        self.fireworks = [] 
        self.sparkles = []
        self.cyber_effects = []

        self.btn_prev = (4, 108, 18, 10)
        self.btn_next = (24, 108, 18, 10)
        self.btn_rot  = (44, 108, 32, 10)
        self.btn_rem  = (78, 108, 32, 10)

        # 流れるスタッフロールのテキスト定義
        self.credits = [
            "THANK YOU FOR PLAYING!",
            "",
            "- STAFF CREDITS -",
            "T. K",
            "GAME DESIGN & CONCEPT",
            "",
            "",
            "PROGRAMMING",
            "M. T",
            "",
            "GRAPHICS & AUDIO ARRANGEMENT",
            "M. T",
            "",
            "SPECIAL THANKS",
            "TEAM TD",
            "AND ALL TEST PLAYERS",
            "",
            "PRESENTED BY MIRAI WORK 2026"
        ]

        pyxel.playm(0, loop=True) 
        pyxel.run(self.update, self.draw)

    def init_audio(self):
        """ プログラム内でSEとBGMを生成 """
        pyxel.sounds[0].set("C3", "P", "6", "N", 4)
        pyxel.sounds[1].set("G4", "S", "5", "F", 3)
        pyxel.sounds[2].set("C2C1", "N", "74", "F", 5)
        pyxel.sounds[3].set("C3E3G3C4", "S", "5555", "NNNF", 6)
        pyxel.sounds[4].set("C2G1D1C1", "N", "7765", "FFFF", 15)
        pyxel.sounds[5].set("E4", "P", "4", "N", 3)

        # タイトル用BGM
        pyxel.sounds[10].set("C2E2G2C3 E2G2C3E3 G2C3E3G3 C3E3G3C4", "T", "5", "N", 12)
        pyxel.sounds[11].set("C1C2C1C2 C1C2C1C2 C1C2C1C2 C1C2C1C2", "S", "4", "N", 12)
        pyxel.musics[0].set([10], [11], [], [])

        # ゲーム中BGM
        pyxel.sounds[12].set("A2C3E3A3 G2B2D3G3 F2A2C3F3 E2G2B2E3", "P", "4", "N", 15)
        pyxel.sounds[13].set("A1A1A1A1 G1G1G1G1 F1F1F1F1 E1E1E1E1", "S", "5", "N", 15)
        pyxel.sounds[14].set("C1 R C1 R C1 R C1 R", "N", "3", "N", 15) 
        pyxel.musics[1].set([12], [13], [14], [])

        # ゲームオーバーBGM
        pyxel.sounds[15].set("D#2 D2 C#2 C2", "T", "6543", "NNNF", 20)
        pyxics = pyxel.musics[2].set([15], [], [], [])

        # エンディングBGM
        pyxel.sounds[16].set("C2D2E2G2 A2B2C3E3 F3G3A3C4 D4E4F4G4", "S", "5", "N", 10)
        pyxel.sounds[17].set("C2 E2 F2 G2", "T", "5", "N", 40)
        pyxel.musics[3].set([16], [17], [], [])

    def setup_stage(self):
        if self.current_stage_idx >= len(self.stages):
            self.scene = "ENDING"
            self.scene_timer = 0
            self.fireworks = []
            self.cyber_effects = []
            self.ending_timer = 0 
            pyxel.stop()
            pyxel.playm(3, loop=True)
            return
            
        if self.current_stage_idx < 0:
            self.current_stage_idx = 0
            
        if self.scene != "TITLE" and self.scene != "HOWTO":
            self.scene = "PLAY"
            
        self.scene_timer = 0
        idx = self.current_stage_idx
        self.grid = [row[:] for row in self.stages[idx]]
        self.block_counts = self.stage_limits[idx][:9]
        
        self.cell_size = 12
        self.offset_x = (130 - len(self.grid[0]) * self.cell_size) // 2
        self.offset_y = (104 - len(self.grid) * self.cell_size) // 2 + 2
        
        self.current_block_idx = next((i for i, c in enumerate(self.block_counts) if c > 0), 0)
        self.current_shape = list(self.all_blocks[self.current_block_idx])
        
        self.cx = self.offset_x + (len(self.grid[0]) // 2) * self.cell_size + (self.cell_size // 2)
        self.cy = self.offset_y + (len(self.grid) // 2) * self.cell_size + (self.cell_size // 2)
        
        self.is_cleared = False
        self.is_gameover = False
        self.clear_timer = 0
        self.gameover_timer = 0 
        self.fireworks = []
        self.grid_particles = []
        self.sparkles = []
        self.cyber_effects = []
        self.flash = 0
        self.shake = 0

        if self.scene == "PLAY":
            pyxel.stop()
            base_speed = 15
            new_speed = max(6, base_speed - (self.current_stage_idx * 2))
            pyxel.sounds[12].speed = new_speed
            pyxel.sounds[13].speed = new_speed
            pyxel.sounds[14].speed = new_speed
            pyxel.playm(1, loop=True)

    def rotate_block(self):
        pyxel.play(3, 1) 
        self.flash = 1
        new_shape = [(-y, x) for x, y in self.current_shape]
        min_x = min(x for x, y in new_shape)
        min_y = min(y for x, y in new_shape)
        self.current_shape = [(x - min_x, y - min_y) for x, y in new_shape]

    def create_grid_particles(self, px, py, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.5)
            self.grid_particles.append([
                px + 6, py + 6,
                math.cos(angle) * speed, math.sin(angle) * speed,
                color, random.randint(10, 20)
            ])

    def create_sparkle(self, x, y, color):
        self.sparkles.append([x, y, color, random.randint(5, 15)])

    def create_mega_fireworks(self, cx, cy):
        count = 55
        base_color = random.choice([7, 9, 10, 11, 12, 14, 15])
        for i in range(count):
            ang = (i / count) * math.pi * 2 + random.uniform(-0.1, 0.1)
            spd = random.uniform(2.0, 5.5)
            self.fireworks.append([cx, cy, math.cos(ang)*spd, math.sin(ang)*spd, base_color, random.randint(30, 50), True])

    def remove_block(self, gx, gy):
        if self.is_on_grid(gx, gy) and self.grid[gy][gx] >= 10:
            pyxel.play(3, 2) 
            b_type = self.grid[gy][gx] - 10
            for r in range(len(self.grid)):
                for c in range(len(self.grid[0])):
                    if self.grid[r][c] == b_type + 10:
                        self.grid[r][c] = 0
                        self.create_grid_particles(self.offset_x + c * self.cell_size, self.offset_y + r * self.cell_size, 8, 12)
            self.block_counts[b_type] += 1
            self.flash = 2
            self.shake = 6
            if self.is_gameover:
                self.is_gameover = False
                pyxel.stop()
                pyxel.playm(1, loop=True) 

    def check_ui_click(self):
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return False
        x, y = self.cx, self.cy
        if self.btn_prev[0] <= x <= self.btn_prev[0]+self.btn_prev[2] and self.btn_prev[1] <= y <= self.btn_prev[1]+self.btn_prev[3]:
            pyxel.play(3, 5); self.change_block(-1); return True
        if self.btn_next[0] <= x <= self.btn_next[0]+self.btn_next[2] and self.btn_next[1] <= y <= self.btn_next[1]+self.btn_next[3]:
            pyxel.play(3, 5); self.change_block(1); return True
        if self.btn_rot[0] <= x <= self.btn_rot[0]+self.btn_rot[2] and self.btn_rot[1] <= y <= self.btn_rot[1]+self.btn_rot[3]:
            self.rotate_block(); return True
        if self.btn_rem[0] <= x <= self.btn_rem[0]+self.btn_rem[2] and self.btn_rem[1] <= y <= self.btn_rem[1]+self.btn_rem[3]:
            gx = (self.cx - self.offset_x) // self.cell_size
            gy = (self.cy - self.offset_y) // self.cell_size
            self.remove_block(gx, gy); return True
                
        sidebar_x = 132
        if sidebar_x <= x <= 180:
            for i in range(9):
                by = 4 + i * 12
                if by <= y <= by + 11:
                    if self.current_block_idx != i: pyxel.play(3, 5)
                    self.current_block_idx = i
                    self.current_shape = list(self.all_blocks[self.current_block_idx])
                    return True
        return False

    def change_block(self, direction):
        self.current_block_idx = (self.current_block_idx + direction) % 9
        self.current_shape = list(self.all_blocks[self.current_block_idx])

    def check_game_over(self):
        for b_idx, count in enumerate(self.block_counts):
            if count <= 0: continue
            test_shape = list(self.all_blocks[b_idx])
            for _ in range(4):
                for gy in range(len(self.grid)):
                    for gx in range(len(self.grid[0])):
                        possible = True
                        for dx, dy in test_shape:
                            nx, ny = gx + dx, gy + dy
                            if not (0 <= nx < len(self.grid[0]) and 0 <= ny < len(self.grid)):
                                possible = False; break
                            if self.grid[ny][nx] != 0:
                                possible = False; break
                        if possible: return False
                new_shape = [(-y, x) for x, y in test_shape]
                mx = min(x for x, y in new_shape)
                my = min(y for x, y in new_shape)
                test_shape = [(x - mx, y - my) for x, y in new_shape]
        return True

    def trigger_gameover(self):
        self.is_gameover = True
        self.gameover_timer = 0
        self.shake = 15
        pyxel.stop()
        pyxel.play(3, 4) 
        pyxel.playm(2, loop=False)

    def update_particles_and_bg(self):
        for layer in self.bg_stars:
            for s in layer:
                s[1] += s[2] 
                if s[1] > 120:
                    s[1] = 0
                    s[0] = random.randint(0, 180)

        for ce in self.cyber_effects[:]:
            ce[0] += ce[2]
            ce[1] += ce[3]
            ce[5] -= 1
            if ce[5] <= 0:
                self.cyber_effects.remove(ce)

        for f in self.fireworks[:]:
            f[0] += f[2] 
            f[1] += f[3] 
            f[3] += 0.05 
            f[5] -= 1    
            if f[5] <= 0 or f[0] < 0 or f[0] > 180 or f[1] > 120:
                self.fireworks.remove(f)
            elif random.random() < 0.2:
                self.create_sparkle(f[0], f[1], f[4])

        for p in self.grid_particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.03 
            p[5] -= 1
            if p[5] <= 0: self.grid_particles.remove(p)

        for sp in self.sparkles[:]:
            sp[3] -= 1
            sp[1] += 0.2
            if sp[3] <= 0: self.sparkles.remove(sp)

    def create_fireworks(self, cx, cy, count, is_premium=False):
        colors = [7, 8, 9, 10, 11, 12, 14, 15] if is_premium else [10, 9, 14, 7]
        base_color = random.choice(colors)
        for i in range(count):
            angle = (i / count) * math.pi * 2 + random.uniform(-0.1, 0.1)
            speed = random.uniform(1.5, 4.0) if is_premium else random.uniform(1.0, 3.0)
            self.fireworks.append([cx, cy, math.cos(angle)*speed, math.sin(angle)*speed, base_color, random.randint(25, 45), is_premium])

    def update(self):
        self.flash = max(0, self.flash - 1)
        self.shake = max(0, self.shake - 1)
        self.neon_pulse = (self.neon_pulse + 1) % 40
        self.scene_timer += 1
        
        self.update_particles_and_bg()
        
        if (pyxel.mouse_x != self.last_mx or pyxel.mouse_y != self.last_my or 
            pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT)):
            self.cx, self.cy = pyxel.mouse_x, pyxel.mouse_y
            self.last_mx, self.last_my = pyxel.mouse_x, pyxel.mouse_y
        
        move_speed = 12 if self.scene == "PLAY" else 3
        if pyxel.btnp(pyxel.KEY_UP, 10, 2) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP): self.cy -= move_speed
        if pyxel.btnp(pyxel.KEY_DOWN, 10, 2) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): self.cy += move_speed
        if pyxel.btnp(pyxel.KEY_LEFT, 10, 2) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): self.cx -= move_speed
        if pyxel.btnp(pyxel.KEY_RIGHT, 10, 2) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): self.cx += move_speed
            
        self.cx = max(0, min(self.cx, 180))
        self.cy = max(0, min(self.cy, 120))

        if self.scene == "TITLE":
            self.title_timer += 1
            
            if pyxel.frame_count % 2 == 0:
                ang = random.uniform(0, math.pi * 2)
                spd = random.uniform(1.5, 5.0)
                self.cyber_effects.append([90, 60, math.cos(ang)*spd, math.sin(ang)*spd, random.choice([7, 9, 10, 11, 14]), 25, "star"])
            
            if self.title_timer % 20 == 0:
                self.cyber_effects.append([90, 38, 0, 0, random.choice([10, 14, 7]), 20, "ring"])

            if self.title_timer % 30 == 0:
                self.create_fireworks(random.randint(20, 160), random.randint(20, 60), 35, is_premium=True)

            if self.scene_timer > 10:
                if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN) or 
                    pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)):
                    pyxel.play(3, 3) 
                    self.scene = "HOWTO"
                    self.scene_timer = 0
                    self.fireworks = []
                    self.cyber_effects = []
            return

        if self.scene == "HOWTO":
            if self.scene_timer > 10:
                if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN) or 
                    pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)):
                    pyxel.play(3, 3)
                    self.current_stage_idx = 0
                    self.scene = "PLAY"
                    self.setup_stage()
            return

        if self.scene == "ENDING":
            self.ending_timer += 1
            
            if pyxel.frame_count % 2 == 0:
                self.cyber_effects.append([random.randint(0, 180), 120, random.uniform(-0.5, 0.5), random.uniform(-2.0, -4.0), random.choice([7, 10, 11, 12, 14, 15]), 35, "bubble"])
            
            if pyxel.frame_count % 6 == 0: 
                self.create_mega_fireworks(random.randint(15, 165), random.randint(15, 75))

            if self.scene_timer > 10:
                # 400フレーム制限を撤廃、または十分に長く設定して最後まで読めるように調整
                if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                    self.scene = "TITLE"
                    self.scene_timer = 0
                    self.title_timer = 0
                    self.is_gameover = False 
                    self.fireworks = []
                    self.cyber_effects = []
                    pyxel.stop()
                    pyxel.playm(0, loop=True)
            return

        if self.scene_timer > 10:
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                if self.is_gameover: 
                    self.scene = "TITLE"; self.scene_timer = 0; self.title_timer = 0; self.is_gameover = False 
                    pyxel.stop(); pyxel.playm(0, loop=True)
                else: self.setup_stage()
                return

        if pyxel.btnp(pyxel.KEY_N): self.current_stage_idx += 1; self.setup_stage(); return
        if pyxel.btnp(pyxel.KEY_P): self.current_stage_idx -= 1; self.setup_stage(); return

        if self.is_cleared:
            self.clear_timer += 1
            if pyxel.frame_count % 8 == 0: 
                self.create_fireworks(random.randint(20, 110), random.randint(20, 60), 20, is_premium=False)
            if self.clear_timer > 120:
                self.current_stage_idx += 1
                self.setup_stage()
            return
            
        if self.is_gameover:
            self.gameover_timer += 1
            if self.scene_timer > 10:
                if (self.gameover_timer > 150 or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or 
                    pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)):
                    self.scene = "TITLE"; self.scene_timer = 0; self.title_timer = 0; self.is_gameover = False 
                    pyxel.stop(); pyxel.playm(0, loop=True)
            return

        for i in range(9):
            if pyxel.btnp(getattr(pyxel, f"KEY_{i+1}")):
                self.current_block_idx = i; self.current_shape = list(self.all_blocks[i]); pyxel.play(3, 5)

        if (pyxel.btnp(pyxel.KEY_LSHIFT) or pyxel.btnp(pyxel.KEY_RSHIFT) or 
            pyxel.mouse_wheel != 0 or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)): self.rotate_block()

        if pyxel.btnp(pyxel.KEY_E) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER): pyxel.play(3, 5); self.change_block(1)
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER): pyxel.play(3, 5); self.change_block(-1)

        if self.check_ui_click(): return

        gx = (self.cx - self.offset_x) // self.cell_size
        gy = (self.cy - self.offset_y) // self.cell_size

        btn_place = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        btn_rotate = pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT)
        btn_remove = pyxel.btnp(pyxel.KEY_BACKSPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X)

        if btn_place and self.scene_timer > 5: 
            if self.block_counts[self.current_block_idx] > 0 and self.can_place(gx, gy):
                pyxel.play(3, 0) 
                for dx, dy in self.current_shape:
                    self.grid[gy + dy][gx + dx] = self.current_block_idx + 10 
                    self.create_grid_particles(self.offset_x + (gx+dx) * self.cell_size, self.offset_y + (gy+dy) * self.cell_size, self.block_colors[self.current_block_idx], 8)
                self.block_counts[self.current_block_idx] -= 1
                self.flash = 3
                self.shake = 4
                
                if all(0 not in row for row in self.grid):
                    self.is_cleared = True; self.clear_timer = 0; pyxel.stop(); pyxel.play(3, 3) 
                else:
                    if self.check_game_over(): self.trigger_gameover()
                
        if btn_rotate:
            if self.is_on_grid(gx, gy) and self.grid[gy][gx] >= 10: self.remove_block(gx, gy)
            else: self.rotate_block()
                
        if btn_remove: self.remove_block(gx, gy)

    def is_on_grid(self, gx, gy):
        return 0 <= gx < len(self.grid[0]) and 0 <= gy < len(self.grid)

    def can_place(self, gx, gy):
        for dx, dy in self.current_shape:
            nx, ny = gx + dx, gy + dy
            if not self.is_on_grid(nx, ny) or self.grid[ny][nx] != 0: return False
        return True

    def text_hd(self, x, y, text, col, shadow_col=0):
        pyxel.text(x+1, y+1, text, shadow_col)
        pyxel.text(x, y, text, col)

    def text_glow(self, x, y, text, col, glow_col=1):
        pyxel.text(x+1, y, text, glow_col)
        pyxel.text(x-1, y, text, glow_col)
        pyxel.text(x, y+1, text, glow_col)
        pyxel.text(x, y-1, text, glow_col)
        pyxel.text(x, y, text, col)

    def draw_cyber_effects(self):
        for ce in self.cyber_effects:
            if ce[6] == "star":
                pyxel.line(ce[0], ce[1], ce[0]-ce[2]*1.8, ce[1]-ce[3]*1.8, ce[4])
                pyxel.pset(ce[0], ce[1], 7) 
            elif ce[6] == "ring":
                r = (20 - ce[5]) * 4
                pyxel.rectb(ce[0] - r, ce[1] - r // 2, r * 2, r, ce[4])
            elif ce[6] == "bubble":
                if ce[5] > 10:
                    pyxel.circb(ce[0], ce[1], 2, ce[4])
                    pyxel.pset(ce[0], ce[1], 7)
                else:
                    pyxel.pset(ce[0], ce[1], ce[4])

    def draw_premium_block(self, x, y, size, block_type):
        base_col = self.block_colors[block_type]
        core_col = 7 if base_col != 14 else 10
        pyxel.rect(x+1, y+1, size, size, 0)
        pyxel.rect(x, y, size, size, base_col)
        highlight = 11 if base_col != 11 else 10
        pyxel.line(x, y, x+size-1, y, highlight)
        pyxel.line(x, y, x, y+size-1, highlight)
        pyxel.line(x, y+size-1, x+size-1, y+size-1, 1)
        pyxel.line(x+size-1, y, x+size-1, y+size-1, 1)
        pyxel.rect(x+3, y+3, size-6, size-6, 0)
        pyxel.rect(x+4, y+4, size-8, size-8, core_col)

    def draw_premium_obstacle(self, x, y, size):
        pyxel.rect(x+1, y+1, size, size, 0) 
        pyxel.rect(x, y, size, size, 1)     
        pyxel.rect(x+2, y+2, size-4, size-4, 5)
        pyxel.rect(x+4, y+4, size-8, size-8, 13)
        pyxel.line(x+2, y+2, x+size-3, y+size-3, 0)
        pyxel.line(x+size-3, y+2, x+2, y+size-3, 0)

    def draw_hologram_preview(self, x, y, w, h, col):
        for dy in range(h):
            if (dy + pyxel.frame_count // 2) % 3 != 0:
                pyxel.line(x, y + dy, x + w - 1, y + dy, col)

    def draw_live_fireworks(self):
        for f in self.fireworks:
            color = f[4]
            if f[6]: 
                if f[5] > 30: color = 7  
                elif f[5] > 18: color = f[4]
                else: color = 8 if f[5] > 8 else 2
            if f[5] > 0:
                pyxel.line(f[0], f[1], f[0] - f[2]*1.2, f[1] - f[3]*1.2, color)
        for sp in self.sparkles:
            pyxel.pset(sp[0], sp[1], sp[2] if sp[3] > 5 else 13)

    def draw(self):
        cam_x = random.randint(-2, 2) if self.shake > 0 else 0
        cam_y = random.randint(-2, 2) if self.shake > 0 else 0
        pyxel.camera(cam_x, cam_y)

        # ← これを先に移動
        pulse_intensity = math.sin(self.neon_pulse * 0.15)

        # --- サイバー背景 ---
        # --- ステージごとの背景色 ---
        stage_bg_colors = [
            1,   # STAGE 1 : 青
            5,   # STAGE 2 : 紫
            3,   # STAGE 3 : 緑
            4,   # STAGE 4 : 茶
            6    # STAGE 5 : 水色
        ]

        # GAME OVER は真っ赤
        if self.is_gameover:
            bg = 8
        else:
            bg = stage_bg_colors[
                self.current_stage_idx % len(stage_bg_colors)
            ]

        pyxel.cls(bg)

        # 流れる星
        for layer in self.bg_stars:
            for s in layer:
                star_col = s[3]

                if self.is_gameover:
                    if star_col == 7:
                        star_col = 8
                    elif star_col == 5:
                        star_col = 2

                pyxel.pset(s[0], s[1], star_col)

                if s[2] > 0.5:
                    pyxel.line(
                        s[0],
                        s[1],
                        s[0],
                        s[1] - s[2] * 4,
                        star_col
                    )
        
        pulse_intensity = math.sin(self.neon_pulse * 0.15)
        grid_col = 1
        if self.scene == "PLAY":
            for i in range(0, 180, 24): pyxel.line(i, 0, i, 120, grid_col)
            for j in range(0, 120, 24): pyxel.line(0, j, 180, j, grid_col)

        for p in self.grid_particles:
            pyxel.circ(p[0], p[1], 1 if p[5] < 8 else 2, p[4] if p[5] > 5 else 13)

        # --- タイトル画面の描画 ---
        if self.scene == "TITLE":
            try:
                pyxel.blt(0, 0, 0, 0, 0, 180, 120)
            except Exception:
                pass

            self.draw_cyber_effects()
            self.draw_live_fireworks() 
            bounce_y = math.sin(self.title_timer * 0.1) * 4
            
            self.text_glow(23, 26 + bounce_y, "FIREWORK COMMITTEE", 7, 10)
            self.text_glow(42, 38 + bounce_y, "- HYPER ULTRA MAX -", 14, 1)
            
            if (pyxel.frame_count // 8) % 2 == 0:
                pyxel.rect(26, 84, 128, 9, 1)
                self.text_hd(31, 86, "SPACE KEY / A BUTTON START", 7, 0)
            else:
                self.text_hd(31, 86, "SPACE KEY / A BUTTON START", 5, 0)
                
            self.text_hd(28, 108, "(C)MIRAI WORK/T.K/arr M.T 2026", 13, 0)
            self.draw_cursor()
            return

        if self.scene == "HOWTO":
            pyxel.rect(5, 5, 120, 110, 0)
            pyxel.rectb(5, 5, 120, 110, 7)
            # ===== FIREWORK =====
            pyxel.text(140, 12, "FIREWORK", 0)
            pyxel.text(138, 12, "FIREWORK", 0)
            pyxel.text(139, 13, "FIREWORK", 0)
            pyxel.text(139, 11, "FIREWORK", 7)
            pyxel.text(139, 12, "FIREWORK", 10)

            # ===== COMMITTEE =====
            pyxel.text(138, 22, "COMMITTEE", 0)
            pyxel.text(136, 22, "COMMITTEE", 0)
            pyxel.text(137, 23, "COMMITTEE", 0)
            pyxel.text(137, 21, "COMMITTEE", 7)
            pyxel.text(137, 22, "COMMITTEE", 10)

            # --- COPYRIGHT ---
            pyxel.text(128, 88, "(C)MIRAIWORK", 0)
            pyxel.text(126, 86, "(C)MIRAIWORK", 5)
            pyxel.text(127, 87, "(C)MIRAIWORK", 7)

            pyxel.text(132, 98, "T.K/arr M.T", 0)
            pyxel.text(130, 96, "T.K/arr M.T", 5)
            pyxel.text(131, 97, "T.K/arr M.T", 7)

            pyxel.text(160, 108, "2026", 0)
            pyxel.text(158, 106, "2026", 5)
            pyxel.text(159, 107, "2026", 7)
            self.text_hd(36, 10, "- HOW TO PLAY -", 10, 1)
            self.text_hd(10, 25, "MOVE  : ARROW / MOUSE", 7, 1)
            self.text_hd(10, 38, "PLACE : [SPACE] / L-CLICK", 10, 1)
            self.text_hd(10, 51, "ROT   : [SHIFT] / R-CLICK", 14, 1)
            self.text_hd(10, 64, "REM   : [BACKSPACE]", 8, 1)
            self.text_hd(10, 77, "STOCK : [Q],[E] / [1]-[9]", 13, 1)
            
            guide_col = pyxel.frame_count % 16 if self.scene_timer > 10 else 5
            self.text_hd(16, 98, ">> CLICK TO START <<", guide_col, 1)
            self.draw_cursor()
            return

        # --- エンディング画面の描画 ---
        if self.scene == "ENDING":
            try:
                pyxel.blt(0, 0, 1, 0, 0, 180, 120)
            except Exception:
                pass

            self.draw_cyber_effects()
            self.draw_live_fireworks() 
            
            # --- スタッフロールのスクロール描画処理 ---
            # 各行の間隔を12ピクセルとし、下から上へ移動
            line_spacing = 12
            total_scroll_height = len(self.credits) * line_spacing
            
            # スクロールの初期Y位置（画面下端120から徐々に上がっていく、速度調整用0.4）
            scroll_y = 120 - (self.ending_timer * 0.4)
            
            # すべてのテキストが画面上部に消え去ったら、スクロール位置をリセット（無限ループ）
            if scroll_y < -total_scroll_height:
                self.ending_timer = 0
                scroll_y = 120

            # 各テキスト行の描画
            for i, line in enumerate(self.credits):
                current_line_y = scroll_y + (i * line_spacing)
                # 画面内（0〜105ピクセル付近）にある場合のみ描画（下部ガイド表示枠と被らないように制御）
                if -10 <= current_line_y <= 90:
                    # テキストの長さから、画面中央に寄せるためのX座標を簡易計算（1文字あたり4ピクセル換算）
                    text_x = (180 - (len(line) * 4)) // 2
                    self.text_hd(text_x, int(current_line_y), line, 7, 1)
            
            # 操作ガイド表示枠（常に最前面の下部に固定表示）
            pyxel.rect(0, 94, 180, 26, 0)
            pyxel.line(0, 94, 180, 94, 5)
            guide_col = 7 if pyxel.frame_count % 16 < 8 else 13
            self.text_hd(32, 98, "R KEY / START TO TITLE", guide_col, 1)
            self.text_hd(28, 110, "(C)MIRAI WORK/T.K/arr M.T 2026", 5, 0)
            return

        for b in [self.btn_prev, self.btn_next, self.btn_rot, self.btn_rem]:
            hover = (b[0] <= self.cx <= b[0]+b[2] and b[1] <= self.cy <= b[1]+b[3])
            pyxel.rect(b[0], b[1], b[2], b[3], 0)
            pyxel.rect(b[0]+1, b[1]+1, b[2]-2, b[3]-2, 13 if hover else 1)
            
        self.text_hd(self.btn_prev[0]+5, self.btn_prev[1]+3, "LB", 7, 0)
        self.text_hd(self.btn_next[0]+5, self.btn_next[1]+3, "RB", 7, 0)
        self.text_hd(self.btn_rot[0]+11, self.btn_rot[1]+3, "ROT", 7, 0)
        self.text_hd(self.btn_rem[0]+11, self.btn_rem[1]+3, "REM", 7, 0)

        self.text_hd(4, 4, f"STG {self.current_stage_idx+1}", 10, 1)

        sidebar_x = 132
        pyxel.rect(sidebar_x, 2, 46, 116, 0)
        pyxel.rect(sidebar_x+1, 3, 44, 114, 1)
        pyxel.rectb(sidebar_x, 2, 46, 116, 5)
        
        for i in range(9):
            y = 4 + i * 12
            is_selected = (i == self.current_block_idx)
            has_item = self.block_counts[i] > 0
            if is_selected: 
                pyxel.rect(sidebar_x+1, y, 44, 11, 2)
                pyxel.line(sidebar_x+1, y+11, sidebar_x+44, y+11, 1)
            
            text_col = 14 if is_selected else (7 if has_item else 5)
            pyxel.text(sidebar_x+3, y+3, f"{i+1}:{self.block_counts[i]}", text_col)
            
            preview_col = self.block_colors[i] if has_item else 5
            bw = max(x for x, y in self.all_blocks[i]) + 1
            bh = max(y for x, y in self.all_blocks[i]) + 1
            
            pitch = 2; center_x = sidebar_x + 34; center_y = y + 5
            start_x = center_x - (bw * pitch) // 2; start_y = center_y - (bh * pitch) // 2
            for dx, dy in self.all_blocks[i]: pyxel.rect(start_x + dx * pitch, start_y + dy * pitch, 2, 2, preview_col)

        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                px, py = self.offset_x + x * self.cell_size, self.offset_y + y * self.cell_size
                if val == -1: continue
                elif val == 0:
                    pyxel.rect(px, py, self.cell_size, self.cell_size, 0)

                    highlight = False

                    if not self.is_cleared and not self.is_gameover:
                        gx = (self.cx - self.offset_x) // self.cell_size
                        gy = (self.cy - self.offset_y) // self.cell_size

                        if self.can_place(gx, gy):
                            for dx, dy in self.current_shape:
                                if gx + dx == x and gy + dy == y:
                                    highlight = True
                                    break

                    # 白枠か通常枠かを1回だけ描画
                    pyxel.rectb(
                        px,
                        py,
                        self.cell_size,
                        self.cell_size,
                        7 if highlight else (1 if pulse_intensity < 0.5 else 5)
                    )
                elif val == -2: self.draw_premium_obstacle(px, py, self.cell_size)
                elif val >= 10: self.draw_premium_block(px, py, self.cell_size, val - 10)

        if not self.is_cleared and not self.is_gameover:
            gx, gy = (self.cx - self.offset_x) // self.cell_size, (self.cy - self.offset_y) // self.cell_size
            can_place_here = self.can_place(gx, gy)
            stock_exists = self.block_counts[self.current_block_idx] > 0

            preview_color = self.block_colors[self.current_block_idx] if (can_place_here and stock_exists) else 8

            for dx, dy in self.current_shape:
                if can_place_here and stock_exists:
                    px = self.offset_x + (gx + dx) * self.cell_size
                    py = self.offset_y + (gy + dy) * self.cell_size

                    # 中のホログラム色
                    self.draw_hologram_preview(
                        px + 1,
                        py + 1,
                        self.cell_size - 2,
                        self.cell_size - 2,
                        preview_color
                    )

                    # 外側だけ白枠
                    pyxel.rectb(
                        px,
                        py,
                        self.cell_size,
                        self.cell_size,
                        7
                    )

                else:
                    self.draw_hologram_preview(
                        self.cx + dx * self.cell_size - (self.cell_size // 2) + 1,
                        self.cy + dy * self.cell_size - (self.cell_size // 2) + 1,
                        self.cell_size - 1,
                        self.cell_size - 1,
                        preview_color
                    )

        if self.is_cleared:
            self.draw_live_fireworks()
            self.text_hd(42, 50, "EXCELLENT!", pyxel.frame_count % 16, 1)

        if self.is_gameover:
            pyxel.rect(0, 45, 130, 24, 0); pyxel.rectb(0, 45, 130, 24, 8)
            self.text_hd(45, 54, "GAME OVER", 8, 1)

        self.draw_cursor()

    # 【補完】途切れていた自作カーソルの描画処理を完全に修復
    def draw_cursor(self):
        pyxel.line(self.cx-2, self.cy, self.cx+6, self.cy, 7)
        pyxel.line(self.cx, self.cy-2, self.cx, self.cy+6, 7)

FireworkPuzzleDeluxe()
