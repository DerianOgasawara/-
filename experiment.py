"""
experiment.py
Streamlit用 協和度評価 心理実験モジュール
（ソースコード内で評価方式・反復回数を固定指定し、被験者側の選択を制限）
"""

import random
import json
import streamlit as st

from intervals import get_interval_data
from audio_loader import load_interval_audio

# ==============================================================================
# 実験設定（ソースコード側で事前に指定してください）
# ==============================================================================
# EVAL_MODE: "4step" (四択ボタン), "2step" (二択ボタン), "slider" (スライダー)
EVAL_MODE = "4step"

# 各音程の反復再生回数 (全13音程 × REPEATS 試行)
REPEATS = 1
# ==============================================================================


def init_session_state():
    """セッション状態の初期化"""
    if "exp_started" not in st.session_state:
        st.session_state.exp_started = False
    if "trials" not in st.session_state:
        st.session_state.trials = []
    if "current_trial_idx" not in st.session_state:
        st.session_state.current_trial_idx = 0
    if "results" not in st.session_state:
        st.session_state.results = []
    if "exp_finished" not in st.session_state:
        st.session_state.exp_finished = False

def generate_trial_list(repeats=3):
    """全13音程データのランダムな試行リストを生成"""
    intervals = get_interval_data()
    trials = []
    for rep in range(repeats):
        shuffled = intervals.copy()
        random.shuffle(shuffled)
        for item in shuffled:
            trials.append({
                "repeat_id": rep + 1,
                "name": item["name"],
                "filename": item["filename"],
                "num": item["ratio"][0],
                "den": item["ratio"][1],
                "semitones": item["semitones"]
            })
    return trials

def run():
    """
    実験の表示・進行処理を行い、app.py (スプレッドシート保存) に引き渡すための辞書データを返すメイン関数
    """
    init_session_state()
    st.subheader("🎵 和音の協和度評価タスク")
    
    # ---------------------------------------------------------
    # 1. 実験案内画面（未開始時）
    # ---------------------------------------------------------
    if not st.session_state.exp_started and not st.session_state.exp_finished:
        st.markdown("""
        **【実験手順】**
        1. 提示される2音の和音（ピアノ録音音源）をよく聴いてください。
        2. その和音の響きが「どの程度協和（きれい・まとまっている）しているか」を直感で回答してください。
        """)
        
        total_trials = 13 * REPEATS
        st.info(f"全 **{total_trials}** 試行のタスクを実施します。準備ができたら以下のボタンを押してください。")
        
        if st.button("実験を開始する", type="primary"):
            st.session_state.trials = generate_trial_list(repeats=REPEATS)
            st.session_state.current_trial_idx = 0
            st.session_state.results = []
            st.session_state.exp_started = True
            st.session_state.exp_finished = False
            st.rerun()
            
        return {
            "status": "not_started",
            "eval_mode": EVAL_MODE,
            "total_trials": 0,
            "results_json": "[]"
        }

    # ---------------------------------------------------------
    # 2. 実験タスク画面（進行中）
    # ---------------------------------------------------------
    if st.session_state.exp_started and not st.session_state.exp_finished:
        trials = st.session_state.trials
        idx = st.session_state.current_trial_idx
        total = len(trials)
        current = trials[idx]
        
        # 進捗表示
        st.progress((idx) / total)
        st.caption(f"試行進捗: {idx + 1} / {total}")
        
        # 録音WAVファイルの読み込みと再生
        audio_bytes = load_interval_audio(current["filename"])
        
        st.markdown("##### 🔊 以下の音声を聴いて評価してください")
        st.audio(audio_bytes, format="audio/wav")
        
        selected_rating = None

        # A. 四択方式 (ボタンを押すと自動で次へ)
        if EVAL_MODE == "4step":
            st.write("**この和音の響きをどう感じますか？**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("不協和", key=f"btn_4_0_{idx}", use_container_width=True):
                    selected_rating = 0.0
            with col2:
                if st.button("やや不協和", key=f"btn_4_33_{idx}", use_container_width=True):
                    selected_rating = 0.33
            with col3:
                if st.button("やや協和", key=f"btn_4_67_{idx}", use_container_width=True):
                    selected_rating = 0.67
            with col4:
                if st.button("協和", key=f"btn_4_100_{idx}", use_container_width=True):
                    selected_rating = 1.0

        # B. 二択方式 (ボタンを押すと自動で次へ)
        elif EVAL_MODE == "2step":
            st.write("**この和音の響きをどう感じますか？**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("不協和", key=f"btn_2_0_{idx}", use_container_width=True):
                    selected_rating = 0.0
            with col2:
                if st.button("協和", key=f"btn_2_100_{idx}", use_container_width=True):
                    selected_rating = 1.0

        # C. スライダー方式
        elif EVAL_MODE == "slider":
            with st.form(key=f"slider_form_{idx}"):
                st.write("**協和度を 0.00 (非常に不協和) 〜 1.00 (非常に協和) で評価してください:**")
                slider_val = st.slider(
                    "協和度",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.01,
                    key=f"slider_{idx}"
                )
                submitted = st.form_submit_button("回答して次へ進む ➔")
                if submitted:
                    selected_rating = slider_val

        # 回答が入力された場合の記録と次の試行への遷移
        if selected_rating is not None:
            st.session_state.results.append({
                "trial_idx": idx + 1,
                "repeat_id": current["repeat_id"],
                "interval_name": current["name"],
                "ratio": f"{current['num']}:{current['den']}",
                "semitones": current["semitones"],
                "rating": selected_rating
            })
            
            if idx + 1 < total:
                st.session_state.current_trial_idx += 1
            else:
                st.session_state.exp_started = False
                st.session_state.exp_finished = True
            st.rerun()
            
        return {
            "status": "in_progress",
            "eval_mode": EVAL_MODE,
            "total_trials": total,
            "results_json": json.dumps(st.session_state.results, ensure_ascii=False)
        }

    # ---------------------------------------------------------
    # 3. 実験完了画面
    # ---------------------------------------------------------
    if st.session_state.exp_finished:
        st.success("🎉 全ての試行が完了しました！画面下の「回答を送信する」ボタンを押して送信を完了してください。")
        
        return {
            "status": "completed",
            "eval_mode": EVAL_MODE,
            "total_trials": len(st.session_state.results),
            "results_json": json.dumps(st.session_state.results, ensure_ascii=False)
        }

# ------------------------------------------------------------------------------
# 単体テスト用 (`streamlit run experiment.py` で単体起動可能)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    st.set_page_config(page_title="協和度評価タスク", layout="wide")
    data = run()
