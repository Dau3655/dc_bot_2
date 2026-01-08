import discord
import os
import asyncio
from discord.ext import commands, tasks
from keep_alive import keep_alive

# === 設定區 ===
# 這裡抓的是環境變數裡的 Token，記得在 Render 設定
TOKEN = os.getenv("DISCORD_TOKEN")
# 請填入跟 1 號機一樣的語音頻道 ID
VOICE_CHANNEL_ID = 911302671863021648 

# === 機器人初始化 ===
intents = discord.Intents.default()
# 雖然沒功能，但開著 Message Content 以後要加功能比較方便
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

# === 核心任務：斷線重連巡邏隊 (備用機專用版) ===
# 每 5 分鐘檢查一次就好，不需要像 1 號機那麼頻繁
@tasks.loop(minutes=5) 
async def check_voice_connection():
    if not bot.is_ready():
        return

    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        print("❌ 找不到目標頻道")
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
    
    # 如果不在頻道內 -> 加入
    if not voice_client:
        print("備用機：偵測到缺席，正在補位...")
        try:
            # self_deaf=True 代表它是「拒聽」狀態，可以省流量
            await channel.connect(self_deaf=True)
            print("備用機：補位成功！")
        except Exception as e:
            print(f"補位失敗: {e}")
            
    # 如果跑錯房間 -> 移動
    elif voice_client.channel.id != VOICE_CHANNEL_ID:
        try:
            await voice_client.move_to(channel)
        except:
            pass

@bot.event
async def on_ready():
    print(f'🤖 備用機 {bot.user} 上線待命中！')
    
    # 設定狀態：讓大家知道它是備用的
    await bot.change_presence(
        status=discord.Status.idle, # 設定為「閒置」(黃燈)，區分 1 號機
        activity=discord.Game(name="備用電源啟動中 ⚡")
    )
    
    # 啟動巡邏
    if not check_voice_connection.is_running():
        check_voice_connection.start()

# 保持網頁喚醒
keep_alive()

if TOKEN:
    bot.run(TOKEN)
else:
    print("錯誤：找不到 Token")