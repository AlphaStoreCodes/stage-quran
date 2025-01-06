# Quran Discord Bot

A dedicated Discord bot for continuous Quran recitation in voice channels, featuring multiple renowned reciters and automatic stage channel management.

## Features

- **Multiple Renowned Reciters** - Features recitations from well-known Qaris including:
  - Abdullah Humaid
  - Ahmad Khedr
  - Abdul Basit Abdul Samad
  - Maher Almaikulai
  - Mahmoud Al-Hosary
  - And many more...

- **24/7 Continuous Playback**
  - Automatically cycles through playlists
  - Seamless transitions between recitations
  - Auto-reconnects if disconnected

- **Stage Channel Support**
  - Automatically joins stage channels
  - Manages speaker permissions
  - Handles stage channel protocols

- **Advanced Features**
  - High-quality audio playback
  - Automatic error recovery
  - Connection status monitoring
  - Smart reconnection system

## Requirements

- Python 3.8 or higher
- FFmpeg
- Discord Bot Token
- Server with Stage Channel permissions

## Installation

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd [bot-directory]
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   - Windows: Download from official website or use package manager
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

4. **Configure the bot**
   Create a `.env` file with:
   ```env
   DISCORD_TOKEN=your_bot_token
   GUILD_ID=your_server_id
   CHANNEL_ID=your_channel_id
   ```

## Configuration

### Environment Variables
- `DISCORD_TOKEN`: Your Discord bot token
- `GUILD_ID`: The ID of your Discord server
- `CHANNEL_ID`: The ID of your stage/voice channel

### Playlist Configuration
Edit `playlist.json` to customize reciters and playlists:
```json
{
    "reciters": [
        {
            "name": "Reciter Name",
            "playList": "YouTube_Playlist_ID"
        }
    ]
}
```

## Running the Bot
You need to join our discord server to the rest files
يجب عليك الانضمام لسيرفرنا الديسكور للملفات الاخرى
بسبب كبر حجمها
https://discord.gg/UhnY5agZRE

## Usage

1. **Start the bot**
   ```bash
   python main.py
   ```

2. **Bot Commands**
   - `/status` - Check bot's current status
   - `/reconnect` - Force bot to reconnect
   - More commands coming soon...

## Troubleshooting

- **Bot not connecting?**
  - Verify your bot token and channel IDs
  - Ensure bot has proper permissions
  - Check if FFmpeg is installed correctly

- **No audio playing?**
  - Verify your playlist.json configuration
  - Check if the YouTube playlists are accessible
  - Ensure FFmpeg is properly installed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all the Qaris who have made their recitations available
- Discord.py community for their excellent library
- yt-dlp team for YouTube download capabilities
