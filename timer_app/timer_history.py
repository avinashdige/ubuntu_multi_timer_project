import os
import json
from pathlib import Path


class TimerHistory:
    """Manages history of timer titles for autocomplete."""

    def __init__(self):
        """Initialize the timer history manager."""
        self.history_file = self._get_history_file_path()
        self.titles = self._load_history()

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

        Returns:
            List of timer titles
        """
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return data.get('titles', [])
        except Exception as e:
            print(f"Warning: Could not load timer history: {e}")
            return []

    def _save_history(self):
        """Save timer title history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump({'titles': self.titles}, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save timer history: {e}")

    def add_title(self, title):
        """Add a timer title to history.

        Args:
            title: Timer title to add
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

        self._save_history()

    def get_titles(self):
        """Get all timer titles in history.

        Returns:
            List of timer titles
        """
        return self.titles.copy()

    def clear_history(self):
        """Clear all timer title history."""
        self.titles = []
        self._save_history()
