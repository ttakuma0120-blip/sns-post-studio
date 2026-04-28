import os
import re
import json
import streamlit as st
import anthropic

# ── Data management ─────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _safe(code: str) -> str:
    return re.sub(r'[^\w\-]', '_', code)

def load_shop_data(code: str) -> dict:
    path = os.path.join(DATA_DIR, f"{_safe(code)}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"shop_name": "", "styles": {}, "active_style": ""}

def save_shop_data(code: str, data: dict):
    with open(os.path.join(DATA_DIR, f"{_safe(code)}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Page config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SNS Post Studio｜飲食店専用",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@300;400;700&family=Shippori+Mincho:wght@400;700&display=swap');

:root {
    --bg: #0e0e10;
    --surface: #18181c;
    --border: #2a2a30;
    --gold: #c9a84c;
    --gold-dim: rgba(201,168,76,0.15);
    --text: #e8e6e0;
    --muted: #7a7870;
    --green: #3db87a;
}

html, body, [class*="css"] {
    font-family: 'Zen Kaku Gothic New', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
.block-container {
    max-width: 780px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
}

/* ── Header ── */
.studio-header { text-align: center; padding: 52px 0 40px; }
.studio-eyebrow { font-size: 0.72rem; letter-spacing: 0.22em; color: var(--gold); text-transform: uppercase; }
.studio-title { font-family: 'Shippori Mincho', serif; font-size: 2.4rem; font-weight: 700; color: #fff; line-height: 1.2; margin-top: 12px; }
.studio-sub { font-size: 0.88rem; color: var(--muted); font-weight: 300; margin-top: 12px; }
.studio-line { width: 48px; height: 1px; background: var(--gold); opacity: 0.5; margin: 24px auto 0; }

/* ── Section cards ── */
.block {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 28px 28px 22px !important;
    margin-bottom: 16px !important;
}
.block-title {
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    color: var(--gold);
    text-transform: uppercase;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}

/* ── Form elements ── */
.stSelectbox > div > div {
    background: var(--bg) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.stSelectbox label, .stTextArea label, .stTextInput label {
    color: var(--muted) !important;
    font-size: 0.8rem !important;
}
.stTextArea textarea, .stTextInput input {
    background: var(--bg) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Zen Kaku Gothic New', sans-serif !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-family: 'Zen Kaku Gothic New', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #c9a84c, #a8843a) !important;
    color: #0e0e10 !important;
    border: none !important;
    padding: 16px !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 24px rgba(201,168,76,0.28) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(201,168,76,0.45) !important;
}
.stButton > button:not([kind="primary"]) {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.83rem !important;
}

/* ── Radio ── */
.stRadio > div { gap: 10px !important; }
.stRadio label {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-size: 0.83rem !important;
}
.stRadio label:hover { border-color: var(--gold) !important; }

/* ── Badges ── */
.learn-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(61,184,122,0.1);
    border: 1px solid rgba(61,184,122,0.25);
    border-radius: 20px;
    color: var(--green);
    font-size: 0.75rem;
    padding: 4px 12px;
}
.code-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--gold-dim);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 20px;
    color: var(--gold);
    font-size: 0.75rem;
    padding: 4px 12px;
}

/* ── Output ── */
.output-wrapper {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-top: 24px;
}
.output-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    background: rgba(201,168,76,0.04);
}
.output-label { font-size: 0.72rem; letter-spacing: 0.16em; color: var(--gold); text-transform: uppercase; }
.output-platform {
    font-size: 0.75rem;
    color: var(--muted);
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 3px 10px;
}

/* ── Misc ── */
.stSpinner > div { border-top-color: var(--gold) !important; }
.stExpander { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; color: var(--muted) !important; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "shop_code" not in st.session_state:
    st.session_state.shop_code = ""
if "shop_data" not in st.session_state:
    st.session_state.shop_data = {}
if "result" not in st.session_state:
    st.session_state.result = ""
if "adding_style" not in st.session_state:
    st.session_state.adding_style = False

# ── Shop code gate ─────────────────────────────────────────────────────────────
if not st.session_state.shop_code:
    st.markdown("""
    <div class="studio-header">
      <div class="studio-eyebrow">✦ Restaurant SNS Studio</div>
      <div class="studio-title">ショップコードを入力</div>
      <p class="studio-sub">あなた専用のデータを呼び出します<br>初回は好きなコードを決めて入力してください</p>
      <div class="studio-line"></div>
    </div>
    """, unsafe_allow_html=True)

    code_input = st.text_input(
        "ショップコード",
        placeholder="例：marumaru や ramen01 など（半角英数字推奨）",
        label_visibility="collapsed",
    )
    if st.button("✦ スタート", type="primary", use_container_width=False):
        if code_input.strip():
            st.session_state.shop_code = code_input.strip()
            st.session_state.shop_data = load_shop_data(code_input.strip())
            st.rerun()
        else:
            st.warning("コードを入力してください")
    st.caption("⚠️ このコードはあなただけが知るパスワードです。忘れないようにメモしてください。")
    st.stop()

# ── Load shop data ─────────────────────────────────────────────────────────────
shop_data: dict = st.session_state.shop_data

# ── Header ─────────────────────────────────────────────────────────────────────
col_h, col_badge = st.columns([5, 1])
with col_h:
    st.markdown("""
    <div class="studio-header" style="padding: 32px 0 28px; text-align:left;">
      <div class="studio-eyebrow">✦ Restaurant SNS Studio</div>
      <div class="studio-title" style="font-size:2rem;">あなたの"声"で書く<br>SNS投稿を、AIが。</div>
      <div class="studio-line" style="margin:20px 0 0;"></div>
    </div>
    """, unsafe_allow_html=True)
with col_badge:
    st.markdown(f'<div style="padding-top:40px;"><div class="code-badge">✦ {st.session_state.shop_code}</div></div>', unsafe_allow_html=True)
    if st.button("ログアウト", key="logout"):
        st.session_state.shop_code = ""
        st.session_state.shop_data = {}
        st.session_state.result = ""
        st.rerun()

# ── Constants ──────────────────────────────────────────────────────────────────
PLATFORM_SPEC = {
    "Instagram": (
        "冒頭1〜2行に「スクロールが止まる」フック（驚き・共感・疑問・数字）を置く\n"
        "改行を効果的に使い、1〜2文で1ブロックにして視認性を高める\n"
        "絵文字は文脈に合った1〜3個を1ブロックに1回程度、センス良く配置する\n"
        "本文の終わりに「保存・シェアしたくなる」一言を添える\n"
        "ハッシュタグは本文の後に1行空けて配置し、15〜20個\n"
        "　（①料理・商品名 ②地域・エリア ③ジャンル・シーン ④感情・気分の4層）\n"
        "文字数の目安：本文150〜280字、全体で最大450字"
    ),
    "X（旧Twitter）": (
        "全体で140字以内（ハッシュタグ含む）に収める\n"
        "冒頭の3〜5語で「思わずRTしたくなる」インパクトを作る\n"
        "改行は1〜2か所まで。テンポよく読める構成にする\n"
        "ハッシュタグは2〜3個、文末または本文中に自然に組み込む\n"
        "「今日だけ」「限定」「実は」などのトリガーワードを活用する"
    ),
    "Facebook": (
        "200〜400字程度の、少し丁寧で読み応えのある文章にする\n"
        "お客様への語りかけ（「皆さんに」「ぜひ〜ください」）を自然に入れる\n"
        "段落を2〜3つに分け、読みやすく構成する\n"
        "ハッシュタグは不要（最大2〜3個まで、必要な場合のみ）\n"
        "地域密着感・人情味を大切にした言葉を選ぶ"
    ),
    "全SNS同時生成": (
        "▼ Instagram用・▼ X（旧Twitter）用・▼ Facebook用 を\n"
        "━━━━━━━━ の区切り線で分けて、それぞれの仕様で出力する"
    ),
}

TONE_SPEC = {
    "にぎやか・元気（感嘆符多め）": "明るく元気な文体。感嘆符「！」を効果的に使用。テンポが良くポジティブなエネルギーがあふれる。",
    "温かみ・アットホーム": "親しみやすく、読んだ人がほっこりするような温かみのある文体。ひらがなを多用し、敬語はほどほどに。",
    "おしゃれ・スタイリッシュ": "洗練された文体。余白と間を大切に。絵文字は最小限で、英語やカタカナを効果的に混ぜる。",
    "丁寧・落ち着いた": "丁寧で落ち着いた敬語体。お客様への誠実さが伝わる品のある表現。感嘆符は控えめに。",
    "グルメライター風（食欲そそる）": "食べ物の色・香り・食感・温度を五感で描写する文体。読んだだけで食べたくなるような表現を使う。",
}

GOAL_CTA = {
    "新メニュー・商品の告知": "新しいメニューへの興奮・発見感を伝え、「試してみたい」と思わせるCTAを入れる",
    "来店・集客の促進": "来店のハードルを下げる表現を使い、「今すぐ行きたい」という気持ちにさせるCTAを入れる",
    "期間限定キャンペーン": "「今だけ」「残りわずか」という希少性・緊急性を適切に盛り込む",
    "日常のつぶやき・近況": "お店の日常を等身大で伝え、フォロワーとの距離を縮めるような温かい文章にする",
    "イベント・特別営業の案内": "日時・内容・申込方法などを明確に伝えつつ、期待感を高める表現を使う",
    "営業案内・空席・定休日のお知らせ": "営業日・定休日・空席状況などの実用情報を、読んで嬉しくなるような温かみのある文章で伝える。無機質にならず、来店したくなる一言を添える",
}

# ── Prompt builder ─────────────────────────────────────────────────────────────
def build_prompt(genre, shop_name, target, menu, extra, goal, platform, tone, past_posts):
    shop_info = f"「{shop_name}」（{genre}）" if shop_name else f"{genre}のお店"
    extra_info = f"\n追加情報・強調点：{extra}" if extra else ""

    if past_posts:
        style_section = f"""## あなたが学習する「このお店の文体」

以下は、このお店がこれまで実際に投稿してきたSNS文です。
これらを徹底的に分析し、以下の8要素を完全に再現してください：

1. 言葉のトーン（明るい/丁寧/フランク/など）
2. 文体（です・ます調 / だ・である調 / ため口など）
3. 絵文字の種類・頻度・配置パターン
4. 改行のリズムと間の取り方
5. よく使うフレーズ・口癖・言い回し
6. ハッシュタグの選び方・数・並べ方
7. 冒頭の入り方（毎回の書き出しパターン）
8. 締めくくりの言葉や読者への語りかけ方

--- 過去の投稿サンプル ここから ---
{past_posts}
--- 過去の投稿サンプル ここまで ---

上記の文体・世界観を85%以上再現した上で、新しい内容を投稿文にしてください。
（注意：文体は真似るが、内容は全く新しくオリジナルに作ること）"""
    else:
        style_section = f"""## 文体指示

{TONE_SPEC[tone]}

あなたは月100万円以上売上げる飲食店のSNS運用を10年担当してきたプロのSNSライターです。
バズる投稿の法則を熟知しており、読んだ人が「行ってみたい」「食べたい」と思わせる文章を書きます。"""

    return f"""あなたはプロのSNSライターです。以下の指示に従って、飲食店のSNS投稿文を作成してください。

{style_section}

## 投稿に使う素材情報

お店：{shop_info}
ターゲット客層：{target}
今日の伝えたいこと：{menu}{extra_info}
この投稿の目的：{goal}
目的に対するCTAの方向性：{GOAL_CTA[goal]}

## プラットフォーム仕様

{PLATFORM_SPEC[platform]}

## 絶対に守るルール

- 前置き・説明・タイトルは一切つけない（投稿文のみを出力）
- AIが書いたと分からないような、自然で人間らしい文章にする
- 「〜のような」「〜という」などの回りくどい表現を避ける
- 「ぜひ」を多用しない（1投稿1回まで）
- 同じ言葉の繰り返しを避け、語彙を豊かに使う
- 読んだ人が「いいね」か「保存」したくなるような文章にする
- お店の実在感・リアリティが伝わる具体的な言葉を選ぶ

投稿文を出力してください："""


# ── Step 01 ── 文体プロフィール ────────────────────────────────────────────────
st.markdown('<div class="block"><div class="block-title">Step 01 ── 文体プロフィール（任意・推奨）</div>', unsafe_allow_html=True)

styles: dict = shop_data.get("styles", {})
active_style: str = shop_data.get("active_style", "")

if not st.session_state.adding_style:
    if styles:
        style_names = list(styles.keys())
        # ラジオで選択
        selected_style = st.radio(
            "使用する文体",
            style_names,
            index=style_names.index(active_style) if active_style in style_names else 0,
            label_visibility="collapsed",
        )
        # 選択が変わったら保存
        if selected_style != shop_data.get("active_style"):
            shop_data["active_style"] = selected_style
            save_shop_data(st.session_state.shop_code, shop_data)
            st.session_state.shop_data = shop_data

        # 選択中の文体の情報 + 削除ボタン
        char_count = len(styles[selected_style])
        col_badge, col_del = st.columns([4, 1])
        with col_badge:
            st.markdown(
                f'<div class="learn-badge">✓ {selected_style} ── {char_count}文字を学習済み</div>',
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("🗑️ 削除", key="del_style"):
                del shop_data["styles"][selected_style]
                remaining = list(shop_data["styles"].keys())
                shop_data["active_style"] = remaining[0] if remaining else ""
                save_shop_data(st.session_state.shop_code, shop_data)
                st.session_state.shop_data = shop_data
                st.rerun()
    else:
        st.caption("※ 文体未登録。追加するとあなたのお店らしい文体で生成できます")
        selected_style = ""

    if st.button("＋ 新しい文体を追加", use_container_width=True):
        st.session_state.adding_style = True
        st.rerun()
else:
    # 新規追加フォーム
    new_name = st.text_input("文体の名前", placeholder="例：通常投稿、ランチ用、夜営業用")
    new_text = st.text_area(
        "過去に投稿したSNS文をここに貼ってください（3〜10件が理想）",
        height=180,
        placeholder="""例）
【1件目】
本日も元気に営業中です🍜
今日のおすすめは「濃厚醤油ラーメン」！
自家製メンマと半熟卵がたまりません…✨
ぜひ食べにきてね！ #ラーメン #大阪グルメ

【2件目】
寒い日はやっぱりここ！
こってり系好きの方、必見です🔥
夜21時まで営業してます〜""",
    )
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💾 保存する", type="primary", use_container_width=True):
            if new_name.strip() and new_text.strip():
                shop_data["styles"][new_name.strip()] = new_text.strip()
                shop_data["active_style"] = new_name.strip()
                save_shop_data(st.session_state.shop_code, shop_data)
                st.session_state.shop_data = shop_data
                st.session_state.adding_style = False
                st.rerun()
            else:
                st.warning("名前と投稿文を両方入力してください")
    with col_b:
        if st.button("キャンセル", use_container_width=True):
            st.session_state.adding_style = False
            st.rerun()

# 選択中の文体テキストを past_posts として以降で使用
active_style_name = shop_data.get("active_style", "")
past_posts = shop_data.get("styles", {}).get(active_style_name, "")

st.markdown('</div>', unsafe_allow_html=True)

# ── Step 02 ── お店の情報 ──────────────────────────────────────────────────────
st.markdown('<div class="block"><div class="block-title">Step 02 ── お店の情報</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox(
        "ジャンル",
        ["ラーメン・麺類", "居酒屋・焼き鳥", "カフェ・喫茶", "寿司・和食",
         "イタリアン・パスタ", "焼肉・ステーキ", "カレー", "中華料理",
         "定食・食堂", "スイーツ・ケーキ", "パン・ベーカリー", "その他"],
    )
with col2:
    saved_name = shop_data.get("shop_name", "")
    shop_name_input = st.text_input(
        "お店の名前",
        value=saved_name,
        placeholder="例：麺処 まるや",
        help="保存ボタンで次回から自動入力されます",
    )
    if shop_name_input != saved_name:
        if st.button("💾 名前を保存", key="save_name"):
            shop_data["shop_name"] = shop_name_input
            save_shop_data(st.session_state.shop_code, shop_data)
            st.session_state.shop_data = shop_data
            st.rerun()

shop_name = shop_name_input

target = st.selectbox(
    "ターゲット客層",
    ["幅広い層（指定なし）", "20〜30代 学生・若者", "ファミリー・子連れ",
     "ビジネスパーソン（ランチ需要）", "女性・カップル", "地元の常連・シニア層"],
)

st.markdown('</div>', unsafe_allow_html=True)

# ── Step 03 ── 今日の投稿内容 ──────────────────────────────────────────────────
st.markdown('<div class="block"><div class="block-title">Step 03 ── 今日の投稿内容</div>', unsafe_allow_html=True)

menu = st.text_area(
    "伝えたいこと・おすすめメニュー",
    height=110,
    help="具体的な価格・数量・特徴を書くほど質が上がります",
    placeholder=(
        "例：本日限定！濃厚味噌ラーメン 780円。自家製チャーシュー増量中。\n"
        "例：新メニュー「抹茶ティラミス」がついに登場しました。\n"
        "例：今週末はランチタイムを30分延長して14時まで営業します。"
    ),
)

col1, col2 = st.columns(2)
with col1:
    extra = st.text_input(
        "追加情報（任意）",
        placeholder="例：数量限定15食 / テイクアウト可 / 本日20時まで",
    )
with col2:
    goal = st.selectbox(
        "投稿の目的",
        ["新メニュー・商品の告知", "来店・集客の促進", "期間限定キャンペーン",
         "日常のつぶやき・近況", "イベント・特別営業の案内", "営業案内・空席・定休日のお知らせ"],
    )

st.markdown('</div>', unsafe_allow_html=True)

# ── Step 04 ── 投稿先 & スタイル ───────────────────────────────────────────────
st.markdown('<div class="block"><div class="block-title">Step 04 ── 投稿先 & スタイル</div>', unsafe_allow_html=True)

selected_platform = st.radio(
    "プラットフォーム",
    ["Instagram", "X（旧Twitter）", "Facebook", "全SNS同時生成"],
    horizontal=True,
    label_visibility="collapsed",
)

if not past_posts.strip():
    tone = st.selectbox("文体スタイル", list(TONE_SPEC.keys()))
else:
    tone = None
    st.caption(f"✓ 文体「{active_style_name}」から自動学習します")

st.markdown('</div>', unsafe_allow_html=True)

# ── API Key ─────────────────────────────────────────────────────────────────────
api_key = st.secrets.get("ANTHROPIC_API_KEY", "")

# ── Buttons ─────────────────────────────────────────────────────────────────────
col_gen, col_reset = st.columns([3, 1])
with col_gen:
    generate = st.button("✦ 投稿文を生成する", type="primary", use_container_width=True)
with col_reset:
    if st.button("リセット", use_container_width=True):
        st.session_state.result = ""
        st.rerun()

# ── Generation ──────────────────────────────────────────────────────────────────
if generate:
    if not menu.strip():
        st.warning("⚠️ Step 03「伝えたいこと・おすすめメニュー」を入力してください")
    elif not api_key:
        st.error("APIキーが設定されていません。管理者にお問い合わせください。")
    else:
        prompt = build_prompt(
            genre=genre, shop_name=shop_name, target=target,
            menu=menu, extra=extra, goal=goal,
            platform=selected_platform, tone=tone, past_posts=past_posts,
        )
        with st.spinner("生成中..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2048,
                    system=(
                        "あなたはプロのSNSライターです。"
                        "指示された投稿文のみを出力し、説明・前置き・マークダウン記法は一切使いません。"
                        "自然で人間らしい、リアリティのある文章を書きます。"
                    ),
                    messages=[{"role": "user", "content": prompt}],
                )
                st.session_state.result = message.content[0].text
            except anthropic.AuthenticationError:
                st.error("APIキーが無効です。正しいキーを入力してください。")
            except anthropic.RateLimitError:
                st.error("APIの利用制限に達しました。しばらく待ってから再試行してください。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# ── Output ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    platform_icons = {
        "Instagram": "📸 Instagram",
        "X（旧Twitter）": "𝕏 X",
        "Facebook": "👥 Facebook",
        "全SNS同時生成": "📋 全SNS",
    }
    platform_label = platform_icons.get(selected_platform, selected_platform)
    result_len = len(st.session_state.result)

    st.markdown(
        f"""<div class="output-wrapper">
  <div class="output-topbar">
    <span class="output-label">✦ 生成された投稿文</span>
    <span class="output-platform">{platform_label} · {result_len}字</span>
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    st.text_area("output", value=st.session_state.result, height=380, label_visibility="collapsed")

    if selected_platform == "X（旧Twitter）" and result_len > 140:
        st.warning(f"X（旧Twitter）は140字以内が推奨です。現在 {result_len} 字（{result_len - 140} 字超過）")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 再生成する", use_container_width=True):
            st.session_state.result = ""
            st.rerun()
    with col2:
        st.download_button(
            "💾 テキストで保存",
            data=st.session_state.result,
            file_name=f"sns_post_{selected_platform}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col3:
        if st.button("📋 別パターン生成", use_container_width=True):
            st.info("Step 03 の内容を少し変えるか、文体スタイルを切り替えて再度生成してみてください。")

# ── Tips ────────────────────────────────────────────────────────────────────────
with st.expander("💡 より良い投稿を生成するコツ"):
    st.markdown("""
**文体学習を使うと格段にクオリティが上がります**

過去の投稿を3件以上貼るだけで、AIがあなたのお店ならではの
絵文字の使い方・改行リズム・口癖・ハッシュタグの選び方
を自動で学習し、「そっくりな文体」で新しい内容を書いてくれます。

---

**入力が具体的なほど、出力の質が上がります**

❌ 「新メニューが出ました」

✅ 「濃厚鶏白湯ラーメン 980円。鶏を8時間炊いたスープ。本日限定20食」

価格・数量・特徴・限定性を入れると、プロ並みの投稿になります。
    """)
