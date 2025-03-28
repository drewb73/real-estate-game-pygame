import pygame
import sys
from game.player import Player
from game.property import Property, generate_properties_for_month
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
        self.load_fonts()
        self.market = MarketAnalytics()
        self.market.generate_monthly_samples(1)

        # Initialize UI elements dictionary first
        self.ui_elements = {}

        # Setup UI before player initialization
        self.setup_ui()

        # Then initialize player
        self.player = self.initialize_player()

        # Scroll functionality
        self.portfolio_scroll_y = 0
        self.portfolio_scroll_height = 0
        self.scroll_dragging = False

        # initialize filtered properties
        self.filtered_properties = []
        self.current_property_type = ""

    def create_back_button(self):
        """Helper function to create consistent back buttons"""
        return Button(
            x=50,
            y=50,
            width=150,
            height=40,
            text="Back",
            action=lambda: self.set_screen("main_menu")
        )
    
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
            self.setup_property_buttons(player.available_properties)
            return player
        except Exception as e:
            print(f"Error in player setup: {e}")
            # Fallback to default player with properties
            player = Player("Player", "Medium", 2_500_000)
            player.available_properties = generate_properties_for_month()
            self.setup_property_buttons(player.available_properties)
            return player
        
    def setup_property_buttons(self, properties):
        """Create buy buttons for available properties"""
        if 'buy_properties' not in self.ui_elements:
            self.ui_elements['buy_properties'] = []
        
        # Clear existing property buttons (keep the Back button if it exists)
        self.ui_elements['buy_properties'] = [
            btn for btn in self.ui_elements.get('buy_properties', [])
            if btn.text == "Back"
        ]
        
        # Add new property buttons
        for i, prop in enumerate(properties):
            self.ui_elements['buy_properties'].append(
                Button(
                    x=550,
                    y=160 + i * 150,
                    width=150,
                    height=40,
                    text=f"Buy ${prop.total_price:,.0f}",
                    action=lambda p=prop: self.buy_property(p)
                )
            )
    
    def load_fonts(self):
        """Load all game fonts with fallbacks"""
        try:
            self.fonts = {
                'small': pygame.font.SysFont("Arial", 16),
                'medium': pygame.font.SysFont("Arial", 24),
                'large': pygame.font.SysFont("Arial", 32),
                'title': pygame.font.SysFont("Arial", 48, bold=True)
            }
        except:
            # fallback to default fonts
            self.fonts = {
                'small': pygame.font.Font(None, 24),
                'medium': pygame.font.Font(None, 32),
                'large': pygame.font.Font(None, 48),
                'title': pygame.font.Font(None, 64)
            }
    
    def setup_ui(self):
        """Create all UI elements"""
        button_width = 200
        button_height = 50
        start_y = 150
        spacing = 10



        self.ui_elements = {
            'main_menu': [
                Button(
                    x=self.SCREEN_WIDTH//2 - button_width//2,
                    y=start_y,
                    width=button_width,
                    height=button_height,
                    text="Buy Properties",
                    action=lambda: self.set_screen("property_type_selection")
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - button_width//2,
                    y=start_y + (button_height + spacing) * 1,
                    width=button_width,
                    height=button_height,
                    text="Sell Properties",
                    action=self.show_wip_sell_properties
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - button_width//2,
                    y=start_y + (button_height + spacing) * 2,
                    width=button_width,
                    height=button_height,
                    text="View Portfolio",
                    action=lambda: self.set_screen("portfolio")
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - button_width//2,
                    y=start_y + (button_height + spacing) * 3,
                    width=button_width,
                    height=button_height,
                    text="Market Data",
                    action=lambda: self.set_screen("market")
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - button_width//2,
                    y=start_y + (button_height + spacing) * 4,
                    width=button_width,
                    height=button_height,
                    text="Advance Month",
                    action=self.show_wip_advance_month
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - button_width//2,
                    y=start_y + (button_height + spacing) * 5,
                    width=button_width,
                    height=button_height,
                    text="Exit & Save",
                    action=self.show_wip_exit_save
                )
            ],
            'property_type_selection': [
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=150,
                    width=200,
                    height=50,
                    text="Duplex",
                    action=lambda: self.show_properties_of_type("Duplex")
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=210,
                    width=200,
                    height=50,
                    text="Triplex",
                    action=lambda: self.show_properties_of_type("Triplex")
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=270,
                    width=200,
                    height=50,
                    text="Fourplex",
                    action=lambda: self.show_properties_of_type("Fourplex")
                ),
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=330,
                    width=200,
                    height=50,
                    text="Apartment",
                    action=lambda: self.show_properties_of_type("Apartment")
                ),
                Button(
                   x=self.SCREEN_WIDTH//2 - 100,
                   y=390,
                   width=200,
                   height=50,
                   text="Apartment Complex",
                   action=lambda: self.show_properties_of_type("Apartment Complex")
                ),
                self.create_back_button()
            ],
            'buy_properties': [self.create_back_button()],
            'portfolio': [self.create_back_button()],
            'market': [self.create_back_button()],
            'wip_screen': [
                Button(
                    x=self.SCREEN_WIDTH//2 - 100,
                    y=400,
                    width=200,
                    height=50,
                    text="Back",
                    action=lambda: self.set_screen("main_menu")
                )
            ]
        }

    def show_properties_of_type(self, property_type):
        """Filter and show properties of specific type"""
        self.current_property_type = property_type
        self.filtered_properties = [p for p in self.player.available_properties 
                                if p.property_type == property_type]
        self.set_screen("buy_properties")
    
    def show_wip_sell_properties(self):
        """Show Work In Progress message for Sell Properties"""
        self.wip_message = "Sell Properties (Coming Soon!)"
        self.set_screen("wip_screen")
    
    def show_wip_advance_month(self):
        """Show Work In Progress message for Advance Month"""
        self.wip_message = "Advance Month (Coming Soon!)"
        self.set_screen("wip_screen")
    
    def show_wip_exit_save(self):
        """Show Work In Progress message for Exit & Save"""
        self.wip_message = "Exit & Save (Coming Soon!)"
        self.set_screen("wip_screen")

    def draw_wip_screen(self):
        """Render the Work In Progress screen"""
        # Header
        header = self.fonts['large'].render(
            self.wip_message,
            True,
            self.COLORS['primary']
        )
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - header.get_width()//2, 200))

        # Draw all UI elements
        for element in self.ui_elements.get('wip_screen', []):
            element.draw(self.screen)
    
    def draw_property_type_selection(self):
        """Render the property type selection screen"""
        # Header
        header = self.fonts['large'].render(
            "Select Property Type",
            True,
            self.COLORS['primary']
        )
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - header.get_width()//2, 50))

        # Draw all UI elements
        for element in self.ui_elements.get('property_type_selection', []):
            element.draw(self.screen)
    
    def draw_buy_properties(self):
        """Render the property purchase screen for selected type"""
        # Header showing current property type
        header = self.fonts['large'].render(
            f"Available {self.current_property_type}s",
            True, self.COLORS['primary']
        )
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - header.get_width()//2, 50))

        # Current capital display
        capital_text = self.fonts['medium'].render(
            f"Capital: ${self.player.capital:,.2f}",
            True, self.COLORS['text']
        )
        self.screen.blit(capital_text, (self.SCREEN_WIDTH - capital_text.get_width() - 50, 50))

        # Property list
        if not self.filtered_properties:
            no_props = self.fonts['medium'].render(
                f"No {self.current_property_type}s available this month!",
                True, self.COLORS['text']
            )
            self.screen.blit(no_props, (self.SCREEN_WIDTH//2 - no_props.get_width()//2, 150))
        else:
            # Render property cards with buy buttons
            for i, prop in enumerate(self.filtered_properties):
                self.draw_property_card(prop, 100, 150 + i * 150)
                
                # Buy button
                buy_btn = Button(
                    x=570,
                    y=160 + i * 150,
                    width=150,
                    height=40,
                    text=f"Buy ${prop.total_price:,.0f}",
                    action=lambda p=prop: self.buy_property(p)
                )
                buy_btn.draw(self.screen)
        
        # Back button
        back_btn = Button(
            x=50,
            y=50,
            width=150,
            height=40,
            text="Back to Types",
            action=lambda: self.set_screen("property_type_selection")
        )
        back_btn.draw(self.screen)
                
    def buy_property(self, property):
        """Handle property purchase"""
        if self.player.capital >= property.total_price:
            self.player.capital -= property.total_price
            self.player.properties.append(property)
            
            # Remove from both available_properties and filtered_properties
            if property in self.player.available_properties:
                self.player.available_properties.remove(property)
            if property in self.filtered_properties:
                self.filtered_properties.remove(property)
            
            print(f"Purchased {property.address} for ${property.total_price:,.2f}")
            
            # Refresh the property buttons after purchase
            self.setup_property_buttons(self.player.available_properties)
        else:
            print("Not enough capital!")

    def set_screen(self, screen_name):
        """Set the current screen and reset scroll position"""
        self.current_screen = screen_name
        if screen_name == "portfolio":
            self.portfolio_scroll_y = 0
    
    def handle_events(self):
        """Handle all pygame events"""
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
                if event.button == 1:  # left click
                    self.handle_click(event.pos)
                    # Check if clicking on scrollbar
                    if self.current_screen == "portfolio":
                        scrollbar_rect = self.get_scrollbar_rect()
                        if scrollbar_rect.collidepoint(event.pos):
                            self.scroll_dragging = True
                
                # Mouse wheel scrolling
                elif event.button == 4:  # scroll up
                    if self.current_screen == "portfolio":
                        self.portfolio_scroll_y = min(0, self.portfolio_scroll_y + 20)
                elif event.button == 5:  # scroll down
                    if self.current_screen == "portfolio":
                        max_scroll = -(self.portfolio_scroll_height - self.SCREEN_HEIGHT + 200)
                        self.portfolio_scroll_y = max(max_scroll, self.portfolio_scroll_y - 20)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # left click release
                    self.scroll_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.scroll_dragging and self.current_screen == "portfolio":
                    # Handle scrollbar dragging
                    scrollbar_rect = self.get_scrollbar_rect()
                    mouse_y = event.pos[1]
                    scroll_ratio = (mouse_y - 150) / (self.SCREEN_HEIGHT - 300)
                    max_scroll = -(self.portfolio_scroll_height - self.SCREEN_HEIGHT + 200)
                    self.portfolio_scroll_y = max_scroll * scroll_ratio

    def handle_click(self, pos):
        """Handle mouse clicks on UI elements"""
        # Adjust click position for scroll offset in portfolio view
        if self.current_screen == "portfolio":
            adjusted_pos = (pos[0], pos[1] - self.portfolio_scroll_y)
            # Check if click is in the property list area
            if 50 <= pos[0] <= self.SCREEN_WIDTH - 50 and 150 <= pos[1] <= self.SCREEN_HEIGHT - 50:
                # Handle property clicks here if needed
                pass
        
        # Handle UI element clicks
        for element in self.ui_elements.get(self.current_screen, []):
            if element.rect.collidepoint(pos):
                element.action()
    
    def update(self):
        """Update game state"""
        pass

    def render(self):
        """Render all game elements"""
        self.screen.fill(self.COLORS['background'])

        # Draw current screen
        if self.current_screen == "main_menu":
            self.draw_main_menu()
        elif self.current_screen == "property_type_selection":
            self.draw_property_type_selection()
        elif self.current_screen == "portfolio":
            self.draw_portfolio()
        elif self.current_screen == "buy_properties":
            self.draw_buy_properties()
        elif self.current_screen == "market":
            self.draw_market_data()
        elif self.current_screen == "wip_screen":
            self.draw_wip_screen()

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
        
        # Draw all UI elements
        for element in self.ui_elements.get('market', []):
            element.draw(self.screen)
    
    def draw_main_menu(self):
        """Draw main menu screen"""
        # Title
        title = self.fonts['title'].render(
            "Real Estate Tycoon",
            True,
            self.COLORS['primary']
        )
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # Player info
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
        """Render portfolio screen with scrollable list"""
        # Header
        header = self.fonts['large'].render(
            "Your Portfolio",
            True,
            self.COLORS['primary']
        )
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - header.get_width()//2, 50))

        # Calculate total height needed for all properties
        self.portfolio_scroll_height = 200 + len(self.player.properties) * 120
        
        # Create a clipping area for the property list
        list_area = pygame.Rect(50, 150, self.SCREEN_WIDTH - 100, self.SCREEN_HEIGHT - 200)
        old_clip = self.screen.get_clip()
        self.screen.set_clip(list_area)

        # Property list
        if not self.player.properties:
            no_props = self.fonts['medium'].render(
                "You don't own any properties yet!",
                True,
                self.COLORS['text']
            )
            self.screen.blit(no_props, (self.SCREEN_WIDTH//2 - no_props.get_width()//2, 150))
        else:
            # Render property cards with scroll offset
            for i, prop in enumerate(self.player.properties):
                self.draw_property_card(prop, 100, 150 + i * 120 + self.portfolio_scroll_y)

        # Reset clipping
        self.screen.set_clip(old_clip)

        # Draw scrollbar if needed
        if self.portfolio_scroll_height > self.SCREEN_HEIGHT - 200:
            # Draw scrollbar track
            pygame.draw.rect(
                self.screen,
                (200, 200, 200),  # Light gray track
                pygame.Rect(self.SCREEN_WIDTH - 20, 150, 10, self.SCREEN_HEIGHT - 200),
                border_radius=5
            )
            # Draw scrollbar thumb
            scrollbar_rect = self.get_scrollbar_rect()
            pygame.draw.rect(
                self.screen,
                self.COLORS['primary'],  # Blue thumb
                scrollbar_rect,
                border_radius=5
            )
        
        # Draw all UI elements (including Back button)
        for element in self.ui_elements.get('portfolio', []):
            element.draw(self.screen)
    
    def draw_property_card(self, property, x, y):
        """Render a property card UI element with all details"""
        # Card background
        card_rect = pygame.Rect(x, y, 450, 140)  # Increased height for more info
        pygame.draw.rect(self.screen, (255, 255, 255), card_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.COLORS['primary'], card_rect, width=2, border_radius=8)
        
        # Property info - organized in two columns
        left_col = x + 10
        right_col = x + 230
        
        # Left column
        name = self.fonts['medium'].render(
            f"{property.property_type}: {property.address}",
            True, self.COLORS['text']
        )
        self.screen.blit(name, (left_col, y + 10))
        
        details_left = [
            f"Units: {property.units}",
            f"Price/Unit: ${property.price_per_unit:,.0f}",
            f"Value: ${property.total_price:,.0f}"
        ]
        
        # Right column
        details_right = [
            f"Rent: ${property.rent_per_unit:,.0f}/unit",
            f"CAP: {property.cap_rate:.1f}%",
            f"Gross Income: ${property.gross_income:,.0f}/yr"
        ]
        
        # Draw left column details
        for i, detail in enumerate(details_left):
            text = self.fonts['small'].render(detail, True, self.COLORS['text'])
            self.screen.blit(text, (left_col, y + 40 + i * 20))
        
        # Draw right column details
        for i, detail in enumerate(details_right):
            text = self.fonts['small'].render(detail, True, self.COLORS['text'])
            self.screen.blit(text, (right_col, y + 40 + i * 20))
        
        # Add valuation indicator
        valuation = ""
        if property.cap_rate >= 7: valuation = "🔥🔥 Premium Investment!"
        elif property.cap_rate >= 5.5: valuation = "🔥 Solid Deal"
        elif property.cap_rate <= 3: valuation = "⚠️⚠️ Money Pit"
        elif property.cap_rate <= 4: valuation = "⚠️ Below Average"
        else: valuation = "➖ Average"
        
        valuation_text = self.fonts['small'].render(valuation, True, self.COLORS['text'])
        self.screen.blit(valuation_text, (left_col, y + 110))
    
    def get_scrollbar_rect(self):
        """Calculate scrollbar position and size"""
        if self.portfolio_scroll_height <= self.SCREEN_HEIGHT - 200:
            return pygame.Rect(0, 0, 0, 0)  # No scrollbar needed
        
        # Calculate scrollbar height based on content
        scrollbar_height = max(50, (self.SCREEN_HEIGHT - 200) ** 2 / self.portfolio_scroll_height)
        
        # Calculate scrollbar position based on current scroll
        scroll_ratio = -self.portfolio_scroll_y / (self.portfolio_scroll_height - self.SCREEN_HEIGHT + 200)
        scrollbar_y = 150 + scroll_ratio * (self.SCREEN_HEIGHT - 300 - scrollbar_height)
        
        return pygame.Rect(self.SCREEN_WIDTH - 20, scrollbar_y, 10, scrollbar_height)
    
    def run(self):
        """Main game loop"""
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