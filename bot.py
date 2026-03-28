import discord
from discord.ext import commands
import random
import asyncio
import datetime
import os
from dotenv import load_dotenv

# ══════════════════════════════════════════
#  CONFIGURAÇÃO
# ══════════════════════════════════════════
TOKEN  = os.getenv("MTQ4Njg5NzkyODkyMzY0ODAwMA.GalcQv.ELufFQoJuW0cVGCYrFl6R5yDyaJeyHKylE1gmE", "MTQ4Njg5NzkyODkyMzY0ODAwMA.GalcQv.ELufFQoJuW0cVGCYrFl6R5yDyaJeyHKylE1gmE")
PREFIX = "!"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ══════════════════════════════════════════
#  CORES DO TEMA
# ══════════════════════════════════════════
COR_PRINCIPAL = 0x5865F2
COR_SUCESSO   = 0x57F287
COR_ERRO      = 0xED4245
COR_AVISO     = 0xFEE75C
COR_INFO      = 0x5865F2
COR_MOD       = 0xFF6B6B
COR_FUN       = 0xFF69B4
COR_GOLD      = 0xFFD700

# ══════════════════════════════════════════
#  HELPER — embed padrão bonito
# ══════════════════════════════════════════
def make_embed(titulo, descricao=None, cor=COR_PRINCIPAL, thumbnail=None, imagem=None, rodape=None):
    e = discord.Embed(title=titulo, description=descricao, color=cor, timestamp=datetime.datetime.utcnow())
    if thumbnail:
        e.set_thumbnail(url=thumbnail)
    if imagem:
        e.set_image(url=imagem)
    if rodape:
        e.set_footer(text=rodape)
    return e

# ══════════════════════════════════════════
#  EVENTOS
# ══════════════════════════════════════════
@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"!help | {len(bot.guilds)} servidor(es)")
    )
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash commands sincronizados")
    except Exception as e:
        print(f"❌ Erro: {e}")
    print(f"🤖 {bot.user} online! Prefixo: {PREFIX}")


@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.text_channels, name="boas-vindas")
    if canal:
        e = make_embed(
            titulo=f"👋 Bem-vindo(a), {member.display_name}!",
            descricao=(
                f"Olá {member.mention}, seja muito bem-vindo(a) ao **{member.guild.name}**!\n\n"
                f"Agora somos **{member.guild.member_count}** membros. 🎉\n"
                f"Leia as regras e aproveite o servidor!"
            ),
            cor=COR_SUCESSO,
            thumbnail=member.display_avatar.url,
            rodape=f"ID: {member.id}"
        )
        if member.guild.icon:
            e.set_author(name=member.guild.name, icon_url=member.guild.icon.url)
        await canal.send(embed=e)


@bot.event
async def on_member_remove(member):
    canal = discord.utils.get(member.guild.text_channels, name="boas-vindas")
    if canal:
        e = make_embed(
            titulo="👋 Até logo!",
            descricao=f"**{member.display_name}** saiu do servidor. Ficamos **{member.guild.member_count}** membros.",
            cor=COR_ERRO,
            thumbnail=member.display_avatar.url
        )
        await canal.send(embed=e)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        e = make_embed("🚫 Sem Permissão", "Você não tem permissão para usar esse comando.", COR_ERRO)
    elif isinstance(error, commands.MemberNotFound):
        e = make_embed("❓ Não Encontrado", "Esse membro não foi encontrado no servidor.", COR_AVISO)
    elif isinstance(error, commands.MissingRequiredArgument):
        e = make_embed("📝 Argumento Faltando", f"Use `{PREFIX}help` para ver como usar o comando.", COR_AVISO)
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.BadArgument):
        e = make_embed("⚠️ Argumento Inválido", "Verifique os argumentos e tente novamente.", COR_AVISO)
    else:
        e = make_embed("❌ Erro", f"```{error}```", COR_ERRO)
    await ctx.send(embed=e, delete_after=8)

