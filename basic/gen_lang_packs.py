#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_lang_packs.py — 自动生成 cfdialog 语言包

生成: zh_TW / ja / ko / ru / fr / es
输出: <lib_dir>/lg/<code>.txt

用法:
    python gen_lang_packs.py              # 生成全部
    python gen_lang_packs.py zh_TW ja     # 只生成指定语言
    python gen_lang_packs.py --force      # 覆盖已存在的
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---- 定位库目录 ----
THIS_DIR = Path(__file__).resolve().parent

try:
    sys.path.insert(0, str(THIS_DIR))
    import cfdialog  # noqa: F401
    LG_DIR = THIS_DIR / "lg"
    LIB_DIR = THIS_DIR
except Exception:
    LG_DIR = THIS_DIR / "lg"
    LIB_DIR = THIS_DIR

# 参考键（从库中取；库没导入成功就用内置的 keys）
try:
    from cfdialog import _BUILTIN_STRINGS  # type: ignore
    KEYS = list(_BUILTIN_STRINGS["en"].keys())
except Exception:
    KEYS = [
        "prompt_folder", "prompt_file", "prompt_any", "prompt_save",
        "prompt_partition", "current_dir", "access_mode", "access_ro",
        "access_rw", "ext_limit", "hidden_on", "selected_n",
        "tips_base", "tips_multi", "tips_manager",
        "err_no_perm", "err_bad_num", "err_bad_type", "err_no_pick",
        "err_not_exist", "err_dir_mismatch", "err_file_mismatch",
        "ask_admin", "ask_root", "no_root", "elevate_failed",
        "elevate_denied", "input_end", "user_cancel",
        "free_name_prompt", "default_is", "readonly_denied",
        "nothing_sel", "must_one", "confirm_delete", "deleted_ok",
        "clip_copied", "clip_cut", "clip_empty", "pasted_ok",
        "renamed_ok", "opened_ok", "attr_hdr", "attr_ro",
        "attr_hidden", "attr_size", "attr_mtime",
        "attr_toggle_ro", "attr_toggle_hidden", "attr_done",
        "no_partitions", "enter_num_or_q", "yes_no_prompt",
        "mode_path", "mode_copy", "work_dir",
        "prompt_rename", "prompt_lang_code", "prompt_lang_name",
        "prompt_ref_lang", "prompt_skip",
    ]


# =========================================================================== #
#                          各语言的翻译数据                                    #
# =========================================================================== #

