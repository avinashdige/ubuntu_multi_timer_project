# Version 1.3 Features

## Desktop Application Integration

### Overview
Multi-Timer is now available as a proper Ubuntu desktop application that appears in your application menu and can auto-start when you log in.

## Features

### 1. Application Menu Integration

**What It Does:**
- Adds Multi-Timer to Ubuntu's application launcher
- Makes the app searchable from the Activities/Applications menu
- Provides a desktop icon for easy access

**How to Access:**
1. Press the **Super key** (Windows key)
2. Type "Multi Timer" in the search
3. Click the icon to launch

**Benefits:**
- No need to open a terminal
- Launch like any other desktop application
- Easier for non-technical users

### 2. Auto-Start at Login

**What It Does:**
- Automatically launches Multi-Timer when you log into Ubuntu
- App starts minimized to system tray
- Timers can be running before you even open any applications

**Use Cases:**
- Start your day with timers already running
- Never forget to launch the app
- Seamless integration with your workflow

**How It Works:**
- Uses Ubuntu's autostart mechanism
- Configured via `~/.config/autostart/`
- Can be enabled/disabled during installation

## Installation

### Quick Install (Recommended)

Run the desktop integration installer:

```bash
./install_desktop.sh
```

This will:
1. Install the application launcher
2. Ask if you want auto-start enabled
3. Update the desktop database
4. Configure everything automatically

**Interactive Prompts:**
```
Do you want Multi-Timer to start automatically when you log in? (y/n):
```
- Choose **y** to enable auto-start
- Choose **n** to only install the application launcher

### Manual Installation

If you prefer to install manually:

#### Application Launcher Only:

```bash
# Create applications directory if it doesn't exist
mkdir -p ~/.local/share/applications

# Copy and edit the desktop file
cp multi-timer.desktop ~/.local/share/applications/
# Edit the file to set the correct Exec path

# Update desktop database
update-desktop-database ~/.local/share/applications
```

#### Auto-Start Configuration:

```bash
# Create autostart directory if it doesn't exist
mkdir -p ~/.config/autostart

# Copy and edit the autostart file
cp multi-timer-autostart.desktop ~/.config/autostart/
# Edit the file to set the correct Exec path
```

## Uninstallation

To remove desktop integration:

```bash
./uninstall_desktop.sh
```

This will:
- Remove the application from the launcher
- Disable auto-start
- Update the desktop database

**Note:** This only removes desktop integration, not the application itself.

## Managing Auto-Start

### Enable Auto-Start

**Method 1: Run installer again**
```bash
./install_desktop.sh
```
Choose 'y' when prompted about auto-start.

**Method 2: GNOME Tweaks**
1. Install GNOME Tweaks: `sudo apt install gnome-tweaks`
2. Open GNOME Tweaks
3. Go to "Startup Applications"
4. Find "Multi Timer" and toggle it on

**Method 3: Manually**
```bash
./install_desktop.sh  # Creates the file automatically
```

### Disable Auto-Start

**Method 1: Run installer**
```bash
./install_desktop.sh
```
Choose 'n' when prompted about auto-start.

**Method 2: GNOME Tweaks**
1. Open GNOME Tweaks
2. Go to "Startup Applications"
3. Find "Multi Timer" and toggle it off

**Method 3: Manually**
```bash
rm ~/.config/autostart/multi-timer-autostart.desktop
```

## File Locations

After installation, you'll find:

**Application Launcher:**
```
~/.local/share/applications/multi-timer.desktop
```

**Auto-Start Configuration:**
```
~/.config/autostart/multi-timer-autostart.desktop
```

## Desktop File Contents

The `.desktop` files contain:
- Application name and description
- Icon (uses system "alarm-clock" icon)
- Execution command (points to `run.sh`)
- Categories (Utility, Clock)
- Keywords for searching

## Compatibility

**Tested On:**
- Ubuntu 22.04 LTS (GNOME)
- Ubuntu 20.04 LTS (GNOME)

