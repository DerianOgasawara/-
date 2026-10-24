import streamlit as st
import gspread
from datetime import datetime

# --- Googleスプレッドシート接続処理 ---
def get_spreadsheet():
    # Streamlit Secretsから認証情報を取得して認証
    credentials = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(dict(credentials))
    # URL指定でシートを開く
    sh = gc.open_by_url(st.secrets["spreadsheet_url"])
    return sh.sheet1  # 先頭のワークシート

st.title("実験・アンケート")

participant_id = st.text_input("被験者ID（例: P001）を入力してください:")

if participant_id:
    st.subheader("タスク")
    choice = st.radio("問1. 直感で魅力的だと思う方を選んでください。", ["選択肢 A", "選択肢 B"])
    score = st.slider("問2. 現在の集中度を1〜5で評価してください。", 1, 5, 3)

    if st.button("回答を送信する"):
        try:
            sheet = get_spreadsheet()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # スプレッドシートの末尾に1行追加
            sheet.append_row([timestamp, participant_id, choice, score])
            
            st.success("回答が正常に送信・保存されました。ご協力ありがとうございました！")
        except Exception as e:
            st.error("データの送信に失敗しました。")
            st.write(f"エラー詳細: {e}")