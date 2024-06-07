from discord import Interaction
def load_patch(interaction, logger):
    Interaction.approve = interaction.approve
    Interaction.deny = interaction.deny
    logger.info("loaded interaction patch")