**Should Work On:**
- Any Ubuntu/Debian-based distribution with GNOME
- Other desktop environments (KDE, XFCE, etc.) with freedesktop.org standards

**Requirements:**
- System must support `.desktop` files
- `~/.local/share/applications/` support
- `~/.config/autostart/` support (for auto-start)

## Troubleshooting

### Application doesn't appear in menu

**Check installation:**
```bash
ls -la ~/.local/share/applications/multi-timer.desktop
```

**Manually update database:**
```bash
update-desktop-database ~/.local/share/applications
```

**Log out and log back in:**
Sometimes the desktop environment needs to be restarted to recognize new applications.

### Auto-start doesn't work

**Check autostart directory ownership:**
```bash
ls -la ~/.config/autostart/
```

If the directory is owned by root, fix it:
```bash
sudo chown -R $USER:$USER ~/.config/autostart/
```

Then run the installer again.

**Verify file exists:**
```bash
ls -la ~/.config/autostart/multi-timer-autostart.desktop
```

**Check file permissions:**
```bash
chmod +x ~/.config/autostart/multi-timer-autostart.desktop
```

**Check desktop environment:**
Some desktop environments handle autostart differently. Check your DE's documentation.

**Test manually:**
```bash
~/.config/autostart/multi-timer-autostart.desktop
```

### Icon doesn't show

The app uses the system "alarm-clock" icon. If it doesn't appear:
- Install an icon theme that includes this icon
- Or add a custom icon to `resources/icons/` and update the desktop files

### Wrong application path

If you moved the project directory after installation:

```bash
./uninstall_desktop.sh  # Remove old integration
./install_desktop.sh    # Reinstall with new path
```

## Advanced Configuration

### Custom Icon

To use a custom icon:

1. Place your icon in `resources/icons/multi-timer.png`
2. Edit the desktop files to use absolute path:
   ```ini
   Icon=/full/path/to/resources/icons/multi-timer.png
   ```
3. Reinstall: `./install_desktop.sh`

### Custom Launch Options

Edit the desktop files to add command-line options:

```ini
Exec=/path/to/project/run.sh --your-options-here
```

### Hide from Application Menu

To only use auto-start without showing in menu:

1. Edit `~/.local/share/applications/multi-timer.desktop`
2. Add: `NoDisplay=true`
3. Or simply don't install the application launcher, only the autostart file

## Version History

### Version 1.3.0 (Current)
- ✅ Desktop application integration
- ✅ Application launcher in Ubuntu menu
- ✅ Auto-start at login support
- ✅ Installation/uninstallation scripts
- ✅ Proper .desktop file configuration

### Version 1.2.0
- ✅ Pinned timer in top bar
- ✅ Auto-pin earliest timer
- ✅ Manual pin/unpin controls

### Version 1.1.0
- ✅ Auto-complete timer titles
- ✅ CLI support
- ✅ Improved notification sounds
- ✅ Timer presets and quick timers

### Version 1.0.0
- ✅ Multiple concurrent timers
- ✅ System tray integration
- ✅ Desktop notifications

## Future Enhancements

Potential improvements for Version 1.4+:
- Custom icon support in installer
- Debian package (.deb) for easier installation
- PPA repository for automatic updates
- System-wide installation option
- Settings GUI for auto-start configuration
- App indicator preferences

---

## Quick Reference

**Install desktop integration:**
```bash
./install_desktop.sh
```

**Uninstall desktop integration:**
```bash
./uninstall_desktop.sh
```

**Enable auto-start:** Run installer, choose 'y'

**Disable auto-start:** Run installer, choose 'n'

**Launch from menu:** Super key → "Multi Timer"

**Check if installed:**
```bash
ls ~/.local/share/applications/multi-timer.desktop
ls ~/.config/autostart/multi-timer-autostart.desktop
```

---

## Support

If you encounter issues with desktop integration:
1. Check file locations and permissions
2. Try logging out and back in
3. Run the installer again
4. Check the troubleshooting section above
5. Verify your desktop environment supports `.desktop` files
