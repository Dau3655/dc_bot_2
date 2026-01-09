import discord
import os
import random as rd # 你這裡用了 rd，下面記得都要用 rd
import asyncio
from discord.ext import commands, tasks
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")
# ⚠️ 請再次確認這裡的 ID 是正確的！
VOICE_CHANNEL_ID = 911302671863021648 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

# === [修正] 狀態更換任務 ===
@tasks.loop(minutes=3)
async def status_task():
    statuses = [
        "咕嚕咕嚕...",
        '我堅信總有一天，人們在真正意義上互相理解的時代一定會到來',
        "備用電源運作中 ⚡",
        
    ]
    
    # 1. 從清單 (statuses) 裡面選，不是從函式選
    current_status = rd.choice(statuses)
    
    # 2. 真正執行「更換狀態」的動作
    # 記得加上 status=discord.Status.idle (維持黃燈)，不然會跳回綠燈
    await bot.change_presence(
        status=discord.Status.idle, 
        activity=discord.Game(name=current_status)
    )

# === 語音巡邏隊 ===
@tasks.loop(minutes=5) 
async def check_voice_connection():
    if not bot.is_ready(): return
    
    print(f"🕵️ 巡邏隊出動：正在尋找頻道 {VOICE_CHANNEL_ID}...", flush=True)
    
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        print(f"❌ 錯誤：找不到 ID 為 {VOICE_CHANNEL_ID} 的語音頻道！", flush=True)
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
    
    # 上線立刻執行一次檢查
    if not check_voice_connection.is_running():
        await check_voice_connection() 
        check_voice_connection.start() 

    # === [修正] 記得要在這裡啟動狀態迴圈！ ===
    if not status_task.is_running():
        status_task.start()
        print("✅ 狀態輪播功能已啟動", flush=True)

keep_alive()

if TOKEN:
    bot.run(TOKEN)
else:
    print("錯誤：找不到 Token", flush=True)