PACKS: dict = {

    # ============================================================== zh_TW
    "zh_TW": {
        "_meta": {
            "code": "zh_TW",
            "name": "繁體中文",
            "name_en": "Traditional Chinese",
            "native_name": "繁體中文",
        },
        "strings": {
            "prompt_folder": "請選擇資料夾",
            "prompt_file": "請選擇檔案",
            "prompt_any": "請選擇檔案或資料夾",
            "prompt_save": "請選擇目標資料夾",
            "prompt_partition": "請選擇分區",
            "current_dir": "目前目錄",
            "access_mode": "存取模式",
            "access_ro": "唯讀",
            "access_rw": "讀寫",
            "ext_limit": "格式限制",
            "hidden_on": "[顯示隱藏檔案]",
            "selected_n": "已選 {n} 項",
            "tips_base": "[編號] 進入/選擇   [s] 選取目前   [s編號] 切換項目   "
                         "[b] 返回上層   [r] 回到起點   [g] 切換分區   [h] 隱藏   [q] 取消",
            "tips_multi": "\n  [a] 全選   [c] 清空   [d] 完成",
            "tips_manager": "  操作: rm=刪除  cp=複製  ct=剪下  ps=貼上  "
                            "rn=重新命名  op=開啟  at=屬性  info=資訊  ls=列表",
            "err_no_perm": "! 沒有權限讀取目前目錄。",
            "err_bad_num": "! 編號超出範圍。",
            "err_bad_type": "! 項目類型不符合選取要求。",
            "err_no_pick": "! 尚未選取任何項目。",
            "err_not_exist": "! 路徑不存在。",
            "err_dir_mismatch": "! 目前目錄不符合選取類型。",
            "err_file_mismatch": "! 該檔案不符合選取要求。",
            "ask_admin": "目前未以系統管理員身分執行，是否要提權？",
            "ask_root": "目前未以 root 執行，是否要取得 root 權限？",
            "no_root": "[cfdialog] 未偵測到 root（su 無法使用），略過提權。",
            "elevate_failed": "[cfdialog] 提權失敗：{msg}",
            "elevate_denied": "[cfdialog] 使用者拒絕了提權請求。",
            "input_end": "輸入結束",
            "user_cancel": "使用者取消選取",
            "free_name_prompt": "檔案名稱（留空使用預設）",
            "default_is": "預設: {name}",
            "readonly_denied": "! 唯讀模式：此操作已停用。",
            "nothing_sel": "! 未選取任何項目。",
            "must_one": "! 請恰好選取一項。",
            "confirm_delete": "確認刪除 {n} 個項目？",
            "deleted_ok": "已刪除 {n} 個項目。",
            "clip_copied": "已複製 {n} 個項目到剪貼簿。",
            "clip_cut": "已剪下 {n} 個項目到剪貼簿。",
            "clip_empty": "! 剪貼簿為空。",
            "pasted_ok": "已貼上 {n} 個項目。",
            "renamed_ok": "已重新命名: {old} -> {new}",
            "opened_ok": "已開啟: {path}",
            "attr_hdr": "{name} 的屬性",
            "attr_ro": "唯讀",
            "attr_hidden": "隱藏",
            "attr_size": "大小",
            "attr_mtime": "修改時間",
            "attr_toggle_ro": "切換唯讀",
            "attr_toggle_hidden": "切換隱藏（僅 Windows）",
            "attr_done": "完成。",
            "no_partitions": "! 未找到分區。",
            "enter_num_or_q": "輸入編號或 q 取消: ",
            "yes_no_prompt": "[y/N]: ",
            "mode_path": "路徑模式",
            "mode_copy": "複製模式",
            "work_dir": "工作目錄",
            "prompt_rename": "新名稱",
            "prompt_lang_code": "系統語言代碼（例如 de、ru、pt_BR）",
            "prompt_lang_name": "語言顯示名稱",
            "prompt_ref_lang": "參考語言（zh_CN 或 en）",
            "prompt_skip": "直接回車保留英語回退",
        },
    },

    # ============================================================== ja
    "ja": {
        "_meta": {
            "code": "ja",
            "name": "日本語",
            "name_en": "Japanese",
            "native_name": "日本語",
        },
        "strings": {
            "prompt_folder": "フォルダを選択してください",
            "prompt_file": "ファイルを選択してください",
            "prompt_any": "ファイルまたはフォルダを選択",
            "prompt_save": "保存先フォルダを選択",
            "prompt_partition": "パーティションを選択",
            "current_dir": "現在のディレクトリ",
            "access_mode": "アクセスモード",
            "access_ro": "読み取り専用",
            "access_rw": "読み書き",
            "ext_limit": "形式制限",
            "hidden_on": "[隠しファイルを表示]",
            "selected_n": "{n} 件選択中",
            "tips_base": "[番号] 移動/選択  [s] 現在を選択  [s番号] 切り替え  "
                         "[b] 上へ  [r] 開始位置  [g] パーティション  [h] 隠し  [q] 取消",
            "tips_multi": "\n  [a] 全選択  [c] クリア  [d] 完了",
            "tips_manager": "  操作: rm=削除  cp=コピー  ct=切り取り  ps=貼り付け  "
                            "rn=名前変更  op=開く  at=属性  info=情報  ls=一覧",
            "err_no_perm": "! 権限がありません。",
            "err_bad_num": "! 範囲外です。",
            "err_bad_type": "! 種類が一致しません。",
            "err_no_pick": "! 何も選択されていません。",
            "err_not_exist": "! パスが存在しません。",
            "err_dir_mismatch": "! 現在のフォルダは条件に合いません。",
            "err_file_mismatch": "! ファイルが条件に合いません。",
            "ask_admin": "管理者として実行されていません。昇格しますか？",
            "ask_root": "root として実行されていません。root 権限を要求しますか？",
            "no_root": "[cfdialog] root（su）が利用できません。",
            "elevate_failed": "[cfdialog] 昇格に失敗: {msg}",
            "elevate_denied": "[cfdialog] ユーザーが拒否しました。",
            "input_end": "入力終了",
            "user_cancel": "キャンセルされました",
            "free_name_prompt": "ファイル名（空欄で既定名）",
            "default_is": "既定: {name}",
            "readonly_denied": "! 読み取り専用モード: この操作は無効です。",
            "nothing_sel": "! 何も選択されていません。",
            "must_one": "! ちょうど 1 件選択してください。",
            "confirm_delete": "{n} 件を削除しますか？",
            "deleted_ok": "{n} 件を削除しました。",
            "clip_copied": "{n} 件をコピーしました。",
            "clip_cut": "{n} 件を切り取りました。",
            "clip_empty": "! クリップボードが空です。",
            "pasted_ok": "{n} 件を貼り付けました。",
            "renamed_ok": "名前変更: {old} -> {new}",
            "opened_ok": "開きました: {path}",
            "attr_hdr": "{name} の属性",
            "attr_ro": "読み取り専用",
            "attr_hidden": "隠し",
            "attr_size": "サイズ",
            "attr_mtime": "更新日時",
            "attr_toggle_ro": "読み取り専用を切替",
            "attr_toggle_hidden": "隠しを切替（Windows のみ）",
            "attr_done": "完了。",
            "no_partitions": "! パーティションが見つかりません。",
            "enter_num_or_q": "番号を入力、q でキャンセル: ",
            "yes_no_prompt": "[y/N]: ",
            "mode_path": "パスのみ",
            "mode_copy": "コピー",
            "work_dir": "作業ディレクトリ",
            "prompt_rename": "新しい名前",
            "prompt_lang_code": "言語コード（例: de, ru, pt_BR）",
            "prompt_lang_name": "言語表示名",
            "prompt_ref_lang": "参照言語（zh_CN または en）",
            "prompt_skip": "Enter で英語のフォールバックを保持",
        },
    },

    # ============================================================== ko
    "ko": {
        "_meta": {
            "code": "ko",
            "name": "한국어",
            "name_en": "Korean",
            "native_name": "한국어",
        },
        "strings": {
            "prompt_folder": "폴더를 선택하세요",
            "prompt_file": "파일을 선택하세요",
            "prompt_any": "파일 또는 폴더를 선택하세요",
            "prompt_save": "저장 폴더를 선택하세요",
            "prompt_partition": "파티션을 선택하세요",
            "current_dir": "현재 디렉터리",
            "access_mode": "접근 모드",
            "access_ro": "읽기 전용",
            "access_rw": "읽기/쓰기",
            "ext_limit": "형식 제한",
            "hidden_on": "[숨김 파일 표시]",
            "selected_n": "{n}개 선택됨",
            "tips_base": "[번호] 이동/선택  [s] 현재 선택  [s번호] 항목 전환  "
                         "[b] 상위로  [r] 시작  [g] 파티션  [h] 숨김  [q] 취소",
            "tips_multi": "\n  [a] 전체 선택  [c] 초기화  [d] 완료",
            "tips_manager": "  작업: rm=삭제  cp=복사  ct=잘라내기  ps=붙여넣기  "
                            "rn=이름변경  op=열기  at=속성  info=정보  ls=목록",
            "err_no_perm": "! 권한이 없습니다.",
            "err_bad_num": "! 범위를 벗어났습니다.",
            "err_bad_type": "! 유형이 일치하지 않습니다.",
            "err_no_pick": "! 아무 것도 선택되지 않았습니다.",
            "err_not_exist": "! 경로가 없습니다.",
            "err_dir_mismatch": "! 현재 폴더가 조건과 맞지 않습니다.",
            "err_file_mismatch": "! 파일이 조건과 맞지 않습니다.",
            "ask_admin": "관리자로 실행되지 않았습니다. 권한을 요청할까요?",
            "ask_root": "root로 실행되지 않았습니다. root 권한을 요청할까요?",
            "no_root": "[cfdialog] root(su)를 사용할 수 없습니다.",
            "elevate_failed": "[cfdialog] 권한 상승 실패: {msg}",
            "elevate_denied": "[cfdialog] 사용자가 거부했습니다.",
            "input_end": "입력 종료",
            "user_cancel": "취소되었습니다",
            "free_name_prompt": "파일 이름 (비우면 기본값)",
            "default_is": "기본: {name}",
            "readonly_denied": "! 읽기 전용 모드: 이 작업은 비활성화되었습니다.",
            "nothing_sel": "! 아무 것도 선택되지 않았습니다.",
            "must_one": "! 정확히 1개를 선택하세요.",
            "confirm_delete": "{n}개를 삭제할까요?",
            "deleted_ok": "{n}개 삭제됨.",
            "clip_copied": "{n}개를 복사했습니다.",
            "clip_cut": "{n}개를 잘라냈습니다.",
            "clip_empty": "! 클립보드가 비어 있습니다.",
            "pasted_ok": "{n}개를 붙여넣었습니다.",
            "renamed_ok": "이름변경: {old} -> {new}",
            "opened_ok": "열림: {path}",
            "attr_hdr": "{name} 속성",
            "attr_ro": "읽기 전용",
            "attr_hidden": "숨김",
            "attr_size": "크기",
            "attr_mtime": "수정 시간",
            "attr_toggle_ro": "읽기 전용 전환",
            "attr_toggle_hidden": "숨김 전환 (Windows 전용)",
            "attr_done": "완료.",
            "no_partitions": "! 파티션이 없습니다.",
            "enter_num_or_q": "번호를 입력하거나 q로 취소: ",
            "yes_no_prompt": "[y/N]: ",
            "mode_path": "경로만",
            "mode_copy": "복사",
            "work_dir": "작업 디렉터리",
            "prompt_rename": "새 이름",
            "prompt_lang_code": "언어 코드 (예: de, ru, pt_BR)",
            "prompt_lang_name": "언어 표시 이름",
            "prompt_ref_lang": "참조 언어 (zh_CN 또는 en)",
            "prompt_skip": "Enter로 영어 폴백 유지",
        },
    },

    # ============================================================== ru
    "ru": {
        "_meta": {
            "code": "ru",
            "name": "Русский",
            "name_en": "Russian",
            "native_name": "Русский",
        },
        "strings": {
            "prompt_folder": "Выберите папку",
            "prompt_file": "Выберите файл",
            "prompt_any": "Выберите файл или папку",
            "prompt_save": "Выберите папку назначения",
            "prompt_partition": "Выберите раздел",
            "current_dir": "Текущий каталог",
            "access_mode": "Режим доступа",
            "access_ro": "только чтение",
            "access_rw": "чтение-запись",
            "ext_limit": "Ограничение формата",
            "hidden_on": "[Скрытые файлы показаны]",
            "selected_n": "Выбрано: {n}",
            "tips_base": "[№] Войти/Выбрать  [s] Текущий  [s№] Переключить  "
                         "[b] Назад  [r] Старт  [g] Раздел  [h] Скрытые  [q] Отмена",
            "tips_multi": "\n  [a] Все  [c] Очистить  [d] Готово",
            "tips_manager": "  опер: rm=удалить  cp=копировать  ct=вырезать  ps=вставить  "
                            "rn=переименовать  op=открыть  at=атрибуты  info=инфо  ls=список",
            "err_no_perm": "! Нет доступа к каталогу.",
            "err_bad_num": "! Номер вне диапазона.",
            "err_bad_type": "! Тип не соответствует.",
            "err_no_pick": "! Ничего не выбрано.",
            "err_not_exist": "! Путь не существует.",
            "err_dir_mismatch": "! Каталог не соответствует условию.",
            "err_file_mismatch": "! Файл не соответствует условию.",
            "ask_admin": "Не запущено от имени администратора. Повысить права?",
            "ask_root": "Не запущено от root. Запросить root?",
            "no_root": "[cfdialog] su недоступен, повышение пропущено.",
            "elevate_failed": "[cfdialog] Ошибка повышения: {msg}",
            "elevate_denied": "[cfdialog] Отказано пользователем.",
            "input_end": "Ввод завершён",
            "user_cancel": "Отменено пользователем",
            "free_name_prompt": "Имя файла (пусто = по умолчанию)",
            "default_is": "по умолчанию: {name}",
            "readonly_denied": "! Только чтение: действие отключено.",
            "nothing_sel": "! Ничего не выбрано.",
            "must_one": "! Выберите ровно один элемент.",
            "confirm_delete": "Удалить {n} элемент(ов)?",
            "deleted_ok": "Удалено: {n}.",
            "clip_copied": "Скопировано в буфер: {n}.",
            "clip_cut": "Вырезано в буфер: {n}.",
            "clip_empty": "! Буфер обмена пуст.",
            "pasted_ok": "Вставлено: {n}.",
            "renamed_ok": "Переименовано: {old} -> {new}",
            "opened_ok": "Открыто: {path}",
            "attr_hdr": "Атрибуты {name}",
            "attr_ro": "только чтение",
            "attr_hidden": "скрытый",
            "attr_size": "размер",
            "attr_mtime": "изменён",
            "attr_toggle_ro": "переключить только чтение",
            "attr_toggle_hidden": "переключить скрытый (только Windows)",
            "attr_done": "Готово.",
            "no_partitions": "! Разделы не найдены.",
            "enter_num_or_q": "Введите номер или q для отмены: ",
            "yes_no_prompt": "[y/N]: ",
            "mode_path": "только путь",
            "mode_copy": "копирование",
            "work_dir": "рабочий каталог",
            "prompt_rename": "Новое имя",
            "prompt_lang_code": "Код языка (напр. de, ru, pt_BR)",
            "prompt_lang_name": "Отображаемое имя",
            "prompt_ref_lang": "Опорный язык (zh_CN или en)",
            "prompt_skip": "Enter — оставить английский",
        },
    },

    # ============================================================== fr
    "fr": {
        "_meta": {
            "code": "fr",
            "name": "Français",
            "name_en": "French",
            "native_name": "Français",
        },
        "strings": {
            "prompt_folder": "Sélectionnez un dossier",
            "prompt_file": "Sélectionnez un fichier",
            "prompt_any": "Sélectionnez un fichier ou un dossier",
            "prompt_save": "Sélectionnez le dossier cible",
            "prompt_partition": "Sélectionnez une partition",
            "current_dir": "Répertoire actuel",
            "access_mode": "Mode d'accès",
            "access_ro": "lecture seule",
            "access_rw": "lecture-écriture",
            "ext_limit": "Limite de format",
            "hidden_on": "[Fichiers cachés affichés]",
            "selected_n": "{n} élément(s) sélectionné(s)",
            "tips_base": "[num] Entrer/Choisir  [s] Sélectionner l'actuel  "
                         "[s<num>] Basculer  [b] Retour  [r] Début  "
                         "[g] Partition  [h] Cachés  [q] Annuler",
            "tips_multi": "\n  [a] Tout  [c] Vider  [d] Terminer",
            "tips_manager": "  ops: rm=supprimer  cp=copier  ct=couper  ps=coller  "
                            "rn=renommer  op=ouvrir  at=attributs  info=info  ls=liste",
            "err_no_perm": "! Aucune permission.",
            "err_bad_num": "! Numéro hors plage.",
            "err_bad_type": "! Type incompatible.",
            "err_no_pick": "! Rien de sélectionné.",
            "err_not_exist": "! Le chemin n'existe pas.",
            "err_dir_mismatch": "! Dossier incompatible.",
            "err_file_mismatch": "! Fichier incompatible.",
            "ask_admin": "Pas administrateur. Demander l'élévation ?",
            "ask_root": "Pas root. Demander les droits root ?",
            "no_root": "[cfdialog] Aucun su disponible.",
            "elevate_failed": "[cfdialog] Échec: {msg}",
            "elevate_denied": "[cfdialog] Refusé par l'utilisateur.",
            "input_end": "Fin de saisie",
            "user_cancel": "Annulé",
            "free_name_prompt": "Nom de fichier (vide = défaut)",
            "default_is": "défaut: {name}",
            "readonly_denied": "! Mode lecture seule: action désactivée.",
            "nothing_sel": "! Rien de sélectionné.",
            "must_one": "! Sélectionnez exactement un élément.",
            "confirm_delete": "Supprimer {n} élément(s) ?",
            "deleted_ok": "{n} élément(s) supprimé(s).",
            "clip_copied": "{n} élément(s) copié(s).",
            "clip_cut": "{n} élément(s) coupé(s).",
            "clip_empty": "! Presse-papiers vide.",
            "pasted_ok": "{n} élément(s) collé(s).",
            "renamed_ok": "Renommé: {old} -> {new}",
            "opened_ok": "Ouvert: {path}",
            "attr_hdr": "Attributs de {name}",
            "attr_ro": "lecture seule",
            "attr_hidden": "caché",
            "attr_size": "taille",
            "attr_mtime": "modifié",
            "attr_toggle_ro": "basculer lecture seule",
            "attr_toggle_hidden": "basculer caché (Windows)",
            "attr_done": "Terminé.",
            "no_partitions": "! Aucune partition.",
            "enter_num_or_q": "Entrez un numéro ou q: ",
            "yes_no_prompt": "[y/N]: ",
            "mode_path": "chemin seulement",
            "mode_copy": "copie",
            "work_dir": "répertoire de travail",
            "prompt_rename": "Nouveau nom",
            "prompt_lang_code": "Code langue (ex: de, ru, pt_BR)",
            "prompt_lang_name": "Nom affiché",
            "prompt_ref_lang": "Langue de référence (zh_CN ou en)",
            "prompt_skip": "Entrée pour garder l'anglais",
        },
    },

    # ============================================================== es
    "es": {
        "_meta": {
            "code": "es",
            "name": "Español",
            "name_en": "Spanish",
            "native_name": "Español",
        },
        "strings": {
            "prompt_folder": "Selecciona una carpeta",
            "prompt_file": "Selecciona un archivo",
            "prompt_any": "Selecciona un archivo o carpeta",
            "prompt_save": "Selecciona la carpeta destino",
            "prompt_partition": "Selecciona una partición",
            "current_dir": "Directorio actual",
            "access_mode": "Modo de acceso",
            "access_ro": "solo lectura",
            "access_rw": "lectura-escritura",
            "ext_limit": "Límite de formato",
            "hidden_on": "[Archivos ocultos mostrados]",
            "selected_n": "{n} elemento(s) seleccionado(s)",
            "tips_base": "[num] Entrar/Elegir  [s] Seleccionar actual  "
                         "[s<num>] Alternar  [b] Atrás  [r] Inicio  "
                         "[g] Partición  [h] Ocultos  [q] Cancelar",
            "tips_multi": "\n  [a] Todo  [c] Limpiar  [d] Listo",
            "tips_manager": "  ops: rm=borrar  cp=copiar  ct=cortar  ps=pegar  "
                            "rn=renombrar  op=abrir  at=atributos  info=info  ls=listar",
            "err_no_perm": "! Sin permisos.",
            "err_bad_num": "! Número fuera de rango.",
            "err_bad_type": "! Tipo incompatible.",
            "err_no_pick": "! Nada seleccionado.",
            "err_not_exist": "! La ruta no existe.",
            "err_dir_mismatch": "! Carpeta incompatible.",
            "err_file_mismatch": "! Archivo incompatible.",
            "ask_admin": "No es administrador. ¿Solicitar elevación?",
            "ask_root": "No es root. ¿Solicitar permisos root?",
            "no_root": "[cfdialog] su no disponible.",
            "elevate_failed": "[cfdialog] Error de elevación: {msg}",
            "elevate_denied": "[cfdialog] Denegado por el usuario.",
            "input_end": "Entrada finalizada",
            "user_cancel": "Cancelado por el usuario",
            "free_name_prompt": "Nombre del archivo (vacío = predeterminado)",
            "default_is": "predeterminado: {name}",
            "readonly_denied": "! Solo lectura: acción deshabilitada.",
            "nothing_sel": "! Nada seleccionado.",
            "must_one": "! Selecciona exactamente un elemento.",
            "confirm_delete": "¿Borrar {n} elemento(s)?",
            "deleted_ok": "Borrados: {n}.",
            "clip_copied": "{n} elemento(s) copiado(s).",
            "clip_cut": "{n} elemento(s) cortado(s).",
            "clip_empty": "! Portapapeles vacío.",
            "pasted_ok": "{n} elemento(s) pegado(s).",
            "renamed_ok": "Renombrado: {old} -> {new}",
            "opened_ok": "Abierto: {path}",
            "attr_hdr": "Atributos de {name}",
            "attr_ro": "solo lectura",
            "attr_hidden": "oculto",
            "attr_size": "tamaño",
            "attr_mtime": "modificado",
            "attr_toggle_ro": "alternar solo lectura",
            "attr_toggle_hidden": "alternar oculto (solo Windows)",
            "attr_done": "Listo.",
            "no_partitions": "! Sin particiones.",
            "enter_num_or_q": "Introduce un número o q: ",
            "yes_no_prompt": "[y/N]: ",
            "mode_path": "solo ruta",
            "mode_copy": "copia",
            "work_dir": "directorio de trabajo",
            "prompt_rename": "Nuevo nombre",
            "prompt_lang_code": "Código de idioma (p. ej. de, ru, pt_BR)",
            "prompt_lang_name": "Nombre visible",
            "prompt_ref_lang": "Idioma de referencia (zh_CN o en)",
            "prompt_skip": "Intro para mantener inglés",
        },
    },
}


