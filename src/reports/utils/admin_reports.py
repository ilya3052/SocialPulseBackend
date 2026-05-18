import os
import subprocess
from datetime import datetime

import xlsxwriter
from xlsxwriter import Workbook

from social_pulse.settings import MEDIA_ROOT, MEDIA_URL


def get_styles(workbook: Workbook):
    title = workbook.add_format()
    title.set_font_name('Times New Roman')
    title.set_font_size(14)
    title.set_bold()
    title.set_align('center')
    title.set_align('vcenter')
    title.set_bg_color('#F8F9FA')
    title.set_border()
    title.set_border_color('#BFBFBF')

    value = workbook.add_format()
    value.set_font_name('Times New Roman')
    value.set_font_size(14)
    value.set_align('center')
    value.set_align('vcenter')
    value.set_bg_color('#F8F9FA')
    value.set_border()
    value.set_border_color('#BFBFBF')

    high_load = workbook.add_format()
    high_load.set_font_name('Times New Roman')
    high_load.set_font_size(14)
    high_load.set_align('center')
    high_load.set_align('vcenter')
    high_load.set_font_color('red')
    high_load.set_bg_color('#F8F9FA')
    high_load.set_border()
    high_load.set_border_color('#BFBFBF')
    high_load.set_num_format("0%")

    medium_load = workbook.add_format()
    medium_load.set_font_name('Times New Roman')
    medium_load.set_font_size(14)
    medium_load.set_align('center')
    medium_load.set_align('vcenter')
    medium_load.set_font_color('yellow')
    medium_load.set_bg_color('#F8F9FA')
    medium_load.set_border()
    medium_load.set_border_color('#BFBFBF')
    medium_load.set_num_format("0%")

    low_load = workbook.add_format()
    low_load.set_font_name('Times New Roman')
    low_load.set_font_size(14)
    low_load.set_align('center')
    low_load.set_align('vcenter')
    low_load.set_font_color('green')
    low_load.set_bg_color('#F8F9FA')
    low_load.set_border()
    low_load.set_border_color('#BFBFBF')
    low_load.set_num_format("0%")

    percentage = workbook.add_format()
    percentage.set_font_name('Times New Roman')
    percentage.set_font_size(14)
    percentage.set_align('center')
    percentage.set_align('vcenter')
    percentage.set_num_format("0%")

    return title, value, high_load, medium_load, low_load, percentage


def mark_zone(workbook, worksheet):
    top_border = workbook.add_format({'top': 1, 'top_color': '#BFBFBF'})
    bottom_border = workbook.add_format({'bottom': 1, 'bottom_color': '#BFBFBF'})
    left_border = workbook.add_format({'left': 1, 'left_color': '#BFBFBF'})
    right_border = workbook.add_format({'right': 1, 'right_color': '#BFBFBF'})

    top_left = workbook.add_format({'top': 1, 'left': 1, 'top_color': '#BFBFBF', 'left_color': '#BFBFBF'})  # B1
    top_right = workbook.add_format({'top': 1, 'right': 1, 'top_color': '#BFBFBF', 'right_color': '#BFBFBF'})  # L1
    bottom_left = workbook.add_format(
        {'bottom': 1, 'left': 1, 'bottom_color': '#BFBFBF', 'left_color': '#BFBFBF'})  # B38
    bottom_right = workbook.add_format(
        {'bottom': 1, 'right': 1, 'bottom_color': '#BFBFBF', 'right_color': '#BFBFBF'})  # L38

    for col in range(2, 9):  # от C до K (индексы 2-8)
        worksheet.write(0, col, '', top_border)

    for col in range(2, 9):  # от C до K
        worksheet.write(35, col, '', bottom_border)

    for row in range(1, 35):  # от строки 2 до 37
        worksheet.write(row, 1, '', left_border)

    for row in range(1, 35):  # от строки 2 до 37
        worksheet.write(row, 9, '', right_border)

    worksheet.write(0, 1, '', top_left)  # B1
    worksheet.write(0, 9, '', top_right)  # L1
    worksheet.write(35, 1, '', bottom_left)  # B38
    worksheet.write(35, 9, '', bottom_right)  # L38

    worksheet.set_column(0, 0, 5)


def insert_header(report_sheet, title):
    report_sheet.merge_range('D1:H1', 'Сводный отчет администратора', title)
    report_sheet.merge_range('D3:H3', f'Дата формирования: {datetime.now().strftime('%d.%m.%Y')}', title)
    report_sheet.merge_range('E5:G5', 'Группы', title)


def insert_group_count(report_sheet, data, title, value):
    report_sheet.merge_range('B11:E11', 'Всего групп подключено', title)
    report_sheet.merge_range('B12:E14', sum(data.values()), value)


def insert_pie(workbook: Workbook, data_sheet, report_sheet, data, percentage_format):
    chart_pie = build_pie(workbook, data_sheet, data, percentage_format)
    report_sheet.insert_chart('G7', chart_pie)


