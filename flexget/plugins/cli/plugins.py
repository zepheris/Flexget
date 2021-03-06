from __future__ import unicode_literals, division, absolute_import
from builtins import *  # noqa pylint: disable=unused-import, redefined-builtin

import logging

from colorclass.toggles import disable_all_colors
from flexget import options
from flexget.event import event
from flexget.plugin import get_plugins
from flexget.terminal import TerminalTable, TerminalTableError, table_parser, console, colorize

log = logging.getLogger('plugins')


def plugins_summary(manager, options):
    if options.table_type == 'porcelain':
        disable_all_colors()
    header = ['Keyword', 'Phases', 'Flags']
    table_data = [header]
    for plugin in sorted(get_plugins(phase=options.phase, interface=options.interface)):
        if options.builtins and not plugin.builtin:
            continue
        flags = []
        if plugin.instance.__doc__:
            flags.append('doc')
        if plugin.builtin:
            flags.append('builtin')
        if plugin.debug:
            if not options.debug:
                continue
            flags.append('developers')
        handlers = plugin.phase_handlers
        roles = []
        for phase in handlers:
            priority = handlers[phase].priority
            roles.append('{0}({1})'.format(phase, priority))

        name = colorize('green', plugin.name) if 'builtin' in flags else plugin.name
        table_data.append([name, ', '.join(roles), ', '.join(flags)])

    try:
        table = TerminalTable(options.table_type, table_data, wrap_columns=[1, 2])
        console(table.output)
    except TerminalTableError as e:
        console('ERROR: %s' % str(e))
        return
    console(colorize('green', ' Built-in plugins'))


@event('options.register')
def register_parser_arguments():
    parser = options.register_command('plugins', plugins_summary, help='Print registered plugin summaries',
                                      parents=[table_parser])
    parser.add_argument('--group', help='Show plugins belonging to this group')
    parser.add_argument('--phase', help='Show plugins that act on this phase')
    parser.add_argument('--builtins', action='store_true', help='Show just builtin plugins')
