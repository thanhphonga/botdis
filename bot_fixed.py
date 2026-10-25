import os
import asyncio
import discord
from discord.ext import commands
from discord import SelectOption

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

BANNER_URL = "https://auto.creavite.co/api/out/j5OBb4qMpFSIss90mc_standard.gif"
TICKET_CATEGORY_ID = 1304102405507514417


class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Đóng Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_button",
    )
    async def close_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "Đã đóng ticket!", ephemeral=True
        )
        await asyncio.sleep(3)
        if interaction.channel is not None:
            await interaction.channel.delete()


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Chọn loại hỗ trợ",
        options=[
            SelectOption(
                label="Nạp thẻ",
                value="nap_the",
                description="Hỗ trợ về nạp thẻ",
            ),
            SelectOption(
                label="Hỗ trợ khiếu nại",
                value="support",
                description="Hỗ trợ khiếu nại",
            ),
            SelectOption(
                label="Hỗ trợ member",
                value="member",
                description="Hỗ trợ cho member",
            ),
        ],
        min_values=1,
        max_values=1,
        custom_id="ticket_select",
    )
    async def select_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh này chỉ dùng được trong máy chủ Discord.",
                ephemeral=True,
            )
            return

        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "Không tìm thấy category ticket. Hãy kiểm tra TICKET_CATEGORY_ID.",
                ephemeral=True,
            )
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
        }
        if bot.user is not None:
            overwrites[bot.user] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )

        try:
            ticket_channel = await category.create_text_channel(
                name=f"ticket-{interaction.user.name}".lower().replace(" ", "-")[:90],
                overwrites=overwrites,
            )
            await interaction.response.send_message(
                f"🎫 Ticket của bạn đã được tạo tại {ticket_channel.mention}!",
                ephemeral=True,
            )

            embed = discord.Embed(
                title="🎟 Ticket Hỗ Trợ",
                description=(
                    f"Chào {interaction.user.mention}, vui lòng đợi hỗ trợ "
                    "từ đội ngũ của chúng tôi."
                ),
                color=discord.Color.blue(),
            )
            embed.set_image(url=BANNER_URL)
            await ticket_channel.send(embed=embed, view=CloseButton())
        except discord.HTTPException as exc:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Không thể tạo ticket. Kiểm tra quyền của bot và category.",
                    ephemeral=True,
                )
            print(f"Lỗi tạo ticket: {exc}")


@bot.event
async def on_ready():
    # Register persistent views once per process, not on every reconnect.
    if not getattr(bot, "_persistent_views_registered", False):
        bot.add_view(TicketView())
        bot.add_view(CloseButton())
        bot._persistent_views_registered = True
    print(f"Bot đã sẵn sàng! Đang chạy với tên: {bot.user}")


@bot.command()
async def ticket(ctx: commands.Context):
    embed = discord.Embed(
        title="📩 Hỗ trợ Ticket",
        description="Vui lòng chọn loại hỗ trợ bên dưới để mở ticket:",
        color=discord.Color.green(),
    )
    embed.set_image(url=BANNER_URL)
    await ctx.send(embed=embed, view=TicketView())


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Lỗi lệnh: {error}")
    await ctx.send("❌ Có lỗi khi chạy lệnh. Hãy kiểm tra log của bot.")


token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError(
        "Thiếu biến môi trường DISCORD_TOKEN. Hãy đặt token trong phần Environment Variables."
    )

bot.run(token)
