"""
experiment.py
Streamlit用 協和度評価 心理実験モジュール（二者択一専用一対比較法）
"""

import random
import itertools
import json
import streamlit as st

from intervals import get_interval_data
from audio_loader import load_interval_audio

# ==============================================================================
# 実験設定
# ==============================================================================
# 1回の実験で行う試行数
NUM_TRIALS = 5
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


def generate_trial_list(num_trials=5):
    """
    指定された試行数に合わせてランダムな比較ペアリストを生成
    """
    intervals = get_interval_data()
    base_pairs = list(itertools.combinations(intervals, 2))  # 全78ペア
    
    if num_trials <= len(base_pairs):
        selected_pairs = random.sample(base_pairs, num_trials)
    else:
        selected_pairs = [random.choice(base_pairs) for _ in range(num_trials)]
        
    trials = []
    for idx, (item_a, item_b) in enumerate(selected_pairs):
        # AとBの提示順序（左右）をランダムに決定
        if random.choice([True, False]):
            first, second = item_a, item_b
        else:
            first, second = item_b, item_a
            
        trials.append({
            "trial_id": idx + 1,
            "interval_a": {
                "name": first["name"],
                "filename": first["filename"],
                "ratio": f"{first['ratio'][0]}:{first['ratio'][1]}",
                "semitones": first["semitones"]
            },
            "interval_b": {
                "name": second["name"],
                "filename": second["filename"],
                "ratio": f"{second['ratio'][0]}:{second['ratio'][1]}",
                "semitones": second["semitones"]
            }
        })
    return trials


def run():
    """
    実験の表示・進行処理を行い、完了時に13x13行列化に最適化したデータを返すメイン関数
    """
    init_session_state()
    st.subheader("🎵 和音の協和度比較タスク")
    
    # ---------------------------------------------------------
    # 1. 実験案内画面（未開始時）
    # ---------------------------------------------------------
    if not st.session_state.exp_started and not st.session_state.exp_finished:
        st.markdown("""
        **【実験手順】**
        1. 提示される **「音程 A」** と **「音程 B」** の2つの和音を聴き比べてください。
        2. 2つのうち、**どちらがより「協和（きれい・まとまっている）している」と感じるか** 直感で回答してください。
        """)
        
        st.info(f"全 **{NUM_TRIALS}** 試行の比較タスクを実施します。準備ができたら以下のボタンを押してください。")
        
        if st.button("実験を開始する", type="primary"):
            st.session_state.trials = generate_trial_list(num_trials=NUM_TRIALS)
            st.session_state.current_trial_idx = 0
            st.session_state.results = []
            st.session_state.exp_started = True
            st.session_state.exp_finished = False
            st.rerun()
            
        return {"status": "not_started"}

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
        
        st.markdown("##### 🔊 2つの音声を聴き比べてください")
        
        # 音程Aと音程Bを横並びで表示・再生
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("### 🅰️ 音程 A")
            audio_a = load_interval_audio(current["interval_a"]["filename"])
            st.audio(audio_a, format="audio/wav")
            
        with col_b:
            st.markdown("### 🅱️ 音程 B")
            audio_b = load_interval_audio(current["interval_b"]["filename"])
            st.audio(audio_b, format="audio/wav")
        
        st.write("---")
        st.write("**どちらの和音のほうが協和していると感じますか？**")
        
        selected_choice = None

        # 二択ボタン
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🅰️ 音程 A の方が協和している", key=f"btn_a_{idx}", use_container_width=True):
                selected_choice = "A"
        with btn_col2:
            if st.button("🅱️ 音程 B の方が協和している", key=f"btn_b_{idx}", use_container_width=True):
                selected_choice = "B"

        # 回答入力後のデータ記録と遷移処理
        if selected_choice is not None:
            semi_a = current["interval_a"]["semitones"]
            semi_b = current["interval_b"]["semitones"]
            
            # 勝者・敗者の半音数を確定
            if selected_choice == "A":
                winner_semi = semi_a
                loser_semi = semi_b
            else:
                winner_semi = semi_b
                loser_semi = semi_a

            st.session_state.results.append({
                "trial_no": idx + 1,
                "semitones_a": semi_a,
                "semitones_b": semi_b,
                "choice": selected_choice,             # "A" or "B"
                "winner_semitone": winner_semi,       # 勝者の半音数 (0~12)
                "loser_semitone": loser_semi,         # 敗者の半音数 (0~12)
                "pair_key": f"{min(semi_a, semi_b)}-{max(semi_a, semi_b)}" # 比較ペア識別キー
            })
            
            if idx + 1 < total:
                st.session_state.current_trial_idx += 1
            else:
                st.session_state.exp_started = False
                st.session_state.exp_finished = True
            st.rerun()
            
        return {"status": "in_progress"}

    # ---------------------------------------------------------
    # 3. 実験完了画面
    # ---------------------------------------------------------
    if st.session_state.exp_finished:
        st.success("🎉 全ての比較試行が完了しました！画面下の「回答を送信する」ボタンを押してください。")
        
        payload = {
            "num_trials": NUM_TRIALS,
            "trials": st.session_state.results
        }

        return {
            "status": "completed",
            "results_json": json.dumps(payload, ensure_ascii=False)
        }


# ------------------------------------------------------------------------------
# 単体テスト用 (`streamlit run experiment.py` で単体起動可能)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    st.set_page_config(page_title="協和度比較タスク", layout="wide")
    data = run()
