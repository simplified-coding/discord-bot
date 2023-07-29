import os
import discord
import datetime, threading
from utils import has_admin
from metrics import prometheus, key
from prometheus_client import Counter

# Constants
GUILD = discord.Object(id=os.environ.get('DISCORD_GUILDID'))

prometheus()
started = Counter('started', '# of times the discord bot has been started')
commandCount = Counter('command_count', '# of commands that have been executed')
commandPing = Counter('command_ping', '# of times the, ping, command has been executed')
commandGetChannelID = Counter('command_channelid', '# of thimes the, get channel id, command has been executed')
commandBulkDelete = Counter('command_bulkdelete', '# of times the, bulk delete, command has been executed')
commandPoll = Counter('command_poll', '# of times the, poll, command has been executed')
commandNoauth = Counter('command_noauth', '# of times a command has been run without the proper autorisation')
commandBadData = Counter('command_baddata', '# of times a command has been run without the proper data')
class DiscordClient(discord.Client):
    # Init
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents) # Init Super
        self.tree = discord.app_commands.CommandTree(self) # Setup command tree

     # Copy global commands to guild
    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)
    
    # On Discord Bot Ready
    async def on_ready(self):
        print(f'Discord Client started as: {self.user}')
        
        # Change Bot Presence
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=os.environ.get('DISCORD_PRESENCE')))

# Setup Bot Intents
bot_intents = discord.Intents.default()

# Setup Discord Client
client = DiscordClient(intents=bot_intents)

# Add Bot Commands
# Ping Command
@client.tree.command(description='Pings the Simplified Coding discord bot.')
async def ping(interaction: discord.Interaction):
    commandCount.inc()
    commandPing.inc()
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)}ms", ephemeral=True)

# Get Channel ID
@client.tree.command(description='Gets the channel ID.')
async def get_channel_id(interaction: discord.Interaction):
    commandCount.inc()
    commandGetChannelID.inc()
    await interaction.response.send_message(f'Channel ID: `{interaction.channel_id}`', ephemeral=True)

# Bulk Delete Command
@client.tree.command(description='[ADMIN] Bulk deletes up to 100 messages.')
@discord.app_commands.describe(message_count='How many messages to delete')
async def bulk_delete(interaction: discord.Interaction, message_count: int):
    commandCount.inc()
    commandBulkDelete.inc()
    if message_count > 100:
        commandBadData.inc()
        await interaction.response.send_message('Bulk delete limit is 100 messages.', ephemeral=True)
    else:
        if has_admin(interaction=interaction):
            await interaction.response.send_message(f'Deleting {message_count} messages.', ephemeral=True)
            await interaction.channel.delete_messages([message async for message in interaction.channel.history(limit=message_count)])
        else:
            commandNoauth.inc()
            await client.get_channel(int(os.environ.get('DISCORD_ADMIN_CHANNELID'))).send(content=f'{interaction.user} tried to run {interaction.command.name} that requires **ADMIN** access, which **he does not have**. **SHAME HIM!**')
            await interaction.response.send_message(f'{interaction.user} does not have admin access!', ephemeral=True)

# Poll Command
@client.tree.command(description='Create a poll')
@discord.app_commands.describe(poll_name='The name of the poll', poll_desc='The poll description', option_a='Option A', option_b='Option B', option_c='Option C', option_d='Option D', option_e='Option E', option_f='Option F')
async def create_poll(interaction: discord.Interaction, poll_name: str, poll_desc: str, option_a: str = None, option_b: str = None, option_c: str = None, option_d: str = None, option_e: str = None, option_f: str = None):
    commandCount.inc()
    commandPoll.inc()

    embed_description = f'{poll_desc}\n\nOptions avainable to vote:\n\n' # Create the embed description

    # Add all of the vote options
    if option_a: embed_description += f':regional_indicator_a: {option_a}\n'
    if option_b: embed_description += f':regional_indicator_b: {option_b}\n'
    if option_c: embed_description += f':regional_indicator_c: {option_c}\n'
    if option_d: embed_description += f':regional_indicator_d: {option_d}\n'
    if option_e: embed_description += f':regional_indicator_e: {option_e}\n'
    if option_f: embed_description += f':regional_indicator_f: {option_f}\n'

    # Create embed and send message
    embed = discord.Embed(title=f'[POLL] {poll_name}', description=embed_description)
    await interaction.response.send_message(embed=embed)
    
    # Gets response message
    response_message = await interaction.original_response()
    
    # Add reactions
    if option_a: await response_message.add_reaction('🇦')
    if option_b: await response_message.add_reaction('🇧')
    if option_c: await response_message.add_reaction('🇨')
    if option_d: await response_message.add_reaction('🇩')
    if option_e: await response_message.add_reaction('🇪')
    if option_f: await response_message.add_reaction('🇫')

# Run Discord Bot
if __name__ == "__main__":
    # Running Discord Bot
    started.inc()
    client.run(os.environ.get('DISCORD_TOKEN'))