import os
import json
from pathlib import Path


class TimerPresets:
    """Manages preset/standard timers configuration."""

    DEFAULT_PRESETS = [
        {"title": "Quick Break", "hours": 0, "minutes": 5, "seconds": 0},
        {"title": "Coffee Break", "hours": 0, "minutes": 10, "seconds": 0},
        {"title": "Pomodoro", "hours": 0, "minutes": 25, "seconds": 0},
        {"title": "Short Meeting", "hours": 0, "minutes": 30, "seconds": 0},
        {"title": "Long Meeting", "hours": 1, "minutes": 0, "seconds": 0},
    ]

    def __init__(self):
        """Initialize the timer presets manager."""
        self.config_file = self._get_config_file_path()
        self.presets = self._load_presets()

    def _get_config_file_path(self):
        """Get the path to the presets configuration file.

        Returns:
            Path object for the config file
        """
        config_dir = Path.home() / '.config' / 'multi-timer-app'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'timer_presets.json'

    def _load_presets(self):
        """Load timer presets from configuration file.

        Returns:
            List of preset timer dictionaries
        """
        if not self.config_file.exists():
            # Create default presets file
            self._save_presets(self.DEFAULT_PRESETS)
            return self.DEFAULT_PRESETS.copy()

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return data.get('presets', self.DEFAULT_PRESETS.copy())
        except Exception as e:
            print(f"Warning: Could not load timer presets: {e}")
            return self.DEFAULT_PRESETS.copy()

    def _save_presets(self, presets=None):
        """Save timer presets to configuration file.

        Args:
            presets: List of preset dictionaries (uses self.presets if None)
        """
        if presets is None:
            presets = self.presets

        try:
            with open(self.config_file, 'w') as f:
                json.dump({'presets': presets}, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save timer presets: {e}")

    def get_presets(self):
        """Get all timer presets.

        Returns:
            List of preset timer dictionaries
        """
        return self.presets.copy()

    def add_preset(self, title, hours, minutes, seconds):
        """Add a new preset timer.

        Args:
            title: Timer title
            hours: Hours component
            minutes: Minutes component
            seconds: Seconds component
        """
        preset = {
            "title": title,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }

        # Check if preset with same title exists
        for i, p in enumerate(self.presets):
            if p['title'] == title:
                # Update existing preset
                self.presets[i] = preset
                self._save_presets()
                return

        # Add new preset
        self.presets.append(preset)
        self._save_presets()

    def remove_preset(self, title):
        """Remove a preset timer by title.

        Args:
            title: Title of the preset to remove

        Returns:
            True if removed, False if not found
        """
        for i, preset in enumerate(self.presets):
            if preset['title'] == title:
                self.presets.pop(i)
                self._save_presets()
                return True
        return False

    def get_quick_timers(self):
        """Get standard quick timer durations (1-12 minutes).

        Returns:
            List of timer dictionaries for quick durations
        """
        durations = [1, 2, 3, 4, 5, 7, 10, 12]
        quick_timers = []

        for minutes in durations:
            quick_timers.append({
                "title": f"{minutes} Minute Timer",
                "hours": 0,
                "minutes": minutes,
                "seconds": 0
            })

        return quick_timers

    def reset_to_defaults(self):
        """Reset presets to default values."""
        self.presets = self.DEFAULT_PRESETS.copy()
        self._save_presets()
