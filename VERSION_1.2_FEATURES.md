# Version 1.2 Features

## Pinned Timer in Ubuntu Top Bar

### Overview
Display a timer countdown directly in Ubuntu's system tray (top bar) without needing to click the icon.

### How It Works

**Auto-Pin Behavior:**
- The timer that will finish soonest is automatically pinned
- Pinned timer's countdown appears next to the app icon in the top bar
- Display format: `00:15:32 Meeting...` (countdown + truncated title)
- Only one timer can be pinned at a time

**When Auto-Pinning Occurs:**
1. **First Timer Added**: Automatically pinned when you create your first timer
2. **Earlier Timer Added**: If you add a timer with less remaining time than the current pin, it becomes pinned automatically
3. **Pinned Timer Completes**: The next earliest timer becomes pinned immediately
4. **Pinned Timer Deleted**: The next earliest timer becomes pinned immediately
5. **No Timers Running**: Label hidden completely

### Manual Pin Control

You can override the auto-pin behavior and manually pin any timer:

1. Click the timer icon in the system tray
2. Select "View Timers" from the menu
3. Find the timer you want to pin
4. Click the **[Pin]** button next to it

**Pin Indicators:**
- Pinned timer shows a 📌 emoji next to its title
- The Pin button changes to **[Unpin]** for the currently pinned timer
- Unpin button is highlighted in blue (suggested-action style)

**To Unpin:**
- Click **[Unpin]** on the currently pinned timer
- The earliest timer will be automatically pinned instead

### Display Format

**In the Top Bar:**
```
00:15:32 Meeting...
```
- Shows hours:minutes:seconds followed by the timer title
- Long titles are automatically truncated to fit
- Maximum ~25 characters total to fit Ubuntu top bar

**In the View Timers Dialog:**
```
📌 Meeting                    00:15:32  [Unpin] [Delete]
Coffee Break                  00:25:00  [Pin]   [Delete]
Work Session                  01:30:00  [Pin]   [Delete]
```

### Use Cases

**Monitor Urgent Deadlines:**
- Keep track of meeting start time while working
- See cooking timer countdown without opening the app

**Multitasking:**
- Glance at important timer while in other applications
- No need to switch windows or click icons

**Prioritize Timers:**
- Manually pin the most important timer
- Override auto-pinning when needed

### Technical Details

**Update Frequency:**
- Label updates every 1 second for smooth countdown
- Immediate update when pin changes

**Performance:**
- Minimal CPU usage (periodic 1-second updates)
- Thread-safe operations
- No impact on other timers

**Edge Cases Handled:**
- Multiple timers with same remaining time: Oldest timer wins
- Rapid timer additions/deletions: Consistent pinning behavior
- Dialog closed: Label continues updating

### Keyboard Shortcuts

None currently. Pin/unpin requires clicking the buttons in the View Timers dialog.

### Known Limitations

1. **Single Pin**: Only one timer can be pinned at a time
2. **No Custom Format**: Display format is fixed (HH:MM:SS Title)
3. **Title Truncation**: Long timer titles are truncated to fit the top bar
4. **No Pin Persistence**: Pin preference is not saved between app restarts

### Future Enhancements (Not Yet Implemented)

- Pin persistence across app restarts
- Configurable display format
- Keyboard shortcuts for pinning
- Multiple pinned timers with cycling
- Customizable title truncation length

---

## Version History

### Version 1.2.0 (Current)
- ✅ Pinned timer display in Ubuntu top bar
- ✅ Auto-pin earliest timer by default
- ✅ Manual pin/unpin controls
- ✅ Visual pin indicator (📌 emoji)
- ✅ Real-time countdown updates (1 second)
- ✅ Thread-safe pinning operations
- ✅ Automatic pin switching on timer completion/deletion

### Version 1.1.0
- ✅ Auto-complete timer titles
- ✅ CLI support for adding timers
- ✅ Improved notification sounds
- ✅ Timer presets and quick timers
- ✅ Standard timer buttons (1-12 minutes)

### Version 1.0.0
- ✅ Multiple concurrent timers
- ✅ System tray integration
- ✅ Desktop notifications
- ✅ Add/View/Delete timers
- ✅ Real-time countdown display

---

## Feedback

If you encounter any issues with the pinned timer feature or have suggestions for improvements, please let us know!

**Common Questions:**

**Q: Can I pin multiple timers at once?**
A: No, only one timer can be pinned at a time. This keeps the top bar uncluttered.

**Q: Why did my pinned timer change automatically?**
A: When the pinned timer completes or is deleted, the next earliest timer is automatically pinned. You can manually re-pin your preferred timer.

**Q: The timer title is cut off. Can I see the full title?**
A: Hover over the timer in the View Timers dialog to see the full title. The top bar display is truncated to fit the available space.

**Q: Can I hide the countdown from the top bar?**
A: Delete or pause all timers and the label will automatically hide. There's no separate setting to disable the display.

**Q: Does the pinned timer affect battery life?**
A: The impact is minimal. The label updates once per second, which is very efficient.
