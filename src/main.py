import pygame
import sys
from game.player import Player
from game.property import Property, generate_properties_for_month  # Add this import
from game.market import MarketAnalytics
from game.ui import Button, TextBox
from game.dialogs import PlayerSetupDialog

class RealEstateGame:
    def __init__(self):
        # initialize pygame
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

        # Initialize critical components first
        self.load_fonts()  # Load fonts BEFORE they're needed
        self.market = MarketAnalytics()
        self.market.generate_monthly_samples(1)

        # Then initialize player and UI
        self.player = self.initialize_player()
        self.ui_elements = self.setup_ui()

        # inialize market
        self.market = MarketAnalytics()
        self.market.generate_monthly_samples(1)
    
    def initialize_player(self):
        """Initialize player through GUI dialog with error handling"""
        try:
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
            
            # Create player and generate initial properties
            player = Player(
                setup_dialog.name,
                setup_dialog.difficulty,
                setup_dialog.capital
            )
            player.available_properties = generate_properties_for_month()
            return player
        except Exception as e:
            print(f"Error in player setup: {e}")
            # Fallback to default player with properties
            player = Player("Player", "Medium", 2_500_000)
            player.available_properties = generate_properties_for_month()
            return player
    
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
        """Create all UI elements"""
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
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=260,
                    width=200,
                    height=50,
                    text="View Portfolio",
                    action=lambda: self.set_screen("portfolio")
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=320,
                    width=200,
                    height=50,
                    text="Market Data",
                    action=lambda: self.set_screen("market")
                )
            ],
            'buy_properties': [
                Button(
                    x=50,
                    y=50,
                    width=150,
                    height=40,
                    text="Back",
                    action=lambda: self.set_screen("main_menu")
                )
            ]
        }
        return ui_elements
    

    def draw_buy_properties(self):
        """Render the property purchase screen"""
        # Header
        header = self.fonts['large'].render(
            "Available Properties",
            True,
            self.COLORS['primary']
        )
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - header.get_width()//2, 50))

        # Property list
        if not self.player.available_properties:
            no_props = self.fonts['medium'].render(
                "No properties available this month!",
                True,
                self.COLORS['text']
            )
            self.screen.blit(no_props, (self.SCREEN_WIDTH//2 - no_props.get_width()//2, 150))
        else:
            # Render property cards with buy buttons
            for i, prop in enumerate(self.player.available_properties):
                self.draw_property_card(prop, 100, 150 + i * 150)
                
                # Add buy button
                buy_btn = Button(
                    x=550,
                    y=160 + i * 150,
                    width=150,
                    height=40,
                    text=f"Buy ${prop.total_price:,.0f}",
                    action=lambda p=prop: self.buy_property(p)
                )
                buy_btn.draw(self.screen)
    
    def buy_property(self, property):
        """Handle property purchase"""
        if self.player.capital >= property.total_price:
            self.player.capital -= property.total_price
            self.player.properties.append(property)
            self.player.available_properties.remove(property)
            print(f"Purchased {property.address} for ${property.total_price:,.2f}")
        else:
            print("Not enough capital!")
    
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
        """Render all game elements"""
        self.screen.fill(self.COLORS['background'])

        # Draw current screen
        if self.current_screen == "main_menu":
            self.draw_main_menu()
        elif self.current_screen == "portfolio":
            self.draw_portfolio()
        elif self.current_screen == "buy_properties":
            self.draw_buy_properties()
        elif self.current_screen == "market":
            self.draw_market_data()

        pygame.display.flip()
    

    def draw_market_data(self):
        """Render market information screen"""
        # Header
        header = self.fonts['large'].render(
            "Market Conditions",
            True,
            self.COLORS['primary']
        )
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - header.get_width()//2, 50))

        # Back button
        back_btn = Button(
            x=50,
            y=50,
            width=150,
            height=40,
            text="Back",
            action=lambda: self.set_screen("main_menu")
        )
        back_btn.draw(self.screen)

        # Market data
        data = self.market.get_latest_market_data()
        if not data:
            no_data = self.fonts['medium'].render(
                "No market data available",
                True,
                self.COLORS['text']
            )
            self.screen.blit(no_data, (self.SCREEN_WIDTH//2 - no_data.get_width()//2, 150))
        else:
            y_pos = 150
            for snapshot in data:
                text = self.fonts['medium'].render(
                    f"{snapshot.property_type}: ${snapshot.avg_price_per_unit:,.0f}/unit, "
                    f"Rent ${snapshot.avg_rent_per_unit:,.0f}, "
                    f"CAP {snapshot.avg_cap_rate:.1f}%",
                    True,
                    self.COLORS['text']
                )
                self.screen.blit(text, (100, y_pos))
                y_pos += 40
    
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
        