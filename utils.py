import discord
import os

def has_admin(interaction: discord.Interaction):
    return (not interaction.user.get_role(int(os.environ.get('DISCORD_ADMIN_ROLEID'))) == None)

def calculateTime(start, end):
    return (end - start) * 10**3