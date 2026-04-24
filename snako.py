import pyray as pr
from collections import deque
import random

class Game:
    def __init__(self):
        # Game Settings
        self.cellsize = 30
        self.cellcount = 25
        self.offset = 75
        self.score = 0
        self.lastUpdateTime = 0.0
        self.addSegment = False
        self.running = True
        self.moving = False
        self.difficultyScreenActive = True
        self.gameOverScreenActive = False
        self.gameWonScreenActive = False
        self.gameSpeed = 0.25
        
        # Colors
        self.blue = pr.Color(63, 153, 216, 255)
        self.darkblue = pr.Color(0, 0, 139, 255)
        
        # Snake state
        self.snakeBody = deque([pr.Vector2(6, 9), pr.Vector2(5, 9)])
        self.snakeDirection = pr.Vector2(1, 0)
        self.foodPosition = pr.Vector2(0, 0)
        
        # Assets (To be loaded during initiation)
        self.foodTexture = None
        self.EatenSound = None
        self.hitSound = None
        self.backgroundMusic = None
        self.easyMusic = None
        self.mediumMusic = None
        self.hardMusic = None
        self.gameOverMusic = None
        self.currentMusic = None

    def elementInDeque(self, element, d):
        for item in d:
            if pr.vector2_equals(item, element):
                return True
        return False

    def eventTriggered(self, interval):
        currentTime = pr.get_time()
        if currentTime - self.lastUpdateTime >= interval:
            self.lastUpdateTime = currentTime
            return True
        return False

    def GenerateRandomCell(self):
        x = pr.get_random_value(0, self.cellcount - 1)
        y = pr.get_random_value(0, self.cellcount - 1)
        return pr.Vector2(x, y)

    def GenerateRandomFoodPos(self):
        position = self.GenerateRandomCell()
        while self.elementInDeque(position, self.snakeBody):
            position = self.GenerateRandomCell()
        return position

    def DrawSnake(self):
        for i in range(len(self.snakeBody)):
            x = self.snakeBody[i].x
            y = self.snakeBody[i].y
            pr.draw_rectangle(int(self.offset + x * self.cellsize + 1), 
                              int(self.offset + y * self.cellsize + 1), 
                              self.cellsize - 2, self.cellsize - 2, self.darkblue)

    def UpdateSnake(self):
        if not self.moving:
            return

        newHead = pr.vector2_add(self.snakeBody[0], self.snakeDirection)
        self.snakeBody.appendleft(newHead) # Equivalent to push_front

        if pr.vector2_equals(newHead, self.foodPosition):
            self.foodPosition = self.GenerateRandomFoodPos()
            self.score += 1
            self.addSegment = True
            pr.play_sound(self.EatenSound)

        if not self.addSegment:
            self.snakeBody.pop() # Equivalent to pop_back
        else:
            self.addSegment = False

    def GameOver(self):
        self.running = False
        self.moving = False
        self.gameOverScreenActive = True
        if self.currentMusic:
            pr.stop_sound(self.currentMusic)
        self.currentMusic = None
        pr.play_sound(self.gameOverMusic)

    def DrawGameOverScreen(self):
        W = 2 * self.offset + self.cellsize * self.cellcount
        pr.draw_rectangle(0, 0, W, W, pr.Color(63, 153, 216, 200))
        
        title = "GAME OVER"
        title_w = pr.measure_text(title, 60)
        pr.draw_text(title, (W - title_w) // 2, 300, 60, self.darkblue)
        
        score_text = f"Final Score: {self.score}"
        score_w = pr.measure_text(score_text, 40)
        pr.draw_text(score_text, (W - score_w) // 2, 400, 40, self.darkblue)
        
        prompt = "Press Enter to Return to Menu"
        prompt_w = pr.measure_text(prompt, 30)
        pr.draw_text(prompt, (W - prompt_w) // 2, 500, 30, self.darkblue)

    def UpdateGameOverScreen(self):
        if pr.is_key_pressed(pr.KEY_ENTER):
            self.snakeBody = deque([pr.Vector2(6, 9), pr.Vector2(5, 9)])
            self.snakeDirection = pr.Vector2(1, 0)
            self.foodPosition = self.GenerateRandomFoodPos()
            self.score = 0
            self.gameOverScreenActive = False
            self.difficultyScreenActive = True
            if self.currentMusic:
                pr.stop_sound(self.currentMusic)
            pr.stop_sound(self.gameOverMusic)
            self.currentMusic = self.backgroundMusic

    def GameWon(self):
        self.running = False
        self.moving = False
        self.gameWonScreenActive = True
        if self.currentMusic:
            pr.stop_sound(self.currentMusic)
        self.currentMusic = None

    def DrawGameWonScreen(self):
        W = 2 * self.offset + self.cellsize * self.cellcount
        pr.draw_rectangle(0, 0, W, W, pr.Color(63, 216, 153, 200))
        
        title = "YOU WIN!"
        title_w = pr.measure_text(title, 60)
        pr.draw_text(title, (W - title_w) // 2, 300, 60, self.darkblue)
        
        score_text = f"Final Score: {self.score}"
        score_w = pr.measure_text(score_text, 40)
        pr.draw_text(score_text, (W - score_w) // 2, 400, 40, self.darkblue)
        
        prompt = "Press Enter to Return to Menu"
        prompt_w = pr.measure_text(prompt, 30)
        pr.draw_text(prompt, (W - prompt_w) // 2, 500, 30, self.darkblue)

    def UpdateGameWonScreen(self):
        if pr.is_key_pressed(pr.KEY_ENTER):
            self.snakeBody = deque([pr.Vector2(6, 9), pr.Vector2(5, 9)])
            self.snakeDirection = pr.Vector2(1, 0)
            self.foodPosition = self.GenerateRandomFoodPos()
            self.score = 0
            self.gameWonScreenActive = False
            self.difficultyScreenActive = True
            if self.currentMusic:
                pr.stop_sound(self.currentMusic)
            self.currentMusic = self.backgroundMusic

    def CheckCollisionWithFood(self):
        if pr.vector2_equals(self.snakeBody[0], self.foodPosition):
            self.foodPosition = self.GenerateRandomFoodPos()
            self.addSegment = True
            self.score += 1
            pr.play_sound(self.EatenSound)

    def CheckCollisionWithEdges(self):
        head = self.snakeBody[0]
        if head.x == self.cellcount or head.x == -1 or head.y == self.cellcount or head.y == -1:
            self.GameOver()
            pr.play_sound(self.hitSound)

    def CheckCollisionWithBody(self):
        headlessBody = deque(self.snakeBody)
        headlessBody.popleft() # Equivalent to pop_front
        if self.elementInDeque(self.snakeBody[0], headlessBody):
            self.GameOver()
            pr.play_sound(self.hitSound)

    def DrawFood(self):
        pr.draw_texture(self.foodTexture, 
                        int(self.offset + self.foodPosition.x * self.cellsize), 
                        int(self.offset + self.foodPosition.y * self.cellsize), 
                        pr.WHITE)

    def DrawDifficultyScreen(self):
        W = 2 * self.offset + self.cellsize * self.cellcount  # 900

        pr.clear_background(self.blue)

        # --- Title ---
        title = "The Snake Born Again"
        title_w = pr.measure_text(title, 40)
        pr.draw_text(title, (W - title_w) // 2, 25, 40, self.darkblue)

        # Separator line under title
        pr.draw_line(40, 75, W - 40, 75, self.darkblue)

        # --- Subtitle ---
        sub = "Select Difficulty"
        sub_w = pr.measure_text(sub, 35)
        pr.draw_text(sub, (W - sub_w) // 2, 110, 35, self.darkblue)

        # Underline for subtitle
        pr.draw_line((W - sub_w) // 2, 150, (W + sub_w) // 2, 150, self.darkblue)

        # --- Difficulty options ---
        opt1 = "Press  1  for  Easy"
        opt2 = "Press  2  for  Medium"
        opt3 = "Press  3  for  Hard"
        opt_size = 30
        for i, opt in enumerate([opt1, opt2, opt3]):
            opt_w = pr.measure_text(opt, opt_size)
            pr.draw_text(opt, (W - opt_w) // 2, 230 + i * 80, opt_size, self.darkblue)

        # --- Footer ---
        footer = "Developed By: Five Monkeys"
        footer_size = 28
        footer_w = pr.measure_text(footer, footer_size)
        pr.draw_line(40, W - 90, W - 40, W - 90, self.darkblue)
        pr.draw_text(footer, (W - footer_w) // 2, W - 75, footer_size, self.darkblue)

    def UpdateDifficultyScreen(self):
        if pr.is_key_pressed(pr.KEY_ONE) or pr.is_key_pressed(pr.KEY_KP_1):
            self.gameSpeed = 0.25
            self.difficultyScreenActive = False
            if self.currentMusic: pr.stop_sound(self.currentMusic)
            self.currentMusic = self.easyMusic
        elif pr.is_key_pressed(pr.KEY_TWO) or pr.is_key_pressed(pr.KEY_KP_2):
            self.gameSpeed = 0.15
            self.difficultyScreenActive = False
            if self.currentMusic: pr.stop_sound(self.currentMusic)
            self.currentMusic = self.mediumMusic
        elif pr.is_key_pressed(pr.KEY_THREE) or pr.is_key_pressed(pr.KEY_KP_3):
            self.gameSpeed = 0.08
            self.difficultyScreenActive = False
            if self.currentMusic: pr.stop_sound(self.currentMusic)
            self.currentMusic = self.hardMusic

    def initating(self):
        pr.init_window(2 * self.offset + self.cellsize * self.cellcount, 
                       2 * self.offset + self.cellsize * self.cellcount, 
                       "The Snake born again")
        pr.set_target_fps(60)

        pr.init_audio_device()
        self.EatenSound = pr.load_sound("eatingSound.mp3")
        self.hitSound = pr.load_sound("hitSound.mp3")
        self.backgroundMusic = pr.load_sound("backgroundMusic.mp3")
        self.easyMusic = pr.load_sound("easyMusic.mp3")
        self.mediumMusic = pr.load_sound("mediumMusic.mp3")
        self.hardMusic = pr.load_sound("hardMusic.mp3")
        self.gameOverMusic = pr.load_sound("gameOverMusic.mp3")
        pr.set_sound_volume(self.backgroundMusic, 0.5)
        pr.set_sound_volume(self.easyMusic, 0.5)
        pr.set_sound_volume(self.mediumMusic, 0.5)
        pr.set_sound_volume(self.hardMusic, 0.5)
        pr.set_sound_volume(self.gameOverMusic, 0.5)
        self.currentMusic = self.backgroundMusic

        image = pr.load_image("apple.png")
        self.foodTexture = pr.load_texture_from_image(image)
        pr.unload_image(image)
        self.foodPosition = self.GenerateRandomFoodPos()

    def gameRun(self):
        while not pr.window_should_close():
            pr.begin_drawing()

            if self.currentMusic and not pr.is_sound_playing(self.currentMusic):
                pr.play_sound(self.currentMusic)

            if self.difficultyScreenActive:
                self.DrawDifficultyScreen()
                self.UpdateDifficultyScreen()
            elif self.gameOverScreenActive or self.gameWonScreenActive:
                pr.clear_background(self.blue)
                bounds = pr.Rectangle(float(self.offset - 5), float(self.offset - 5), 
                                      float(self.cellsize * self.cellcount + 10), float(self.cellsize * self.cellcount + 10))
                pr.draw_rectangle_lines_ex(bounds, 5, self.darkblue)
                pr.draw_text("The Hungry Snake :3", 235, 20, 40, self.darkblue)
                pr.draw_text("Apples Eaten: ", self.offset - 5, self.offset + self.cellcount * self.cellsize + 10, 40, self.darkblue)
                pr.draw_text(f"{self.score}", 355, self.offset + self.cellcount * self.cellsize + 10, 40, self.darkblue)
                self.DrawFood()
                self.DrawSnake()
                
                if self.gameOverScreenActive:
                    self.DrawGameOverScreen()
                    self.UpdateGameOverScreen()
                else:
                    self.DrawGameWonScreen()
                    self.UpdateGameWonScreen()
            else:
                if self.eventTriggered(self.gameSpeed):
                    if self.running:
                        self.UpdateSnake()
                        self.CheckCollisionWithFood()
                        self.CheckCollisionWithEdges()
                        self.CheckCollisionWithBody()
                        if len(self.snakeBody) >= self.cellcount * self.cellcount:
                            self.GameWon()

                # Movement Controls
                if (pr.is_key_pressed(pr.KEY_UP) or pr.is_key_pressed(pr.KEY_W)) and self.snakeDirection.y != 1:
                    self.snakeDirection = pr.Vector2(0, -1)
                    self.running = True
                    self.moving = True
                if (pr.is_key_pressed(pr.KEY_DOWN) or pr.is_key_pressed(pr.KEY_S)) and self.snakeDirection.y != -1:
                    self.snakeDirection = pr.Vector2(0, 1)
                    self.running = True
                    self.moving = True
                if (pr.is_key_pressed(pr.KEY_RIGHT) or pr.is_key_pressed(pr.KEY_D)) and self.snakeDirection.x != -1:
                    self.snakeDirection = pr.Vector2(1, 0)
                    self.running = True
                    self.moving = True
                if (pr.is_key_pressed(pr.KEY_LEFT) or pr.is_key_pressed(pr.KEY_A)) and self.snakeDirection.x != 1:
                    self.snakeDirection = pr.Vector2(-1, 0)
                    self.running = True
                    self.moving = True

                pr.clear_background(self.blue)
                
                # Draw grid boundary
                bounds = pr.Rectangle(float(self.offset - 5), float(self.offset - 5), 
                                      float(self.cellsize * self.cellcount + 10), float(self.cellsize * self.cellcount + 10))
                pr.draw_rectangle_lines_ex(bounds, 5, self.darkblue)
                
                # Draw UI
                pr.draw_text("The Snake born again", 235, 20, 40, self.darkblue)
                pr.draw_text("Apples Eaten: ", self.offset - 5, self.offset + self.cellcount * self.cellsize + 10, 40, self.darkblue)
                pr.draw_text(f"{self.score}", 355, self.offset + self.cellcount * self.cellsize + 10, 40, self.darkblue)
                
                self.DrawFood()
                self.DrawSnake()

            pr.end_drawing()

    def unloading(self):
        pr.unload_sound(self.EatenSound)
        pr.unload_sound(self.hitSound)
        pr.unload_sound(self.backgroundMusic)
        pr.unload_sound(self.easyMusic)
        pr.unload_sound(self.mediumMusic)
        pr.unload_sound(self.hardMusic)
        pr.unload_sound(self.gameOverMusic)
        pr.unload_texture(self.foodTexture)
        pr.close_audio_device()
        pr.close_window()


if __name__ == "__main__":
    game = Game()
    game.initating()
    game.gameRun()
    game.unloading()