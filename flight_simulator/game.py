import pygame
from utils import load_sprite, bomb_collides_with_enemy, remove_off_the_screen_height, get_text_surface
from models import PlayerPlane, EnemyPlane, AmmoDrop
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Game:
    def __init__(self):
        self.__init__pygame()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running, self.playing = True, True
        self.state_stack = []
        self.load_states()
        pass
    
    def _mainloop(self):
        while self.playing:
            self._handle_input()
            self._process_game_logic()
            self._draw()
        pass
    
    def __init__pygame(self):
        pygame.init()
        pygame.display.set_caption("SkyFlight - Flight Simulator")
        pass

    def _handle_input(self):
        self.state_stack[-1]._handle_input()
        pass

    def _process_game_logic(self):
        self.state_stack[-1]._process_game_logic()
        pass

    def _draw(self):
        self.state_stack[-1]._draw()
        pygame.display.flip()
        self.clock.tick(60)
        pass

    def load_states(self):
        self.flight_simulator = MainMenu(self)
        self.state_stack.append(self.flight_simulator)


#############################################################################


# abstract class for representing states
class State():
    def __init__(self, game):
        self.game = game
        self.previous_state = None
    
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
        pass
    
    def _process_game_logic(self):
        pass

    def _draw(self):
        pass

    def enter_state(self):
        # to keep previous state
        if len(self.game.state_stack) > 1:
            self.previous_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()


#############################################################################


class FlightSimulator(State):
    # maybe feature
    SCROLLING_Y = 0
    def __init__(self, game):
        super().__init__(game)

        self.background = load_sprite("space_background", False)


        self.score = 0
        self.level = 0

        self.lifebar = load_sprite("lives")
        self.ammobar = load_sprite("bomb")


        self.ADD_ENEMY = pygame.USEREVENT+1
        pygame.time.set_timer(self.ADD_ENEMY, 1500 - self.level, 1000)

        self.ADD_AMMO_DROP = pygame.USEREVENT+2
        pygame.time.set_timer(self.ADD_AMMO_DROP, 5000, 500)
        
        self.enemies = []
        self.bombs = []
        self.ammo_drops = []

        self.plane = PlayerPlane(self.bombs.append)
        pass    


    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            elif event.type == self.ADD_ENEMY:
                new_enemy = EnemyPlane()
                self.enemies.append(new_enemy)
            elif event.type == self.ADD_AMMO_DROP:
                new_ammodrop = AmmoDrop()
                self.ammo_drops.append(new_ammodrop)
            elif (event.type == pygame.KEYDOWN and 
            event.key == pygame.K_p):
                new_state = PauseMenu(self.game)
                new_state.enter_state()
            elif (self.plane.lives <= 0):
                new_state = EndGame(self.game, self.score)
                new_state.enter_state()

        pressed_keys = pygame.key.get_pressed()
        if self.plane:
            self.plane.move(pressed_keys)


    def _process_game_logic(self):
        for game_object in [*self.enemies, *self.bombs, *self.ammo_drops]:
            game_object.move()
        
        for bomb in self.bombs[:]:
            for enemy in self.enemies[:]:
                if bomb_collides_with_enemy(bomb, enemy):
                    self.score += 50
                    self.bombs.remove(bomb)
                    self.enemies.remove(enemy)
                    break
        
        for ammo_drop in self.ammo_drops[:]:
            if self.plane.rect.colliderect(ammo_drop):
                self.score += 10
                self.plane.ammo += 5
                self.ammo_drops.remove(ammo_drop)
                break
            
        # remove bombs off the screen from rendering
        for bomb in self.bombs[:]:
            if bomb.rect.bottom < 0:
                self.bombs.remove(bomb)
        
        if self.plane:
            for enemy in self.enemies[:]:
                if enemy.rect.top > SCREEN_HEIGHT:
                    self.enemies.remove(enemy)
                    self.plane.lives -= 1
        
        remove_off_the_screen_height(self.ammo_drops)        
        pass


    def _draw(self):
        self.game.screen.blit(self.background, (0, FlightSimulator.SCROLLING_Y))
        # render all game objects
        for game_object in self._get_all_game_objects():
            game_object.draw(self.game.screen)        
        
        # render lives and ammo on top of everything
        if self.plane.lives > 0:
            for lifeNum in range(self.plane.lives):
                self.game.screen.blit(self.lifebar, (lifeNum * self.lifebar.get_width(), 0))
        
        for ammoLeft in range(self.plane.ammo):
            self.game.screen.blit(self.ammobar, (ammoLeft * (self.ammobar.get_width()+2) + 10, self.lifebar.get_height()))

        self.score_box = get_text_surface("Score: " + str(self.score), 50)
        self.score_rect = self.score_box.get_rect(
            topright = (SCREEN_WIDTH - 20, 20)
        )
        self.game.screen.blit(self.score_box, self.score_rect)
        pass


    def _get_all_game_objects(self):
        game_objects = [*self.enemies, *self.bombs, *self.ammo_drops]
        if self.plane:
            game_objects.append(self.plane)
        return game_objects


