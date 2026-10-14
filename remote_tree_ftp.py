import ftplib
import difflib
import hashlib
import html
import io
import json
import os
import posixpath
import re
import ssl
import tempfile
import datetime
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor

import sublime
import sublime_plugin

SETTINGS = 'RemoteTreeFTP.sublime-settings'
SESSIONS = {}
TREE_STATE = 'RemoteTreeFTP-tree.sublime-settings'
BACKUP_LOCK = threading.Lock()


TRANSLATIONS = {
    "Подключение…": "Connecting…",
    "Выполняется…": "Working…",
    "Недопустимые символы в пути": "Invalid characters in path",
    "Введите 3 или 4 восьмеричные цифры: например, 644, 755 или 0755.": "Enter 3 or 4 octal digits, for example 644, 755 or 0755.",
    "Недопустимый путь рабочего файла": "Invalid working file path",
    "Элемент больше не доступен в дереве. Обновите каталог.": "This item is no longer available in the tree. Refresh the directory.",
    "RemoteTreeFTP: отправка…": "RemoteTreeFTP: uploading…",
    "Поддерживаются ftp и ftps (explicit TLS)": "Only FTP and explicit FTPS are supported",
    " — сейчас: ": " — current: ",
    "неизвестны": "unknown",
    "Для этого файла пока нет резервных копий. Они создаются перед отправкой изменений.": "No backups for this file yet. Backups are created before uploading changes.",
    "Восстановленная копия — отправьте вручную после проверки": "Restored copy — review it and upload manually",
    "Копировать путь": "Copy path",
    "Создать файл…": "Create file…",
    "Создать папку…": "Create folder…",
    "Изменить права…": "Change permissions…",
    "Дождитесь завершения текущих операций с сервером и повторите действие.": "Wait for the current server operations to finish, then try again.",
    "Операция завершена. Обновите каталог.": "Operation completed. Refresh the directory.",
    "● изменён": "● modified",
    "↑ отправка…": "↑ uploading…",
    "✓ на сервере": "✓ on server",
    "! ошибка отправки": "! upload failed",
    "⚠ изменён на сервере": "⚠ changed on server",
    "Снимок на момент проверки. «−» — сервер, «+» — ваша сохранённая версия.\nДля повторной отправки вернитесь к файлу и выберите «Отправить текущий файл».\n\n": "Snapshot at the time of checking. “−” is the server, “+” is your saved version.\nTo retry, return to the file and choose “Upload Current File”.\n\n",
    "Сравнение: ": "Compare: ",
    "Права (цифрами) — ": "Permissions (digits) — ",
    "Просмотреть копию": "View backup",
    "Сравнить с сервером": "Compare with server",
    "Восстановить в редактор (отправка вручную)": "Restore in editor (manual upload)",
    "История версий…": "Version history…",
    "Переименовать…": "Rename…",
    "Удалить…": "Delete…",
    "RemoteTreeFTP: путь скопирован": "RemoteTreeFTP: path copied",
    "Путь находится за пределами корневого каталога.": "The path is outside the root directory.",
    "Корневой каталог нельзя переименовать или удалить.": "The root directory cannot be renamed or deleted.",
    "RemoteTreeFTP: ошибка отправки": "RemoteTreeFTP: upload failed",
    "RemoteTreeFTP: отправка остановлена — файл изменён на сервере": "RemoteTreeFTP: upload stopped — file changed on server",
    "Отменить отправку": "Cancel upload",
    "Посмотреть различия": "View differences",
    "Серверная версия → ваша сохранённая версия": "Server version → your saved version",
    "Перезаписать моей версией…": "Overwrite with my version…",
    "Требуется подтверждение": "Confirmation required",
    "Пароль FTP": "FTP password",
    "Название подключения": "Connection name",
    "Адрес сервера (без ftp://)": "Server address (without ftp://)",
    "Логин": "Username",
    "Порт": "Port",
    "Начальная папка": "Starting folder",
    "Подключение сохранено. Выберите File → RemoteTreeFTP → Подключиться…": "Connection saved. Choose File → RemoteTreeFTP → Connect…",
    "Сначала сохраните файл.": "Save the file first.",
    "Готово": "Ready",
    " для ": " for ",
    "Резервная копия — только просмотр": "Backup — read only",
    "Введите одно имя без / и \\, не . или ..": "Enter a single name without / or \\\\, not . or ..",
    "Такое имя уже существует на сервере. Выберите другое.": "This name already exists on the server. Choose another.",
    "Отключить": "Disconnect",
    "есть новые изменения": "new unsaved changes",
    "отправлено": "uploaded",
    "Перезаписать": "Overwrite",
    " — файл изменился на сервере": " — file changed on server",
    "Файлы различаются, но текстовое сравнение недоступно: это двоичный файл или кодировка отличается от UTF-8.\nСервер: {} байт. Локальная копия: {} байт.": "The files differ, but text comparison is unavailable: this is a binary file or its encoding is not UTF-8.\nServer: {} bytes. Local copy: {} bytes.",
    "Отправлять при сохранении": "Upload on save",
    "Отправлять только вручную": "Upload manually only",
    "RemoteTreeFTP: не удалось открыть настройки: ": "RemoteTreeFTP: could not open settings: ",
    "Сервер не подтвердил изменение прав: ": "The server did not confirm the permissions change: ",
    "Сервер подтвердил права ": "Server confirmed permissions ",
    "Сначала закройте открытые файлы этого элемента во всех окнах RemoteTreeFTP.\nЭто исключит отправку сохранений по старому пути.": "Close the affected files in all RemoteTreeFTP windows first.\nThis prevents saving to the old path.",
    "В файле есть новые несохранённые правки. Сохраните его и повторите выбор.": "The file has new unsaved changes. Save it and try again.",
    "Перезаписать серверный файл вашей сохранённой версией?\n": "Overwrite the server file with your saved version?\n",
    "Сервер: ": "Server: ",
    "Локальная копия: ": "Local copy: ",
    "Сохранить пароль в связке ключей macOS": "Save password in macOS Keychain",
    "Использовать только в этой сессии": "Use only for this session",
    "Настройки изменились во время редактирования. Откройте мастер заново.": "Settings changed while editing. Open the wizard again.",
    "Ошибка: ": "Error: ",
    "папку": "folder",
    "файл": "file",
    " Удаляются только пустые папки.": " Only empty folders can be deleted.",
    "Удалить": "Delete",
    "Новое имя": "New name",
    "Неизвестная операция": "Unknown operation",
    "Обновить": "Refresh",
    "Поле не должно быть пустым.": "This field cannot be empty.",
    "Имя файла": "File name",
    "Имя папки": "Folder name",
    "Порт должен быть от 1 до 65535.": "The port must be between 1 and 65535.",
    "Введите адрес без протокола, пути и пробелов.": "Enter an address without protocol, path or spaces.",
    "Удалить {} с сервера?\n{}\n\nОтменить удаление нельзя.{}": "Delete this {} from the server?\n{}\n\nThis cannot be undone.{}",
    "<body>RemoteTreeFTP: отключено. Локальные копии открытых файлов сохранены.</body>": "<body>RemoteTreeFTP: disconnected. Local copies of open files have been kept.</body>",
    "Не удалось сохранить пароль в связке ключей. Подключение продолжится без сохранения.": "Could not save the password in Keychain. Connecting without saving it.",
    "Подключиться…": "Connect…",
    "Добавить сервер…": "Add Server…",
    "Изменить сервер…": "Edit Server…",
    "Подключиться с другим паролем…": "Connect with Another Password…",
    "Настройки (файл)…": "Settings (File)…",
    "Обновить дерево": "Refresh Tree",
    "Отправить текущий файл": "Upload Current File",
    "Отключиться": "Disconnect"
}

