# Multi-Timer Application - Project Requirements

## Project Overview
A system tray application for Ubuntu that allows users to manage multiple named timers simultaneously with desktop notifications.

## Core Requirements

### 1. System Tray Integration
- Application must run in the Ubuntu top bar (system tray)
- Display a clickable icon that opens the menu
- Application should run in the background without a main window

### 2. Timer Functionality

#### Add Timer
- User can create multiple timers simultaneously
- Each timer requires:
  - **Title/Name**: Text label to identify the timer
  - **Duration**: Time in hours, minutes, and/or seconds
- Input should be simple and quick to use
- No limit on number of concurrent timers

#### View Timers
- Display all active timers in a list view
- Each timer entry must show:
  - Timer title/name
  - Remaining time counting down in real-time (HH:MM:SS format)
- List updates dynamically as timers count down
- Clear visual indication of which timers are running

#### Delete Timer
- Each timer in the view has a delete/remove button
- Clicking delete immediately stops and removes that timer
- No confirmation dialog needed (simple one-click deletion)

### 3. Notifications
- When a timer reaches 00:00:00, trigger a desktop notification
- Notification must display:
  - The timer's title/name
  - Clear indication that the timer has finished
- Use Ubuntu's native notification system
- Notification should be visible even if the app menu is closed
- **Sound Alert**: Play an audible alert sound when the notification appears
  - Use system notification sound or include a default alert sound
  - Sound should be clear and attention-grabbing but not jarring

## Technical Specifications

### Platform
- Target OS: Ubuntu (recent versions with GNOME desktop)
- Must support system tray/top bar integration

### User Interface Requirements
- Menu opens from system tray icon
- Interface should be lightweight and fast
- Clear separation between:
  1. "Add Timer" option
  2. "View Timers" option
- Timer view should auto-refresh to show countdown

### Timer Behavior
- Timers run independently in the background
- Timers continue running when menu is closed
- Each timer counts down to zero then stops
- Timer removal is immediate and clean

### User Experience Goals
- **Quick Entry**: Adding a timer should take minimal clicks/keystrokes
- **At-a-glance**: Users can quickly see all running timers and their status
- **Non-intrusive**: App runs in background without cluttering workspace
- **Reliable Notifications**: Users won't miss when a timer completes

## Suggested Menu Structure

```
[Timer Icon] (in top bar)
├─ Add Timer
│  └─ Opens dialog/form with:
│     ├─ Title input field
│     └─ Time input (hours/minutes/seconds)
│     └─ Start/Create button
│
├─ View Timers
│  └─ Shows scrollable list:
│     ├─ Timer 1: "Meeting" - 15:32 remaining [Delete]
│     ├─ Timer 2: "Coffee" - 03:45 remaining [Delete]
│     └─ (updates in real-time)
│
└─ Quit (optional)
```

## Implementation Notes
- Use appropriate system tray library for Ubuntu/GNOME
- Timer precision: 1-second intervals acceptable
- Persistent timers between app restarts (optional feature, not required)
- Multiple timer completion notifications should be handled gracefully

## Success Criteria
- [ ] Application appears in Ubuntu top bar
- [ ] Can add unlimited named timers
- [ ] All timers countdown simultaneously
- [ ] View shows real-time countdown for all active timers
- [ ] Desktop notifications trigger with timer name when complete
- [ ] Timers can be individually deleted with one click
- [ ] Application is stable and doesn't crash with multiple timers

## Out of Scope (Not Required)
- Timer editing/pausing
- Timer history or statistics
- Recurring/repeating timers
- Timer templates or presets

Version 1.1 requirements:
1. Auto-complete timer titles
2. CLI support: Through CLI as well, we should be able to add timers.
3. Sounds not being played for the notifications at the moment.
4. There should be some way to define standard timers (titles and their time) that we usually always need to start timers for. These should always be available and we should just need to click start on it. May be once we click the system icon, the "Add Timer" option should have an arrow that displays all these standard timer options that we can start easily.
5. Also, provide standard timer options like 1 minute timer button, 2 minute timer button, 3,4,5,7,10,12 minute timer buttons.

Version 1.2 requirements:
1. Can we also provide a way with which I would be able simply pin one of the timers running down? By default, it would be the earliest timer that would finish. But we can always override this pin with other timers and pin other timers instead. At once, one timer can be pinned. The pinned timer and its title would be visible running down in the Ubuntu top bar (system tray) similar to how date and time are visible directly and we do not need to click anything to view them. As soon as, the timer finishes, the next earliest available timer and its title would be shown there instead. If no timer is available, then nothing would be displayed there.
