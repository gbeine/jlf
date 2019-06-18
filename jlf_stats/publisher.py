"""
Jira Stats Publisher.

Takes a report config detailing which reports to publish and
a Jira Wrapper which provides the data for the reports
"""

import os
import pandas as pd
import logging

from xlsxwriter.utility import xl_rowcol_to_cell

_state_default_colours = ['#8dd3c7',
                          '#ffffb3',
                          '#bebada',
                          '#fb8072',
                          '#80b1d3',
                          '#fdb462',
                          '#b3de69',
                          '#fccde5',
                          '#d9d9d9',
                          '#bc80bd',
                          '#ccebc5',
                          '#ffed6f']


def publish(config, jira, from_date, to_date):

    writer = None

    if config['format'] == 'xlsx':
        excel_basename = config['name']
        excel_filename = os.path.join(config['location'],
                                      excel_basename + '.xlsx')
        writer = pd.ExcelWriter(excel_filename, engine='xlsxwriter')

    for report in config['reports']:

        data = None

        if report['metric'] == 'history':
            data = jira.history(from_date, to_date)

        if data is not None:
            if isinstance(writer, pd.ExcelWriter):

                sheet_name = []

                sheet_name.append(report['metric'])

                worksheet_name = worksheet_title('-'.join(sheet_name))

                data.to_excel(writer, worksheet_name)


                if report['metric'] == 'history':
                    if 'format' in report:
                        formats = report['format']
                    else:
                        formats = format_states(config['states'])
                    workbook = writer.book
                    sheets = [sheet for sheet in workbook.worksheets() if sheet.name[-7:] == 'history']
                    # Do the colouring in
                    for sheet in sheets:
                        colour_cfd(workbook, sheet, data, formats)

    if isinstance(writer, pd.ExcelWriter):
        writer.save()


def format_states(states):

    formats = {}

    for index, state in enumerate(states):
        try:
            formats[state] = {'color': _state_default_colours[index]}
        except IndexError:
            rebased_index = index
            while rebased_index >= len(_state_default_colours):
                rebased_index = rebased_index - len(_state_default_colours)
            formats[state] = {'color': _state_default_colours[rebased_index]}

    return formats


def colour_cfd(workbook, worksheet, data, formats):

    workbook_formats = {}

    for i, row in enumerate(data.values):
        for j, cell in enumerate(row):

            try:
                color = formats[cell]['color']
                if color not in workbook_formats:

                    new_format = workbook.add_format()
                    new_format.set_bg_color(color)
                    workbook_formats[color] = new_format

                cell_ref = xl_rowcol_to_cell(i+1, j+1)
                worksheet.write(cell_ref, cell, workbook_formats[color])
            except KeyError:
                pass


def worksheet_title(full_title):
    """
    Shorten the title if it is not going to fit on the worksheet
    """

    _MAX_LENGTH = 30

    excess = len(full_title) - _MAX_LENGTH

    if excess > 0:
        parts = full_title.split('-')
        shorten_by = excess / len(parts)

        short_title = full_title

        while len(short_title) > _MAX_LENGTH:
            longest = max(parts[:-1], key=len)
            if len(longest) > shorten_by:
                parts[parts.index(longest)] = longest[:-shorten_by]

                short_title = ''
                for part in parts[:-1]:
                    short_title += part
                    short_title += '-'

                short_title += parts[-1]
            else:
                short_title = short_title[:_MAX_LENGTH-len(parts[-1])] + parts[-1]

        return short_title

    else:
        return full_title
