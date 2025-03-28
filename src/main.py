
import pygame
import sys
from game.player import Player
from game.property import Property
from game.market import MarketAnalytics
from game.ui import Button, TextBox
from game.dialogs import PlayerSetupDialog

class RealEstateGame:
    def __init__(self):
        # inistialize pygame
        pygame.init()

        # Game constants
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.FPS = 60

        # colors
        self.COLORS = {
            'background': (240, 240, 240),
            'primary': (30, 136, 229),
            'secondary': (255, 152, 0),
            'text': (50,50,50),
            'highlight': (255, 193, 7)
        }

        # setup display
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Real Estate Investment Simulator")
        self.clock = pygame.time.Clock()


        # Game state
        self.running = True
        self.current_screen = "main_menu"

        # initialize game components
        self.player = self.initialize_player()
        self.ui_elements = self.setup_ui()

        # load fonts
        self.load_fonts()

        # inialize market
        self.market = MarketAnalytics()
        self.market.generate_monthly_samples(1)
    
    def initialize_player(self):
        """Initialize player through GUI dialog"""
        setup_dialog = PlayerSetupDialog(self.screen, self.fonts)
        
        while not setup_dialog.complete:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                setup_dialog.handle_event(event)
            
            setup_dialog.update()
            
            self.screen.fill((240, 240, 240))
            setup_dialog.draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)
        
        return Player(
            setup_dialog.name,
            setup_dialog.difficulty,
            setup_dialog.capital
        )
    
    def load_fonts(self):
        # load all game fonts
        try:
            self.fonts = {
                'small': pygame.font.SysFont("Arial", 16),
                'medium': pygame.font.SysFont("Arial", 24),
                'large': pygame.font.SysFont("Arial", 32),
                'title': pygame.font.SysFont("Arial", 48, bold=True)
            }
        except:
            # fallback to default fonts if specified ones arent available
            self.fonts = {
                'small': pygame.font.Font(None, 24),
                'medium': pygame.font.Font(None, 32),
                'large': pygame.font.Font(None, 48),
                'title': pygame.font.Font(None, 64)
            }
    
    def setup_ui(self):
        # create initial UI elements
        ui_elements = {
            'main_menu': [
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=200,
                    width=200,
                    height=50,
                    text="Buy Properties",
                    action=lambda: self.set_screen("buy_properties")
                ),
                # add more buttons in future
            ],
            # Other screen UI elemetns in future
        }
        return ui_elements
    
    def set_screen(self, screen_name):
        # set the current screen to the specified screen name
        self.current_screen = screen_name
    
    def handle_events(self):
        # Handle all pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_screen == "main_menu":
                        self.running = False
                    else:
                        self.set_screen("main_menu")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left click
                    self.handle_click(event.pos)

    
    def handle_click(self,pos):
        #handle mouse clicks on ui elements
        for element in self.ui_elements.get(self.current_screen, []):
            if element.rect.collidepoint(pos):
                element.action()
    
    def update(self):
        # update game state
        # update market data if needed
        pass

    def render(self):
        # render all game elements
        self.screen.fill(self.COLORS['background'])

        # draw current sccreen
        if self.current_screen == "main_menu":
            self.draw_main_menu()
        elif self.current_screen == "portfolio":
            self.draw_portfolio()
        # draw other screens in future

        pygame.display.flip()
    
    def draw_main_menu(self):
        # draw main menu elements
        # title
        title = self.fonts['title'].render(
            "Real Estate Tycoon",
            True,
            self.COLORS['primary']
        )
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # player info
        capital_text = self.fonts['medium'].render(
            f"Capital: ${self.player.capital:,.2f}",
            True,
            self.COLORS['text']
        )
        self.screen.blit(capital_text, (50, 50))

        # Draw UI elements
        for element in self.ui_elements.get('main_menu',[]):
            element.draw(self.screen)
    
    def draw_portfolio(self):
        # render portfolio screen
        header = self.fonts['large'].render(
            "Your Portfolio",
            True,
            self.COLORS['primary']
        )
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - header.get_width()//2, 50))

        # Proeprty list
        if not self.player.properties:
            no_props = self.fonts['medium'].render(
                "You dont own any properties yet!",
                True,
                self.COLORS['text']
            )
            self.screen.blit(no_props, (self.SCREEN_WIDTH//2 - no_props.get_width()//2, 150))
        else:
            # render proeprty cards
            for i, prop in enumerate(self.player.properties):
                self.draw_property_card(prop, 100, 150 + i * 120)
    
    def draw_property_card(self, property, x, y):
        """Render a property card UI element"""
        # Card background
        card_rect = pygame.Rect(x, y, 400, 100)
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            card_rect,
            border_radius=8
        )
        pygame.draw.rect(
            self.screen,
            self.COLORS['primary'],
            card_rect,
            width=2,
            border_radius=8
        )
        
        # Property info
        name = self.fonts['medium'].render(
            f"{property.property_type}: {property.address}",
            True,
            self.COLORS['text']
        )
        self.screen.blit(name, (x + 10, y + 10))
        
        # More property details...
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RealEstateGame()
    game.run()  
        