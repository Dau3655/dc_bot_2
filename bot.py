import discord
import os
import asyncio
from discord.ext import commands, tasks
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")
# ⚠️ 請再次確認這裡的 ID 是正確的！
VOICE_CHANNEL_ID = 911302671863021648 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

@tasks.loop(minutes=5) 
async def check_voice_connection():
    if not bot.is_ready(): return
    
    print(f"🕵️ 巡邏隊出動：正在尋找頻道 {VOICE_CHANNEL_ID}...", flush=True)
    
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        print(f"❌ 錯誤：找不到 ID 為 {VOICE_CHANNEL_ID} 的語音頻道！", flush=True)
        print("💡 可能原因：1. ID 填錯 / 2. 機器人沒權限看該頻道 / 3. 機器人還沒讀取完伺服器資料", flush=True)
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
    
    if not voice_client:
        print("🏃 發現機器人不在頻道內，嘗試加入...", flush=True)
        try:
            await channel.connect(self_deaf=True)
            print("✅ 成功加入語音頻道！", flush=True)
        except Exception as e:
            print(f"🔥 加入失敗，錯誤原因: {e}", flush=True)
    else:
        print("👌 機器人已經在頻道內，沒事。", flush=True)

@bot.event
async def on_ready():
    print(f'🤖 備用機 {bot.user} 上線了！ID: {bot.user.id}', flush=True)
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="備用電源 ⚡"))
    
    # 上線立刻執行一次檢查，不用等 5 分鐘
    if not check_voice_connection.is_running():
        await check_voice_connection() # 強制先跑一次
        check_voice_connection.start() # 然後設定循環

keep_alive()

if TOKEN:
    bot.run(TOKEN)
else:
    print("錯誤：找不到 Token", flush=True)