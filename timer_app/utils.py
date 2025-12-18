import os
import sys


def format_time(seconds):
    """Convert seconds to HH:MM:SS format.

    Args:
        seconds: Integer number of seconds

    Returns:
        String in format "HH:MM:SS"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_time(hours, minutes, seconds):
    """Convert hours, minutes, seconds to total seconds.

    Args:
        hours: Integer hours (0-23)
        minutes: Integer minutes (0-59)
        seconds: Integer seconds (0-59)

    Returns:
        Total seconds as integer
    """
    return hours * 3600 + minutes * 60 + seconds


def validate_timer_input(title, hours, minutes, seconds):
    """Validate timer input parameters.

    Args:
        title: Timer title string
        hours: Integer hours
        minutes: Integer minutes
        seconds: Integer seconds

    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not title or not title.strip():
        return False, "Timer title cannot be empty"

    if len(title) > 50:
        return False, "Title too long (max 50 characters)"

    total_seconds = parse_time(hours, minutes, seconds)
    if total_seconds < 1:
        return False, "Duration must be at least 1 second"

    return True, None


def get_resource_path(filename):
    """Get absolute path to a resource file.

    Args:
        filename: Relative path from resources directory (e.g., "icons/timer.png")

    Returns:
        Absolute path to the resource file
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, "resources", filename)
