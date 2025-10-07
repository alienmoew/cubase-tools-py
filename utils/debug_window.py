"""
Debug Window - Cửa sổ debug log riêng biệt cho Cubase Auto Tool.
"""
import customtkinter as CTK
import threading
import time
from datetime import datetime


class DebugWindow:
    """Cửa sổ debug log riêng biệt."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.text_widget = None
        self.log_buffer = []  # Buffer để lưu trữ logs
        self.max_lines = 1000  # Giới hạn số dòng log
        self.is_auto_scroll = True  # Auto scroll to bottom
        self._lock = threading.Lock()
    
    def create_window(self):
        """Tạo cửa sổ debug."""
        if self.window is None or not self.window.winfo_exists():
            self.window = CTK.CTkToplevel()
            self.window.title("Debug Console - Cubase Auto Tool")
            self.window.geometry("800x600")
            self.window.resizable(True, True)
            
            # Icon và style
            try:
                self.window.after(201, lambda: self.window.iconbitmap(''))
            except:
                pass
            
            # Main container
            main_frame = CTK.CTkFrame(self.window, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title
            title_label = CTK.CTkLabel(
                main_frame,
                text="🐛 Debug Console",
                font=("Arial", 16, "bold"),
                text_color="#FF9800"
            )
            title_label.pack(pady=(0, 10))
            
            # Controls frame
            controls_frame = CTK.CTkFrame(main_frame, fg_color="transparent")
            controls_frame.pack(fill="x", pady=(0, 10))
            
            # Clear button
            clear_btn = CTK.CTkButton(
                controls_frame,
                text="Clear Logs",
                command=self._clear_logs,
                width=100,
                height=30,
                fg_color="#E91E63",
                hover_color="#C2185B"
            )
            clear_btn.pack(side="left", padx=(0, 10))
            
            # Auto-scroll toggle
            self.auto_scroll_switch = CTK.CTkSwitch(
                controls_frame,
                text="Auto Scroll",
                command=self._toggle_auto_scroll,
                width=40,
                height=20
            )
            self.auto_scroll_switch.select()  # Default: ON
            self.auto_scroll_switch.pack(side="left", padx=(0, 10))
            
            # Export button
            export_btn = CTK.CTkButton(
                controls_frame,
                text="Export Logs",
                command=self._export_logs,
                width=100,
                height=30,
                fg_color="#4CAF50",
                hover_color="#45A049"
            )
            export_btn.pack(side="left")
            
            # Stats label
            self.stats_label = CTK.CTkLabel(
                controls_frame,
                text="Lines: 0",
                font=("Arial", 10),
                text_color="#888888"
            )
            self.stats_label.pack(side="right")
            
            # Text display frame with scrollbar
            text_frame = CTK.CTkFrame(main_frame, fg_color="#1E1E1E", corner_radius=8)
            text_frame.pack(fill="both", expand=True)
            
            # Create text widget with scrollbar
            self.text_widget = CTK.CTkTextbox(
                text_frame,
                font=("Consolas", 10),
                fg_color="#1E1E1E",
                text_color="#FFFFFF",
                corner_radius=0,
                wrap="word"
            )
            self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Load existing logs
            self._load_existing_logs()
            
            # Protocol để cleanup khi đóng
            self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            print("🐛 Debug window created successfully")
        else:
            # Nếu window đã tồn tại, đưa lên foreground
            self.window.lift()
            self.window.focus()
    
    def show(self):
        """Hiển thị cửa sổ debug."""
        self.create_window()
        if self.window:
            self.window.deiconify()  # Show if minimized
            self.window.lift()
            self.window.focus()
    
    def add_log(self, message, level="INFO"):
        """Thêm log message với thread-safe."""
        with self._lock:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Color coding based on level
            color = {
                "INFO": "#FFFFFF",
                "SUCCESS": "#4CAF50", 
                "WARNING": "#FF9800",
                "ERROR": "#F44336",
                "DEBUG": "#2196F3"
            }.get(level, "#FFFFFF")
            
            # Format message
            formatted_msg = f"[{timestamp}] [{level}] {message}\n"
            
            # Add to buffer
            self.log_buffer.append({
                'text': formatted_msg,
                'color': color,
                'timestamp': time.time()
            })
            
            # Limit buffer size
            if len(self.log_buffer) > self.max_lines:
                self.log_buffer.pop(0)
            
            # Update UI if window exists
            if self.text_widget:
                self._update_display()
    
    def _update_display(self):
        """Cập nhật hiển thị trong text widget."""
        if not self.text_widget:
            return
            
        try:
            # Clear and rebuild display
            self.text_widget.delete("1.0", "end")
            
            for log_entry in self.log_buffer:
                # Insert text (note: CTkTextbox doesn't support text coloring like tkinter Text)
                self.text_widget.insert("end", log_entry['text'])
            
            # Auto scroll to bottom if enabled
            if self.is_auto_scroll:
                self.text_widget.see("end")
            
            # Update stats
            self._update_stats()
            
        except Exception as e:
            print(f"Error updating debug display: {e}")
    
    def _load_existing_logs(self):
        """Load existing logs từ print statements."""
        # Thêm một số log mẫu để demo
        sample_logs = [
            ("🚀 Cubase Auto Tool started", "INFO"),
            ("✅ GUI initialized successfully", "SUCCESS"),
            ("🔧 Loading default values...", "INFO"),
            ("⚙️ Settings loaded", "INFO"),
            ("🎨 Theme applied: dark", "INFO")
        ]
        
        for msg, level in sample_logs:
            self.add_log(msg, level)
    
    def _clear_logs(self):
        """Xóa tất cả logs."""
        with self._lock:
            self.log_buffer.clear()
            if self.text_widget:
                self.text_widget.delete("1.0", "end")
                self._update_stats()
        print("🧹 Debug logs cleared")
    
    def _toggle_auto_scroll(self):
        """Toggle auto scroll."""
        self.is_auto_scroll = self.auto_scroll_switch.get()
        print(f"📜 Auto scroll: {'ON' if self.is_auto_scroll else 'OFF'}")
    
    def _export_logs(self):
        """Export logs to file."""
        try:
            filename = f"debug_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Cubase Auto Tool Debug Logs\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                for log_entry in self.log_buffer:
                    f.write(log_entry['text'])
            
            print(f"📄 Logs exported to: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting logs: {e}")
    
    def _update_stats(self):
        """Cập nhật statistics."""
        if self.stats_label:
            line_count = len(self.log_buffer)
            self.stats_label.configure(text=f"Lines: {line_count}")
    
    def _on_window_close(self):
        """Xử lý khi đóng cửa sổ."""
        if self.window:
            self.window.withdraw()  # Hide instead of destroy
            print("🐛 Debug window hidden")