# =========================================================================== #
#                          生成逻辑                                            #
# =========================================================================== #

def _write_pack(code: str, data: dict, force: bool = False) -> bool:
    LG_DIR.mkdir(parents=True, exist_ok=True)
    target = LG_DIR / f"{code}.txt"
    if target.exists() and not force:
        print(f"  跳过（已存在）: {target.name}")
        return False

    meta = data.get("_meta", {})
    strings = data.get("strings", {})

    lines: List[str] = []
    lines.append("# cfdialog language pack")
    lines.append(f"# code={meta.get('code', code)}")
    lines.append(f"# name={meta.get('name', code)}")
    lines.append(f"# name_en={meta.get('name_en', code)}")
    lines.append(f"# native_name={meta.get('native_name', code)}")
    lines.append("#")
    lines.append("# Format:")
    lines.append("#   # key=value    metadata (ignored by runtime)")
    lines.append("#   key=value      string")
    lines.append("#")
    lines.append("")

    # 按 KEYS 顺序写，缺的用英语回退
    from_ = {}
    for k in KEYS:
        from_[k] = strings.get(k)
    # 其余未列入 KEYS 的也写出来
    for k, v in strings.items():
        if k not in from_:
            from_[k] = v

    for k, v in from_.items():
        if v is None:
            continue
        lines.append(f"{k}={v}")

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✔ 写入: {target}  ({len(strings)} 条)")
    return True


def main(argv: List[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    force = "--force" in argv

    if args:
        targets = args
    else:
        targets = ["zh_TW", "ja", "ko", "ru", "fr", "es"]

    print(f"库目录: {LIB_DIR}")
    print(f"语言包目录: {LG_DIR}")
    print(f"目标语言: {targets}")
    print(f"强制覆盖: {force}")
    print()

    count = 0
    for code in targets:
        if code not in PACKS:
            print(f"  ! 未知语言: {code}")
            continue
        if _write_pack(code, PACKS[code], force=force):
            count += 1

    print()
    print(f"完成，共 {count} 个语言包。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))