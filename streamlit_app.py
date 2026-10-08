import re
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="맞춤형 개념 심화 & 마인드맵 단권화",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 [무료/무로그인] 사용자 입력 맞춤 심화 마인드맵 생성기")
st.caption(
    "로그인이나 API 키 없이 작동하며, 입력하신 어떤 주제든 100% 동적으로 읽어서 요약 및 심화 내용으로 확장합니다."
)

st.markdown("---")

# 1단계: 마인드맵 기본 틀 (산화 등 고정 예시 없는 완전 빈 입력창)
st.subheader("1️⃣ 마인드맵 기본 틀 작성")

col_input1, col_input2 = st.columns([1, 1])

with col_input1:
    main_concept = st.text_input(
        "📍 [중심 노드] 오늘 공부한 핵심 개념",
        placeholder="예: 미분, 광합성, 피타고라스 정리, 프랑스 혁명, 자바스크립트 변수 등",
    )
    basic_def = st.text_area(
        "📝 [기본 정의] 내가 이해한 기본 개념/정의",
        placeholder="오늘 공부한 내용의 기본적인 정의나 핵심 개념을 적어주세요.",
        height=100,
    )

with col_input2:
    branch1 = st.text_area(
        "🌿 [가지 1] 세부 메모 / 인상 깊었던 포인트",
        placeholder="기억에 남는 세부 메모나 중요 포인트를 입력하세요.",
        height=70,
    )
    branch2 = st.text_area(
        "🌿 [가지 2] 관련 예시 / 적용 분야",
        placeholder="생각나는 연관 사례나 적용되는 분야를 입력하세요.",
        height=70,
    )

generate_btn = st.button(
    "🚀 작성한 내용으로 요약 & 심화 확장하기",
    type="primary",
    use_container_width=True,
)


# 서버 지연 없이 3중 자동 전환되는 무로그인 AI 호출 함수
def call_free_ai_multi_provider(prompt_text):
    # Provider 1: Pollinations AI (로그인/키 없는 오픈 무료 API)
    try:
        response = requests.post(
            "https://text.pollinations.ai/",
            json={
                "messages": [{"role": "user", "content": prompt_text}],
                "model": "openai",
            },
            timeout=8,
        )
        if response.status_code == 200 and len(response.text.strip()) > 50:
            return response.text
    except Exception:
        pass

    # Provider 2: DuckDuckGo AI Chat
    try:
        from duckduckgo_search import DDGS

        ddgs = DDGS()
        res = ddgs.chat(prompt_text, model="gpt-4o-mini")
        if res and len(res.strip()) > 50:
            return res
    except Exception:
        pass

    # Provider 3: g4f (GPT4Free)
    try:
        import g4f

        res = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o_mini,
            messages=[{"role": "user", "content": prompt_text}],
        )
        if res and len(str(res).strip()) > 50:
            return str(res)
    except Exception:
        pass

    return None


# 외부 AI 서버 응답 지연 시에도 입력한 주제 그대로 100% 동적 구성하는 동적 생성기 (고정 예시 없음)
def generate_dynamic_fallback(main_concept, basic_def, branch1, branch2):
    clean_concept = main_concept.replace('"', "'")
    clean_def = basic_def.replace('"', "'")
    clean_b1 = branch1.replace('"', "'") if branch1 else "세부 원리 파악"
    clean_b2 = branch2.replace('"', "'") if branch2 else "상위 응용 분야"

    dot_code = f"""
    digraph Mindmap {{
        rankdir=LR;
        node [fontname="Malgun Gothic, sans-serif", shape=box, style="filled,rounded", color="#2B3A42", fillcolor="#E8F1F5", fontsize=11];
        edge [color="#3F51B5", arrowhead=vee];

        Root [label="{clean_concept}", fillcolor="#1E88E5", fontcolor="white", fontsize=14, shape=ellipse];

        UserSummary [label="0. 입력 내용 요약", fillcolor="#B3E5FC"];
        Def [label="1. 심화 정의 스펙트럼", fillcolor="#C8E6C9"];
        Mech [label="2. 핵심 원리 및 메커니즘", fillcolor="#FFE0B2"];
        App [label="3. 실전 응용 분야", fillcolor="#FFF9C4"];

        Root -> UserSummary; Root -> Def; Root -> Mech; Root -> App;

        US1 [label="기본 정의: {clean_def[:20]}..."];
        UserSummary -> US1;

        Def1 [label="기초 수준: {clean_def[:25]}"];
        Def2 [label="전공/심화 수준: {clean_concept}의 확장 학문 체계"];
        Def -> Def1; Def -> Def2;

        Mech1 [label="핵심 포인트: {clean_b1[:25]}"];
        Mech -> Mech1;

        App1 [label="응용 예시: {clean_b2[:25]}"];
        App -> App1;
    }}
    """

    markdown_text = f"""
### 📌 0. 작성하신 내용 핵심 요약
* **중심 개념**: {main_concept}
* **기본 정의**: {basic_def}
* **세부 메모**: {branch1 if branch1.strip() else "없음"}
* **관련 예시**: {branch2 if branch2.strip() else "없음"}

---

### 📘 1. 심화 정의의 스펙트럼
* **기초 정의**: {basic_def}
* **학문적 심화 정의**: {main_concept} 개념의 학문적 정의 및 심화 전공 분야의 확장 해석

---

### ⚡ 2. 핵심 원리 및 메커니즘
* **원리 요약**: {branch1 if branch1.strip() else main_concept + "의 핵심 작용 메커니즘"}

---

### 🔬 3. 분야별 실전 심화 응용 예시
* **실전 응용 사례**: {branch2 if branch2.strip() else main_concept + "가 적용되는 산업/학문 분야"}
"""
    return dot_code, markdown_text


