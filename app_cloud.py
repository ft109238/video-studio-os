import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 頁面基本配置
# ==========================================
st.set_page_config(
    page_title="個人工作台 OS (雲端版)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. Google Sheets 正規連線 (穩定防報錯)
# ==========================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    # 優先讀取雲端 Secrets，本地如果有檔案就讀本地
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("google_key.json", scopes=SCOPES)
    return gspread.authorize(creds)

gc = get_gspread_client()
# 透過試算表專屬 ID 開啟，絕對不會有網址參數解析錯誤
SPREADSHEET_ID = "1nHilkYdVW9Qx55wbRofXfN4b6xbJWbRG9NGDWtbQPiw"
sh = gc.open_by_key(SPREADSHEET_ID)

def get_data(worksheet_name):
    """從指定的 Google 試算表分頁讀取資料"""
    try:
        ws = sh.worksheet(worksheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"讀取資料表 {worksheet_name} 失敗：{e}")
        return pd.DataFrame()

def save_data(worksheet_name, df):
    """將 DataFrame 回寫至 Google 試算表"""
    try:
        ws = sh.worksheet(worksheet_name)
        ws.clear()
        # 寫入欄位名稱與全部資料
        ws.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error(f"寫入資料表失敗：{e}")

# ==========================================
# 3. 模組：短影音企劃庫
# ==========================================
def render_video_studio():
    st.title("🎬 短影音腳本工作室 (雲端同步中)")
    st.caption("資料已即時連動至 Google 試算表")

    df_scripts = get_data("scripts")
    tab_create, tab_manage = st.tabs(["✍️ 撰寫新企劃", "📚 腳本庫管理"])

    # --- 分頁 1：撰寫腳本 ---
    with tab_create:
        with st.form("script_form", clear_on_submit=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                v_title = st.text_input("影片標題 / 封面大字", placeholder="例如：關於我每天都在聊什麼 #05")
            with c2:
                v_category = st.selectbox("選題分類", ["職涯/搞錢", "思維認知", "日常工具/效率", "其他"])

            st.markdown("#### 🎯 腳本結構拆解 (口播導向)")
            v_hook = st.text_area("1. 黃金 3 秒開頭 (Hook / 停留理由)", height=80)
            v_body = st.text_area("2. 核心內容主體 (Body / 痛點拆解與方案)", height=160)
            v_cta = st.text_input("3. 行動召喚 (CTA / 引導互動)")

            col_tag, col_status = st.columns([3, 1])
            with col_tag:
                v_tags = st.text_input("Hashtags / 標籤 (以空格分隔)")
            with col_status:
                v_status = st.selectbox("目前進度", ["選題靈感", "已完稿待錄", "已錄製待剪", "已拍完", "已發布"])

            total_words = len(v_hook) + len(v_body) + len(v_cta)
            est_seconds = int(total_words / 4.2) if total_words > 0 else 0
            st.caption(f"📊 預估總字數：~{total_words} 字 ｜ 預估時長：約 {est_seconds} 秒")

            if st.form_submit_button("☁️ 儲存並同步至雲端", type="primary"):
                if v_title.strip() and v_hook.strip():
                    new_row = pd.DataFrame([{
                        "id": int(datetime.now().timestamp()),
                        "title": v_title.strip(),
                        "category": v_category,
                        "hook": v_hook.strip(),
                        "body": v_body.strip(),
                        "cta": v_cta.strip(),
                        "tags": v_tags.strip(),
                        "status": v_status,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }])
                    updated_df = pd.concat([df_scripts, new_row], ignore_index=True)
                    save_data("scripts", updated_df)
                    st.toast("已同步儲存至 Google 試算表！", icon="🎉")
                    st.rerun()
                else:
                    st.warning("請填寫標題與開頭 Hook！")

    # --- 分頁 2：瀏覽與管理 ---
    with tab_manage:
        if df_scripts.empty:
            st.info("目前雲端試算表中尚無腳本。")
        else:
            status_filter = st.selectbox("狀態篩選", ["全部", "選題靈感", "已完稿待錄", "已錄製待剪", "已拍完", "已發布"])
            display_df = df_scripts if status_filter == "全部" else df_scripts[df_scripts["status"] == status_filter]

            st.write(f"共找到 **{len(display_df)}** 篇腳本：")
            for idx, row in display_df.iterrows():
                with st.expander(f"【{row['status']}】{row['title']} ({row['category']})"):
                    st.markdown(f"**🪝 Hook 開頭：**\n> {row['hook']}")
                    st.markdown(f"**📝 主體內容：**\n{row['body']}")
                    st.markdown(f"**📣 CTA：** `{row['cta']}`")
                    st.caption(f"🏷️ 標籤：{row['tags']} ｜ 日期：{row['created_at']}")

                    if st.button("🗑️ 刪除腳本", key=f"del_{row['id']}"):
                        df_scripts = df_scripts[df_scripts["id"] != row["id"]]
                        save_data("scripts", df_scripts)
                        st.toast("腳本已從雲端刪除！", icon="🗑️")
                        st.rerun()

# ==========================================
# 4. 側邊欄導航
# ==========================================
with st.sidebar:
    st.title("⚡ 雲端工作台")
    st.success("🟢 Google Sheets 連線正常")
    menu = st.radio("模組導航", ["短影音腳本庫", "查看試算表原表"])

if menu == "短影音腳本庫":
    render_video_studio()
elif menu == "查看試算表原表":
    st.title("📊 Google 試算表原生資料預覽")
    st.dataframe(get_data("scripts"), use_container_width=True)