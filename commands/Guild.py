from discord import app_commands
import sys

sys.path.insert(1, sys.path[0].replace("command", ""))
from utils import Config

guild_group = app_commands.Group(name="guild", description="Guild management commands")
Config.client.tree.add_command(guild_group)