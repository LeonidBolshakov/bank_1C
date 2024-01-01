''' Программа преобразования банковской выписки в формате 1-С
    А именно, если в секции документа есть непустые значения даты списания и даты поступления средств,
    то значение даты списания устанавливается пустым
'''

from tkinter import filedialog
from os.path import split as path_split
from os import getcwd
import const as c

#   Ключом строки называются первые символы строки.
#   Функция проверяет явлется ли передаваемый параметр ключом строки.
#   Параметры:
#       1. Строка, проверяемая на наличие ключа.
#       2. Проверяемый ключ
#   Результат.
#       1. True  - Если праметр является ключом строки
#       2. False - Если праметр не является ключом строки
def is_row_key(line: str, key: str) -> bool:
    return line.startswith(key)

#   Функция проверяет содержит ли строка информацию о
#   списании или поступлении средств.
#   Параметры.
#       1. Строка.
#       2. Ключ, определяющий списание или поступление средств.
#   Результат.
#       1. True  - Строка содержит информацию о списании или поступлении средств
#       2. False - В противном случае

def there_is_movement_funds(line: str, key: str):
    if is_row_key(line, key):
        return True if line.strip() != key else False
    return False

#   Функция чтения секции банковской выписки
#   Параметры.
#       1. Список строк банковой выписки.
#       2. Индекс строки текущий (подлежащей обработке) строки банковской выписки.
#   Результат.
#       1. Список строк очередной секции банковской выписки.
def read_section(bank_statement_input: list[str], pointer_in_input: int) -> list[str]:
    result = []
    while True:
        try:
            line = bank_statement_input[pointer_in_input]
        except IndexError:
            return result
        result.append(line)
        pointer_in_input += 1
        if is_row_key(line, c.НАЧАЛО_СЕКЦИИ):
            if len(result) != 1:
                result.pop()
                return result
        if is_row_key(line,c.КОНЕЦ_СЕКЦИИ):
            return result

#   Функция опрелдеяет: является ли секция информацией о банковском документе.
#   Параметры.
#       1. Список строк секции
#   Результат.
#       1.  True    - Если секция - банковский документ.
#           False   - Если секция не является банкоским документом.
def is_section_document (section: list[str]) -> bool:
    return True if is_row_key(section[0], c.НАЧАЛО_СЕКЦИИ) else False

#   Функция сохраняет секцию в выходном списке
#   Параметры.
#       1. Список строк выходного документа.
#       2. Список строк секции.
#   Результат.
#       1. None.
def save_output(bank_statement_output: list[str], section: list[str]) -> None:
    bank_statement_output.extend(section)

#   Функция контролирует секцию документа на одновременное наличие
#   признаков наличия поступления и списания средств.
#   При одновременном наличии, один из признаков отменяется.
#   Признак наличия финансовой операции.
#       1. Наличие строки ДатаХХХХХ=Нечто
#       2. Нечто - не пусто.
#   Параметр.
#       1. Список строк секции.
#   Результат.
#       1. Список строк секции.
def check_date_section(bank_section: list[str]) -> None:
    data_received = False
    data_written_off = False
    for line in bank_section:
        if there_is_movement_funds(line, c.ПРИЗНАК_ПОСТУПЛЕНИЯ):
            data_received = True
        if there_is_movement_funds(line, c.ПРИЗНАК_СПИСАНИЯ):
            data_written_off = True
    resultat = []
    for line in bank_section:
        if is_row_key(line, c.ПРИЗНАК_СПИСАНИЯ):
            if data_received and data_written_off:
                line = c.ПРИЗНАК_СПИСАНИЯ + '\n'
        resultat.append(line)
    return resultat

#   Функция формируюет полные пути входного и выходного файлов банковской выписки
#   Параметры.
#       Отсутсвуют.
#   Результат.
#       1. Картеж (полный путь входного файла, полный путь выходного файла)
def get_filenames():
    filepath_input = filedialog.askopenfilename(initialdir= getcwd(),
                                    title= 'Выберите файл, пришедший из банка',
                                    filetypes = [('текстовый файл', '*.txt')])
    if filepath_input == '':
        exit(1)

    filepath_output = path_split(filepath_input)[0] + '\\' + c.ИМЯ_ФАЙЛА
    return (filepath_input, filepath_output)

#   Главная функция программы.
#   Читает и обрабатывет входной файл, формирует выходной файл.
def main():
    filepath_input, filepath_output = get_filenames()
    with open(filepath_input) as input_file:
        bank_statement_input = input_file.readlines()
        pointer_in_input = 0
        bank_statement_output = []
        while True:
            section = read_section(bank_statement_input, pointer_in_input)
            if len(section) == 0:
                break
            else:
                pointer_in_input += len(section)
            if is_section_document(section):
                section = check_date_section(section)
            save_output(bank_statement_output, section)

    with open(filepath_output, 'w') as output_file:
        for line in bank_statement_output:
            output_file.writelines(line)

if __name__ == '__main__':
    main()
