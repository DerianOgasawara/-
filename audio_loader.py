"""
audio_loader.py
録音したWAV音声ファイルを読み込んでバイナリ形式で返すモジュール
`experiment.py` を変更せず、試行ごとにC3〜B3の基準音をランダム切り替え。
起動時に全ファイルの存在確認を行い、不足があればエラー表示（ダミー音生成なし）。
"""

import os
import random
import streamlit as st

AUDIO_DIR = "audio"

# C3 〜 B3 の 12 基準音リスト
BASE_NOTES = [
    "C3", "Cs3", "D3", "Ds3", "E3", "F3", 
    "Fs3", "G3", "Gs3", "A3", "As3", "B3"
]

# 13音程のWAVファイル名リスト
INTERVAL_FILENAMES = [
    "unison.wav", "minor_2nd.wav", "major_2nd.wav", "minor_3rd.wav",
    "major_3rd.wav", "perfect_4th.wav", "tritone.wav", "perfect_5th.wav",
    "minor_6th.wav", "major_6th.wav", "minor_7th.wav", "major_7th.wav",
    "octave.wav"
]

# フォルダ名のシャープ表記（C#3等）への相互対応マップ
NOTE_ALT_MAP = {
    "Cs3": "C#3", "Ds3": "D#3", "Fs3": "F#3", "Gs3": "G#3", "As3": "A#3"
}


def check_audio_files() -> list[str]:
    """
    全基準音（C3〜B3）× 13音程のWAVファイルが存在するか確認し、
    不足しているファイルパスのリストを返す。
    """
    missing_files = []
    
    for base_note in BASE_NOTES:
        alt_base_note = NOTE_ALT_MAP.get(base_note, base_note)
        for filename in INTERVAL_FILENAMES:
            paths_to_check = [
                os.path.join(AUDIO_DIR, base_note, filename),
                os.path.join(AUDIO_DIR, alt_base_note, filename),
                os.path.join(AUDIO_DIR, f"{base_note}_{filename}"),
                os.path.join(AUDIO_DIR, filename),
            ]
            # いずれの検索パスにもファイルが存在しない場合は不足リストに追加
            if not any(os.path.exists(p) for p in paths_to_check):
                missing_files.append(f"{AUDIO_DIR}/{base_note}/{filename}")
                
    return missing_files


def get_current_trial_base_note() -> str:
    """
    experiment.py が管理している session_state.current_trial_idx を参照し、
    試行ごとにランダムな基準音を決定・保持する。
    """
    if "trial_base_notes" not in st.session_state:
        st.session_state.trial_base_notes = {}
        
    current_idx = st.session_state.get("current_trial_idx", 0)
    
    # 現在の試行番号に基準音が未割り当てならランダム決定
    if current_idx not in st.session_state.trial_base_notes:
        st.session_state.trial_base_notes[current_idx] = random.choice(BASE_NOTES)
        
    return st.session_state.trial_base_notes[current_idx]


def load_interval_audio(filename: str) -> bytes:
    """
    audio/ ディレクトリ配下のWAVファイルを読み込み、バイナリデータを返す。
    初回読み込み時に全ファイルのチェックを実施し、不足時は画面に警告を出して処理を中断する。
    """
    # セッション中に一度だけ全音声ファイルの事前確認を実行
    if "audio_checked" not in st.session_state:
        st.session_state.audio_checked = True
        missing = check_audio_files()
        if missing:
            st.error(f"⚠️ 以下の音声ファイルが見つかりません（計 {len(missing)} 件）:")
            for m in missing[:15]:  # 最大15件まで画面にリスト表示
                st.write(f"- `{m}`")
            if len(missing) > 15:
                st.write(f"  ...他 {len(missing) - 15} 件")

    # 現在の試行に割り当てられた基準音を取得
    base_note = get_current_trial_base_note()
    alt_base_note = NOTE_ALT_MAP.get(base_note, base_note)
    
    # ファイル検索パスの優先順位
    paths_to_check = [
        os.path.join(AUDIO_DIR, base_note, filename),          # 例: audio/Cs3/unison.wav
        os.path.join(AUDIO_DIR, alt_base_note, filename),      # 例: audio/C#3/unison.wav
        os.path.join(AUDIO_DIR, f"{base_note}_{filename}"),    # 例: audio/Cs3_unison.wav
        os.path.join(AUDIO_DIR, filename),                     # 例: audio/unison.wav (フォールバック)
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
            
    # ファイルが見つからない場合はエラーを表示して例外発生（ダミー音生成は行わない）
    err_msg = f"音声ファイルが見つかりません: {filename} (基準音: {base_note})"
    st.error(f"❌ {err_msg}")
    raise FileNotFoundError(err_msg)
