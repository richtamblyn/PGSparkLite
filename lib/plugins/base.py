class Plugin:

    max = 1
    min = 0

    def __init__(self, name, type, enabled):        
        self.name = name
        self.effect_type = type
        self.enabled = enabled        
    
    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False