"""Modern CustomTkinter GUI for AutoCensorVideo."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Callable

import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk

from autocensor.config import Config, load_config, save_config, list_profiles, load_profile, save_profile
from autocensor.constants import (
    SUPPORTED_VIDEO,
    OVERLAY_TYPE_BLUR,
    OVERLAY_TYPE_PIXELATE,
    OVERLAY_TYPE_EMOJI,
    OVERLAY_TYPE_BOX,
    OVERLAY_TYPE_IMAGE,
    DEFAULT_BLUR_STRENGTH,
    DEFAULT_PIXELATE_STRENGTH,
    DEFAULT_PADDING,
    DEFAULT_OPACITY,
    DEFAULT_SCALE,
)

logger = logging.getLogger(__name__)


class VideoPreviewFrame(ctk.CTkFrame):
    """Video preview frame with playback controls."""

    def __init__(self, master: Any, on_box_added: Callable[[tuple[int, int, int, int], str], None], **kwargs):
        super().__init__(master, **kwargs)
        self.video_path: Path | None = None
        self.cap: cv2.VideoCapture | None = None
        self.current_frame: int = 0
        self.total_frames: int = 0
        self.fps: float = 30.0
        self.is_playing: bool = False
        self.frame_task: threading.Thread | None = None
        self.on_box_added = on_box_added

        # Manual editing mode
        self.edit_mode: bool = False
        self.editing_box_type: str = "face"  # "face" or "private"
        self.drawing: bool = False
        self.start_x: int = 0
        self.start_y: int = 0
        self.manual_boxes: dict[int, list[tuple[tuple[int, int, int, int], str]]] = {}  # frame -> [(box, type), ...]
        self.current_display_frame: np.ndarray | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the video preview UI."""
        # Video display
        self.video_label = ctk.CTkLabel(
            self,
            text="No video loaded",
            font=("Arial", 16),
            fg_color=("gray10", "gray10")
        )
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # Playback controls
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=5)

        # Play/Pause button
        self.play_button = ctk.CTkButton(
            controls_frame,
            text="▶",
            width=50,
            command=self.toggle_playback
        )
        self.play_button.pack(side="left", padx=5)

        # Frame slider
        self.frame_slider = ctk.CTkSlider(
            controls_frame,
            from_=0,
            to=100,
            command=self.on_slider_change
        )
        self.frame_slider.pack(side="left", fill="x", expand=True, padx=5)

        # Frame counter
        self.frame_label = ctk.CTkLabel(
            controls_frame,
            text="0 / 0",
            width=80
        )
        self.frame_label.pack(side="left", padx=5)

        # Manual editing controls
        edit_frame = ctk.CTkFrame(self, fg_color="transparent")
        edit_frame.pack(fill="x", padx=10, pady=5)

        # Edit mode toggle
        self.edit_mode_button = ctk.CTkButton(
            edit_frame,
            text="✏️ Manual Edit",
            width=100,
            command=self.toggle_edit_mode
        )
        self.edit_mode_button.pack(side="left", padx=5)

        # Box type selector
        self.box_type_menu = ctk.CTkOptionMenu(
            edit_frame,
            values=["Face", "Private"],
            command=self.set_box_type,
            width=100
        )
        self.box_type_menu.set("Face")
        self.box_type_menu.pack(side="left", padx=5)
        self.box_type_menu.configure(state="disabled")

        # Clear boxes button
        self.clear_button = ctk.CTkButton(
            edit_frame,
            text="🗑️ Clear",
            width=80,
            command=self.clear_manual_boxes
        )
        self.clear_button.pack(side="left", padx=5)
        self.clear_button.configure(state="disabled")

        # Bind mouse events for drawing
        self.video_label.bind("<Button-1>", self.on_mouse_down)
        self.video_label.bind("<B1-Motion>", self.on_mouse_drag)
        self.video_label.bind("<ButtonRelease-1>", self.on_mouse_up)

    def load_video(self, video_path: Path) -> bool:
        """Load a video file.

        Args:
            video_path: Path to video file.

        Returns:
            True if loaded successfully, False otherwise.
        """
        try:
            if self.cap is not None:
                self.cap.release()

            self.cap = cv2.VideoCapture(str(video_path))
            if not self.cap.isOpened():
                return False

            self.video_path = video_path
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.current_frame = 0

            self.frame_slider.configure(to=self.total_frames - 1)
            self.frame_label.configure(text=f"0 / {self.total_frames}")

            # Load first frame
            self.load_frame(0)
            self.video_label.configure(text="")

            return True

        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            return False

    def load_frame(self, frame_num: int) -> None:
        """Load a specific frame.

        Args:
            frame_num: Frame number to load.
        """
        if self.cap is None:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()

        if ret:
            self.current_frame = frame_num
            self._display_frame(frame)
            self.frame_slider.set(frame_num)
            self.frame_label.configure(text=f"{frame_num} / {self.total_frames}")

    def _display_frame(self, frame: np.ndarray) -> None:
        """Display a frame in the video label.

        Args:
            frame: BGR image frame.
        """
        self.current_display_frame = frame.copy()

        # Draw manual boxes if in edit mode
        if self.edit_mode and self.current_frame in self.manual_boxes:
            for box, box_type in self.manual_boxes[self.current_frame]:
                x1, y1, x2, y2 = box
                color = (0, 255, 0) if box_type == "face" else (255, 0, 0)  # Green for face, Red for private
                cv2.rectangle(self.current_display_frame, (x1, y1), (x2, y2), color, 2)

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(self.current_display_frame, cv2.COLOR_BGR2RGB)

        # Resize to fit label
        label_width = self.video_label.winfo_width()
        label_height = self.video_label.winfo_height()

        if label_width > 1 and label_height > 1:
            frame_rgb = cv2.resize(frame_rgb, (label_width, label_height))

        # Convert to PIL Image
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)

        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo

    def toggle_playback(self) -> None:
        """Toggle video playback."""
        if self.cap is None:
            return

        self.is_playing = not self.is_playing
        self.play_button.configure(text="⏸" if self.is_playing else "▶")

        if self.is_playing:
            self.frame_task = threading.Thread(target=self._playback_loop, daemon=True)
            self.frame_task.start()
        else:
            if self.frame_task:
                self.frame_task = None

    def _playback_loop(self) -> None:
        """Playback loop for video."""
        while self.is_playing and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                self.is_playing = False
                self.play_button.configure(text="▶")
                break

            self.current_frame += 1
            self._display_frame(frame)

            # Update UI from main thread
            self.after(0, lambda: self.frame_slider.set(self.current_frame))
            self.after(0, lambda: self.frame_label.configure(
                text=f"{self.current_frame} / {self.total_frames}"
            ))

            # Control playback speed
            delay = int(1000 / self.fps)
            self.after(delay, lambda: None)

    def on_slider_change(self, value: float) -> None:
        """Handle slider change.

        Args:
            value: Slider value.
        """
        if self.cap is not None and not self.is_playing:
            self.load_frame(int(value))

    def close(self) -> None:
        """Clean up resources."""
        self.is_playing = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def toggle_edit_mode(self) -> None:
        """Toggle manual editing mode."""
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.edit_mode_button.configure(text="✓ Done", fg_color="#FF6B6B")
            self.box_type_menu.configure(state="normal")
            self.clear_button.configure(state="normal")
            self.video_label.configure(cursor="crosshair")
        else:
            self.edit_mode_button.configure(text="✏️ Manual Edit", fg_color=None)
            self.box_type_menu.configure(state="disabled")
            self.clear_button.configure(state="disabled")
            self.video_label.configure(cursor="arrow")

    def set_box_type(self, value: str) -> None:
        """Set the box type for manual editing.

        Args:
            value: Box type ("Face" or "Private").
        """
        self.editing_box_type = value.lower()

    def clear_manual_boxes(self) -> None:
        """Clear all manual boxes for the current frame."""
        if self.current_frame in self.manual_boxes:
            del self.manual_boxes[self.current_frame]
            # Redisplay current frame
            if self.cap is not None:
                self.load_frame(self.current_frame)

    def on_mouse_down(self, event) -> None:
        """Handle mouse down event for drawing boxes.

        Args:
            event: Mouse event.
        """
        if not self.edit_mode or self.cap is None:
            return

        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event) -> None:
        """Handle mouse drag event for drawing boxes.

        Args:
            event: Mouse event.
        """
        if not self.drawing or not self.edit_mode or self.current_display_frame is None:
            return

        # Show preview of box being drawn
        frame = self.current_display_frame.copy()
        label_width = self.video_label.winfo_width()
        label_height = self.video_label.winfo_height()

        # Calculate scale factors
        if label_width > 1 and label_height > 1:
            frame_height, frame_width = frame.shape[:2]
            scale_x = frame_width / label_width
            scale_y = frame_height / label_height

            x1 = int(self.start_x * scale_x)
            y1 = int(self.start_y * scale_y)
            x2 = int(event.x * scale_x)
            y2 = int(event.y * scale_y)

            color = (0, 255, 0) if self.editing_box_type == "face" else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (label_width, label_height))
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            self.video_label.configure(image=photo)
            self.video_label.image = photo

    def on_mouse_up(self, event) -> None:
        """Handle mouse up event to complete box drawing.

        Args:
            event: Mouse event.
        """
        if not self.drawing or not self.edit_mode or self.cap is None:
            return

        self.drawing = False

        # Calculate actual coordinates
        label_width = self.video_label.winfo_width()
        label_height = self.video_label.winfo_height()

        if label_width > 1 and label_height > 1:
            frame_height, frame_width = self.current_display_frame.shape[:2]
            scale_x = frame_width / label_width
            scale_y = frame_height / label_height

            x1 = int(self.start_x * scale_x)
            y1 = int(self.start_y * scale_y)
            x2 = int(event.x * scale_x)
            y2 = int(event.y * scale_y)

            # Ensure box is valid
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            # Only add if box has size
            if x2 - x1 > 5 and y2 - y1 > 5:
                box = (x1, y1, x2, y2)

                # Add to manual boxes
                if self.current_frame not in self.manual_boxes:
                    self.manual_boxes[self.current_frame] = []
                self.manual_boxes[self.current_frame].append((box, self.editing_box_type))

                # Notify callback
                if self.on_box_added:
                    self.on_box_added(box, self.editing_box_type)

                # Redisplay with new box
                self.load_frame(self.current_frame)

    def get_manual_boxes(self, frame_num: int) -> list[tuple[tuple[int, int, int, int], str]]:
        """Get manual boxes for a specific frame.

        Args:
            frame_num: Frame number.

        Returns:
            List of (box, type) tuples.
        """
        return self.manual_boxes.get(frame_num, [])