# 2단계: 입력 기반 동적 처리
if generate_btn:
    if not main_concept.strip() or not basic_def.strip():
        st.warning("⚠️ [중심 노드]와 [기본 정의]를 입력하신 후 버튼을 눌러주세요!")
    else:
        st.markdown("---")
        st.subheader(f"2️⃣ '{main_concept}' 요약 및 심화 확장 결과")

        with st.spinner(
            f"입력하신 '{main_concept}' 내용을 분석하여 마인드맵과 심화 정리 노드를 생성 중입니다..."
        ):
            user_input_context = f"""
            [사용자가 직접 작성한 내용]
            - 중심 개념: {main_concept}
            - 기본 정의: {basic_def}
            - 세부 메모: {branch1 if branch1.strip() else "내용 없음"}
            - 관련 예시: {branch2 if branch2.strip() else "내용 없음"}
            """

            prompt = f"""
            {user_input_context}

            너는 학문 전문 튜터다.
            공부법, 생기부, 메타인지 등의 일반적인 학습 팁이나 잡소리는 절대로 쓰지 마라.
            오직 사용자가 입력한 [{main_concept}] 주제에만 집중하여 작성해라.

            작성 규칙:
            1. [0. 사용자 입력 내용 핵심 요약]: 사용자가 적은 정의와 메모를 명확히 정리
            2. [1. 심화 정의의 스펙트럼]: 해당 주제의 기초부터 고급/전공 수준의 정의 확장
            3. [2. 핵심 메커니즘/원리/수식]: 수학/과학인 경우 관련 수식과 반응식/메커니즘, 인문/사회인 경우 핵심 이론/원리와 구조화된 논리 정리
            4. [3. 분야별 실전 심화 응용]: 입력된 주제가 실제 상위 학문, 산업, 실무에서 응용되는 딥한 예시 제시

            출력 형식 (반드시 아래 두 구분자를 사용해라):
            ===GRAPHVIZ===
            digraph Mindmap {{
                rankdir=LR;
                node [fontname="Malgun Gothic, sans-serif", shape=box, style="filled,rounded", color="#2B3A42", fillcolor="#E8F1F5", fontsize=11];
                edge [color="#3F51B5", arrowhead=vee];
                // 사용자가 입력한 {main_concept}에 대한 요약 노드 및 심화 확장 노드가 포함된 Graphviz 다이어그램 코드 작성 (한국어 라벨 사용)
            }}
            ===MARKDOWN===
            (0. 요약 / 1. 심화 정의 / 2. 핵심 메커니즘/원리 / 3. 분야별 응용 사례 마크다운 작성)
            """

            content = call_free_ai_multi_provider(prompt)

            if content:
                dot_match = re.search(
                    r"===GRAPHVIZ===\s*(.*?)\s*===MARKDOWN===",
                    content,
                    re.DOTALL,
                )
                md_match = re.search(
                    r"===MARKDOWN===\s*(.*)", content, re.DOTALL
                )

                if dot_match and md_match:
                    dot_code = dot_match.group(1).strip()
                    dot_code = re.sub(r"```dot|```graphviz|```", "", dot_code)
                    markdown_text = md_match.group(1).strip()
                else:
                    dot_code, markdown_text = generate_dynamic_fallback(
                        main_concept, basic_def, branch1, branch2
                    )
            else:
                # 무료 AI 서버 지연 시에도 산화 예시 없이 사용자가 입력한 개념으로 다이렉트 구성
                dot_code, markdown_text = generate_dynamic_fallback(
                    main_concept, basic_def, branch1, branch2
                )

            col_res1, col_res2 = st.columns([1, 1])
            with col_res1:
                st.subheader("📌 입력 내용 기반 심화 마인드맵")
                try:
                    st.graphviz_chart(dot_code, use_container_width=True)
                except Exception:
                    fallback_dot, _ = generate_dynamic_fallback(
                        main_concept, basic_def, branch1, branch2
                    )
                    st.graphviz_chart(fallback_dot, use_container_width=True)

            with col_res2:
                st.subheader("📚 입력 내용 기반 심화 정리 노트")
                st.markdown(markdown_text)