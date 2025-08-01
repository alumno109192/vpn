"""Dialog modules for VPN Manager application."""

from .config_dialog import ConfigureDialog
from .edit_dialog import EditDialog
from .sudo_dialog import SudoPasswordDialog

__all__ = ['SudoPasswordDialog', 'ConfigureDialog', 'EditDialog']
