#!/usr/bin/env python3
"""
Quick test to verify all components are working before running the GUI.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing Multi-Timer Application Setup...")
print("=" * 50)

# Test 1: GTK imports
print("\n1. Testing GTK imports...")
try:
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('AppIndicator3', '0.1')
    gi.require_version('Notify', '0.7')
    from gi.repository import Gtk, AppIndicator3, Notify
    print("   ✓ GTK 3, AppIndicator3, and Notify imported successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Additional dependencies
print("\n2. Testing additional dependencies...")
try:
    import notify2
    print("   ✓ notify2 imported successfully")
except Exception as e:
    print(f"   ✗ Error importing notify2: {e}")

try:
    from playsound import playsound
    print("   ✓ playsound imported successfully")
except Exception as e:
    print(f"   ✗ Warning: playsound import failed: {e}")
    print("     (Sound alerts will fall back to system beep)")

# Test 3: Application modules
print("\n3. Testing application modules...")
try:
    from timer_app.utils import format_time, validate_timer_input
    from timer_app.timer_model import Timer, TimerManager
    from timer_app.timer_thread import TimerThread
    from timer_app.notifications import NotificationHandler
    from timer_app.app import TimerApp
    print("   ✓ All application modules imported successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 4: Utility functions
print("\n4. Testing utility functions...")
try:
    assert format_time(3661) == "01:01:01", "format_time failed"
    assert format_time(0) == "00:00:00", "format_time failed"
    assert format_time(59) == "00:00:59", "format_time failed"

    is_valid, msg = validate_timer_input("Test", 0, 0, 10)
    assert is_valid, "Valid input rejected"

    is_valid, msg = validate_timer_input("", 0, 0, 10)
    assert not is_valid, "Empty title accepted"

    is_valid, msg = validate_timer_input("Test", 0, 0, 0)
    assert not is_valid, "Zero duration accepted"

    print("   ✓ Utility functions working correctly")
except AssertionError as e:
    print(f"   ✗ Assertion failed: {e}")
    sys.exit(1)

# Test 5: Timer model
print("\n5. Testing timer model...")
try:
    manager = TimerManager()
    # Don't actually start timers in test, just verify creation
    timer = Timer("Test Timer", 60)
    assert timer.title == "Test Timer"
    assert timer.total_seconds == 60
    assert timer.remaining_seconds == 60
    print("   ✓ Timer model working correctly")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("✓ All tests passed! Your application is ready to run.")
print("\nTo start the application:")
print("  ./run.sh")
print("\nOr:")
print("  source venv/bin/activate")
print("  python3 timer_app/main.py")
print("=" * 50)
