import pygame
from .ui import Button, TextBox

class PlayerSetupDialog:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts
        self.name = ""
        self.difficulty = "Medium"
        self.complete = False
        
        # UI Elements
        self.name_input = TextBox(
            x=400, y=200, width=300, height=40,
            placeholder="Enter your name"
        )
        
        self.easy_btn = Button(
            x=400, y=300, width=200, height=50,
            text="Easy ($5M)",
            action=lambda: self.set_difficulty("Easy", 5_000_000)
        )
        
        self.medium_btn = Button(
            x=400, y=360, width=200, height=50,
            text="Medium ($2.5M)",
            action=lambda: self.set_difficulty("Medium", 2_500_000)
        )
        
        self.hard_btn = Button(
            x=400, y=420, width=200, height=50,
            text="Hard ($1M)",
            action=lambda: self.set_difficulty("Hard", 1_000_000)
        )
        
        self.start_btn = Button(
            x=400, y=500, width=200, height=60,
            text="Start Game",
            action=self.complete_setup
        )
        
        self.ui_elements = [
            self.name_input,
            self.easy_btn,
            self.medium_btn,
            self.hard_btn,
            self.start_btn
        ]
    
    def set_difficulty(self, difficulty, capital):
        self.difficulty = difficulty
        self.capital = capital
        # Visual feedback
        self.easy_btn.current_color = self.easy_btn.colors['normal']
        self.medium_btn.current_color = self.medium_btn.colors['normal']
        self.hard_btn.current_color = self.hard_btn.colors['normal']
        
        if difficulty == "Easy":
            self.easy_btn.current_color = (13, 71, 161)
        elif difficulty == "Medium":
            self.medium_btn.current_color = (13, 71, 161)
        else:
            self.hard_btn.current_color = (13, 71, 161)
    
    def complete_setup(self):
        self.name = self.name_input.text
        if self.name and hasattr(self, 'capital'):
            self.complete = True
    
    def handle_event(self, event):
        for element in self.ui_elements:
            if hasattr(element, 'handle_event'):
                element.handle_event(event)
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        for element in self.ui_elements:
            if hasattr(element, 'update'):
                element.update(mouse_pos, mouse_clicked)
    
    def draw(self):
        # Title
        title = self.fonts['title'].render(
            "Real Estate Tycoon - New Game",
            True,
            (30, 136, 229)
        )
        self.screen.blit(title, (400 - title.get_width()//2, 100))
        
        # Name prompt
        name_label = self.fonts['medium'].render(
            "Enter your name:",
            True,
            (50, 50, 50)
        )
        self.screen.blit(name_label, (400, 170))
        
        # Difficulty prompt
        diff_label = self.fonts['medium'].render(
            "Select difficulty:",
            True,
            (50, 50, 50)
        )
        self.screen.blit(diff_label, (400, 270))
        
        # Draw all UI elements
        for element in self.ui_elements:
            element.draw(self.screen)