import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import yt_dlp
from discord import PCMVolumeTransformer, FFmpegPCMAudio
import asyncio
from pytube import Playlist
import logging
import os
from datetime import datetime
import base64
import subprocess
import sys
import time
from dotenv import load_dotenv

_COPYRIGHT='\n╔═══════════════════════════════════════════════════════════════╗\n║                                                               ║\n║       Copyright (c) 2024 Alpha Store. All rights reserved.    ║\n║                                                              ║\n╚═══════════════════════════════════════════════════════════════╝\n'
_REQUIRED_LOGO='░█████╗░██╗░░░░░██████╗░██╗░░██╗░█████╗░  ░██████╗████████╗░█████╗░██████╗░███████╗\n██╔══██╗██║░░░░░██╔══██╗██║░░██║██╔══██╗  ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝\n███████║██║░░░░░██████╔╝███████║███████║  ╚█████╗░░░░██║░░░██║░░██║██████╔╝█████╗░░\n██╔══██║██║░░░░░██╔═══╝░██╔══██║██╔══██║  ░╚═══██╗░░░██║░░░██║░░██║██╔══██╗██╔══╝░░\n██║░░██║███████╗██║░░░░░██║░░██║██║░░██║  ██████╔╝░░░██║░░░╚█████╔╝██║░░██║███████╗\n╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝  ╚═════╝░░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝╚══════╝'
def _v0(p):return os.path.exists(p)
def _v1(p):
	try:
		with open(p,'r',encoding='utf-8')as A:return A.read().strip()
	except:return''
def _v3():
	J='requirements.data';I='playlist.json';H='LICENSE';G='readme.md';B='reciters'
	try:
		print(_COPYRIGHT);time.sleep(1);K=[G,H,'.env',I,J];C=[A for A in K if not _v0(A)]
		if C:print(f"\nError: Missing required files: {', '.join(C)}");sys.exit(1)
		D=_v1(H)
		if not D:print('Error: Invalid configuration - LICENSE file is empty');sys.exit(1)
		if _REQUIRED_LOGO.strip()not in D:print('Error: Invalid configuration - LICENSE logo verification failed');sys.exit(1)
		try:
			with open(I,'r')as L:
				A=json.load(L)
				if B not in A or not isinstance(A[B],list):print("Error: Invalid configuration - playlist.json missing 'reciters' array");sys.exit(1)
				for E in A[B]:
					if'name'not in E or'playList'not in E:print('Error: Invalid configuration - playlist.json reciter missing required fields');sys.exit(1)
		except json.JSONDecodeError:print('Error: Invalid configuration - playlist.json is not valid JSON');sys.exit(1)
		except:print('Error: Invalid configuration - playlist.json read failed');sys.exit(1)
		F=_v1(J)
		if not F:print('Error: Invalid configuration - requirements.data is empty');sys.exit(1)
		if _REQUIRED_LOGO.strip()not in F:print('Error: Invalid configuration - requirements.data logo verification failed');sys.exit(1)
		M=_v1(G)
		if not M:print('Error: Invalid configuration - readme.md is empty');sys.exit(1)
		print(_REQUIRED_LOGO);print('\nInitialization successful...\n');return True
	except Exception as N:print(f"Error: Configuration verification failed - {str(N)}");return False
    
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not all([TOKEN, GUILD_ID, CHANNEL_ID]):
    print("Error: Missing required environment variables. Please check your .env file.")
    sys.exit(1)

if not _v3():
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

class QuranBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True
        
        super().__init__(command_prefix='!', intents=intents)
        self.current_track = None
        self.is_playing = False
        self.reconnect_attempts = 0
        self.MAX_RECONNECT_ATTEMPTS = 5
        self.last_disconnect_time = 0
        self.RECONNECT_COOLDOWN = 30  # seconds

    async def setup_hook(self):
        await self.tree.sync()
        self.bg_task = self.loop.create_task(self.check_stage_loop())

    async def check_stage_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                guild = self.get_guild(int(GUILD_ID))
                if not guild:
                    await self.connect_to_stage()
                else:
                    voice_client = guild.voice_client
                    channel = guild.get_channel(int(CHANNEL_ID))
                    
                    if not voice_client or not voice_client.is_connected() or voice_client.channel != channel:
                        await self.connect_to_stage()
                    elif not self.is_playing:
                        await play_playlist(voice_client, playlists)
            except Exception as e:
                print(f"Error in check_stage_loop: {e}")
                await self.connect_to_stage()
            
            await asyncio.sleep(300)  # Sleep for 5 minutes

    async def connect_to_stage(self):
        try:
            # Check if we're within cooldown period
            current_time = time.time()
            if current_time - self.last_disconnect_time < self.RECONNECT_COOLDOWN:
                return

            # Reset reconnect attempts if it's been a while
            if current_time - self.last_disconnect_time > self.RECONNECT_COOLDOWN * 2:
                self.reconnect_attempts = 0

            # Check reconnection attempts
            if self.reconnect_attempts >= self.MAX_RECONNECT_ATTEMPTS:
                print(f"Max reconnection attempts ({self.MAX_RECONNECT_ATTEMPTS}) reached. Waiting for cooldown...")
                return

            guild = self.get_guild(int(GUILD_ID))
            if not guild:
                return

            channel = guild.get_channel(int(CHANNEL_ID))
            if not channel:
                return

            if guild.voice_client:
                await guild.voice_client.disconnect()

            voice_client = await channel.connect()
            
            if isinstance(channel, discord.StageChannel):
                await guild.me.edit(suppress=False)
                
            if not self.is_playing:
                await play_playlist(voice_client, playlists)

            # Reset reconnect attempts on successful connection
            self.reconnect_attempts = 0
            print(f"Successfully connected to {channel.name}")

        except Exception as e:
            print(f"Error in connect_to_stage: {e}")
            self.reconnect_attempts += 1
            self.last_disconnect_time = time.time()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.user.id:  # If the bot's voice state changed
            if before.channel and not after.channel:  # Bot was disconnected
                print("Bot was disconnected from voice channel. Attempting to reconnect...")
                self.last_disconnect_time = time.time()
                self.is_playing = False
                await self.connect_to_stage()
            elif not before.channel and after.channel:  # Bot joined a channel
                if isinstance(after.channel, discord.StageChannel):
                    try:
                        await asyncio.sleep(1)  # Wait a bit for connection to stabilize
                        await member.guild.me.edit(suppress=False)
                    except Exception as e:
                        print(f"Error unsuppressing bot: {e}")

bot = QuranBot()

with open('playlist.json', 'r') as f:
    playlists = json.load(f)['reciters']

async def get_voice_client(force_reconnect=False):
    try:
        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            return None

        if force_reconnect and guild.voice_client:
            await guild.voice_client.disconnect()

        channel = guild.get_channel(int(CHANNEL_ID))
        if not channel:
            return None

        if not guild.voice_client:
            voice_client = await channel.connect()
            if isinstance(channel, discord.StageChannel):
                await guild.me.edit(suppress=False)
            return voice_client

        return guild.voice_client
    except Exception:
        return None

async def get_playlist_urls(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        return list(playlist.video_urls)
    except Exception:
        return []

async def download_youtube_audio(url):
    temp_dir = 'temp_downloads'
    try:
        # Create temp directory if it doesn't exist
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # Generate unique filename using timestamp
        timestamp = int(time.time() * 1000)
        filename = f'audio_{timestamp}'
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{temp_dir}/{filename}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }
        
        # Download in a separate thread to avoid blocking
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        await asyncio.get_event_loop().run_in_executor(None, download)
        
        # Find the generated mp3 file
        mp3_file = f'{temp_dir}/{filename}.mp3'
        if not os.path.exists(mp3_file):
            # If mp3 not found, look for any file with the timestamp
            for file in os.listdir(temp_dir):
                if file.startswith(f'audio_{timestamp}'):
                    old_path = os.path.join(temp_dir, file)
                    # Convert to mp3 if needed
                    if not file.endswith('.mp3'):
                        os.system(f'ffmpeg -i "{old_path}" -vn -acodec libmp3lame -q:a 2 "{mp3_file}" -y')
                        os.remove(old_path)
                    else:
                        os.rename(old_path, mp3_file)
                    break
        
        if not os.path.exists(mp3_file):
            raise Exception("Failed to find or convert downloaded audio file")
            
        # Clean old files
        current_time = time.time()
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            # Remove files older than 1 hour
            if current_time - os.path.getctime(file_path) > 3600:
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # Return the audio source
        return discord.FFmpegPCMAudio(mp3_file)
        
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

