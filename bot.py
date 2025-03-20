import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import Embed
from discord.ui import TextInput, Modal
import os
from datetime import datetime

# Obter o token do GitHub Secrets
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("Token não encontrado! Verifique se o GitHub Secret 'DISCORD_TOKEN' foi configurado corretamente.")

prefixo = "!"
id_servidor = 123456789012345678  # Id do servidor onde o bot está

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefixo, intents=intents)

# Canal de logs
log_channel_id = 1311421932683661363  # Substitua com o ID do canal de logs

def enviar_log(guild, criado_por, nome_canal, new_channel):
    log_channel = discord.utils.get(guild.text_channels, id=1311421932683661363)
    if log_channel:
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Criar o Embed para a mensagem de log
        embed = Embed(
            title="📋 Novo Canal de Ponto Criado",
            description=f"**Nome do Canal:** {nome_canal}\n**Criado por:** {criado_por.mention}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Data e Hora", value=timestamp)
        
        # Adicionar o ID do canal real ao rodapé
        embed.set_footer(text=f"ID do Canal: {new_channel.id}")

        # Enviar o Embed para o canal de logs
        bot.loop.create_task(log_channel.send(embed=embed))

class CanalModal(Modal):
    def __init__(self):
        super().__init__(title="Nome do Canal")
        self.nome_canal = TextInput(
            label="Qual o nome do canal?", placeholder="Digite o nome do canal", required=True, max_length=100
        )
        self.add_item(self.nome_canal)

    async def on_submit(self, interaction: discord.Interaction):
        nome = self.nome_canal.value
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="═════ •『BATE PONTO』• ═════")

        if category is None:
            await interaction.response.send_message("Não encontrei a categoria mencionada.", ephemeral=True)
            return

        nome_com_prefixo = f"『📑』{nome}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        try:
            new_channel = await guild.create_text_channel(nome_com_prefixo, category=category, overwrites=overwrites)
            mensagem = (
                "QRA:\n\nINICIO:\n\nPAUSA:\n\nCONTINUIDADE:\n\nFINAL:\n\nTOTAL:\n\nPRINTS:\n\n"
                "(OBs: A partir de hoje, É obrigatório marcar início e fim das pausas)"
            )
            await new_channel.send(mensagem)
            await new_channel.send(f"\n{interaction.user.mention}")
            await interaction.response.send_message(f'Canal "{new_channel.name}" criado com sucesso!', ephemeral=True)

            # Enviar log sobre o canal criado
            enviar_log(guild, interaction.user, new_channel.name, new_channel)

        except Exception as e:
            await interaction.response.send_message(f'Ocorreu um erro ao criar o canal: {str(e)}', ephemeral=True)

class CriarCanalView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Criar Bate Ponto", style=discord.ButtonStyle.green, custom_id="criar_canal")
    async def criar_canal_button(self, interaction: discord.Interaction, button: Button):
        modal = CanalModal()
        await interaction.response.send_modal(modal)

@bot.command()
async def canal(ctx):
    embed = Embed(
        title="Criar Bate Ponto",
        description="Para criar seu Bate Ponto clique no botão abaixo.",
        color=discord.Color.blue()
    )
    view = CriarCanalView()
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    bot.add_view(CriarCanalView())  # Garante que a view continue funcionando após reinício
    print(f'{bot.user} está conectado ao Discord!')

bot.run(token)