# ══════════════════════════════════════════
#  MODERAÇÃO
# ══════════════════════════════════════════
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="Nenhum motivo informado"):
    if member == ctx.author:
        return await ctx.send(embed=make_embed("❌ Erro", "Você não pode se banir.", COR_ERRO))
    if member.top_role >= ctx.author.top_role:
        return await ctx.send(embed=make_embed("❌ Erro", "Você não pode banir alguém com cargo igual ou superior ao seu.", COR_ERRO))
    try:
        await member.send(embed=make_embed(
            "🔨 Você foi banido",
            f"Você foi banido de **{ctx.guild.name}**\n**Motivo:** {motivo}",
            COR_ERRO
        ))
    except:
        pass
    await member.ban(reason=f"{ctx.author} | {motivo}")
    e = make_embed("🔨 Ban Aplicado", cor=COR_MOD, thumbnail=member.display_avatar.url, rodape=f"Moderador: {ctx.author}")
    e.add_field(name="👤 Usuário", value=f"{member.mention}\n`{member}`", inline=True)
    e.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    e.add_field(name="📝 Motivo", value=motivo, inline=False)
    await ctx.send(embed=e)


@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, usuario: str):
    bans = [entry async for entry in ctx.guild.bans()]
    alvo = None
    for entry in bans:
        if str(entry.user.id) == usuario or str(entry.user) == usuario or entry.user.name.lower() == usuario.lower():
            alvo = entry.user
            break
    if not alvo:
        return await ctx.send(embed=make_embed("❓ Não Encontrado", f"Nenhum ban encontrado para `{usuario}`.\nUse o ID ou nome do usuário.", COR_AVISO))
    await ctx.guild.unban(alvo, reason=f"Desbanido por {ctx.author}")
    e = make_embed("✅ Unban Aplicado", cor=COR_SUCESSO, thumbnail=alvo.display_avatar.url, rodape=f"Moderador: {ctx.author}")
    e.add_field(name="👤 Usuário", value=f"`{alvo}`", inline=True)
    e.add_field(name="🆔 ID", value=f"`{alvo.id}`", inline=True)
    await ctx.send(embed=e)


@bot.command(name="banlist")
@commands.has_permissions(ban_members=True)
async def banlist(ctx):
    bans = [entry async for entry in ctx.guild.bans()]
    if not bans:
        return await ctx.send(embed=make_embed("📋 Lista de Bans", "Nenhum usuário banido.", COR_INFO))
    lista = "\n".join([f"`{i+1}.` **{entry.user}** — {entry.reason or 'sem motivo'}" for i, entry in enumerate(bans[:20])])
    e = make_embed("📋 Lista de Bans", lista, COR_MOD, rodape=f"Total: {len(bans)} banido(s)")
    await ctx.send(embed=e)


@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, motivo="Nenhum motivo informado"):
    if member == ctx.author:
        return await ctx.send(embed=make_embed("❌ Erro", "Você não pode se expulsar.", COR_ERRO))
    try:
        await member.send(embed=make_embed(
            "👢 Você foi expulso",
            f"Você foi expulso de **{ctx.guild.name}**\n**Motivo:** {motivo}",
            COR_AVISO
        ))
    except:
        pass
    await member.kick(reason=f"{ctx.author} | {motivo}")
    e = make_embed("👢 Kick Aplicado", cor=COR_AVISO, thumbnail=member.display_avatar.url, rodape=f"Moderador: {ctx.author}")
    e.add_field(name="👤 Usuário", value=f"{member.mention}\n`{member}`", inline=True)
    e.add_field(name="📝 Motivo", value=motivo, inline=False)
    await ctx.send(embed=e)


@bot.command(name="timeout", aliases=["mute"])
@commands.has_permissions(moderate_members=True)
async def timeout_cmd(ctx, member: discord.Member, minutos: int = 10, *, motivo="Sem motivo"):
    await member.timeout(datetime.timedelta(minutes=minutos), reason=motivo)
    e = make_embed("⏱️ Timeout Aplicado", cor=COR_AVISO, thumbnail=member.display_avatar.url, rodape=f"Moderador: {ctx.author}")
    e.add_field(name="👤 Usuário", value=member.mention, inline=True)
    e.add_field(name="⏰ Duração", value=f"`{minutos}` minuto(s)", inline=True)
    e.add_field(name="📝 Motivo", value=motivo, inline=False)
    await ctx.send(embed=e)


