# """Display Base

# """
# from datetime import datetime
# import random

# import arrow
# from rich.console import Console
# from rich.table import Table

# from pignus import misc
# from pignus.utils import date_utils


# class DisplayBase:

#     def __init__(self, settings, args):
#         self.last_color = None
#         self.console = Console()
#         self.settings = settings
#         self.args = args
#         self.table = Table(show_header=False, header_style="bold magenta")
#         self.db_started = datetime(2021, 12, 6)

#     def bold(self, text):
#         """Make a given value render bold to the console."""
#         return "[bold]%s[/bold]" % str(text)

#     def str_format(self, raw) -> str:
#         """Take any input and format it for console display."""
#         if isinstance(raw, list):
#             ret = ", ".join(raw)
#         else:
#             ret = raw
#         return ret

#     def set_image_repository_colors(self, images):
#         self.image_repo_colors = {}
#         last_color = None
#         for image in images:
#             image_repo = misc.parse_image_dir(image.name)
#             repo_base = image_repo["repo_base"]
#             if repo_base in self.image_repo_colors:
#                 continue
#             else:
#                 self.image_repo_colors[repo_base] = self.random_color(not_color=last_color)
#                 last_color = self.image_repo_colors[repo_base]
#         return True

#     def render_image(self, image_name: str) -> str:
#         image_repo = misc.parse_image_dir(image_name)
#         color = self.image_repo_colors[image_repo["repo_base"]]
#         if image_repo["repo_base"] == image_repo["sub_image"]:
#             ret = image_name
#         else:
#             ret = "[%s]%s/[/%s]%s" % (color, image_repo["repo_base"], color, image_repo["sub_image"])
#         return ret

#     def render_field(
#         self, anything, color: str = None, bold: bool = False, underline: bool = False
#     ) -> str:
#         """Renders a string for console display."""
#         pad_outs = []
#         if isinstance(anything, list):
#             print_str = ", ".join(anything)
#         else:
#             print_str = str(anything)
#         if color:
#             pad_outs.append(color)
#         if bold:
#             pad_outs.append("bold")
#         if underline:
#             pad_outs.append("underline")

#         if pad_outs:
#             pad_outs_str = " ".join(pad_outs)
#             print_str = "[%s]%s[/%s]" % (pad_outs_str, print_str, pad_outs_str)
#         return str(print_str)

#     def rf(
#         self, anything, color: str = None, bold: bool = False, underline: bool = False
#     ) -> str:
#         """Alias for render field."""
#         return self.render_field(anything, color, bold, underline)

#     def render_date(self, the_arrow, more: bool = False) -> str:
#         """Render a date for console display."""
#         if not the_arrow:
#             return ""
#         if not isinstance(the_arrow, arrow.arrow.Arrow):
#             return ""
#         # @todo: Set this to user local time
#         mtn = arrow.now("America/Denver").tzinfo
#         the_arrow.astimezone(mtn)

#         db_start_date = arrow.get(2021, 10, 21)

#         if the_arrow < db_start_date:
#             ret = "Since records began (Oct 10th 2021)"
#         else:
#             ret = the_arrow.humanize()
#         if more:
#             fmt = "YYYY-MM-DD HH:mm:ss"
#             ret += " (%s)" % the_arrow.format(fmt)

#         return ret

#     def render_date_live(self, the_arrow, more: bool = False) -> str:
#         """Render a date for console display."""
#         if not the_arrow:
#             return ""
#         if not isinstance(the_arrow, arrow.arrow.Arrow):
#             return ""
#         mtn = arrow.now("America/Denver").tzinfo
#         the_arrow.astimezone(mtn)

#         if the_arrow > arrow.get(date_utils.now()).shift(hours=-1):
#             return "[green bold]LIVE[/green bold]"
#         return the_arrow.humanize()

#     def random_color(self, not_color: str = None) -> str:
#         """Pick a "random color", if supplied a "not_color" that color will be removed from being
#         an option.
#         """
#         colors = [
#             "bright_blue",
#             "yellow",
#             "bright_yellow",
#             "cyan",
#             "purple",
#             "magenta",
#             "deep_pink3",
#             "plum3",
#             "light_salmon1",
#             "deep_sky_blue4",
#         ]
#         if not_color and not_color in colors:
#             colors.remove(not_color)
#         chosen = colors[random.randint(0, len(colors) - 1)]
#         return chosen

#     def add_row(self, *row_args, pad: int = 0) -> True:
#         table_data = []
#         for cell in row_args:
#             if cell:
#                 cell = str(cell)
#             table_data.append(cell)

#         # Pad out cells to the left
#         if pad > 0:
#             i = 1
#             while i <= pad:
#                 table_data.insert(i - 1, "")
#                 i += 1

#         self.table.add_row(*table_data)
#         return True

#     def add_rows(self, rows: list):
#         for row in rows:
#             self.add_row(row)
#         return True

#     def render_header(self, header) -> str:
#         return "[bold]%s[/bold]" % (header)

#     def show(self, level: int, field=None) -> bool:
#         if field and self.sel_field(field):
#             return True
#         if self.field_display >= level:
#             return True
#         return False

#     def sel_field(self, field):
#         if field in self.fields:
#             return True
#         else:
#             False

#     def set_display_scale(self):
#         """Determine how much of the Images details to show."""
#         auto_scale_image_details = True
#         if auto_scale_image_details:
#             if len(self.images) > 10:
#                 self.field_display = 1

# # End File: automox/pignus/src/pignus/display/display_base.py
