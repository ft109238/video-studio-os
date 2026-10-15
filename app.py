import json
import os
from datetime import datetime
import streamlit as st

# ==========================================
# 1. 頁面基本配置
# ==========================================
st.set_page_config(
    page_title="個人工作台 OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 本地 JSON 檔案讀寫機制
# ==========================================
DATA_FILE = "workspace_data.json"

DEFAULT_DATA = {
    "user_name": "Creator",
    "notes": "隨手記下的靈感與選題...",
    "tasks": [
        {"id": 1, "title": "整理下一期腳本選題", "status": "進行中"},
        {"id": 2, "title": "優化 Canva 封面排版模版", "status": "待處理"}
    ],
    "video_scripts": [
        {
            "id": 101,
            "title": "你適合用什麼方式賺錢？",
            "category": "職涯/搞錢",
            "hook": "為什麼很多人下班搞副業，忙了半年一毛錢都沒賺到？",
            "body": "核心在於你選的模式適不適合你的精力分配。如果你下班已經很累，別碰重交付，先從輕量化內容開始...",
            "cta": "留言『搞錢指南』，發你這份適合上班族的輕量副業清單！",
            "tags": ["個人成長", "副業思維", "自媒體實戰"],
            "status": "已拍完",
            "created_at": "2026-10-12"
        }
    ]
}

def load_data():
    """讀取本地 JSON 檔案"""
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 兼容舊版 JSON 結構
            if "video_scripts" not in data:
                data["video_scripts"] = DEFAULT_DATA["video_scripts"]
            return data
    except Exception:
        return DEFAULT_DATA.copy()

def save_data(data=None):
    """寫入本地 JSON 檔案"""
    if data is None:
        data = {
            "user_name": st.session_state.user_name,
            "notes": st.session_state.notes,
            "tasks": st.session_state.tasks,
            "video_scripts": st.session_state.video_scripts
        }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================================
# 3. 初始化 Session State
# ==========================================
if "initialized" not in st.session_state:
    saved_data = load_data()
    st.session_state.user_name = saved_data.get("user_name", DEFAULT_DATA["user_name"])
    st.session_state.notes = saved_data.get("notes", DEFAULT_DATA["notes"])
    st.session_state.tasks = saved_data.get("tasks", DEFAULT_DATA["tasks"])
    st.session_state.video_scripts = saved_data.get("video_scripts", DEFAULT_DATA["video_scripts"])
    st.session_state.initialized = True


# ==========================================
# 4. 功能模組：短影音企劃庫 (新增核心模組)
# ==========================================

def render_video_studio():
    """短影音企劃、腳本拆解與標籤庫"""
    st.title("🎬 短影音腳本工作室")
    st.caption("結構化拆解：前3秒黃金吸睛鉤子 ➔ 核心痛點乾貨 ➔ 導流行動召喚 (CTA)")

    tab_create, tab_manage = st.tabs(["✍️ 撰寫新企劃", "📚 腳本庫管理"])

    # --- 分頁 1：結構化腳本撰寫 ---
    with tab_create:
        with st.form("script_form", clear_on_submit=True):
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                v_title = st.text_input("影片標題 / 封面大字", placeholder="例如：關於我每天都在聊什麼 #05")
            with col_t2:
                v_category = st.selectbox("選題分類", ["職涯/搞錢", "思維認知", "日常工具/效率", "其他"])

            st.markdown("#### 🎯 腳本結構拆解 (口播導向)")
            v_hook = st.text_area(
                "1. 黃金 3 秒開頭 (Hook / 停留理由)",
                placeholder="痛點提問或反常識觀點，例如：『你以為只要努力就能翻身？其實多數人一開始就挑錯賽道了...』",
                height=80
            )
            v_body = st.text_area(
                "2. 核心內容主體 (Body / 痛點拆解與方案)",
                placeholder="精簡 2~3 個要點，適合 60 秒以內講完的口語化內容...",
                height=160
            )
            v_cta = st.text_input(
                "3. 行動召喚 (CTA / 引導互動)",
                placeholder="例如：追蹤我不迷路 / 留言關鍵字領取思維導圖"
            )

            col_tag, col_status = st.columns([3, 1])
            with col_tag:
                v_tags_input = st.text_input("Hashtags / 標籤 (以逗號或空格分隔)", placeholder="例如：自媒體 短影音 口播 搞錢思維")
            with col_status:
                v_status = st.selectbox("目前進度", ["選題靈感", "已完稿待錄", "已錄製待剪", "已拍完", "已發布"])

            # 字數與時長即時評估小提示
            total_words = len(v_hook) + len(v_body) + len(v_cta)
            est_seconds = int(total_words / 4.2) if total_words > 0 else 0
            st.caption(f"📊 預估總字數：~{total_words} 字 ｜ 依常態語速(~250字/分)預估時長：約 {est_seconds} 秒 (建議控制在 45~60 秒內)")

            submitted = st.form_submit_button("💾 儲存並加入腳本庫", type="primary")
            if submitted:
                if v_title.strip() and v_hook.strip():
                    tags_list = [t.strip().lstrip("#") for t in v_tags_input.replace(",", " ").split() if t.strip()]
                    new_script = {
                        "id": int(datetime.now().timestamp()),
                        "title": v_title.strip(),
                        "category": v_category,
                        "hook": v_hook.strip(),
                        "body": v_body.strip(),
                        "cta": v_cta.strip(),
                        "tags": tags_list,
                        "status": v_status,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.video_scripts.insert(0, new_script)
                    save_data()
                    st.toast("腳本已成功存入本地庫！", icon="🎉")
                    st.rerun()
                else:
                    st.warning("請至少填寫標題與開頭 Hook！")

    # --- 分頁 2：腳本庫瀏覽與管理 ---
    with tab_manage:
        if not st.session_state.video_scripts:
            st.info("目前還沒有任何腳本，點擊上方『撰寫新企劃』來建立你的第一支影片吧！")
        else:
            # 篩選器
            filter_col1, filter_col2 = st.columns([1, 2])
            with filter_col1:
                status_filter = st.selectbox("狀態篩選", ["全部"] + ["選題靈感", "已完稿待錄", "已錄製待剪", "已拍完", "已發布"])

            filtered_scripts = [
                s for s in st.session_state.video_scripts
                if status_filter == "全部" or s.get("status") == status_filter
            ]

            st.write(f"共找到 **{len(filtered_scripts)}** 篇腳本：")

            for idx, script in enumerate(filtered_scripts):
                with st.expander(f"【{script.get('status', '待辦')}】{script['title']} ({script.get('category', '通用')})", expanded=False):
                    c_info, c_action = st.columns([4, 1])
                    with c_info:
                        st.markdown(f"**🪝 Hook 開頭：**\n> {script['hook']}")
                        st.markdown(f"**📝 主體內容：**\n{script['body']}")
                        st.markdown(f"**📣 CTA：** `{script['cta']}`")
                        
                        # 渲染標籤膠囊
                        if script.get("tags"):
                            tags_html = " ".join([f"`#{t}`" for t in script["tags"]])
                            st.write(f"🏷️ **標籤：** {tags_html}")
                        st.caption(f"建立日期：{script.get('created_at', '未知')}")

                    with c_action:
                        # 狀態快速變更
                        curr_status = script.get("status", "選題靈感")
                        status_options = ["選題靈感", "已完稿待錄", "已錄製待剪", "已拍完", "已發布"]
                        new_stat = st.selectbox(
                            "切換狀態",
                            options=status_options,
                            index=status_options.index(curr_status) if curr_status in status_options else 0,
                            key=f"status_sel_{script['id']}"
                        )
                        if new_stat != curr_status:
                            script["status"] = new_stat
                            save_data()
                            st.rerun()

                        st.write("---")
                        if st.button("🗑️ 刪除腳本", key=f"del_script_{script['id']}"):
                            st.session_state.video_scripts = [s for s in st.session_state.video_scripts if s["id"] != script["id"]]
                            save_data()
                            st.rerun()


# ==========================================
# 5. 其他既有分頁
# ==========================================

def render_dashboard():
    """總覽儀表板"""
    st.title("⚡ 儀表板總覽")
    st.caption(f"歡迎回來，{st.session_state.user_name}！今天是 {datetime.now().strftime('%Y-%m-%d')}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="進行中任務", value=len(st.session_state.tasks))
    with col2:
        st.metric(label="腳本庫總量", value=len(st.session_state.video_scripts))
    with col3:
        ready_to_record = len([s for s in st.session_state.video_scripts if s.get("status") == "已完稿待錄"])
        st.metric(label="待錄製腳本", value=f"{ready_to_record} 篇")
    with col4:
        st.metric(label="靈感暫存字數", value=len(st.session_state.notes))
        
    st.divider()
    
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("🎬 近期影片腳本")
        for s in st.session_state.video_scripts[:3]:
            st.write(f"- **[{s.get('status', '企劃中')}]** {s['title']} `{s.get('category', '')}`")
            
    with col_right:
        st.subheader("📝 快速便籤預覽")
        st.info(st.session_state.notes[:80] + ("..." if len(st.session_state.notes) > 80 else ""))


def render_content_planner():
    """任務與內容管理"""
    st.title("📌 任務待辦管理")
    with st.expander("➕ 新增一筆任務", expanded=False):
        new_task_title = st.text_input("任務名稱", placeholder="例如：剪輯第 4 集影片")
        new_task_status = st.selectbox("初始狀態", ["待處理", "進行中", "已完成"])
        if st.button("確認新增", type="primary"):
            if new_task_title.strip():
                st.session_state.tasks.append({
                    "id": int(datetime.now().timestamp()),
                    "title": new_task_title.strip(),
                    "status": new_task_status
                })
                save_data()
                st.toast("任務已新增！", icon="💾")
                st.rerun()

    st.subheader("任務清單")
    if not st.session_state.tasks:
        st.info("目前沒有待辦任務。")
    else:
        for idx, task in enumerate(st.session_state.tasks):
            col_t, col_s, col_del = st.columns([3, 1, 1])
            with col_t:
                st.write(f"**{idx + 1}. {task['title']}**")
            with col_s:
                st.caption(f"狀態：`{task['status']}`")
            with col_del:
                if st.button("刪除", key=f"del_{task['id']}"):
                    st.session_state.tasks.pop(idx)
                    save_data()
                    st.rerun()


def render_scratchpad():
    """靈感草稿區"""
    st.title("💡 靈感草稿區")
    updated_notes = st.text_area(label="筆記內容", value=st.session_state.notes, height=300)
    if st.button("儲存筆記", type="primary"):
        st.session_state.notes = updated_notes
        save_data()
        st.toast("筆記已存檔！", icon="💾")


def render_settings():
    """系統設定"""
    st.title("⚙️ 系統設定")
    new_name = st.text_input("使用者暱稱", value=st.session_state.user_name)
    if st.button("更新暱稱"):
        st.session_state.user_name = new_name
        save_data()
        st.success("暱稱已儲存！")
    
    st.divider()
    if st.button("恢復為預設資料", type="secondary"):
        save_data(DEFAULT_DATA)
        st.session_state.clear()
        st.rerun()


# ==========================================
# 6. 側邊欄導航 (更新選單)
# ==========================================
with st.sidebar:
    st.title("⚡ 工作台導航")
    menu_selection = st.radio(
        label="選擇功能模組",
        options=["總覽儀表板", "短影音腳本庫", "任務待辦管理", "靈感草稿區", "系統設定"],
        index=1  # 預設直接開在腳本庫
    )
    st.divider()
    st.caption(f"目前腳本總數：{len(st.session_state.video_scripts)} 篇")
    st.caption(f"儲存檔案：`{DATA_FILE}`")


# ==========================================
# 7. 主路由分發
# ==========================================
if menu_selection == "總覽儀表板":
    render_dashboard()
elif menu_selection == "短影音腳本庫":
    render_video_studio()
elif menu_selection == "任務待辦管理":
    render_content_planner()
elif menu_selection == "靈感草稿區":
    render_scratchpad()
elif menu_selection == "系統設定":
    render_settings()