"""
Base Component - Base class cho tất cả GUI components.
"""
import customtkinter as CTK


class BaseComponent:
    """Base class cho tất cả GUI components."""
    
    def __init__(self, parent, main_window):
        """
        Initialize component.
        
        Args:
            parent: Parent widget (CTkFrame)
            main_window: Reference to MainWindow instance để access shared resources
        """
        self.parent = parent
        self.main_window = main_window
        self.container = None
        
        # Quick access to common resources from main_window
        self.settings_manager = main_window.settings_manager
        self.default_values = main_window.default_values
        
    def create(self):
        """
        Create and return the component's main container.
        Must be implemented by subclasses.
        
        Returns:
            CTkFrame: The component's main container widget
        """
        raise NotImplementedError("Subclasses must implement create() method")
    
    def destroy(self):
        """Cleanup and destroy the component."""
        if self.container:
            self.container.destroy()
            self.container = None
    
    def show(self):
        """Show the component."""
        if self.container:
            self.container.pack(fill="both", expand=True)
    
    def hide(self):
        """Hide the component."""
        if self.container:
            self.container.pack_forget()
    
    def get_detector(self, detector_name):
        """
        Get detector instance from main_window.
        
        Args:
            detector_name: Name of detector (e.g., 'tone_detector', 'xvox_detector')
            
        Returns:
            Detector instance or None
        """
        return getattr(self.main_window, detector_name, None)
    
    def pause_auto_detect(self):
        """Pause auto-detect trong main window."""
        if hasattr(self.main_window, 'pause_auto_detect_for_manual_action'):
            self.main_window.pause_auto_detect_for_manual_action()
    
    def resume_auto_detect(self):
        """Resume auto-detect trong main window."""
        if hasattr(self.main_window, 'resume_auto_detect_after_manual_action'):
            self.main_window.resume_auto_detect_after_manual_action()