def tr(text):
    language = sublime.load_settings(SETTINGS).get('language', 'ru')
    return TRANSLATIONS.get(text, text) if language == 'en' else text


def safe_path(path):
    if '\r' in path or '\n' in path or '\x00' in path:
        raise ValueError(tr('Недопустимые символы в пути'))
    return path


def numeric_mode(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-7]{3,4}', value):
        raise ValueError(tr('Введите 3 или 4 восьмеричные цифры: например, 644, 755 или 0755.'))
    return format(int(value, 8), '03o')


def unix_list_modes(lines):
    result = {}
    for line in lines:
        match = re.match(r'^([d-])([rwxStTs-]{9})[+@.]?\s+\S+\s+\S+\s+\S+\s+\d+\s+\S+\s+\S+\s+\S+\s(.+)$', line)
        if not match:
            continue
        bits, name = match.group(2), match.group(3)
        mode = 0
        for index, char in enumerate(bits):
            if char in 'rwxst':
                mode |= 1 << (8 - index)
        if bits[2] in 'sS': mode |= 0o4000
        if bits[5] in 'sS': mode |= 0o2000
        if bits[8] in 'tT': mode |= 0o1000
        result[name] = format(mode, '03o')
    return result


def refresh_tab_names(window):
    if not window:
        return
    for view in window.views():
        info = view.settings().get('remote_tree_ftp')
        if info and view.file_name() == info.get('local'):
            # Keep a disk-backed buffer's natural name and saved state untouched.
            view.set_status('remote_tree_ftp_path', 'FTP: ' + info['path'])


def working_file(cache, path):
    safe_path(path)
    components = path.lstrip('/').split('/')
    if not components or any(part in ('', '.', '..') for part in components):
        raise ValueError(tr('Недопустимый путь рабочего файла'))
    return os.path.join(cache, 'server', *components)


