"""Dialog modules for VPN Manager application."""

from .sudo_dialog import SudoPasswordDialog
from .config_dialog import ConfigureDialog
from .edit_dialog import EditDialog

__all__ = ['SudoPasswordDialog', 'ConfigureDialog', 'EditDialog']