@bot.command(name="untimeout", aliases=["unmute"])
@commands.has_permissions(moderate_members=True)
async def untimeout_cmd(ctx, member: discord.Member):
    await member.timeout(None)
    e = make_embed("✅ Timeout Removido", cor=COR_SUCESSO, rodape=f"Por {ctx.author}")
    e.add_field(name="👤 Usuário", value=member.mention)
    await ctx.send(embed=e)


@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, motivo="Sem motivo"):
    e = make_embed("⚠️ Aviso Emitido", cor=COR_AVISO, thumbnail=member.display_avatar.url, rodape=f"Moderador: {ctx.author}")
    e.add_field(name="👤 Usuário", value=member.mention, inline=True)
    e.add_field(name="📝 Motivo", value=motivo, inline=False)
    await ctx.send(embed=e)
    try:
        dm = make_embed("⚠️ Você recebeu um aviso", f"Você foi avisado em **{ctx.guild.name}**\n**Motivo:** {motivo}", COR_AVISO)
        await member.send(embed=dm)
    except:
        pass


@bot.command(name="clear", aliases=["purge", "limpar"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, quantidade: int = 10):
    if quantidade > 100:
        return await ctx.send(embed=make_embed("❌ Limite", "Máximo de 100 mensagens por vez.", COR_ERRO))
    await ctx.channel.purge(limit=quantidade + 1)
    msg = await ctx.send(embed=make_embed("🗑️ Mensagens Deletadas", f"`{quantidade}` mensagem(ns) removida(s).", COR_SUCESSO))
    await asyncio.sleep(4)
    await msg.delete()


@bot.command(name="lock", aliases=["fechar"])
@commands.has_permissions(manage_channels=True)
async def lock(ctx, canal: discord.TextChannel = None):
    canal = canal or ctx.channel
    await canal.set_permissions(ctx.guild.default_role, send_messages=False)
    e = make_embed("🔒 Canal Bloqueado", f"{canal.mention} foi bloqueado para membros.", COR_ERRO, rodape=f"Por {ctx.author}")
    await ctx.send(embed=e)


@bot.command(name="unlock", aliases=["abrir"])
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, canal: discord.TextChannel = None):
    canal = canal or ctx.channel
    await canal.set_permissions(ctx.guild.default_role, send_messages=True)
    e = make_embed("🔓 Canal Desbloqueado", f"{canal.mention} foi desbloqueado.", COR_SUCESSO, rodape=f"Por {ctx.author}")
    await ctx.send(embed=e)


@bot.command(name="slowmode", aliases=["slow"])
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, segundos: int = 0):
    await ctx.channel.edit(slowmode_delay=segundos)
    if segundos == 0:
        e = make_embed("✅ Slowmode Desativado", f"O slowmode foi removido de {ctx.channel.mention}.", COR_SUCESSO)
    else:
        e = make_embed("🐌 Slowmode Ativado", f"Slowmode de **{segundos}s** em {ctx.channel.mention}.", COR_AVISO)
    await ctx.send(embed=e)


@bot.command(name="nick")
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, novo_nick: str = None):
    antigo = member.display_name
    await member.edit(nick=novo_nick)
    e = make_embed("✏️ Nick Alterado", cor=COR_INFO, rodape=f"Por {ctx.author}")
    e.add_field(name="👤 Usuário", value=member.mention, inline=False)
    e.add_field(name="Antes", value=antigo, inline=True)
    e.add_field(name="Depois", value=novo_nick or member.name, inline=True)
    await ctx.send(embed=e)


@bot.command(name="addrole", aliases=["darRole"])
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, cargo: discord.Role):
    await member.add_roles(cargo)
    e = make_embed("✅ Cargo Adicionado", cor=COR_SUCESSO, rodape=f"Por {ctx.author}")
    e.add_field(name="👤 Usuário", value=member.mention, inline=True)
    e.add_field(name="🏷️ Cargo", value=cargo.mention, inline=True)
    await ctx.send(embed=e)