#############################################################################


class EndGame(State):
    def __init__(self, game, score):
        super().__init__(game)

        self.text_box1 = get_text_surface(f"Final Score:", 100)
        self.text_rect1 = self.text_box1.get_rect(
            center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100)
        )

        self.text_box2 = get_text_surface(f"{score}", 100)
        self.text_rect2 = self.text_box2.get_rect(
            center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        )

        self.text_box3 = get_text_surface(f"Press Enter For Main Menu", 70)
        self.text_rect3 = self.text_box3.get_rect(
            center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2+100)
        )


    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and 
                event.key == pygame.K_ESCAPE):
                quit()
            elif (event.type == pygame.KEYDOWN and 
            event.key == pygame.K_RETURN):
                self.game.state_stack.pop()
                self.game.state_stack.pop()


    def _draw(self):
        self.previous_state._draw()
        self.game.screen.blit(self.text_box1, self.text_rect1)
        self.game.screen.blit(self.text_box2, self.text_rect2)
        self.game.screen.blit(self.text_box3, self.text_rect3)


#############################################################################


class MainMenu(State):
    def __init__(self, game):
        super().__init__(game)

        self.background = load_sprite("space_background", False)

        self.text_box = get_text_surface("Press Enter To Start", 100)
        self.text_rect = self.text_box.get_rect(
            center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        )

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and 
                event.key == pygame.K_ESCAPE):
                quit()
            elif (event.type == pygame.KEYDOWN and 
            event.key == pygame.K_RETURN):
                new_state = FlightSimulator(self.game)
                new_state.enter_state()
    
    # def _process_game_logic(self):
    #     super()._process_game_logic()
    
    def _draw(self):
        self.game.screen.blit(self.background, (0,0))
        self.game.screen.blit(self.text_box, self.text_rect)


#############################################################################



class PauseMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.menu = load_sprite("pause_menu")
        self.menu_rect = self.menu.get_rect(
            center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        )
        self.menu_options = {0 : "play", 1 : "restart", 2 : "options", 3 : "exit"}
        self.index = 0

        self.cursor = load_sprite("cursor")
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.x = self.menu_rect.x + 85

        self.cursor_start_y = self.menu_rect.y + 195
        self.cursor_rect.y = self.cursor_start_y

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and 
                event.key == pygame.K_ESCAPE):
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.exit_state()
                elif event.key == pygame.K_UP:
                    self.index = (self.index - 1) % len(self.menu_options)
                    self.cursor_rect.y = self.cursor_start_y + (90 * self.index)
                elif event.key == pygame.K_DOWN:
                    self.index = (self.index + 1) % len(self.menu_options)
                    self.cursor_rect.y = self.cursor_start_y + (90 * self.index)
                elif event.key == pygame.K_RETURN:
                    self._transition_state()
    
    def _transition_state(self):
        if self.menu_options[self.index] == "play":
            self.exit_state()
        elif self.menu_options[self.index] == "restart":
            self.game.state_stack.pop()
            self.game.state_stack.pop()
            new_state = FlightSimulator(self.game)
            new_state.enter_state()
        elif self.menu_options[self.index] == "options":
            pass # add
        elif self.menu_options[self.index] == "exit":
            while len(self.game.state_stack) > 1:
                self.game.state_stack.pop()

    def _process_game_logic(self):
        return super()._process_game_logic()

    def _draw(self):
        self.previous_state._draw()
        self.game.screen.blit(self.menu, self.menu_rect)
        self.game.screen.blit(self.cursor, self.cursor_rect)



