import streamlit as st
from scrape import get_page_html, extract_body_content, clean_body_content, split_dom_content
from parse import parse_content, test_case_generator

# === Инициализация session_state ===
if "dom_content" not in st.session_state:
    st.session_state.dom_content = None
if "pars_description" not in st.session_state:
    st.session_state.pars_description = None
if "urls" not in st.session_state:
    st.session_state.urls = [""]
if "pars_description_test_case" not in st.session_state:
    st.session_state.pars_description_test_case = None
if "generated_test_cases" not in st.session_state:
    st.session_state.generated_test_cases = None
if "generated_result" not in st.session_state:
    st.session_state.generated_result = None

# === CSS для прокрутки больших блоков ===
st.markdown(
    """
    <style>
        /* Фикс прокрутки больших блоков в Streamlit */
        .main .block-container {
            max-width: 100%;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Главный фикс: заставляем контент растягиваться и прокручиваться */
        section.main > div {
            height: auto !important;
            overflow: visible !important;
        }

        /* Если используется st.markdown или st.text для длинного текста */
        div[data-testid="stMarkdown"] {
            overflow: visible;
            height: auto;
        }

        /* Для expander'ов — разрешаем внутреннюю прокрутку */
        div[data-testid="stExpander"] div[role="region"] {
            overflow: auto;
            max-height: 70vh;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Генератор проверок. Alpha0.1")

# === Управление URL-источниками ===
if st.button("➕ Добавить источник данных", key="add_url_main"):
    st.session_state.urls.append("")

for i in range(len(st.session_state.urls)):
    col1, col2 = st.columns([15, 1])
    with col1:
        st.session_state.urls[i] = st.text_input(
            f"Источник данных url {i+1}",
            value=st.session_state.urls[i],
            key=f"url_input_{i}",
            label_visibility="collapsed"
        )

# === Запуск сбора данных ===
if st.button("Запуск"):
    all_content = []
    source_number = 1
    for url in st.session_state.urls:
        if url.strip():
            try:
                r = get_page_html(url=url)
                r = extract_body_content(r)
                r = clean_body_content(r)
                source_header = f"\n\n=== Источник {source_number} ===\n"
                all_content.append(source_header + r)
                source_number += 1
            except Exception as e:
                st.error(f"Ошибка при обработке {url}: {str(e)}")
    st.session_state.dom_content = "\n".join(all_content)

# === Отображение собранных данных ===
if st.session_state.dom_content:
    with st.expander("Посмотреть данные из источников"):
        st.markdown(st.session_state.dom_content)

    # Уточнения для обработки
    input_description = st.text_area(
        "Введи уточнения, которые помогут AI лучше обработать информацию",
        value=st.session_state.pars_description or "",
        key="description_input"
    )
    st.session_state.pars_description = input_description

    if st.button("Обработать данные"):
        generation_placeholder = st.empty()
        with generation_placeholder:
            st.write("Обработка...")

        try:
            generated_result = parse_content(
                dom_content=st.session_state.dom_content,
                user_request=st.session_state.pars_description
            )
            st.session_state.generated_result = generated_result
        except Exception as e:
            st.error(f"Ошибка при обработке: {str(e)}")
        finally:
            generation_placeholder.empty()

    # === Отображение результата обработки ===
    if st.session_state.generated_result:
        with st.expander("Посмотреть обработанные данные"):
            st.markdown(st.session_state.generated_result)

        # Уточнения для генерации проверок
        input_description_test_case = st.text_area(
            "Введи уточнения, которые помогут AI создать проверки",
            value=st.session_state.pars_description_test_case or "",
            key="description_input_test_case"
        )
        st.session_state.pars_description_test_case = input_description_test_case

        if st.button("Сгенерировать проверки"):
            generation_placeholder = st.empty()
            with generation_placeholder:
                st.write("Генерация проверок...")

            try:
                generated_test_cases = test_case_generator(
                    dom_content=st.session_state.generated_result,
                    user_request=st.session_state.pars_description_test_case
                )
                st.session_state.generated_test_cases = generated_test_cases
            except Exception as e:
                st.error(f"Ошибка при генерации проверок: {str(e)}")
            finally:
                generation_placeholder.empty()

        # === Отображение сгенерированных проверок ===
        if st.session_state.generated_test_cases:
            st.markdown(st.session_state.generated_test_cases)
