import os
import json
from pathlib import Path


class TimerHistory:
    """Manages history of timer titles for autocomplete."""

    def __init__(self):
        """Initialize the timer history manager."""
        self.history_file = self._get_history_file_path()
        self.titles = []
        self.title_durations = {}
        self._load_history()

    def _get_history_file_path(self):
        """Get the path to the history file.

        Returns:
            Path object for the history file
        """
        config_dir = Path.home() / '.config' / 'multi-timer-app'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'timer_history.json'

    def _load_history(self):
        """Load timer title history from file.

        Loads both titles list and title_durations dict (backward compatible).
        """
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                self.titles = data.get('titles', [])
                self.title_durations = data.get('title_durations', {})
        except Exception as e:
            print(f"Warning: Could not load timer history: {e}")

    def _save_history(self):
        """Save timer title history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump({
                    'titles': self.titles,
                    'title_durations': self.title_durations
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save timer history: {e}")

    def add_title(self, title, hours=None, minutes=None, seconds=None):
        """Add a timer title to history with optional duration.

        Args:
            title: Timer title to add
            hours: Hours component of duration (optional)
            minutes: Minutes component of duration (optional)
            seconds: Seconds component of duration (optional)
        """
        if not title or not title.strip():
            return

        title = title.strip()

        # Remove title if it already exists (we'll add it to the front)
        if title in self.titles:
            self.titles.remove(title)

        # Add to the beginning (most recent first)
        self.titles.insert(0, title)

        # Keep only the most recent 50 titles
        self.titles = self.titles[:50]

        # Store duration if provided
        if hours is not None or minutes is not None or seconds is not None:
            self.title_durations[title] = {
                'hours': hours or 0,
                'minutes': minutes or 0,
                'seconds': seconds or 0
            }

        self._save_history()

    def get_titles(self):
        """Get all timer titles in history.

        Returns:
            List of timer titles
        """
        return self.titles.copy()

    def get_duration_for_title(self, title):
        """Get the last-used duration for a title.

        Args:
            title: Timer title to look up

        Returns:
            Dict with keys 'hours', 'minutes', 'seconds' or None if not found
        """
        if not title:
            return None
        return self.title_durations.get(title.strip())

    def clear_history(self):
        """Clear all timer title history."""
        self.titles = []
        self.title_durations = {}
        self._save_history()
