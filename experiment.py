import streamlit as st

def run():
    """実験の表示・処理を行い、結果データを返すメイン関数"""
    st.subheader("心理実験タスク")
    
    st.write("画面の指示に従って回答してください。")
    
    # 入力画面
    choice = st.radio("直感で選んでください", ["選択肢 A", "選択肢 B"])
    confidence = st.slider("確信度", 1, 5, 3)
    
    # 測定結果や回答データを辞書形式で返す
    return {
        "choice": choice,
        "confidence": confidence
    }

# ------------------------------------------------------------------------------
# 単体テスト用（ターミナルで `streamlit run my_experiment.py` と打つと単体で起動する）
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    st.title("【単体テストモード】")
    data = run()
    
    if st.button("テスト送信"):
        st.write("取得されたデータ:", data)