class Session:
    def __init__(self, window, profile, password):
        self.window, self.profile, self.password = window, profile, password
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.root = posixpath.normpath('/' + profile.get('remote_path', '/').lstrip('/'))
        self.expanded, self.entries = set(), {}
        identity = [profile.get('host'), profile.get('port', 21),
                    profile.get('protocol', 'ftps'), profile.get('username'), self.root]
        self.state_key = hashlib.sha256(json.dumps(identity).encode('utf-8')).hexdigest()
        self.active_path = None
        self.file_states = {}
        self.upload_versions = {}
        self.remote_hashes = {}
        self.permissions = {}
        self.sheet = None
        self.status = tr('Подключение…')
        self.closed = False
        self.pending = 0
        self.cache = tempfile.mkdtemp(prefix='RemoteTreeFTP-')

    def remember(self):
        state = sublime.load_settings(TREE_STATE)
        state.set(self.state_key, sorted(self.expanded))
        sublime.save_settings(TREE_STATE)

    def restore(self):
        saved = sublime.load_settings(TREE_STATE).get(self.state_key, None)
        if saved is None:
            self.browse(self.root)
            return
        paths = {p for p in saved if isinstance(p, str) and
                 (p == self.root or p.startswith(self.root.rstrip('/') + '/'))}
        def fetch(ftp):
            result = {}
            for path in sorted(paths, key=lambda p: (p.count('/'), p)):
                if path != self.root and posixpath.dirname(path) not in result:
                    continue
                try:
                    result[path] = self.listing(ftp, path)
                except ftplib.error_perm as exc:
                    if path == self.root or not str(exc).startswith('550'):
                        raise
            return result
        def done(result):
            self.entries.update(result)
            self.expanded = set(result)
            self.remember()
        self.work(fetch, done)

    def owns(self, view):
        info = view.settings().get('remote_tree_ftp')
        return info if (info and info.get('session') == id(self)
                        and view.file_name() == info.get('local')) else None

    def connection(self):
        p = self.profile
        protocol = p.get('protocol', 'ftps')
        if protocol not in ('ftp', 'ftps'):
            raise ValueError(tr('Поддерживаются ftp и ftps (explicit TLS)'))
        ftp = (ftplib.FTP_TLS(context=ssl.create_default_context())
               if protocol == 'ftps' else ftplib.FTP())
        ftp.encoding = p.get('encoding', 'utf-8')
        try:
            ftp.connect(p['host'], int(p.get('port', 21)), timeout=25)
            ftp.login(p.get('username', 'anonymous'), self.password)
            if protocol == 'ftps':
                ftp.prot_p()
            ftp.set_pasv(p.get('passive', True))
            return ftp
        except Exception:
            ftp.close()
            raise

    def work(self, action, done, on_error=None):
        if self.closed:
            return
        self.pending += 1
        def run():
            if self.closed:
                return
            try:
                with self.connection() as ftp:
                    result = action(ftp)
                def finish():
                    self.pending -= 1
                    if not self.closed:
                        self.status = tr('Готово')
                        done(result)
                        self.render()
                sublime.set_timeout(finish)
            except Exception as exc:
                message = str(exc).replace(self.password, '***') if self.password else str(exc)
                def failed(message=message):
                    self.pending -= 1
                    if not self.closed:
                        self.status = tr('Ошибка: ') + message
                        if on_error:
                            on_error(message)
                        self.render()
                        sublime.error_message('RemoteTreeFTP: ' + message)
                sublime.set_timeout(failed)
        self.status = tr('Выполняется…')
        self.render()
        self.pool.submit(run)

    def listing(self, ftp, path):
        safe_path(path)
        modes = {}
        try:
            rows = []
            for name, facts in ftp.mlsd(path):
                facts = {k.lower(): v for k, v in facts.items()}
                try:
                    mode = numeric_mode(facts.get('unix.mode'))
                except ValueError:
                    mode = None
                if facts.get('type') == 'cdir':
                    self.permissions[path] = mode
                if facts.get('type') not in ('cdir', 'pdir'):
                    rows.append((name, facts.get('type') == 'dir'))
                    modes[name] = mode
        except ftplib.error_perm as exc:
            if not str(exc).startswith(('500', '501', '502', '504')):
                raise
            ftp.cwd(path)
            rows = []
            for item in ftp.nlst():
                name = posixpath.basename(item.rstrip('/'))
                if name in ('.', '..', ''):
                    continue
                try:
                    ftp.cwd(posixpath.join(path, name))
                    is_dir = True
                except ftplib.error_perm:
                    is_dir = False
                finally:
                    ftp.cwd(path)
                rows.append((name, is_dir))
        if any(modes.get(name) is None for name, _ in rows) and hasattr(ftp, 'retrlines'):
            lines = []
            try:
                ftp.retrlines('LIST ' + path, lines.append)
                fallback = unix_list_modes(lines)
                for name, mode in fallback.items():
                    if not modes.get(name):
                        modes[name] = mode
            except ftplib.error_perm:
                pass  # Directory browsing still works if LIST is prohibited.
        for name, _ in rows:
            if name not in ('.', '..') and '/' not in name:
                self.permissions[posixpath.join(path, name)] = modes.get(name)
        return sorted([(n, d) for n, d in rows if n not in ('.', '..') and '/' not in n],
                      key=lambda row: (not row[1], row[0].casefold()))

    def browse(self, path):
        if path in self.expanded:
            self.expanded = {p for p in self.expanded if p != path and
                             not p.startswith(path.rstrip('/') + '/')}
            self.remember()
            self.render()
            return
        def done(rows):
            self.entries[path] = rows
            self.expanded.add(path)
            self.remember()
        self.work(lambda ftp: self.listing(ftp, path), done)

    def edit_permissions(self, path):
        if not self.can_mutate(path, False):
            return
        try:
            self.directory_at(path)
        except ValueError as exc:
            sublime.error_message(str(exc))
            return
        current = self.permissions.get(path)
        def entered(value):
            try:
                mode = numeric_mode(value.strip())
            except ValueError as exc:
                sublime.message_dialog(str(exc))
                self.edit_permissions(path)
                return
            if not self.can_mutate(path, False):
                return
            def change(ftp):
                response = ftp.sendcmd('SITE CHMOD ' + mode + ' ' + safe_path(path))
                if not response.startswith('2'):
                    raise ValueError(tr('Сервер не подтвердил изменение прав: ') + response)
            def done(_):
                self.permissions[path] = mode
                self.status = tr('Сервер подтвердил права ') + mode + tr(' для ') + posixpath.basename(path)
            self.work(change, done)
        caption = tr('Права (цифрами) — ') + path + tr(' — сейчас: ') + (current or tr('неизвестны'))
        self.window.show_input_panel(caption, current or '', entered, None, None)

    def backup_folder(self, path):
        # Outside Packages/User: not loaded as plugin code or synced as settings.
        return os.path.join(os.path.dirname(sublime.packages_path()), 'RemoteTreeFTP Backups',
                            self.state_key, hashlib.sha256(path.encode('utf-8')).hexdigest())

    def save_backup(self, path, content):
        folder = self.backup_folder(path)
        with BACKUP_LOCK:
            os.makedirs(folder, mode=0o700, exist_ok=True)
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
            destination = os.path.join(folder, stamp + '-' + uuid.uuid4().hex + '.bak')
            fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=folder)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, destination)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            copies = sorted(name for name in os.listdir(folder) if name.endswith('.bak'))
            for old in copies[:-10]:
                os.unlink(os.path.join(folder, old))

    def history(self, path):
        folder = self.backup_folder(path)
        try:
            copies = sorted((name for name in os.listdir(folder) if name.endswith('.bak')), reverse=True)
        except FileNotFoundError:
            copies = []
        except OSError as exc:
            sublime.error_message('RemoteTreeFTP: ' + str(exc))
            return
        if not copies:
            sublime.message_dialog(tr('Для этого файла пока нет резервных копий. Они создаются перед отправкой изменений.'))
            return
        def choose(index):
            if index < 0 or self.closed:
                return
            try:
                with open(os.path.join(folder, copies[index]), 'rb') as stream:
                    content = stream.read()
            except OSError as exc:
                sublime.error_message('RemoteTreeFTP: ' + str(exc))
                return
            def action(selected):
                if selected < 0 or self.closed:
                    return
                if selected == 0:
                    local = self.copy_backup(path, content)
                    view = self.window.open_file(local, group=min(1, self.window.num_groups() - 1))
                    view.set_read_only(True)
                    view.set_status('remote_tree_ftp', tr('Резервная копия — только просмотр'))
                elif selected == 1:
                    def fetch(ftp):
                        stream = io.BytesIO()
                        ftp.retrbinary('RETR ' + safe_path(path), stream.write)
                        return stream.getvalue()
                    self.work(fetch, lambda current: self.show_difference(path, current, content))
                elif selected == 2:
                    self.restore_backup(path, content)
            self.window.show_quick_panel([tr('Просмотреть копию'), tr('Сравнить с сервером'),
                                          tr('Восстановить в редактор (отправка вручную)')], action)
        labels = []
        for name in copies:
            try:
                date = datetime.datetime.strptime(name.split('-')[0], '%Y%m%dT%H%M%S.%fZ')
                label = date.replace(tzinfo=datetime.timezone.utc).astimezone().strftime('%d.%m.%Y %H:%M:%S')
            except ValueError:
                label = name
            labels.append([label, path])
        self.window.show_quick_panel(labels, choose)

    def copy_backup(self, path, content):
        folder = tempfile.mkdtemp(prefix='restore-', dir=self.cache)
        local = os.path.join(folder, posixpath.basename(path))
        with open(local, 'wb') as stream:
            stream.write(content)
        return local

    def restore_backup(self, path, content):
        def fetch(ftp):
            stream = io.BytesIO()
            ftp.retrbinary('RETR ' + safe_path(path), stream.write)
            return hashlib.sha256(stream.getvalue()).hexdigest()
        def done(baseline):
            local = self.copy_backup(path, content)
            view = self.window.open_file(local, group=min(1, self.window.num_groups() - 1))
            view.settings().set('remote_tree_ftp', {'session': id(self), 'path': path, 'local': local,
                                                  'manual_only': True, 'restore_hash': baseline})
            refresh_tab_names(self.window)
            view.set_status('remote_tree_ftp', tr('Восстановленная копия — отправьте вручную после проверки'))
            self.active_path = path
            self.file_states[path] = 'modified'
        self.work(fetch, done)

    def directory_at(self, path):
        if path == self.root:
            return True
        for name, directory in self.entries.get(posixpath.dirname(path), []):
            if posixpath.join(posixpath.dirname(path), name) == path:
                return directory
        raise ValueError(tr('Элемент больше не доступен в дереве. Обновите каталог.'))

    def context_menu(self, path):
        try:
            directory = self.directory_at(path)
        except ValueError as exc:
            sublime.error_message('RemoteTreeFTP: ' + str(exc))
            return
        parent = path if directory else posixpath.dirname(path)
        options = [(tr('Копировать путь'), 'copy'), (tr('Создать файл…'), 'file'),
                   (tr('Создать папку…'), 'folder')]
        options.append((tr('Изменить права…'), 'permissions'))
        if not directory:
            options.append((tr('История версий…'), 'history'))
        if path != self.root:
            options += [(tr('Переименовать…'), 'rename'), (tr('Удалить…'), 'delete')]
        def choose(index):
            if index < 0 or self.closed:
                return
            action = options[index][1]
            if action == 'copy':
                sublime.set_clipboard(path)
                sublime.status_message(tr('RemoteTreeFTP: путь скопирован'))
            elif action == 'permissions':
                self.edit_permissions(path)
            elif action == 'history':
                self.history(path)
            elif action == 'delete':
                if not self.can_mutate(path, True):
                    return
                kind = tr('папку') if directory else tr('файл')
                note = tr(' Удаляются только пустые папки.') if directory else ''
                if sublime.ok_cancel_dialog(tr('Удалить {} с сервера?\n{}\n\nОтменить удаление нельзя.{}').format(kind, path, note), tr('Удалить')):
                    self.mutate('delete', path, directory)
            else:
                target = path if action == 'rename' else parent
                if not self.can_mutate(target, action == 'rename'):
                    return
                caption = tr('Новое имя') if action == 'rename' else (tr('Имя файла') if action == 'file' else tr('Имя папки'))
                initial = posixpath.basename(path) if action == 'rename' else ''
                self.window.show_input_panel(caption, initial,
                    lambda name: self.mutate(action, target, directory, name), None, None)
        self.window.show_quick_panel([[caption, path if action in ('copy', 'rename', 'delete', 'history', 'permissions') else parent]
                                     for caption, action in options], choose)

    def can_mutate(self, path, affects_existing):
        if self.closed:
            return False
        if self.pending or any(owner.pending for owner in SESSIONS.values()
                               if owner.state_key == self.state_key):
            sublime.message_dialog(tr('Дождитесь завершения текущих операций с сервером и повторите действие.'))
            return False
        if affects_existing:
            for window in sublime.windows():
                for view in window.views():
                    info = view.settings().get('remote_tree_ftp')
                    owner = SESSIONS.get(window.id())
                    if (info and owner and owner.state_key == self.state_key and
                            (info['path'] == path or info['path'].startswith(path.rstrip('/') + '/'))):
                        sublime.message_dialog(tr('Сначала закройте открытые файлы этого элемента во всех окнах RemoteTreeFTP.\nЭто исключит отправку сохранений по старому пути.'))
                        return False
        return True

    def mutate(self, action, path, directory, name=''):
        if not self.can_mutate(path, action in ('rename', 'delete')):
            return
        try:
            safe_path(path)
            if path != self.root and not path.startswith(self.root.rstrip('/') + '/'):
                raise ValueError(tr('Путь находится за пределами корневого каталога.'))
            if action in ('rename', 'delete') and path == self.root:
                raise ValueError(tr('Корневой каталог нельзя переименовать или удалить.'))
            parent = posixpath.dirname(path) if action in ('rename', 'delete') else path
            target = None
            if action != 'delete':
                safe_path(name)
                if not name or name in ('.', '..') or '/' in name or '\\' in name:
                    raise ValueError(tr('Введите одно имя без / и \\, не . или ..'))
                target = posixpath.join(parent, name)
                if action == 'rename' and target == path:
                    return
        except ValueError as exc:
            sublime.error_message('RemoteTreeFTP: ' + str(exc))
            return
        def perform(ftp):
            if target:
                if any(child == name for child, _ in self.listing(ftp, parent)):
                    raise ValueError(tr('Такое имя уже существует на сервере. Выберите другое.'))
            if action == 'file':
                ftp.storbinary('STOR ' + target, io.BytesIO(b''))
            elif action == 'folder':
                ftp.mkd(target)
            elif action == 'rename':
                ftp.rename(path, target)
            elif action == 'delete':
                if directory:
                    ftp.rmd(path)
                else:
                    ftp.delete(path)
            else:
                raise ValueError(tr('Неизвестная операция'))
            # A failed refresh must not make a successful mutation look failed.
            try:
                return self.listing(ftp, parent)
            except Exception:
                return None
        def done(rows):
            if action in ('rename', 'delete'):
                prefix = path.rstrip('/') + '/'
                self.expanded = {p for p in self.expanded if p != path and not p.startswith(prefix)}
                for mapping in (self.entries, self.file_states, self.upload_versions, self.remote_hashes, self.permissions):
                    for old in list(mapping):
                        if old == path or old.startswith(prefix):
                            mapping.pop(old, None)
                if self.active_path == path:
                    self.active_path = None
            if rows is not None:
                self.entries[parent] = rows
                self.expanded.add(parent)
            else:
                self.entries.pop(parent, None)
                self.expanded.discard(parent)
                self.status = tr('Операция завершена. Обновите каталог.')
            self.remember()
        self.work(perform, done)

    def link(self, label, action, path='', css_class=''):
        url = sublime.command_url('remote_tree_ftp_action', {'action': action, 'path': path})
        return '<a class="{}" href="{}">{}</a>'.format(css_class, url, html.escape(label))

    def render(self):
        if self.closed or not self.window.is_valid():
            return
        style = ('<body id="remote-tree-ftp"><style>body{padding:12px}'
                 'a{text-decoration:none}p{margin:6px 0}.entry{padding:3px 0}'
                 'a.folder{color:#E5BD70;font-weight:bold}a.file{color:#D3DAE3}'
                 '.status{color:#93A1B2;font-size:0.9rem}'
                 '.light a.folder{color:#876000}.light a.file{color:#303846}'
                 '.light .status{color:#687382}'
                 '.selected{background-color:#394E65}.light .selected{background-color:#DFEAF7}'
                 '.badge{font-size:0.85rem;color:#93A1B2}.error{color:#F28B82}'
                 '.modified{color:#E5BD70}.conflict{color:#F2A36B}.sent{color:#89C997}'
                 '.light .badge{color:#526170}.light .error{color:#B3261E}'
                 '.light .conflict{color:#994A00}.light .modified{color:#876000}.light .sent{color:#26743B}'
                 'a.actions{color:#93A1B2;padding:0 8px}.light a.actions{color:#526170}'
                 'a.mode{font-size:0.85rem;color:#A8BDD2;background-color:#354250;padding:1px 5px;border-radius:3px}'
                 '.light a.mode{color:#42576C;background-color:#E3EAF1}</style>')
        parts = [style,
                 '<h3>' + html.escape(self.profile.get('name', self.profile['host'])) + '</h3>',
                 '<p>' + self.link(tr('Обновить'), 'refresh') + ' · ' + self.link(tr('Отключить'), 'disconnect') + '</p>',
                 '<p class="status">' + html.escape(self.status) + '</p>']
        def row(path, name, directory, depth):
            label = ('▾ ▰ ' if path in self.expanded else '▸ ▰ ') if directory else '　▤ '
            state = self.file_states.get(path, '') if not directory else ''
            labels = {'modified': tr('● изменён'), 'uploading': tr('↑ отправка…'),
                      'sent': tr('✓ на сервере'), 'error': tr('! ошибка отправки'),
                      'conflict': tr('⚠ изменён на сервере')}
            badge = (' <span class="badge {}">{}</span>'.format(state, labels[state])
                     if state in labels else '')
            selected = ' selected' if not directory and path == self.active_path else ''
            parts.append('<div class="entry{}" style="padding-left:{}px">'.format(selected, depth * 20) +
                         self.link(label + name, 'browse' if directory else 'open', path,
                                   'folder' if directory else 'file') + ' ' +
                         self.link(self.permissions.get(path) or '—', 'permissions', path, 'mode') + badge +
                         self.link('⋯', 'menu', path, 'actions') + '</div>')
            if directory and path in self.expanded:
                for child, is_dir in self.entries.get(path, []):
                    row(posixpath.join(path, child), child, is_dir, depth + 1)
        row(self.root, self.root, True, 0)
        parts.append('</body>')
        content = ''.join(parts)
        if self.sheet and self.sheet in self.window.sheets():
            self.sheet.set_contents(content)
        else:
            self.sheet = self.window.new_html_sheet('RemoteTreeFTP', content, group=0)

    def open(self, path):
        safe_path(path)
        local = working_file(self.cache, path)
        folder = os.path.dirname(local)
        existing = self.window.find_open_file(local)
        if existing:
            self.active_path = path
            self.window.focus_view(existing)
            self.render()
            return
        def download(ftp):
            os.makedirs(folder, exist_ok=True)
            temporary = local + '.download'
            try:
                with open(temporary, 'wb') as stream:
                    ftp.retrbinary('RETR ' + path, stream.write)
                os.replace(temporary, local)
                with open(local, 'rb') as stream:
                    self.remote_hashes[path] = hashlib.sha256(stream.read()).hexdigest()
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        def done(_):
            view = self.window.open_file(local, group=min(1, self.window.num_groups() - 1))
            view.settings().set('remote_tree_ftp', {'path': path, 'local': local, 'session': id(self)})
            self.active_path = path
            refresh_tab_names(self.window)
            view.set_status('remote_tree_ftp', 'RemoteTreeFTP: ' + path)
        self.work(download, done)

    def upload(self, view, expected_remote=None):
        info = self.owns(view)
        if not info or self.closed:
            return
        path = info['path']
        version = self.upload_versions.get(path, 0) + 1
        self.upload_versions[path] = version
        revision = view.change_count()
        def failed(message):
            if self.upload_versions.get(path) == version:
                self.file_states[path] = 'error'
                view.set_status('remote_tree_ftp', tr('RemoteTreeFTP: ошибка отправки'))
        try:
            with open(info['local'], 'rb') as stream:
                data = stream.read()
        except OSError as exc:
            failed(str(exc))
            self.render()
            sublime.error_message(str(exc))
            return
        self.file_states[path] = 'uploading'
        view.set_status('remote_tree_ftp', tr('RemoteTreeFTP: отправка…'))
        def transfer(ftp):
            server = io.BytesIO()
            ftp.retrbinary('RETR ' + safe_path(path), server.write)
            remote = server.getvalue()
            current_hash = hashlib.sha256(remote).hexdigest()
            local_hash = hashlib.sha256(data).hexdigest()
            baseline = expected_remote if expected_remote is not None else info.get('restore_hash', self.remote_hashes.get(path))
            if current_hash != local_hash and current_hash != baseline:
                return {'conflict': remote, 'hash': current_hash}
            if current_hash != local_hash:
                self.save_backup(path, remote)
                ftp.storbinary('STOR ' + safe_path(path), io.BytesIO(data))
            # Update in the serial worker so a queued save sees our latest upload.
            self.remote_hashes[path] = local_hash
            return {'sent': True}
        def done(result):
            if self.upload_versions.get(path) != version:
                return
            if 'conflict' in result:
                self.file_states[path] = 'conflict'
                view.set_status('remote_tree_ftp', tr('RemoteTreeFTP: отправка остановлена — файл изменён на сервере'))
                self.conflict_menu(view, path, version, data, result['conflict'], result['hash'])
                return
            if info.get('manual_only'):
                info['restore_hash'] = hashlib.sha256(data).hexdigest()
                view.settings().set('remote_tree_ftp', info)
            changed = view.change_count() != revision or view.is_dirty()
            self.file_states[path] = 'modified' if changed else 'sent'
            view.set_status('remote_tree_ftp', 'RemoteTreeFTP: ' +
                            (tr('есть новые изменения') if changed else tr('отправлено')))
        self.work(transfer, done, failed)

    def conflict_menu(self, view, path, version, local, remote, remote_hash):
        def choose(index):
            if self.closed or not self.owns(view) or self.upload_versions.get(path) != version:
                return
            if index == 1:
                self.show_difference(path, remote, local)
            elif index == 2:
                if view.is_dirty():
                    sublime.message_dialog(tr('В файле есть новые несохранённые правки. Сохраните его и повторите выбор.'))
                    return
                if sublime.ok_cancel_dialog(tr('Перезаписать серверный файл вашей сохранённой версией?\n') + path,
                                            tr('Перезаписать')):
                    # Recheck the observed server version, never bypass checking.
                    self.upload(view, expected_remote=remote_hash)
        self.window.show_quick_panel([
            [tr('Отменить отправку'), path + tr(' — файл изменился на сервере')],
            [tr('Посмотреть различия'), tr('Серверная версия → ваша сохранённая версия')],
            [tr('Перезаписать моей версией…'), tr('Требуется подтверждение')]
        ], choose)

    def show_difference(self, path, remote, local):
        try:
            # UTF-8 diff is lossless. Do not silently replace undecodable bytes.
            before = remote.decode('utf-8')
            after = local.decode('utf-8')
            if '\x00' in before or '\x00' in after:
                raise ValueError('binary')
            diff = ''.join(difflib.unified_diff(before.splitlines(keepends=True),
                           after.splitlines(keepends=True), fromfile=tr('Сервер: ') + path,
                           tofile=tr('Локальная копия: ') + path))
            text = (tr('Снимок на момент проверки. «−» — сервер, «+» — ваша сохранённая версия.\nДля повторной отправки вернитесь к файлу и выберите «Отправить текущий файл».\n\n') + diff)
        except (UnicodeDecodeError, ValueError):
            text = (tr('Файлы различаются, но текстовое сравнение недоступно: это двоичный файл или кодировка отличается от UTF-8.\nСервер: {} байт. Локальная копия: {} байт.')).format(len(remote), len(local))
        panel = self.window.new_file()
        panel.set_name(tr('Сравнение: ') + posixpath.basename(path))
        panel.set_scratch(True)
        panel.run_command('append', {'characters': text})
        panel.set_read_only(True)
        panel.assign_syntax('Packages/Diff/Diff.sublime-syntax')


