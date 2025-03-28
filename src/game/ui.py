import pygame

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.colors = {
            'normal': (30, 136, 229),
            'hover': (66, 165, 245),
            'pressed': (13, 71, 161)
        }
        self.current_color = self.colors['normal']
        self.font = pygame.font.SysFont("Arial", 20)
    
    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.current_color,
            self.rect,
            border_radius=5
        )
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def update(self, mouse_pos, mouse_clicked):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.colors['hover']
            if mouse_clicked:
                self.current_color = self.colors['pressed']
                if self.action:
                    self.action()
        else:
            self.current_color = self.colors['normal']

class TextBox:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.font = pygame.font.SysFont("Arial", 20)
    
    def draw(self, surface):
        color = (50, 50, 50) if self.active else (150, 150, 150)
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        if self.text:
            text_surf = self.font.render(self.text, True, (0, 0, 0))
        else:
            text_surf = self.font.render(self.placeholder, True, (200, 200, 200))
        
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode