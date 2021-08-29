class Plugin:
    def __init__(self, name, type, enabled):
        
        self.name = name
        self.effect_type = type
        self.enabled = enabled

        self.max = 1
        self.min = 0
    
    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False