async def play_playlist(voice_client: discord.VoiceClient, playlists):
    if not voice_client or voice_client.is_playing():
        return

    bot.is_playing = False
    
    try:
        for playlist in playlists:
            if not voice_client.is_connected():
                return
                
            urls = await get_playlist_urls(f"https://www.youtube.com/playlist?list={playlist['playList']}")
            
            for url in urls:
                if not voice_client.is_connected():
                    return
                    
                audio = await download_youtube_audio(url)
                if audio:
                    try:
                        voice_client.play(
                            discord.PCMVolumeTransformer(audio, volume=1.0),
                            after=lambda e: asyncio.run_coroutine_threadsafe(
                                play_next(voice_client, urls, url), bot.loop
                            )
                        )
                        bot.is_playing = True
                        bot.current_track = url
                        
                        while voice_client.is_playing():
                            await asyncio.sleep(1)
                            
                    except Exception as e:
                        print(f"Error playing audio: {e}")
                            
                await asyncio.sleep(1)  # Small delay between tracks
                
                # Clean up old files after each track
                try:
                    temp_dir = 'temp_downloads'
                    current_time = time.time()
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if current_time - os.path.getctime(file_path) > 3600:  # 1 hour
                            try:
                                os.remove(file_path)
                            except:
                                pass
                except Exception as e:
                    print(f"Error cleaning up files: {e}")
                    
    except Exception as e:
        print(f"Error in playlist: {e}")
        bot.is_playing = False

async def play_next(voice_client, playlist, current_url):
    if not voice_client or not voice_client.is_connected():
        return

    try:
        temp_dir = 'temp_downloads'
        os.remove(os.path.join(temp_dir, f'audio_{int(time.time() * 1000)}.mp3'))
    except:
        pass

    try:
        next_index = playlist.index(current_url) + 1
        if next_index < len(playlist):
            audio = await download_youtube_audio(playlist[next_index])
            if audio:
                voice_client.play(
                    discord.PCMVolumeTransformer(audio, volume=1.0),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        play_next(voice_client, playlist, playlist[next_index]), bot.loop
                    )
                )
                bot.current_track = playlist[next_index]
                return
    except Exception as e:
        print(f"Error in play_next: {e}")

    bot.is_playing = False

@bot.tree.command(name="status", description="Check the bot's current status")
async def status(interaction: discord.Interaction):
    try:
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            await interaction.response.send_message(f"Connected to {voice_client.channel.name}\nCurrently playing: {bot.current_track if bot.current_track else 'Nothing'}")
        else:
            await interaction.response.send_message("Not connected to any voice channel")
    except Exception:
        await interaction.response.send_message("An error occurred while checking status")

@bot.tree.command(name="reconnect", description="Force the bot to reconnect")
async def reconnect(interaction: discord.Interaction):
    try:
        voice_client = await get_voice_client(force_reconnect=True)
        if voice_client:
            await interaction.response.send_message("Successfully reconnected!")
            if not bot.is_playing:
                await play_playlist(voice_client, playlists)
        else:
            await interaction.response.send_message("Failed to reconnect")
    except Exception:
        await interaction.response.send_message("An error occurred while reconnecting")

@bot.event
async def on_ready():
    try:
        voice_client = await get_voice_client()
        if voice_client and not bot.is_playing:
            await play_playlist(voice_client, playlists)
    except Exception:
        pass

bot.run(TOKEN)