class RemoteTreeFtpConnectCommand(sublime_plugin.WindowCommand):
    def run(self, prompt_password=False):
        profiles = sublime.load_settings(SETTINGS).get('profiles', [])
        if not profiles:
            self.window.run_command('remote_tree_ftp_profile')
            return
        def choose(index):
            if index < 0:
                return
            profile = dict(profiles[index])
            def connect(password):
                sublime.run_command('new_window')
                window = sublime.active_window()
                window.set_layout({'cols': [0, 0.30, 1], 'rows': [0, 1], 'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]})
                session = Session(window, profile, password)
                SESSIONS[window.id()] = session
                session.restore()
            def entered(password):
                if sublime.platform() == 'osx':
                    def choice(selected):
                        if selected < 0:
                            return
                        if selected == 0:
                            def save():
                                try:
                                    from .keychain import access
                                    access(profile, password)
                                except Exception:
                                    sublime.set_timeout(lambda: sublime.error_message(
                                        tr('Не удалось сохранить пароль в связке ключей. Подключение продолжится без сохранения.')))
                                sublime.set_timeout(lambda: connect(password))
                            sublime.set_timeout_async(save)
                        else:
                            connect(password)
                    self.window.show_quick_panel([tr('Сохранить пароль в связке ключей macOS'),
                                                  tr('Использовать только в этой сессии')], choice)
                else:
                    connect(password)
            def prompt():
                panel = self.window.show_input_panel(tr('Пароль FTP'), '', entered, None, None)
                panel.settings().set('password', True)
            if prompt_password or sublime.platform() != 'osx':
                prompt()
                return
            def lookup():
                try:
                    from .keychain import access
                    password = access(profile)
                except Exception:
                    password = None
                sublime.set_timeout(lambda: connect(password) if password is not None else prompt())
            sublime.set_timeout_async(lookup)
        self.window.show_quick_panel([p.get('name', p.get('host', 'Server')) for p in profiles], choose)


class RemoteTreeFtpProfileCommand(sublime_plugin.WindowCommand):
    def run(self, edit=False):
        original = list(sublime.load_settings(SETTINGS).get('profiles', []))
        def start(index=None):
            if index is not None and index < 0:
                return
            profile = dict(original[index]) if index is not None else {
                'protocol': 'ftp', 'port': 21, 'remote_path': '/', 'upload_on_save': True}
            fields = [('name', tr('Название подключения')), ('host', tr('Адрес сервера (без ftp://)')),
                      ('username', tr('Логин')), ('port', tr('Порт')), ('remote_path', tr('Начальная папка'))]
            def field(step):
                if step == len(fields):
                    self.window.show_quick_panel(['FTP', 'FTPS (explicit TLS)'], protocol,
                                                  selected_index=1 if profile.get('protocol') == 'ftps' else 0)
                    return
                key, caption = fields[step]
                def accept(value):
                    value = value.strip()
                    try:
                        safe_path(value)
                        if not value:
                            raise ValueError(tr('Поле не должно быть пустым.'))
                        if key == 'port':
                            value = int(value)
                            if not 1 <= value <= 65535:
                                raise ValueError(tr('Порт должен быть от 1 до 65535.'))
                        elif key == 'host' and ('/' in value or any(c.isspace() for c in value)):
                            raise ValueError(tr('Введите адрес без протокола, пути и пробелов.'))
                        elif key == 'remote_path':
                            value = posixpath.normpath('/' + value.lstrip('/'))
                    except ValueError as exc:
                        sublime.message_dialog(str(exc))
                        field(step)
                        return
                    profile[key] = value
                    field(step + 1)
                self.window.show_input_panel(caption, str(profile.get(key, '')), accept, None, None)
            def protocol(selected):
                if selected < 0:
                    return
                profile['protocol'] = ('ftp', 'ftps')[selected]
                self.window.show_quick_panel([tr('Отправлять при сохранении'), tr('Отправлять только вручную')], finish,
                                              selected_index=0 if profile.get('upload_on_save', True) else 1)
            def finish(selected):
                if selected < 0:
                    return
                profile['upload_on_save'] = selected == 0
                settings = sublime.load_settings(SETTINGS)
                latest = list(settings.get('profiles', []))
                if index is None:
                    latest.append(profile)
                else:
                    if latest != original:
                        sublime.message_dialog(tr('Настройки изменились во время редактирования. Откройте мастер заново.'))
                        return
                    latest[index] = profile
                settings.set('profiles', latest)
                sublime.save_settings(SETTINGS)
                sublime.message_dialog(tr('Подключение сохранено. Выберите File → RemoteTreeFTP → Подключиться…'))
            field(0)
        if edit and original:
            self.window.show_quick_panel([p.get('name', p.get('host', 'Server')) for p in original], start)
        else:
            start()


class RemoteTreeFtpSettingsCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command('edit_settings', {
            'base_file': '${packages}/RemoteTreeFTP/' + SETTINGS,
            'default': '{\n    "language": "en",\n    "profiles": []\n}\n'
        })



class RemoteTreeFtpActionCommand(sublime_plugin.WindowCommand):
    def run(self, action, path=''):
        session = SESSIONS.get(self.window.id())
        if not session or session.closed:
            return
        if action == 'permissions':
            session.edit_permissions(path)
        elif action == 'menu':
            session.context_menu(path or session.active_path or session.root)
        elif action == 'browse':
            session.browse(path)
        elif action == 'open':
            session.open(path)
        elif action == 'refresh':
            paths = sorted(session.expanded) or [session.root]
            def done(results):
                session.entries.update(results)
                session.expanded.update(paths)
            session.work(lambda ftp: {p: session.listing(ftp, p) for p in paths}, done)
        elif action == 'disconnect':
            session.closed = True
            session.password = ''
            session.pool.shutdown(wait=False)
            if session.sheet and session.sheet in self.window.sheets():
                session.sheet.set_contents(tr('<body>RemoteTreeFTP: отключено. Локальные копии открытых файлов сохранены.</body>'))
            SESSIONS.pop(self.window.id(), None)


class RemoteTreeFtpUploadCommand(sublime_plugin.WindowCommand):
    def run(self):
        session = SESSIONS.get(self.window.id())
        view = self.window.active_view()
        if session and view:
            if view.is_dirty():
                sublime.message_dialog(tr('Сначала сохраните файл.'))
            else:
                session.upload(view)


class RemoteTreeFtpListener(sublime_plugin.EventListener):
    def session_for(self, view):
        window = view.window()
        session = SESSIONS.get(window.id()) if window else None
        return session if session and not session.closed and session.owns(view) else None

    def on_load(self, view):
        refresh_tab_names(view.window())

    def on_activated(self, view):
        refresh_tab_names(view.window())
        session = self.session_for(view)
        if session:
            session.active_path = session.owns(view)['path']
            session.render()

    def on_modified(self, view):
        # Loading a downloaded file also emits modification events.
        # Only a dirty, fully loaded buffer represents unsaved user edits.
        if view.is_loading() or not view.is_dirty():
            return
        session = self.session_for(view)
        if session:
            path = session.owns(view)['path']
            if session.file_states.get(path) != 'modified':
                session.file_states[path] = 'modified'
                session.render()

    def on_post_save(self, view):
        session = self.session_for(view)
        if (session and session.profile.get('upload_on_save', True)
                and not session.owns(view).get('manual_only')):
            session.upload(view)

    def on_close(self, view):
        window = view.window()
        sublime.set_timeout(lambda: refresh_tab_names(window))
        session = self.session_for(view)
        if session and session.active_path == session.owns(view)['path']:
            session.active_path = None
            session.render()

    def on_pre_close_window(self, window):
        session = SESSIONS.pop(window.id(), None)
        if session:
            session.closed = True
            session.pool.shutdown(wait=False)
            session.password = ''


def plugin_unloaded():
    for session in list(SESSIONS.values()):
        session.closed = True
        session.pool.shutdown(wait=False)
        session.password = ''
    SESSIONS.clear()


class RemoteTreeFtpMenuCommand(sublime_plugin.WindowCommand):
    def run(self, target, label, params=None):
        self.window.run_command(target, params or {})

    def description(self, target, label, params=None):
        if label.startswith('RemoteTreeFTP: '):
            return 'RemoteTreeFTP: ' + tr(label[len('RemoteTreeFTP: '):])
        return tr(label)


class RemoteTreeFtpLanguageCommand(sublime_plugin.WindowCommand):
    def run(self, language=None):
        if language is None:
            self.window.show_quick_panel(['Русский', 'English'],
                lambda index: self.run(('ru', 'en')[index]) if index >= 0 else None)
            return
        if language not in ('ru', 'en'):
            return
        settings = sublime.load_settings(SETTINGS)
        settings.set('language', language)
        sublime.save_settings(SETTINGS)
        for session in list(SESSIONS.values()):
            # Status messages already assembled remain valid; switch them to the
            # localized idle/busy state. Badges and controls render dynamically.
            session.status = tr('Выполняется…') if session.pending else tr('Готово')
            session.render()
        sublime.status_message('RemoteTreeFTP: ' + ('Русский' if language == 'ru' else 'English'))

    def is_checked(self, language=None):
        return language == sublime.load_settings(SETTINGS).get('language', 'ru')