class DetectionStatsFrame(ctk.CTkFrame):
    """Frame displaying detection statistics."""

    def __init__(self, master: Any, on_process: Callable[[], None], **kwargs):
        super().__init__(master, **kwargs)
        self.on_process = on_process
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the detection statistics UI."""
        title = ctk.CTkLabel(
            self,
            text="Detection Statistics",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        # Stats labels
        self.faces_label = ctk.CTkLabel(
            self,
            text="Faces: 0",
            font=("Arial", 12)
        )
        self.faces_label.pack(pady=5)

        self.private_label = ctk.CTkLabel(
            self,
            text="Private Regions: 0",
            font=("Arial", 12)
        )
        self.private_label.pack(pady=5)

        self.confidence_label = ctk.CTkLabel(
            self,
            text="Avg Confidence: 0%",
            font=("Arial", 12)
        )
        self.confidence_label.pack(pady=5)

        # Progress bar
        self.progress_label = ctk.CTkLabel(
            self,
            text="Processing Progress",
            font=("Arial", 12)
        )
        self.progress_label.pack(pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Arial", 11)
        )
        self.status_label.pack(pady=5)

        # Process button
        self.process_button = ctk.CTkButton(
            self,
            text="▶ Start Processing",
            command=self.on_process,
            fg_color="#2CC985",
            hover_color="#239A6F"
        )
        self.process_button.pack(pady=10)

    def update_stats(self, faces: int, private: int, confidence: float) -> None:
        """Update detection statistics.

        Args:
            faces: Number of faces detected.
            private: Number of private regions detected.
            confidence: Average confidence score.
        """
        self.faces_label.configure(text=f"Faces: {faces}")
        self.private_label.configure(text=f"Private Regions: {private}")
        self.confidence_label.configure(text=f"Avg Confidence: {confidence:.1%}")

    def update_progress(self, current: int, total: int, status: str) -> None:
        """Update progress bar.

        Args:
            current: Current frame count.
            total: Total frame count.
            status: Status message.
        """
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)
        self.status_label.configure(text=status)

    def set_processing(self, is_processing: bool) -> None:
        """Set processing state.

        Args:
            is_processing: Whether processing is active.
        """
        if is_processing:
            self.process_button.configure(state="disabled", text="Processing...")
        else:
            self.process_button.configure(state="normal", text="▶ Start Processing")


class ConfigEditorFrame(ctk.CTkFrame):
    """Configuration editor frame."""

    def __init__(self, master: Any, config: Config, on_save: Callable[[Config], None], **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.on_save = on_save
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the configuration editor UI."""
        title = ctk.CTkLabel(
            self,
            text="Configuration",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        # Scrollable frame for options
        scroll_frame = ctk.CTkScrollableFrame(self, label_text="Overlay Settings")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Face overlay settings
        self._add_overlay_section(scroll_frame, "Face", self.config["overlay"]["face"])
        self._add_overlay_section(scroll_frame, "Private", self.config["overlay"]["private"])

        # Save button
        save_button = ctk.CTkButton(
            self,
            text="Save Configuration",
            command=self.save_config
        )
        save_button.pack(pady=10)

    def _add_overlay_section(self, parent: Any, region: str, settings: dict[str, Any]) -> None:
        """Add overlay settings section.

        Args:
            parent: Parent widget.
            region: Region name (Face or Private).
            settings: Overlay settings dictionary.
        """
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=5)

        label = ctk.CTkLabel(
            section_frame,
            text=f"{region} Overlay",
            font=("Arial", 12, "bold")
        )
        label.pack(pady=5)

        # Overlay type
        type_label = ctk.CTkLabel(section_frame, text="Type:")
        type_label.pack(anchor="w", padx=5)

        type_menu = ctk.CTkOptionMenu(
            section_frame,
            values=[OVERLAY_TYPE_BLUR, OVERLAY_TYPE_PIXELATE, OVERLAY_TYPE_EMOJI,
                   OVERLAY_TYPE_BOX, OVERLAY_TYPE_IMAGE],
            command=lambda v: self._update_setting(region, "type", v)
        )
        type_menu.set(settings.get("type", OVERLAY_TYPE_BLUR))
        type_menu.pack(fill="x", padx=5, pady=2)

        # Strength
        strength_label = ctk.CTkLabel(section_frame, text="Strength:")
        strength_label.pack(anchor="w", padx=5)

        strength_slider = ctk.CTkSlider(
            section_frame,
            from_=3,
            to=100,
            number_of_steps=97,
            command=lambda v: self._update_setting(region, "strength", int(v))
        )
        strength_slider.set(settings.get("strength", DEFAULT_BLUR_STRENGTH))
        strength_slider.pack(fill="x", padx=5, pady=2)

        # Padding
        padding_label = ctk.CTkLabel(section_frame, text="Padding:")
        padding_label.pack(anchor="w", padx=5)

        padding_slider = ctk.CTkSlider(
            section_frame,
            from_=0,
            to=1,
            number_of_steps=100,
            command=lambda v: self._update_setting(region, "padding", round(v, 2))
        )
        padding_slider.set(settings.get("padding", DEFAULT_PADDING))
        padding_slider.pack(fill="x", padx=5, pady=2)

        # Opacity
        opacity_label = ctk.CTkLabel(section_frame, text="Opacity:")
        opacity_label.pack(anchor="w", padx=5)

        opacity_slider = ctk.CTkSlider(
            section_frame,
            from_=0,
            to=1,
            number_of_steps=100,
            command=lambda v: self._update_setting(region, "opacity", round(v, 2))
        )
        opacity_slider.set(settings.get("opacity", DEFAULT_OPACITY))
        opacity_slider.pack(fill="x", padx=5, pady=2)

    def _update_setting(self, region: str, key: str, value: Any) -> None:
        """Update a configuration setting.

        Args:
            region: Region name (Face or Private).
            key: Setting key.
            value: New value.
        """
        self.config["overlay"][region][key] = value

    def save_config(self) -> None:
        """Save the configuration."""
        save_config(self.config)
        self.on_save(self.config)


