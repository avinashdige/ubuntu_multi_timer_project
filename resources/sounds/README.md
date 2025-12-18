# Alert Sound

Place your alert sound file here (OGG format recommended for Linux).

Filename: `alert.ogg`

If no custom sound is provided, the application will fall back to a system beep.

You can find free sounds at:
- https://freesound.org/
- https://www.zapsplat.com/
- Or use this command to convert an existing sound:
  ```bash
  ffmpeg -i input.mp3 alert.ogg
  ```

Recommended: Short alert sound (1-3 seconds), clear but not jarring.