@bot.command(name="removerole", aliases=["tirarRole"])
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, cargo: discord.Role):
    await member.remove_roles(cargo)
    e = make_embed("✅ Cargo Removido", cor=COR_SUCESSO, rodape=f"Por {ctx.author}")
    e.add_field(name="👤 Usuário", value=member.mention, inline=True)
    e.add_field(name="🏷️ Cargo", value=cargo.mention, inline=True)
    await ctx.send(embed=e)

# ══════════════════════════════════════════
#  EMBEDS & ANÚNCIOS
# ══════════════════════════════════════════
@bot.command(name="embed")
@commands.has_permissions(manage_messages=True)
async def embed_cmd(ctx, titulo: str, *, descricao: str):
    """!embed "Título aqui" Descrição aqui"""
    e = discord.Embed(title=titulo, description=descricao, color=COR_PRINCIPAL, timestamp=datetime.datetime.utcnow())
    e.set_footer(text=f"Por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.message.delete()
    await ctx.send(embed=e)


@bot.command(name="anuncio")
@commands.has_permissions(manage_messages=True)
async def anuncio(ctx, *, texto: str):
    e = discord.Embed(title="📢 Anúncio", description=texto, color=COR_GOLD, timestamp=datetime.datetime.utcnow())
    if ctx.guild.icon:
        e.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
    e.set_footer(text=f"Anunciado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.message.delete()
    await ctx.send("@everyone", embed=e)


@bot.command(name="say", aliases=["falar"])
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, mensagem: str):
    await ctx.message.delete()
    await ctx.send(mensagem)

# ══════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    if latency < 100:
        cor, status = COR_SUCESSO, "🟢 Excelente"
    elif latency < 200:
        cor, status = COR_AVISO, "🟡 Normal"
    else:
        cor, status = COR_ERRO, "🔴 Alto"
    e = make_embed("🏓 Pong!", cor=cor)
    e.add_field(name="Latência", value=f"`{latency}ms`", inline=True)
    e.add_field(name="Status", value=status, inline=True)
    await ctx.send(embed=e)


@bot.command(name="userinfo", aliases=["ui", "perfil"])
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles  = [r.mention for r in reversed(member.roles) if r.name != "@everyone"]
    status_map = {
        discord.Status.online:  "🟢 Online",
        discord.Status.idle:    "🟡 Ausente",
        discord.Status.dnd:     "🔴 Não Perturbe",
        discord.Status.offline: "⚫ Offline"
    }
    e = make_embed(
        titulo=f"👤 {member.display_name}",
        cor=member.color if member.color.value else COR_PRINCIPAL,
        thumbnail=member.display_avatar.url,
        rodape=f"ID: {member.id}"
    )
    e.add_field(name="🏷️ Tag", value=f"`{member}`", inline=True)
    e.add_field(name="📡 Status", value=status_map.get(member.status, "Desconhecido"), inline=True)
    e.add_field(name="🤖 Bot?", value="✅ Sim" if member.bot else "❌ Não", inline=True)
    e.add_field(name="📅 Conta criada", value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
    e.add_field(name="📥 Entrou no servidor", value=f"<t:{int(member.joined_at.timestamp())}:D>", inline=True)
    e.add_field(name=f"🏷️ Cargos ({len(roles)})", value=" ".join(roles[:10]) if roles else "Nenhum", inline=False)
    await ctx.send(embed=e)


@bot.command(name="serverinfo", aliases=["si", "servidor"])
async def serverinfo(ctx):
    g       = ctx.guild
    bots    = sum(1 for m in g.members if m.bot)
    humanos = g.member_count - bots
    e = make_embed(titulo=f"🏠 {g.name}", cor=COR_PRINCIPAL, rodape=f"ID: {g.id}")
    if g.icon:
        e.set_thumbnail(url=g.icon.url)
    if g.banner:
        e.set_image(url=g.banner.url)
    e.add_field(name="👑 Dono", value=g.owner.mention, inline=True)
    e.add_field(name="📅 Criado em", value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
    e.add_field(name="👥 Membros", value=f"`{g.member_count}` total\n`{humanos}` humanos | `{bots}` bots", inline=False)
    e.add_field(name="💬 Canais", value=f"`{len(g.text_channels)}` texto | `{len(g.voice_channels)}` voz", inline=True)
    e.add_field(name="🏷️ Cargos", value=f"`{len(g.roles)}`", inline=True)
    e.add_field(name="😀 Emojis", value=f"`{len(g.emojis)}`", inline=True)
    e.add_field(name="🚀 Boosts", value=f"`{g.premium_subscription_count}` (Nível {g.premium_tier})", inline=True)
    await ctx.send(embed=e)


@bot.command(name="avatar", aliases=["av", "foto"])
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    e = make_embed(
        titulo=f"🖼️ Avatar de {member.display_name}",
        cor=member.color if member.color.value else COR_PRINCIPAL,
        imagem=member.display_avatar.url,
        rodape=f"ID: {member.id}"
    )
    e.description = f"[Abrir em tamanho completo]({member.display_avatar.url})"
    await ctx.send(embed=e)


@bot.command(name="banner")
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    user   = await bot.fetch_user(member.id)
    if not user.banner:
        return await ctx.send(embed=make_embed("❌ Sem Banner", f"{member.mention} não tem banner.", COR_AVISO))
    e = make_embed(titulo=f"🖼️ Banner de {member.display_name}", cor=COR_PRINCIPAL, imagem=user.banner.url)
    e.description = f"[Abrir em tamanho completo]({user.banner.url})"
    await ctx.send(embed=e)


@bot.command(name="roleinfo", aliases=["cargoinfo"])
async def roleinfo(ctx, *, cargo: discord.Role):
    e = make_embed(titulo=f"🏷️ {cargo.name}", cor=cargo.color)
    e.add_field(name="🆔 ID", value=f"`{cargo.id}`", inline=True)
    e.add_field(name="👥 Membros", value=f"`{len(cargo.members)}`", inline=True)
    e.add_field(name="📍 Posição", value=f"`{cargo.position}`", inline=True)
    e.add_field(name="🎨 Cor", value=str(cargo.color), inline=True)
    e.add_field(name="📌 Mencionável", value="✅" if cargo.mentionable else "❌", inline=True)
    e.add_field(name="📅 Criado em", value=f"<t:{int(cargo.created_at.timestamp())}:D>", inline=True)
    await ctx.send(embed=e)


@bot.command(name="botinfo")
async def botinfo(ctx):
    e = make_embed("🤖 Info do Bot", cor=COR_PRINCIPAL, thumbnail=bot.user.display_avatar.url)
    e.add_field(name="👤 Nome", value=f"`{bot.user}`", inline=True)
    e.add_field(name="🆔 ID", value=f"`{bot.user.id}`", inline=True)
    e.add_field(name="🌐 Servidores", value=f"`{len(bot.guilds)}`", inline=True)
    e.add_field(name="👥 Usuários", value=f"`{sum(g.member_count for g in bot.guilds)}`", inline=True)
    e.add_field(name="🏓 Latência", value=f"`{round(bot.latency*1000)}ms`", inline=True)
    e.add_field(name="⚙️ Prefixo", value=f"`{PREFIX}`", inline=True)
    await ctx.send(embed=e)

# ══════════════════════════════════════════
#  DIVERSÃO
# ══════════════════════════════════════════
LOROTAS = [
    "Dizem que **{user}** tem QI de planta carnívora.",
    "**{user}** tentou dividir por zero e sobreviveu.",
    "Fontes confiáveis afirmam que **{user}** ronca em código Morse.",
    "**{user}** foi banido do Google por saber demais.",
    "Cientistas confirmam: **{user}** é feito de 70% de besteira.",
    "Segundo a NASA, **{user}** tem a gravidade de um buraco negro de drama.",
    "**{user}** já ganhou um Oscar por fazer absolutamente nada.",
    "Dizem que **{user}** treinou Pokémon antes de aprender a falar.",
    "Um estudo da USP comprova: **{user}** inventou a procrastinação.",
    "**{user}** foi o responsável pelo apagão de 2009. Sim, aquele.",
    "Especialistas afirmam que **{user}** consegue dormir de olho aberto.",
    "**{user}** perdeu para si mesmo no xadrez.",
    "Vizinhos relatam que **{user}** fala com a geladeira às 3 da manhã.",
    "**{user}** foi o último a saber que o Titanic afundou.",
    "Consta que **{user}** tentou carregar o celular pelo P2 do fone.",
]

@bot.command(name="lorota", aliases=["lie", "mentira"])
async def lorota(ctx, member: discord.Member = None):
    member = member or ctx.author
    frase  = random.choice(LOROTAS).replace("{user}", member.display_name)
    e = make_embed("🤥 Lorota do Dia", frase, COR_FUN, thumbnail=member.display_avatar.url)
    e.set_footer(text="100% confiável | Fonte: confiei")
    await ctx.send(embed=e)


@bot.command(name="dado", aliases=["dice", "rolar"])
async def dado(ctx, lados: int = 6):
    if lados < 2:
        return await ctx.send(embed=make_embed("❌ Inválido", "O dado precisa ter pelo menos 2 lados.", COR_ERRO))
    resultado = random.randint(1, lados)
    e = make_embed("🎲 Dado Rolado", f"Você rolou um **d{lados}** e tirou...\n# {resultado}", COR_PRINCIPAL)
    await ctx.send(embed=e)


@bot.command(name="8ball", aliases=["bola"])
async def ball8(ctx, *, pergunta: str):
    respostas = [
        ("✅ Sim, com certeza!", COR_SUCESSO),
        ("✅ Definitivamente!", COR_SUCESSO),
        ("✅ Pode contar com isso!", COR_SUCESSO),
        ("🤔 Difícil dizer agora...", COR_AVISO),
        ("🤔 Tente novamente mais tarde.", COR_AVISO),
        ("❌ Não parece.", COR_ERRO),
        ("❌ De jeito nenhum!", COR_ERRO),
    ]
    resposta, cor = random.choice(respostas)
    e = make_embed("🎱 Magic 8-Ball", cor=cor)
    e.add_field(name="❓ Pergunta", value=pergunta, inline=False)
    e.add_field(name="🔮 Resposta", value=f"**{resposta}**", inline=False)
    await ctx.send(embed=e)


@bot.command(name="coinflip", aliases=["moeda"])
async def coinflip(ctx):
    resultado = random.choice(["Cara", "Coroa"])
    emoji     = "🌕" if resultado == "Cara" else "⭐"
    e = make_embed(f"{emoji} {resultado}!", f"A moeda caiu em **{resultado}**!", COR_GOLD)
    await ctx.send(embed=e)


@bot.command(name="ship")
async def ship(ctx, user1: discord.Member, user2: discord.Member = None):
    user2    = user2 or ctx.author
    porcento = random.randint(0, 100)
    cheios   = porcento // 10
    barra    = "❤️" * cheios + "🖤" * (10 - cheios)
    if porcento >= 80:   comentario = "💞 Match perfeito!"
    elif porcento >= 60: comentario = "😊 Boa combinação!"
    elif porcento >= 40: comentario = "🙂 Pode funcionar..."
    elif porcento >= 20: comentario = "😬 Vai com calma..."
    else:                comentario = "💔 Nem tente..."
    e = make_embed("💘 Compatibilidade Amorosa", cor=0xFF1493)
    e.description = f"**{user1.display_name}** 💕 **{user2.display_name}**\n\n{barra}\n**{porcento}%** — {comentario}"
    await ctx.send(embed=e)


@bot.command(name="pp")
async def pp(ctx, member: discord.Member = None):
    member  = member or ctx.author
    tamanho = random.randint(0, 30)
    pp_str  = "8" + "=" * tamanho + "D"
    e = make_embed("📏 Medidor Científico", cor=COR_FUN, thumbnail=member.display_avatar.url)
    e.description = f"O PP de **{member.display_name}** mede:\n```{pp_str}```\n**{tamanho} cm** 🔬"
    e.set_footer(text="Medição 100% científica | não nos responsabilizamos")
    await ctx.send(embed=e)


@bot.command(name="abraco", aliases=["hug"])
async def abraco(ctx, member: discord.Member):
    e = make_embed("🤗 Abraço!", f"**{ctx.author.display_name}** deu um abraço em **{member.display_name}**! 💖", COR_FUN)
    await ctx.send(embed=e)


@bot.command(name="tapa", aliases=["slap"])
async def tapa(ctx, member: discord.Member):
    e = make_embed("👋 TAPA!", f"**{ctx.author.display_name}** deu um tapa em **{member.display_name}**! 😤", COR_ERRO)
    await ctx.send(embed=e)


@bot.command(name="rps", aliases=["pedra"])
async def rps(ctx, escolha: str):
    opcoes  = ["pedra", "papel", "tesoura"]
    emojis  = {"pedra": "🪨", "papel": "📄", "tesoura": "✂️"}
    escolha = escolha.lower()
    if escolha not in opcoes:
        return await ctx.send(embed=make_embed("❌ Inválido", "Escolha: `pedra`, `papel` ou `tesoura`", COR_ERRO))
    bot_escolha = random.choice(opcoes)
    if escolha == bot_escolha:
        resultado, cor = "🤝 Empate!", COR_AVISO
    elif (escolha == "pedra" and bot_escolha == "tesoura") or \
         (escolha == "papel" and bot_escolha == "pedra") or \
         (escolha == "tesoura" and bot_escolha == "papel"):
        resultado, cor = "🏆 Você venceu!", COR_SUCESSO
    else:
        resultado, cor = "💀 Você perdeu!", COR_ERRO
    e = make_embed(f"🎮 Pedra, Papel, Tesoura — {resultado}", cor=cor)
    e.add_field(name="Você", value=f"{emojis[escolha]} {escolha.title()}", inline=True)
    e.add_field(name="Bot", value=f"{emojis[bot_escolha]} {bot_escolha.title()}", inline=True)
    await ctx.send(embed=e)


@bot.command(name="random", aliases=["aleatorio"])
async def random_num(ctx, minimo: int = 1, maximo: int = 100):
    if minimo >= maximo:
        return await ctx.send(embed=make_embed("❌ Inválido", "O mínimo precisa ser menor que o máximo.", COR_ERRO))
    resultado = random.randint(minimo, maximo)
    e = make_embed("🎰 Número Aleatório", f"Entre `{minimo}` e `{maximo}`:\n# {resultado}", COR_PRINCIPAL)
    await ctx.send(embed=e)

# ══════════════════════════════════════════
#  HELP
# ══════════════════════════════════════════
@bot.command(name="help", aliases=["ajuda", "comandos"])
async def help_cmd(ctx):
    e = discord.Embed(
        title="📖 Comandos do Bot",
        description=f"Prefixo: `{PREFIX}` — Use `{PREFIX}<comando>`",
        color=COR_PRINCIPAL,
        timestamp=datetime.datetime.utcnow()
    )
    e.set_thumbnail(url=bot.user.display_avatar.url)
    e.add_field(
        name="🛡️ Moderação",
        value="`ban` `unban` `banlist` `kick`\n`timeout` `untimeout` `warn`\n`clear` `lock` `unlock` `slowmode`\n`nick` `addrole` `removerole`",
        inline=False
    )
    e.add_field(
        name="📋 Embeds & Anúncios",
        value="`embed` `anuncio` `say`",
        inline=False
    )
    e.add_field(
        name="🔍 Utilidades",
        value="`ping` `userinfo` `serverinfo`\n`avatar` `banner` `roleinfo` `botinfo`",
        inline=False
    )
    e.add_field(
        name="🎉 Diversão",
        value="`lorota` `dado` `8ball` `coinflip`\n`ship` `pp` `abraco` `tapa` `rps` `random`",
        inline=False
    )
    e.set_footer(text=f"Bot criado com discord.py | {len(bot.commands)} comandos")
    await ctx.send(embed=e)

# ══════════════════════════════════════════
#  START
# ══════════════════════════════════════════
bot.run(TOKEN)
