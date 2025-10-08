"""
Footer Component - Version, Theme, Debug buttons và Copyright.
"""
import customtkinter as CTK
import config
from gui.components.base_component import BaseComponent


class Footer(BaseComponent):
    """Component cho footer với controls và thông tin."""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        
        # UI element references
        self.theme_button = None
        self.debug_button = None
        self.copyright_label = None
        
    def create(self):
        """Tạo footer."""
        # Footer container - minimal height
        self.container = CTK.CTkFrame(self.parent, fg_color="#1F1F1F", corner_radius=0, height=25)
        self.container.pack_propagate(False)
        
        footer_frame = CTK.CTkFrame(self.container, fg_color="transparent")
        footer_frame.pack(fill="both", expand=True, padx=8, pady=3)
        
        # App version (left side)
        version_label = CTK.CTkLabel(
            footer_frame,
            text=f"{config.APP_VERSION}",
            font=("Arial", 10),
            text_color="gray"
        )
        version_label.pack(side="left")
        
        # Debug button
        self.debug_button = CTK.CTkButton(
            footer_frame,
            text="D",
            command=self._show_debug_window,
            width=25,
            height=18,
            font=("Arial", 10),
            corner_radius=3,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        self.debug_button.pack(side="left", padx=(2, 0))
        
        # Copyright (right side)
        self.copyright_label = CTK.CTkLabel(
            footer_frame,
            text=config.COPYRIGHT,
            font=("Arial", 12, "bold"),
            text_color="#FF6B6B",
            cursor="hand2"
        )
        self.copyright_label.pack(side="right")
        
        # Make copyright clickable (copy phone to clipboard)
        self.copyright_label.bind("<Button-1>", self._copy_phone)
        
        return self.container
    
    # ==================== EVENT HANDLERS ====================
    
    def _toggle_theme(self):
        """Toggle theme."""
        self.main_window._toggle_theme()
    
    def _show_debug_window(self):
        """Hiển thị debug window."""
        self.main_window._show_debug_window()
    
    def _copy_phone(self, event):
        """Copy phone number to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(config.CONTACT_INFO['phone'])
            # Temporary feedback
            original_text = self.copyright_label.cget("text")
            self.copyright_label.configure(text="Đã copy số!", text_color="#00aa00")
            self.main_window.root.after(2000, lambda: self.copyright_label.configure(
                text=original_text, text_color="#FF6B6B"))
            print(f"📞 Copied phone number to clipboard: {config.CONTACT_INFO['phone']}")
        except ImportError:
            print(f"📞 Phone: {config.CONTACT_INFO['phone']}")

