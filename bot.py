import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import datetime
import os

# ──────────────────────────────────────────
#  CONFIGURAÇÃO — troque o token aqui
# ──────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN", "SEU_TOKEN_AQUI")  # use variável de ambiente!
PREFIX = "!"

# ──────────────────────────────────────────
#  INTENTS
# ──────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ══════════════════════════════════════════
#  EVENTOS
# ══════════════════════════════════════════

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidor(es) 👀"
        )
    )
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")
    print(f"🤖 Bot online como {bot.user} | Prefixo: {PREFIX}")


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="boas-vindas")
    if channel:
        embed = discord.Embed(
            title="👋 Bem-vindo(a)!",
            description=f"Seja bem-vindo(a) ao **{member.guild.name}**, {member.mention}!\nAgora somos **{member.guild.member_count}** membros.",
            color=0x00FF7F,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=member.guild.name, icon_url=member.guild.icon.url if member.guild.icon else None)
        await channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar esse comando.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membro não encontrado.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argumento faltando. Use `{PREFIX}help` para ver como usar.")
    else:
        await ctx.send(f"❌ Erro: `{error}`")

# ══════════════════════════════════════════
#  MODERAÇÃO
# ══════════════════════════════════════════

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="Nenhum motivo informado"):
    await member.ban(reason=motivo)
    embed = discord.Embed(title="🔨 Ban", color=0xFF0000)
    embed.add_field(name="Usuário", value=member.mention)
    embed.add_field(name="Motivo", value=motivo)
    embed.add_field(name="Moderador", value=ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, motivo="Nenhum motivo informado"):
    await member.kick(reason=motivo)
    embed = discord.Embed(title="👢 Kick", color=0xFF8C00)
    embed.add_field(name="Usuário", value=member.mention)
    embed.add_field(name="Motivo", value=motivo)
    embed.add_field(name="Moderador", value=ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command(name="timeout", aliases=["mute"])
@commands.has_permissions(moderate_members=True)
async def timeout_cmd(ctx, member: discord.Member, minutos: int = 10, *, motivo="Sem motivo"):
    duration = datetime.timedelta(minutes=minutos)
    await member.timeout(duration, reason=motivo)
    embed = discord.Embed(title="⏱️ Timeout", color=0xFFA500)
    embed.add_field(name="Usuário", value=member.mention)
    embed.add_field(name="Duração", value=f"{minutos} minuto(s)")
    embed.add_field(name="Motivo", value=motivo)
    await ctx.send(embed=embed)


@bot.command(name="untimeout", aliases=["unmute"])
@commands.has_permissions(moderate_members=True)
async def untimeout_cmd(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"✅ Timeout removido de {member.mention}.")


@bot.command(name="clear", aliases=["purge"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, quantidade: int = 10):
    await ctx.channel.purge(limit=quantidade + 1)
    msg = await ctx.send(f"🗑️ {quantidade} mensagem(ns) deletada(s).")
    await asyncio.sleep(3)
    await msg.delete()


@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Canal bloqueado.")


@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Canal desbloqueado.")


@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, motivo="Sem motivo"):
    embed = discord.Embed(title="⚠️ Aviso", color=0xFFFF00)
    embed.add_field(name="Usuário", value=member.mention)
    embed.add_field(name="Motivo", value=motivo)
    embed.add_field(name="Moderador", value=ctx.author.mention)
    await ctx.send(embed=embed)
    try:
        await member.send(f"⚠️ Você recebeu um aviso em **{ctx.guild.name}**:\n`{motivo}`")
    except:
        pass

# ══════════════════════════════════════════
#  EMBEDS
# ══════════════════════════════════════════

@bot.command(name="embed")
@commands.has_permissions(manage_messages=True)
async def embed_cmd(ctx, titulo: str, *, descricao: str):
    """!embed "Título aqui" Descrição aqui"""
    embed = discord.Embed(title=titulo, description=descricao, color=0x5865F2)
    embed.set_footer(text=f"Criado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.message.delete()
    await ctx.send(embed=embed)


@bot.command(name="anuncio")
@commands.has_permissions(manage_messages=True)
async def anuncio(ctx, *, texto: str):
    embed = discord.Embed(
        title="📢 Anúncio",
        description=texto,
        color=0xFFD700,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text=f"Por {ctx.author.display_name}")
    await ctx.message.delete()
    await ctx.send("@everyone", embed=embed)

# ══════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════

@bot.command(name="userinfo", aliases=["ui"])
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    embed = discord.Embed(title=f"👤 {member.display_name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Conta criada", value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Entrou no servidor", value=member.joined_at.strftime("%d/%m/%Y"))
    embed.add_field(name=f"Cargos ({len(roles)})", value=" ".join(roles) if roles else "Nenhum", inline=False)
    embed.add_field(name="Bot?", value="✅" if member.bot else "❌")
    await ctx.send(embed=embed)


@bot.command(name="serverinfo", aliases=["si"])
async def serverinfo(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"🏠 {g.name}", color=0x5865F2)
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="ID", value=g.id)
    embed.add_field(name="Dono", value=g.owner.mention)
    embed.add_field(name="Membros", value=g.member_count)
    embed.add_field(name="Canais", value=len(g.channels))
    embed.add_field(name="Cargos", value=len(g.roles))
    embed.add_field(name="Criado em", value=g.created_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=embed)


@bot.command(name="avatar", aliases=["av"])
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Avatar de {member.display_name}", color=member.color)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    cor = 0x00FF00 if latency < 100 else 0xFFFF00 if latency < 200 else 0xFF0000
    embed = discord.Embed(title="🏓 Pong!", description=f"Latência: **{latency}ms**", color=cor)
    await ctx.send(embed=embed)

# ══════════════════════════════════════════
#  DIVERSÃO / LOROTA
# ══════════════════════════════════════════

LOROTAS = [
    "Dizem que {user} tem QI de planta carnívora.",
    "{user} tentou dividir por zero e sobreviveu.",
    "Fontes confiáveis afirmam que {user} ronca em Morse.",
    "{user} foi banido do Google por saber demais.",
    "Cientistas confirmam: {user} é feito de 70% de besteira.",
    "Segundo a NASA, {user} tem a gravidade de um buraco negro de drama.",
    "{user} já ganhou um Oscar por fazer nada.",
    "Dizem que {user} treinou Pokémon antes de aprender a falar.",
    "Um estudo da USP comprova: {user} invented procrastination.",
    "{user} foi o responsável pelo apagão de 2009. Sim, aquele.",
]

@bot.command(name="lorota", aliases=["lie", "mentira"])
async def lorota(ctx, member: discord.Member = None):
    member = member or ctx.author
    frase = random.choice(LOROTAS).replace("{user}", member.display_name)
    embed = discord.Embed(
        title="🤥 Lorota do dia",
        description=frase,
        color=0xFF69B4
    )
    embed.set_footer(text="100% confiável | Fonte: confiei")
    await ctx.send(embed=embed)


@bot.command(name="dado", aliases=["dice", "rolar"])
async def dado(ctx, lados: int = 6):
    resultado = random.randint(1, lados)
    await ctx.send(f"🎲 Você rolou um d{lados} e tirou **{resultado}**!")


@bot.command(name="8ball")
async def ball8(ctx, *, pergunta: str):
    respostas = [
        "✅ Sim, com certeza!", "✅ Definitivamente!", "✅ Parece que sim.",
        "🤔 Difícil dizer agora...", "🤔 Tente novamente mais tarde.",
        "❌ Não parece.", "❌ Não.", "❌ De jeito nenhum!",
    ]
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x1a1a2e)
    embed.add_field(name="Pergunta", value=pergunta, inline=False)
    embed.add_field(name="Resposta", value=random.choice(respostas), inline=False)
    await ctx.send(embed=embed)


@bot.command(name="coinflip", aliases=["moeda"])
async def coinflip(ctx):
    resultado = random.choice(["🪙 Cara!", "🪙 Coroa!"])
    await ctx.send(resultado)


@bot.command(name="ship")
async def ship(ctx, user1: discord.Member, user2: discord.Member = None):
    user2 = user2 or ctx.author
    porcentagem = random.randint(0, 100)
    bar = "❤️" * (porcentagem // 10) + "🖤" * (10 - porcentagem // 10)
    embed = discord.Embed(title="💘 Compatibilidade amorosa", color=0xFF1493)
    embed.description = f"**{user1.display_name}** + **{user2.display_name}**\n\n{bar}\n**{porcentagem}%**"
    await ctx.send(embed=embed)

# ══════════════════════════════════════════
#  HELP CUSTOMIZADO
# ══════════════════════════════════════════

@bot.command(name="help", aliases=["ajuda"])
async def help_cmd(ctx):
    embed = discord.Embed(title="📖 Comandos do Bot", color=0x5865F2)
    embed.add_field(
        name="🛡️ Moderação",
        value="`ban` `kick` `timeout` `untimeout` `clear` `lock` `unlock` `warn`",
        inline=False
    )
    embed.add_field(
        name="📋 Embeds & Anúncios",
        value='`embed "Título" Descrição` `anuncio Texto`',
        inline=False
    )
    embed.add_field(
        name="🔍 Utilidades",
        value="`userinfo` `serverinfo` `avatar` `ping`",
        inline=False
    )
    embed.add_field(
        name="🎉 Diversão",
        value="`lorota` `dado` `8ball` `coinflip` `ship`",
        inline=False
    )
    embed.set_footer(text=f"Prefixo: {PREFIX}  |  Use {PREFIX}<comando>")
    await ctx.send(embed=embed)

# ══════════════════════════════════════════
#  START
# ══════════════════════════════════════════
bot.run(TOKEN)
