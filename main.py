import os
import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ============================================================
# ROLE IDs
# ============================================================

ROLES = {

    # Management
    "management": 1544962832184119386,

    # Levels
    "level_50": 1545279664082255883,
    "level_40": 1545279492912844912,
    "level_30": 1545279359231983646,
    "level_20": 1545279227236974683,
    "level_10": 1545279034680680488,
    "level_5": 1545278882616180746,

    # Special roles
    "divas": 1545546903360512120,
    "monarchs": 1545697705345421313,
    "kitten": 1545546997090750555,
    "artist": 1544962843802345512,
    "imperial_alpha": 1548537294967935078,
    "melodist": 1544962844984872980,
    "moon_beam_maidan": 1545546500933689454,
    "mistic_warden": 1546068438475079730,
    "prettiest_apsara": 1545546815707807774,
    "warriors": 1548530578343600238,
    "over_seers": 1546068303296856134,
    "the_sinister_one": 1546068900695777290,
    "hawties": 1545546654005076059,
    "ivory": 1548537480943247430,
    "infinite_resonance": 1546068248443752478,
    "spotify": 1545521005617881229,
    "scarlet_witch": 1545546442939047956,
    "the_luminaries": 1546068160229285909,
    "snow_princess": 1545546343513325670,
    "spiderman": 1547711437693124732,
    "commander": 1546068384473550908,

    # Support / Admin
    "vc_help": 1546591858145235004,
    "ticket_admin": 1545145899725103144,

    # Managers
    "hangout_manager": 1548241328490414191,
    "gaming_manager": 1548241961104834682,
    "singing_manager": 1548240879804874752,

    # Head Mods
    "head_hangout_mod": 1548226719167807528,
    "head_gaming_mod": 1548226503949418648,
    "head_singing_mod": 1548225761767465000,

    # Mods
    "hangout_mod": 1545047689329115136,
    "gaming_mod": 1545046367137964125,
    "singing_mod": 1544962834767675412,

    # Junior Mods
    "junior_hangout_mod": 1548226826998906920,
    "junior_gaming_mod": 1548226617254354994,
    "junior_singing_mod": 1548226374119063562,
}


# ============================================================
# WHO CAN GIVE WHICH ROLE?
# ============================================================

ROLE_PERMISSIONS = {

    # Management can give all listed roles
    ROLES["management"]: set(ROLES.values()),


    # Hangout Manager
    ROLES["hangout_manager"]: {
        ROLES["head_hangout_mod"],
        ROLES["hangout_mod"],
        ROLES["junior_hangout_mod"],
    },


    # Gaming Manager
    ROLES["gaming_manager"]: {
        ROLES["head_gaming_mod"],
        ROLES["gaming_mod"],
        ROLES["junior_gaming_mod"],
    },


    # Singing Manager
    ROLES["singing_manager"]: {
        ROLES["head_singing_mod"],
        ROLES["singing_mod"],
        ROLES["junior_singing_mod"],
        ROLES["artist"],
        ROLES["melodist"],
        ROLES["spotify"],
    },


    # Head Hangout Mod
    ROLES["head_hangout_mod"]: {
        ROLES["hangout_mod"],
        ROLES["junior_hangout_mod"],
    },


    # Head Gaming Mod
    ROLES["head_gaming_mod"]: {
        ROLES["gaming_mod"],
        ROLES["junior_gaming_mod"],
    },


    # Head Singing Mod
    ROLES["head_singing_mod"]: {
        ROLES["singing_mod"],
        ROLES["junior_singing_mod"],
        ROLES["artist"],
        ROLES["melodist"],
        ROLES["spotify"],
    },


    # Singing Mod
    ROLES["singing_mod"]: {
        ROLES["artist"],
        ROLES["melodist"],
        ROLES["spotify"],
    },
}


# ============================================================
# BOT READY
# ============================================================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Command sync error: {e}")


# ============================================================
# /giverole COMMAND
# ============================================================

@bot.tree.command(
    name="giverole",
    description="Give an authorized role to a member."
)
@app_commands.describe(
    member="The member who should receive the role",
    role="The role you want to give"
)
async def giverole(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    # --------------------------------------------------------
    # Check which authorized roles the command user has
    # --------------------------------------------------------

    user_role_ids = {r.id for r in interaction.user.roles}

    allowed_roles = set()

    for user_role_id in user_role_ids:
        if user_role_id in ROLE_PERMISSIONS:
            allowed_roles.update(
                ROLE_PERMISSIONS[user_role_id]
            )

    # --------------------------------------------------------
    # Check if requested role is authorized
    # --------------------------------------------------------

    if role.id not in allowed_roles:

        await interaction.response.send_message(
            "❌ You are not authorized to give this role.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # Don't allow the bot to give @everyone
    # --------------------------------------------------------

    if role.is_default():

        await interaction.response.send_message(
            "❌ You cannot give the @everyone role.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # Discord role hierarchy check
    # --------------------------------------------------------

    if role >= interaction.guild.me.top_role:

        await interaction.response.send_message(
            "❌ I cannot give this role because my bot role is "
            "not higher than the role I'm trying to give.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # Check if member already has role
    # --------------------------------------------------------

    if role in member.roles:

        await interaction.response.send_message(
            f"ℹ️ {member.mention} already has {role.mention}.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # Give role
    # --------------------------------------------------------

    try:

        await member.add_roles(
            role,
            reason=f"Role given by {interaction.user}"
        )

        await interaction.response.send_message(
            f"✅ Added {role.mention} to {member.mention}."
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Discord rejected the role change. "
            "Check my Manage Roles permission and role hierarchy.",
            ephemeral=True
        )

    except Exception as e:

        print(f"Error giving role: {e}")

        await interaction.response.send_message(
            "❌ Something went wrong while giving the role.",
            ephemeral=True
        )


# ============================================================
# START BOT
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable is missing."
    )

bot.run(TOKEN)
