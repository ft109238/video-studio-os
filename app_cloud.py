import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 頁面基本配置
# ==========================================
st.set_page_config(
    page_title="短影音腳本工作室 (雲端同步版)",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. Google Sheets 正規連線 (雲端/本地雙支援)
# ==========================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("google_key.json", scopes=SCOPES)
    return gspread.authorize(creds)

gc = get_gspread_client()
SPREADSHEET_ID = "1nHilkYdVW9Qx55wbRofXfN4b6xbJWbRG9NGDWtbQPiw"
sh = gc.open_by_key(SPREADSHEET_ID)

def get_data(worksheet_name="scripts"):
    """從 Google 試算表讀取資料"""
    try:
        ws = sh.worksheet(worksheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"讀取資料失敗：{e}")
        return pd.DataFrame()

def save_data(worksheet_name, df):
    """將 DataFrame 回寫至 Google 試算表"""
    try:
        ws = sh.worksheet(worksheet_name)
        ws.clear()
        ws.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error(f"寫入資料失敗：{e}")

CATEGORIES = ["職涯/搞錢", "AI工具/效率", "護理/生活日常", "個人成長", "其他"]
STATUS_OPTIONS = ["選題靈感", "大綱擬定", "腳本完成", "已拍攝", "已發布"]

# ==========================================
# 3. 對話框彈窗：強制防呆刪除確認
# ==========================================
@st.dialog("⚠️ 刪除確認")
def confirm_delete_dialog(item_id, item_title, df_all):
    st.write(f"您確定要永久刪除企劃：**【{item_title}】** 嗎？")
    st.caption("此操作將直接從 Google 試算表中抹除，無法復原。")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌ 放棄返回", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("🗑️ 確定刪除", type="primary", use_container_width=True):
            updated_df = df_all[df_all["id"].astype(str) != str(item_id)]
            save_data("scripts", updated_df)
            st.success("已從雲端試算表刪除！")
            time.sleep(0.6)
            st.rerun()

# ==========================================
# 4. 對話框彈窗：直接原地編輯完整內容
# ==========================================
@st.dialog("✏️ 編輯腳本內容", width="large")
def edit_script_dialog(row_data, df_all):
    cat_idx = CATEGORIES.index(row_data.get("category", "其他")) if row_data.get("category") in CATEGORIES else 0
    stat_idx = STATUS_OPTIONS.index(row_data.get("status", "選題靈感")) if row_data.get("status") in STATUS_OPTIONS else 0
    
    e_title = st.text_input("影片標題 / 封面大字", value=str(row_data.get("title", "")))
    e_cat = st.selectbox("選題分類", CATEGORIES, index=cat_idx)
    e_hook = st.text_area("1. 黃金 3 秒開頭 (Hook)", value=str(row_data.get("hook", "")), height=80)
    e_body = st.text_area("2. 核心內容主體 (Body)", value=str(row_data.get("body", "")), height=140)
    e_cta = st.text_area("3. 行動召喚 (CTA)", value=str(row_data.get("cta", "")), height=70)
    
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        e_tags = st.text_input("關鍵標籤", value=str(row_data.get("tags", "")))
    with c_sub2:
        e_stat = st.selectbox("進度狀態", STATUS_OPTIONS, index=stat_idx)

    if st.button("💾 儲存修改並同步至雲端", type="primary", use_container_width=True):
        if not e_title.strip():
            st.error("標題不能為空！")
        else:
            mask = df_all["id"].astype(str) == str(row_data["id"])
            if mask.any():
                df_all.loc[mask, "title"] = e_title.strip()
                df_all.loc[mask, "category"] = e_cat
                df_all.loc[mask, "hook"] = e_hook.strip()
                df_all.loc[mask, "body"] = e_body.strip()
                df_all.loc[mask, "cta"] = e_cta.strip()
                df_all.loc[mask, "tags"] = e_tags.strip()
                df_all.loc[mask, "status"] = e_stat
                save_data("scripts", df_all)
                st.success("✅ 修改成功！")
                time.sleep(0.6)
                st.rerun()

# ==========================================
# 5. 主畫面渲染
# ==========================================
st.title("🎬 短影音腳本工作室 (雲端同步中)")
st.caption("資料已即時連動至 Google 試算表")

df_scripts = get_data("scripts")

tab_write, tab_manage = st.tabs(["✍️ 撰寫新企劃", "📚 腳本庫管理"])

# --- 分頁 1：撰寫新企劃 ---
with tab_write:
    col1, col2 = st.columns([3, 1])
    with col1:
        new_title = st.text_input("影片標題 / 封面大字", placeholder="例如：關於我每天都在聊什麼 #06")
    with col2:
        new_category = st.selectbox("選題分類", CATEGORIES)

    st.markdown("#### 🎯 腳本結構拆解 (口播導向)")
    new_hook = st.text_area("1. 黃金 3 秒開頭 (Hook / 停留理由)", placeholder="捕捉痛點、提問或懸念 (非必填)...", height=80)
    new_body = st.text_area("2. 核心內容主體 (Body / 痛點拆解與方案)", placeholder="精簡論點、步驟教學或故事...", height=140)
    new_cta = st.text_area("3. 行動召喚 (CTA / 引導互動)", placeholder="引導留言、關注下一集...", height=70)

    col_sub1, col_sub2 = st.columns([2, 1])
    with col_sub1:
        new_tags = st.text_input("關鍵標籤 / 主題詞", placeholder="副業, 自媒體, 思考")
    with col_sub2:
        new_status = st.selectbox("製作進度狀態", STATUS_OPTIONS)

    if st.button("☁️ 儲存並同步至雲端", type="primary"):
        # 防呆優化：只驗證標題，Hook 可完全留白
        if not new_title.strip():
            st.error("⚠️ 請至少填寫「影片標題」以便存檔！")
        else:
            with st.spinner("正在同步至 Google 試算表..."):
                new_id = int(datetime.now().strftime("%d%H%M%S"))
                new_entry = {
                    "id": new_id,
                    "title": new_title.strip(),
                    "category": new_category,
                    "hook": new_hook.strip(),
                    "body": new_body.strip(),
                    "cta": new_cta.strip(),
                    "tags": new_tags.strip(),
                    "status": new_status,
                    "created_at": datetime.now().strftime("%Y-%m-%d")
                }
                df_scripts = pd.concat([df_scripts, pd.DataFrame([new_entry])], ignore_index=True)
                save_data("scripts", df_scripts)
                st.success("✅ 新靈感已同步至雲端！")
                time.sleep(0.6)
                st.rerun()

# --- 分頁 2：腳本庫管理 ---
with tab_manage:
    filter_val = st.selectbox("狀態篩選", ["全部"] + STATUS_OPTIONS)
    filtered = df_scripts if filter_val == "全部" else df_scripts[df_scripts["status"] == filter_val]
    st.write(f"共找到 {len(filtered)} 篇腳本：")

    if not filtered.empty:
        for _, row in filtered.iterrows():
            with st.expander(f"【{row.get('status', '未定')}】 {row.get('title', '無標題')} ({row.get('category', '無分類')})"):
                col_left, col_right = st.columns([3, 1])
                
                with col_left:
                    st.markdown(f"🪝 **Hook 開頭：**\n\n{row.get('hook', '（無）')}")
                    st.markdown(f"📝 **主體內容：**\n\n{row.get('body', '（無）')}")
                    st.markdown(f"📣 **CTA：**\n\n{row.get('cta', '（無）')}")
                    st.caption(f"🏷️ 標籤：{row.get('tags', '')} ｜ 建立日期：{row.get('created_at', '')}")

                with col_right:
                    # 原生狀態快速切換選單
                    curr_status = row.get("status", "選題靈感")
                    stat_index = STATUS_OPTIONS.index(curr_status) if curr_status in STATUS_OPTIONS else 0
                    
                    changed_status = st.selectbox(
                        "切換狀態",
                        STATUS_OPTIONS,
                        index=stat_index,
                        key=f"status_select_{row['id']}"
                    )
                    
                    # 狀態改變立即自動更新試算表
                    if changed_status != curr_status:
                        mask = df_scripts["id"].astype(str) == str(row["id"])
                        df_scripts.loc[mask, "status"] = changed_status
                        save_data("scripts", df_scripts)
                        st.success("狀態已更新！")
                        time.sleep(0.4)
                        st.rerun()

                st.divider()
                btn_c1, btn_c2 = st.columns([1, 5])
                with btn_c1:
                    if st.button("✏️ 編輯內容", key=f"edit_btn_{row['id']}"):
                        edit_script_dialog(row, df_scripts)

                with btn_c2:
                    if st.button("🗑️ 刪除", key=f"del_btn_{row['id']}"):
                        confirm_delete_dialog(row["id"], row.get("title", ""), df_scripts)