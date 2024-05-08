import discord
from discord import app_commands
from discord.ext import commands
import json
import os


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Commandes trouvées: {len(synced)}")
    except Exception as e:
        print(e)

@bot.event
async def on_message_delete(message):
    embed = discord.Embed(
        title="Message Supprimé",
        description=f"Un message a été supprimé dans {message.channel.mention}.",
        color=discord.Color.red()
    )
    embed.add_field(name="**Auteur du Message:**", value=message.author.mention)
    embed.add_field(name="**Contenu du Message Supprimé:**", value=message.content or "Aucun contenu", inline=False)
    embed.set_footer(text=f"Message ID: {message.id}")

    log_channel = discord.utils.get(message.guild.text_channels, name="logs-message")
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
        embed.set_footer(text=f"Message ID: {before.id}")
        embed.add_field(name="**Auteur du Message**", value=before.author.mention, inline=False)
        embed.add_field(name="**Ancien Message:**", value=before.content or "Aucun contenu", inline=False)
        embed.add_field(name="**Nouveau Message:**", value=after.content or "Aucun contenu", inline=False)
        log_channel = discord.utils.get(before.guild.text_channels, name="logs-message")
        if log_channel:
            await log_channel.send(embed=embed)

@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        ban_entry = entry

    embed = discord.Embed(
        title="Membre Banni",
        description=f"Un nouveau bannissement à eu lieu !",
        color=discord.Color.red()
    )
    embed.add_field(name="**Membre Banni:**", value=user.mention, inline=False)
    embed.add_field(name="**Banni Par:**", value=ban_entry.user.mention, inline=False)
    embed.add_field(name="**Raison:**", value=ban_entry.reason or "Aucune raison spécifiée", inline=False)
    created_at = user.created_at.strftime("%d/%m/%Y")
    embed.add_field(name="**Date de création du compte:**", value=created_at, inline=False)
    log_channel = discord.utils.get(guild.text_channels, name="logs-sanctions")
    if log_channel:
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        kick_entry = entry
    embed = discord.Embed(
        title="Membre Expulsé",
        description=f"Un nouvelle expulsion à eu lieu !",
        color=discord.Color.orange()
    )
    embed.add_field(name="**Membre Expulsé:**", value=member.mention, inline=False)
    embed.add_field(name="**Expulsé Par:**", value=kick_entry.user.mention, inline=False)
    embed.add_field(name="**Raison:**", value=kick_entry.reason or "Aucune raison spécifiée", inline=False)
    created_at = member.created_at.strftime("%d/%m/%Y")
    embed.add_field(name="**Date de création du compte:**", value=created_at, inline=False)
    log_channel = discord.utils.get(member.guild.text_channels, name="logs-sanctions")
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
        log_channel = discord.utils.get(after.guild.text_channels, name="💻〡logs-global")
        if log_channel:
            await log_channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="logs-join-leave")
    if welcome_channel:
        embed = discord.Embed(
            title="Un joueur vient de rejoindre le serveur",
            description=f"**Joueur:** {member.name} , {member.mention}\n",
            color=discord.Color.green()
        )
        created_at = member.created_at.strftime("%d/%m/%Y")
        embed.add_field(name="**Date de création du compte:**", value=created_at, inline=False)
        await welcome_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    departure_channel = discord.utils.get(member.guild.text_channels, name="logs-join-leave")
    if departure_channel:
        embed = discord.Embed(
            title="Un joueur vient de quitter le serveur",
            description=f"**Joueur:** {member.name} , {member.mention}\n",
            color=discord.Color.red()
        )
        created_at = member.created_at.strftime("%d/%m/%Y")
        embed.add_field(name="**Date de création du compte:**", value=created_at, inline=False)
        await departure_channel.send(embed=embed)            

