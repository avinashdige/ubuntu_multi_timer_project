# Deadlock Fix - Version 1.2

## Problem Description

After implementing the Version 1.2 pinned timer feature, the application would hang (deadlock) when a timer completed. The timer would show 00:00:01, the notification would appear, but then the process would freeze and require killing the PID.

## Root Causes (Two Issues Fixed)

### Issue 1: Calling Callbacks While Holding Lock

The first deadlock was caused by calling `_notify_pin_changed()` while holding the timer manager's lock. Here's what happened:

1. `on_timer_complete()` acquired the lock
2. Called `_notify_pin_changed()` **while still holding the lock**
3. `_notify_pin_changed()` called `GLib.idle_add(callback)`
4. The callback (`on_pin_changed` in `TimerApp`) executed
5. `on_pin_changed` called `update_indicator_label()`
6. `update_indicator_label()` called `get_pinned_timer()`
7. `get_pinned_timer()` tried to acquire the **same lock** → **DEADLOCK**

### Issue 2: Reentrant Lock Attempt (Critical!)

The **actual cause** of the hang at 00:00:01 was a reentrant lock attempt:

1. `on_timer_complete()` acquired the lock
2. Called `_auto_pin_earliest()` **while holding the lock**
3. `_auto_pin_earliest()` called `get_earliest_timer()`
4. `get_earliest_timer()` tried to acquire the **same lock again** → **DEADLOCK!**

Python's `threading.Lock()` is **NOT reentrant** - you cannot acquire it twice from the same thread. This caused the process to freeze permanently.

## The Fix

### Fix 1: Release Lock Before Notifying

Restructured all methods to ensure `_notify_pin_changed()` is called **after** releasing the lock:

### Changed Methods in `timer_model.py`:

1. **`_notify_pin_changed()`**
   - Now acquires its own lock just to copy the callback list
   - Releases lock before calling `GLib.idle_add()`
   - Added clear documentation about avoiding deadlock

2. **`set_pinned_timer()`**
   - Uses flag `should_notify` to track if notification is needed
   - Releases lock before calling `_notify_pin_changed()`

3. **`add_timer()`**
   - Uses flag `should_notify` to track if notification is needed
   - Releases lock before calling `_notify_pin_changed()`

4. **`delete_timer()`**
   - Uses flag `should_notify` to track if notification is needed
   - Releases lock before calling `_notify_pin_changed()`

5. **`on_timer_complete()`**
   - Uses flag `should_notify` to track if notification is needed
   - Releases lock before calling `_notify_pin_changed()`

### Fix 2: Create Non-Locking Internal Helper (Critical Fix!)

Created `_get_earliest_timer_unlocked()` to avoid reentrant lock attempts:

6. **`_get_earliest_timer_unlocked()`** (NEW)
   - Internal helper that finds earliest timer **without acquiring lock**
   - Should only be called when lock is already held
   - Contains the actual min() logic from `get_earliest_timer()`

7. **`get_earliest_timer()`** (MODIFIED)
   - Now just acquires lock and calls `_get_earliest_timer_unlocked()`
   - Public API remains unchanged

8. **`_auto_pin_earliest()`** (MODIFIED)
   - Now calls `_get_earliest_timer_unlocked()` instead of `get_earliest_timer()`
   - No longer attempts to reacquire the lock
   - **This was the critical fix that resolved the 00:00:01 hang!**

## Testing

To verify the fix works:

1. Run the application:
   ```bash
   ./run.sh
   ```

2. Add a short timer (e.g., 10 seconds):
   - Click system tray icon → Add Timer → Custom Timer
   - Title: "Test", Duration: 0h 0m 10s
   - Click "Start Timer"

3. Watch the countdown in the top bar

4. Wait for timer to complete:
   - Notification should appear
   - Timer should be removed from the list
   - Next timer (if any) should be auto-pinned
   - **Application should NOT hang**

5. Verify the application is still responsive:
   - Click the system tray icon
   - Try adding another timer
   - Try viewing timers

## Expected Behavior After Fix

- ✅ Timers complete normally
- ✅ Notifications appear
- ✅ Sound alerts play
- ✅ Pinned timer switches to next earliest
- ✅ Application remains responsive
- ✅ No need to kill the process

## Technical Details

### Principle 1: Never Call Callbacks While Holding a Lock

**Never call callbacks while holding a lock if those callbacks might try to reacquire the same lock**.

Solution pattern:
```python
should_notify = False

with self.lock:
    # Do work that changes pin state
    should_notify = True

# Release lock before notifying
if should_notify:
    self._notify_pin_changed()
```

This ensures:
1. Pin state changes are atomic (protected by lock)
2. Callbacks can safely call back into TimerManager methods
3. No circular lock acquisition → no deadlock

### Principle 2: Avoid Reentrant Lock Attempts

Python's `threading.Lock()` is **NOT reentrant**. If you try to acquire it twice from the same thread, it will deadlock immediately.

**Bad pattern** (causes deadlock):
```python
with self.lock:
    # Call a method that also acquires self.lock
    self._auto_pin_earliest()
        earliest = self.get_earliest_timer()  # DEADLOCK HERE!
            with self.lock:  # Same thread, same lock → FREEZE
                # Never reaches here
```

**Good pattern** (use unlocked internal helper):
```python
with self.lock:
    # Call internal helper that doesn't acquire lock
    self._auto_pin_earliest()
        earliest = self._get_earliest_timer_unlocked()  # OK!
            # Already have lock, no acquisition needed
```

This pattern is used throughout the codebase:
- Public method (e.g., `get_earliest_timer()`) acquires lock
- Internal helper (e.g., `_get_earliest_timer_unlocked()`) assumes lock is held
- Methods that are called within locked sections use the internal helper

### Why This Matters

The 00:00:01 hang occurred because:
1. Timer completed at exactly 0 seconds
2. `on_timer_complete()` acquired the lock
3. Called `_auto_pin_earliest()` (still holding lock)
4. Which called `get_earliest_timer()` (tried to reacquire lock)
5. **DEADLOCK** - thread blocked waiting for itself to release the lock
6. GTK main loop frozen, entire application hung

The notification appeared because it happened **before** the deadlock (in step 2-3). But then the app froze trying to find the next timer to pin.
