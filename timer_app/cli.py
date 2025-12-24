#!/usr/bin/env python3
"""
Command-line interface for the Multi-Timer application.
"""
import sys
import argparse
import dbus


def get_timer_service():
    """Get the DBus service for the timer app.

    Returns:
        DBus proxy object for the timer service

    Raises:
        Exception if the service is not available
    """
    try:
        bus = dbus.SessionBus()
        proxy = bus.get_object(
            'com.github.MultiTimerApp',
            '/com/github/MultiTimerApp'
        )
        return dbus.Interface(proxy, 'com.github.MultiTimerApp')
    except dbus.exceptions.DBusException as e:
        raise Exception(
            "Could not connect to Multi-Timer app. "
            "Make sure the app is running in the system tray."
        ) from e


def parse_duration(duration_str):
    """Parse a duration string into hours, minutes, seconds.

    Supported formats:
    - "5m" - 5 minutes
    - "1h30m" - 1 hour 30 minutes
    - "2h" - 2 hours
    - "90s" - 90 seconds
    - "1h30m45s" - 1 hour 30 minutes 45 seconds

    Args:
        duration_str: Duration string to parse

    Returns:
        Tuple of (hours, minutes, seconds)

    Raises:
        ValueError if the format is invalid
    """
    hours = 0
    minutes = 0
    seconds = 0

    duration_str = duration_str.lower().strip()

    # Parse hours
    if 'h' in duration_str:
        parts = duration_str.split('h')
        try:
            hours = int(parts[0])
            duration_str = parts[1] if len(parts) > 1 else ''
        except ValueError:
            raise ValueError(f"Invalid hours value in duration: {duration_str}")

    # Parse minutes
    if 'm' in duration_str:
        parts = duration_str.split('m')
        try:
            minutes = int(parts[0])
            duration_str = parts[1] if len(parts) > 1 else ''
        except ValueError:
            raise ValueError(f"Invalid minutes value in duration: {duration_str}")

    # Parse seconds
    if 's' in duration_str:
        parts = duration_str.split('s')
        try:
            seconds = int(parts[0])
        except ValueError:
            raise ValueError(f"Invalid seconds value in duration: {duration_str}")
    elif duration_str and duration_str.strip():
        # If there's leftover text, it's invalid
        raise ValueError(f"Invalid duration format: {duration_str}")

    if hours == 0 and minutes == 0 and seconds == 0:
        raise ValueError("Duration must be greater than 0")

    return hours, minutes, seconds


def add_timer(args):
    """Add a timer via CLI.

    Args:
        args: Parsed command-line arguments
    """
    try:
        service = get_timer_service()

        # Parse duration
        hours, minutes, seconds = parse_duration(args.duration)

        # Add timer
        success = service.AddTimer(args.title, hours, minutes, seconds)

        if success:
            print(f"✓ Timer '{args.title}' started for {hours}h {minutes}m {seconds}s")
        else:
            print("✗ Failed to add timer", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_timers(args):
    """List all active timers.

    Args:
        args: Parsed command-line arguments
    """
    try:
        service = get_timer_service()
        timers = service.GetTimers()

        if not timers:
            print("No active timers")
            return

        print(f"Active timers ({len(timers)}):")
        print("-" * 50)
        for timer_id, title, remaining, _ in timers:
            print(f"  {title}: {remaining}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def delete_timer(args):
    """Delete a timer via CLI.

    Args:
        args: Parsed command-line arguments
    """
    try:
        service = get_timer_service()

        # Get all timers to find the one matching the title
        timers = service.GetTimers()

        matching_timer = None
        for timer_id, title, _, _ in timers:
            if title.lower() == args.title.lower():
                matching_timer = timer_id
                break

        if not matching_timer:
            print(f"✗ Timer '{args.title}' not found", file=sys.stderr)
            sys.exit(1)

        success = service.DeleteTimer(matching_timer)

        if success:
            print(f"✓ Timer '{args.title}' deleted")
        else:
            print("✗ Failed to delete timer", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Command-line interface for Multi-Timer app',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a 5 minute timer
  timer-cli add "Coffee" 5m

  # Add a 1 hour 30 minute timer
  timer-cli add "Meeting" 1h30m

  # Add a timer with seconds
  timer-cli add "Quick task" 2m30s

  # List all active timers
  timer-cli list

  # Delete a timer
  timer-cli delete "Coffee"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add timer command
    add_parser = subparsers.add_parser('add', help='Add a new timer')
    add_parser.add_argument('title', help='Timer title/name')
    add_parser.add_argument(
        'duration',
        help='Duration (e.g., 5m, 1h30m, 2h, 90s, 1h30m45s)'
    )
    add_parser.set_defaults(func=add_timer)

    # List timers command
    list_parser = subparsers.add_parser('list', help='List all active timers')
    list_parser.set_defaults(func=list_timers)

    # Delete timer command
    delete_parser = subparsers.add_parser('delete', help='Delete a timer')
    delete_parser.add_argument('title', help='Timer title/name to delete')
    delete_parser.set_defaults(func=delete_timer)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
