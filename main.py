import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')

@bot.event
async def on_message_delete(message):
    embed = discord.Embed(
        title="Message Supprimé",
        description=f"Un message a été supprimé dans {message.channel.mention}.",
        color=discord.Color.blurple()
    )
    avatar_url = message.author.avatar_url
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="**Auteur du Message:**", value=message.author.mention)
    embed.add_field(name="**Contenu du Message Supprimé:**", value=message.content or "Aucun contenu")
    embed.set_footer(text=f"Message ID: {message.id}")

    log_channel = discord.utils.get(message.guild.text_channels, name="log-message")
    if log_channel:
        await log_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        embed = discord.Embed(
            title="Message Modifié",
            description=f"Un message a été modifié dans {before.channel.mention}.",
            color=discord.Color.blue()
        )
        avatar_url = before.author.avatar_url
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text=f"Message ID: {before.id}")
        embed.add_field(name="**Auteur du Message**", value=before.author.mention, inline=False)
        embed.add_field(name="**Ancien Message:**", value=before.content or "Aucun contenu", inline=False)
        embed.add_field(name="**Nouveau Message:**", value=after.content or "Aucun contenu", inline=False)
        log_channel = discord.utils.get(before.guild.text_channels, name="log-message")
        if log_channel:
            await log_channel.send(embed=embed)

@bot.event
async def on_member_ban(guild, user):
    audit_log_entries = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
    ban_entry = audit_log_entries[0]

    embed = discord.Embed(
        title="Membre Banni",
        description=f"Un nouveau bannissement à eu lieu !",
        color=discord.Color.red()
    )
    avatar_url = user.avatar_url
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="**Membre Banni:**", value=user.mention)
    embed.add_field(name="**Banni Par:**", value=ban_entry.user.mention)
    embed.add_field(name="**Raison:**", value=ban_entry.reason or "Aucune raison spécifiée")
    log_channel = discord.utils.get(guild.text_channels, name="log")
    if log_channel:
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # Récupère les informations sur l'expulsion
    audit_log_entries = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten()
    kick_entry = audit_log_entries[0]
    embed = discord.Embed(
        title="Membre Expulsé",
        description=f"Un nouvelle expulsion à eu lieu !",
        color=discord.Color.orange()
    )
    avatar_url = member.avatar_url
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="**Membre Expulsé:**", value=member.mention)
    embed.add_field(name="**Expulsé Par:**", value=kick_entry.user.mention)
    embed.add_field(name="**Raison:**", value=kick_entry.reason or "Aucune raison spécifiée")
    log_channel = discord.utils.get(member.guild.text_channels, name="log")
    if log_channel:
        await log_channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    added_roles = set(after.roles) - set(before.roles)
    
    if added_roles:
        role = added_roles.pop()

        embed = discord.Embed(
            title="Rôle Ajouté",
            description=f"**Joueur Modifié:** {after.mention}\n"
                        f"**Rôle Ajouté:** {role.mention}\n"
                        f"**Modifié Par:** {after.guild.me.mention}",
            color=discord.Color.green()
        )
        log_channel = discord.utils.get(after.guild.text_channels, name="log")
        if log_channel:
            await log_channel.send(embed=embed)

bot.run('YOUR_TOKEN_HERE')