@bot.tree.command(name="note", description="Donner une note à un utilisateur")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user = "Utilisateur à noté")
@app_commands.describe(note = "Note")
async def warn(interaction: discord.Interaction, user: discord.User, note: int):
    warn_channel = discord.utils.get(interaction.guild.text_channels, name="⛔〡𝑾𝒂𝒓𝒏𝒔")
    notes = charger_notes()
    user_id = str(user.id)
    noteur = interaction.user.mention
    if user_id in notes:
        notes[user_id]['Notes'].append((note, noteur))
    else:
        notes[user_id] = {'Notes': [(note, noteur)], 'Moyenne': 0}
    
    # Calculer la moyenne des notes
    notes[user_id]['Moyenne'] = sum(n[0] for n in notes[user_id]['Notes']) / len(notes[user_id]['Notes'])
    
    sauvegarder_notes(notes)
    
    await warn_channel.send(f"{interaction.user.mention} a attribué une note de {note} à {user.mention}.")

@bot.tree.command(name="initialisernotes", description="Initialise toutes les notes des joueurs")
@app_commands.checks.has_permissions(manage_messages=True)    
async def initialise(interaction: discord.Interaction):
    members = interaction.guild.members
    notes = {}
    sauvegarder_notes(notes)
    for member in members:
        user_id = str(member.id)
        notes[user_id] = {'Notes': [[20, interaction.user.mention]], 'Moyenne': 20}
    
    sauvegarder_notes(notes)
    await interaction.response.send_message("Toutes les notes des joueurs ont été initialisées avec une note de 20.")

@bot.tree.command(name="moyenne", description="Voir la moyenne d'un utilisateur")
@app_commands.describe(user = "Utilisateur à voir")
async def moyenne(interaction: discord.Interaction, user: discord.User):
    notes = charger_notes()
    user_id = str(user.id)
    if user_id in notes:
        moyenne = notes[user_id]['Moyenne']
        notes_list = '\n'.join([f"({i+1}) **{n[0]}** par {n[1]}" for i, n in enumerate(notes[user_id]['Notes'])])
        embed = discord.Embed(
            title=f"Moyenne de {user.name}",
            description=f"La moyenne de {user.mention} est de {moyenne:.2f}",
            color=discord.Color.green()
        )
        embed.add_field(name="Notes:", value=notes_list, inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"Aucune note n'a été trouvée pour {user.mention}.")

@bot.tree.command(name="clearnote", description="Supprimer toutes les notes d'un utilisateur")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user = "Utilisateur à réinitialiser")
async def clearnote(interaction: discord.Interaction, user: discord.User):
    warn_channel = discord.utils.get(interaction.guild.text_channels, name="⛔〡𝑾𝒂𝒓𝒏𝒔")
    notes = charger_notes()
    user_id = str(user.id)
    if user_id in notes:
        del notes[user_id]
        sauvegarder_notes(notes)
        await interaction.response.send_message(f"Les notes de {user.mention} ont été réinitialisées.")
    else:
        await interaction.response.send_message(f"Aucune note n'a été trouvée pour {user.mention}.")

@bot.tree.command(name="supprnote", description="Supprimer une note d'un utilisateur")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user = "L'utilisateur en question")
@app_commands.describe(position = "Position de la note ( voir via /moyenne )")
async def supprnote(interaction: discord.Interaction,user: discord.User, position: int):
    warn_channel = discord.utils.get(interaction.guild.text_channels, name="⛔〡𝑾𝒂𝒓𝒏𝒔")
    notes = charger_notes()
    user_id = str(user.id)
    if user_id in notes:
        if 0 < position <= len(notes[user_id]['Notes']):
            del notes[user_id]['Notes'][position - 1]
            if len(notes[user_id]['Notes']) > 0:
                notes[user_id]['Moyenne'] = sum(n[0] for n in notes[user_id]['Notes']) / len(notes[user_id]['Notes'])
            else:
                notes[user_id]['Moyenne'] = 0
            sauvegarder_notes(notes)
            await interaction.response.send_message(f"La note à la position {position} de {user.mention} a été supprimée.")
        else:
            await interaction.response.send_message(f"La position de la note doit être comprise entre 1 et {len(notes[user_id]['Notes'])}.")
    else:
        await interaction.response.send_message(f"Aucune note n'a été trouvée pour {user.mention}.")
    
def sauvegarder_notes(data):
    with open('Notes.json', 'w') as file:
        json.dump(data, file)

def charger_notes():
    try:
        with open('Notes.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data

bot.run('MTE3NDg0MTkzNjM1MjM4NzA4Mw.GOiWi_.fCdnXrfnqd44woE-nMVan_eQhm9-otqWzMuDVk')