def build_pie(workbook: Workbook, data_sheet, data, format):
    vk, tg = data.values()
    total = tg + vk

    data_sheet.write('A1', 'TG')
    data_sheet.write('B1', 'ВК')

    data_sheet.write_number('A2', tg)
    data_sheet.write_number('B2', vk)
    data_sheet.write_number('C2', total)

    vk_percentage = int(vk / total) if total else 0
    tg_percentage = int(tg / total) if total else 0

    data_sheet.write_number('A3', vk_percentage, format)
    data_sheet.write_number('B3', tg_percentage, format)

    pie_chart = workbook.add_chart({"type": "pie"})
    pie_chart.add_series({
        'categories': '=Данные!$A$1:$B$1',
        'values': '=Данные!$A$2:$B$2',
        'data_labels': {
            'percentage': True,
            'font': {
                'color': 'white',
                'size': 11
            }
        },
        'points': [
            {'fill': {'color': '#156082'}},  # Цвет для TG (замените на нужный)
            {'fill': {'color': '#8599AA'}},  # Цвет для BK (замените на нужный)
        ]
    })
    pie_chart.set_legend({"position": 'top'})

    pie_chart.set_size({'width': 256, 'height': 250})
    return pie_chart


def insert_service_accounts(report_sheet, data, title, value):
    vk, tg = data.values()

    report_sheet.merge_range('B20:J20', 'Сервисные аккаунты', title)

    report_sheet.merge_range('B22:E22', 'ВК подключено', title)
    report_sheet.merge_range('G22:J22', 'ТГ подключено', title)

    report_sheet.merge_range('B23:E24', vk, value)
    report_sheet.merge_range('G23:J24', tg, value)


def insert_service_account_loading(report_sheet, account_info, groups_info, title, value, high_load, medium_load,
                                   low_load):
    _min = account_info.get('min')
    _max = account_info.get('max')

    vk, tg = groups_info.values()
    total = vk + tg

    min_percentage = int(_min.get('count') / total) if total else 0
    max_percentage = int(_max.get('count') / total) if total else 0

    if min_percentage < 0.3:
        min_style = low_load
    elif 0.3 <= min_percentage < 0.7:
        min_style = medium_load
    else:
        min_style = high_load

    if max_percentage < 0.3:
        max_style = low_load
    elif 0.3 <= max_percentage < 0.7:
        max_style = medium_load
    else:
        max_style = high_load

    report_sheet.merge_range('B29:J29', 'Нагрузка сервисных аккаунтов', title)

    report_sheet.merge_range('B31:E31', 'Минимальная нагрузка', title)
    report_sheet.merge_range('G31:J31', 'Максимальная нагрузка', title)
    report_sheet.merge_range('B32:D33', _min.get('name'), value)
    report_sheet.merge_range('G32:I33', _max.get('name'), value)
    report_sheet.merge_range('E32:E33', min_percentage, min_style)
    report_sheet.merge_range('J32:J33', max_percentage, max_style)
    report_sheet.merge_range('B34:E34', f'{_min.get('count')} групп из {total} подключенных', value)
    report_sheet.merge_range('G34:J34', f'{_max.get('count')} групп из {total} подключенных', value)


def generate_admin_report_excel(data):
    filename = f"admin_report_{datetime.now().strftime('%d.%m.%Y_%H%M%S')}.xlsx"
    xlsx_path = os.path.join(MEDIA_ROOT, 'reports', 'xlsx', 'admin')
    os.makedirs(xlsx_path, exist_ok=True)
    filepath = os.path.join(xlsx_path, filename)
    relative_path = os.path.join(MEDIA_URL, 'reports', 'xlsx', filename).replace('\\', '/')

    workbook = xlsxwriter.Workbook(filepath)

    report_sheet = workbook.add_worksheet('Отчет')
    report_sheet.set_default_row(18.75)
    data_sheet = workbook.add_worksheet('Данные')
    data_sheet.hide()

    title, value, high_load, medium_load, low_load, percentage_format = get_styles(workbook)

    group_info = data.get('group_aggregated_info')
    account_info = data.get('service_account_aggregated_info')
    account_load_info = data.get('service_account_loading')

    mark_zone(workbook, report_sheet)
    insert_header(report_sheet, title)
    insert_group_count(report_sheet, group_info, title, value)
    insert_pie(workbook, data_sheet, report_sheet, account_info, percentage_format)
    insert_service_accounts(report_sheet, account_info, title, value)
    insert_service_account_loading(report_sheet, account_load_info, group_info, title, value, high_load, medium_load,
                                   low_load)

    workbook.close()
    return filepath, relative_path


def generate_admin_report_pdf(file_path):
    out_dir = os.path.join(MEDIA_ROOT, 'reports', 'pdf', 'admin')
    os.makedirs(out_dir, exist_ok=True)

    command_convert = [
        'soffice',
        '--headless',  # Режим без графического интерфейса
        '--convert-to', 'pdf:calc_pdf_Export:Zoom=100',  # Формат на выходе
        '--outdir', out_dir,  # Папка для сохранения
        file_path
    ]
    base_name = os.path.splitext(os.path.basename(file_path))[0]  # имя без расширения
    output_path = os.path.join(out_dir, f"{base_name}.pdf")
    relative_path = os.path.join(MEDIA_URL, os.path.relpath(output_path, MEDIA_ROOT)).replace('\\', '/')

    subprocess.run(command_convert, capture_output=True, text=True, check=True)
    os.remove(file_path)
    return output_path, relative_path
