"""
Mass parameter module for gravity simulation.
This is a modular parameter that can be easily extended or replaced.
"""

class MassParameter:
    """Represents a mass parameter for a gravitational body."""
    
    def __init__(self, value=1000.0, unit="kg"):
        """
        Initialize mass parameter.
        
        Args:
            value: Mass value (default: 1000.0)
            unit: Unit of measurement (default: "kg")
        """
        self.value = value
        self.unit = unit
    
    def get_value(self):
        """Get the mass value."""
        return self.value
    
    def set_value(self, value):
        """Set the mass value."""
        self.value = value
    
    def get_display_name(self):
        """Get display name for GUI."""
        return "Mass"
    
    def get_unit(self):
        """Get the unit of measurement."""
        return self.unit