class SidebarFrame(ctk.CTkFrame):
    """Sidebar with file browser and profiles."""

    def __init__(self, master: Any, on_file_select: Callable[[Path], None],
                 on_profile_load: Callable[[str], None], on_export_boxes: Callable[[], None],
                 on_load_boxes: Callable[[], None], **kwargs):
        super().__init__(master, **kwargs)
        self.on_file_select = on_file_select
        self.on_profile_load = on_profile_load
        self.on_export_boxes = on_export_boxes
        self.on_load_boxes = on_load_boxes
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the sidebar UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="AutoCensorVideo",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)

        # File selection
        file_button = ctk.CTkButton(
            self,
            text="📁 Select Video",
            command=self.select_file
        )
        file_button.pack(fill="x", padx=10, pady=5)

        batch_button = ctk.CTkButton(
            self,
            text="📂 Batch Process",
            command=self.select_batch
        )
        batch_button.pack(fill="x", padx=10, pady=5)

        # Separator
        separator = ctk.CTkFrame(self, height=2, fg_color="gray30")
        separator.pack(fill="x", padx=10, pady=15)

        # Profiles
        profiles_label = ctk.CTkLabel(
            self,
            text="Profiles",
            font=("Arial", 12, "bold")
        )
        profiles_label.pack(pady=5)

        self.profile_menu = ctk.CTkOptionMenu(
            self,
            values=list_profiles(),
            command=self.on_profile_load
        )
        self.profile_menu.pack(fill="x", padx=10, pady=5)

        save_profile_button = ctk.CTkButton(
            self,
            text="💾 Save Profile",
            command=self.save_profile
        )
        save_profile_button.pack(fill="x", padx=10, pady=5)

        # Separator
        separator2 = ctk.CTkFrame(self, height=2, fg_color="gray30")
        separator2.pack(fill="x", padx=10, pady=15)

        # Settings
        settings_button = ctk.CTkButton(
            self,
            text="⚙️ Settings",
            command=self.open_settings
        )
        settings_button.pack(fill="x", padx=10, pady=5)

        # Manual boxes
        export_button = ctk.CTkButton(
            self,
            text="📤 Export Boxes",
            command=self.on_export_boxes
        )
        export_button.pack(fill="x", padx=10, pady=5)

        load_button = ctk.CTkButton(
            self,
            text="📥 Load Boxes",
            command=self.on_load_boxes
        )
        load_button.pack(fill="x", padx=10, pady=5)

    def select_file(self) -> None:
        """Select a single video file."""
        from tkinter import filedialog

        root = ctk.CTk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Select Video",
            filetypes=[("Video files", SUPPORTED_VIDEO), ("All files", "*.*")]
        )

        root.destroy()

        if file_path:
            self.on_file_select(Path(file_path))

    def select_batch(self) -> None:
        """Select multiple video files for batch processing."""
        from tkinter import filedialog

        root = ctk.CTk()
        root.withdraw()

        file_paths = filedialog.askopenfilenames(
            title="Select Videos",
            filetypes=[("Video files", SUPPORTED_VIDEO), ("All files", "*.*")]
        )

        root.destroy()

        if file_paths:
            for file_path in file_paths:
                self.on_file_select(Path(file_path))

    def save_profile(self) -> None:
        """Save current configuration as a profile."""
        # This would need a dialog to enter profile name
        # For now, just log it
        logger.info("Save profile clicked")

    def open_settings(self) -> None:
        """Open settings dialog."""
        logger.info("Settings clicked")

    def export_manual_boxes(self) -> None:
        """Export manual boxes to JSON."""
        import json
        from tkinter import filedialog

        if not self.manual_boxes:
            logger.warning("No manual boxes to export")
            return

        root = ctk.CTk()
        root.withdraw()

        file_path = filedialog.asksaveasfilename(
            title="Export Manual Boxes",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        root.destroy()

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.manual_boxes, f, indent=2)
            logger.info(f"Manual boxes exported to: {file_path}")

    def load_manual_boxes(self) -> None:
        """Load manual boxes from JSON."""
        import json
        from tkinter import filedialog

        root = ctk.CTk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Load Manual Boxes",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        root.destroy()

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.manual_boxes = json.load(f)
                self.video_preview.manual_boxes = self.manual_boxes
                logger.info(f"Manual boxes loaded from: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load manual boxes: {e}")


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.config = load_config()
        self.video_path: Path | None = None
        self.is_processing: bool = False
        self.total_faces_detected: int = 0
        self.total_private_detected: int = 0
        self.manual_boxes: dict[int, list[tuple[tuple[int, int, int, int], str]]] = {}

        self._setup_window()
        self._setup_layout()

    def on_file_select(self, file_path: Path) -> None:
        """Handle file selection.

        Args:
            file_path: Path to selected file.
        """
        self.video_path = file_path
        self.video_preview.load_video(file_path)
        logger.info(f"Selected video: {file_path}")

    def on_profile_load(self, profile_name: str) -> None:
        """Handle profile loading.

        Args:
            profile_name: Name of profile to load.
        """
        profile = load_profile(profile_name)
        if profile:
            self.config = profile
            # Refresh config editor
            self.config_editor.config = profile
            logger.info(f"Loaded profile: {profile_name}")

    def on_config_save(self, config: Config) -> None:
        """Handle configuration save.

        Args:
            config: Configuration to save.
        """
        self.config = config
        logger.info("Configuration saved")

    def on_manual_box_added(self, box: tuple[int, int, int, int], box_type: str) -> None:
        """Handle manual box addition.

        Args:
            box: Bounding box coordinates (x1, y1, x2, y2).
            box_type: Type of box ("face" or "private").
        """
        logger.info(f"Manual box added: {box} ({box_type})")

    def export_manual_boxes(self) -> None:
        """Export manual boxes to JSON."""
        import json
        from tkinter import filedialog

        if not self.manual_boxes:
            logger.warning("No manual boxes to export")
            return

        root = ctk.CTk()
        root.withdraw()

        file_path = filedialog.asksaveasfilename(
            title="Export Manual Boxes",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        root.destroy()

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.manual_boxes, f, indent=2)
            logger.info(f"Manual boxes exported to: {file_path}")

    def load_manual_boxes(self) -> None:
        """Load manual boxes from JSON."""
        import json
        from tkinter import filedialog

        root = ctk.CTk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Load Manual Boxes",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        root.destroy()

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.manual_boxes = json.load(f)
                self.video_preview.manual_boxes = self.manual_boxes
                logger.info(f"Manual boxes loaded from: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load manual boxes: {e}")

    def _setup_window(self) -> None:
        """Setup the main window."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("AutoCensorVideo v2.0")
        self.geometry("1400x900")

        # Set window icon if available
        # self.iconbitmap("icon.ico")

    def _setup_layout(self) -> None:
        """Setup the main layout."""
        # Create grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = SidebarFrame(
            self,
            width=200,
            corner_radius=0,
            on_file_select=self.on_file_select,
            on_profile_load=self.on_profile_load,
            on_export_boxes=self.export_manual_boxes,
            on_load_boxes=self.load_manual_boxes
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Main content area
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=3)
        self.main_content.grid_columnconfigure(1, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

        # Video preview
        self.video_preview = VideoPreviewFrame(
            self.main_content,
            on_box_added=self.on_manual_box_added
        )
        self.video_preview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Right panel (stats + config)
        self.right_panel = ctk.CTkFrame(self.main_content)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)

        # Detection stats
        self.detection_stats = DetectionStatsFrame(
            self.right_panel,
            on_process=self.start_processing
        )
        self.detection_stats.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Config editor
        self.config_editor = ConfigEditorFrame(
            self.right_panel,
            self.config,
            self.on_config_save
        )
        self.config_editor.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def on_file_select(self, file_path: Path) -> None:
        """Handle file selection.

        Args:
            file_path: Path to selected file.
        """
        self.video_path = file_path
        self.video_preview.load_video(file_path)
        logger.info(f"Selected video: {file_path}")

    def on_profile_load(self, profile_name: str) -> None:
        """Handle profile loading.

        Args:
            profile_name: Name of profile to load.
        """
        profile = load_profile(profile_name)
        if profile:
            self.config = profile
            # Refresh config editor
            self.config_editor.config = profile
            logger.info(f"Loaded profile: {profile_name}")

    def on_config_save(self, config: Config) -> None:
        """Handle configuration save.

        Args:
            config: Configuration to save.
        """
        self.config = config
        logger.info("Configuration saved")

    def on_manual_box_added(self, box: tuple[int, int, int, int], box_type: str) -> None:
        """Handle manual box addition.

        Args:
            box: Bounding box coordinates (x1, y1, x2, y2).
            box_type: Type of box ("face" or "private").
        """
        logger.info(f"Manual box added: {box} ({box_type})")

    def start_processing(self) -> None:
        """Start video processing in a separate thread."""
        if self.video_path is None:
            logger.warning("No video selected")
            return

        if self.is_processing:
            return

        self.is_processing = True
        self.detection_stats.set_processing(True)

        # Run processing in a separate thread
        processing_thread = threading.Thread(target=self._process_video, daemon=True)
        processing_thread.start()

    def _process_video(self) -> None:
        """Process the video (runs in separate thread)."""
        try:
            from autocensor.detectors import FaceDetector, PrivateDetector
            from autocensor.video_processor import VideoProcessor

            # Initialize detectors
            face_detector = FaceDetector(self.config)
            private_detector = PrivateDetector(self.config)

            # Initialize video processor
            processor = VideoProcessor(self.config)

            # Reset counters
            self.total_faces_detected = 0
            self.total_private_detected = 0

            # Define progress callback
            def progress_callback(current: int, total: int, faces: int, private: int) -> None:
                """Update UI during processing."""
                self.total_faces_detected += faces
                self.total_private_detected += private

                self.after(0, lambda: self.detection_stats.update_progress(
                    current, total, f"Processing frame {current} / {total}"
                ))
                self.after(0, lambda: self.detection_stats.update_stats(
                    self.total_faces_detected,
                    self.total_private_detected,
                    0.85
                ))

            # Process video with progress callback
            output = processor.process_video(
                self.video_path,
                face_detector,
                private_detector,
                preview_mode=False,
                export_detections=False,
                progress_callback=progress_callback
            )

            # Get stats
            stats = processor.get_stats()

            # Update UI from main thread
            self.after(0, lambda: self.detection_stats.update_stats(
                stats["faces_detected"],
                stats["private_regions_detected"],
                0.85  # Placeholder confidence
            ))

            self.after(0, lambda: self.detection_stats.update_progress(
                stats["total_frames"],
                stats["total_frames"],
                "Complete!"
            ))

            logger.info(f"Processing complete: {output}")

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.after(0, lambda: self.detection_stats.update_progress(
                0, 0, f"Error: {e}"
            ))

        finally:
            self.is_processing = False
            self.after(0, lambda: self.detection_stats.set_processing(False))

    def run(self) -> None:
        """Run the application."""
        self.mainloop()


def launch_gui() -> None:
    """Launch the GUI application."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    launch_gui()
