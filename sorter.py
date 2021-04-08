import eyed3
import os
from pathlib import Path
import argparse


def check_dir_w(dst_dir):
    """Функция проверяет наличие директории и прав на запись в нее"""
    if not os.path.exists(dst_dir):
        print(f"[ERR]: Каталог {dst_dir} не существует")
        writable = False
    else:
        try:
            f_path = os.path.join(dst_dir, 'test')
            f = open(f_path, 'w')
            f.close()
            os.remove(f_path)
            writable = True
        except PermissionError:
            print(f"[ERR]: Отказано в доступе")
            writable = False
    return writable


def create_dir(dst_dir, artist, album):
    """Функция создает директорию вида <директория назначения>/<исполнитель>/<альбом>/"""
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    if not os.path.exists(os.path.join(dst_dir, artist)):
        os.mkdir(os.path.join(dst_dir, artist))
    if not os.path.exists(os.path.join(dst_dir, artist, album)):
        os.mkdir(os.path.join(dst_dir, artist, album))
    return os.path.join(dst_dir, artist, album)


def normalize_name(name):
    """ Функция проверяет наличие в строке символов, запрещенных в именовании файлов и папок """
    forbidden_symbols_win = ("/", "\\", ":", "*", "?", "\"", "<", ">", "|", "+")
    forbidden_symbols_nix = ("/", "\0")
    if os.name == "nt":
        for symbol in forbidden_symbols_win:
            name = name.replace(symbol, "")
    elif os.name == "posix":
        for symbol in forbidden_symbols_nix:
            name = name.replace(symbol, "")
    return name.strip()


def decode(text):
    """Костыль для исправления кодировки. Кодирует из cp1252 в cp1251. Если не сможет, то оставит без изменения"""
    try:
        return text.encode("cp1252").decode("cp1251")
    except UnicodeEncodeError:
        return text


try:
    # Парсим командную строку
    # ----------------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Sorting music files')
    parser.add_argument(
        '-s',
        '--src_dir',
        type=str,
        default=os.getcwd(),
        help='TEXT  Source directory'
    )
    parser.add_argument(
        '-d',
        '--dst_dir',
        type=str,
        default=os.getcwd(),
        help='TEXT  Destination directory'
    )
    cmd_args = parser.parse_args()
    dst_dir = cmd_args.dst_dir
    src_dir = cmd_args.src_dir
    while not check_dir_w(dst_dir):
        dst_dir = input("Введите путь до каталога назначения или exit для завершения работы программы: ")
        if dst_dir == "exit":
            break
    if dst_dir != 'exit':
        files = os.listdir(path=src_dir)
        for file in files:
            path_to_src_file = os.path.join(src_dir, file)
            if os.path.isfile(path_to_src_file):
                exp = Path(path_to_src_file).suffix
                mediafile = eyed3.load(path_to_src_file)
                if mediafile:
                    if mediafile.tag and mediafile.tag.artist and mediafile.tag.album:
                        if mediafile.tag.title:
                            title = normalize_name(decode(mediafile.tag.title))
                        else:
                            title = file[:len(file) - len(Path(file).suffix)]
                        artist = normalize_name(decode(mediafile.tag.artist))
                        album = normalize_name(decode(mediafile.tag.album))
                        file_name = " - ".join([title, artist, album]) + exp
                        path_to_dir = create_dir(dst_dir, artist, album)
                        if path_to_dir is not None:
                            full_dst_path = os.path.join(path_to_dir, file_name)
                            full_src_path = os.path.join(src_dir, file)
                            try:
                                os.rename(full_src_path, full_dst_path)
                            except FileExistsError:
                                print(f"[INFO]: Файл {full_dst_path} уже существует")
                            print(f"[INFO]: {full_src_path} -> {full_dst_path}")
                    else:
                        print(f"[INFO]: Отсутствуют необходимые теги. Файл {file} не был изменен")
        print("[INFO]: Done")
    else:
        print("[INFO]: Работа программы завершена")
except KeyboardInterrupt:
    print("[INFO]: Работа программы прервана пользователем")
    
