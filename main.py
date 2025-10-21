import streamlit as st
from scrape import get_page_html, extract_body_content, clean_body_content, split_dom_content
from parse import parse_content

# Инициализация переменных в session_state, если они не существуют
if "dom_content" not in st.session_state:
    st.session_state.dom_content = ""
if "pars_description" not in st.session_state:
    st.session_state.pars_description = None

st.title("AI")

url = st.text_input("Источник данных url", key="url_input")

if st.button("Запуск"):
    if url:
        r = get_page_html(url=url)
        r = extract_body_content(r)
        r = clean_body_content(r)
        st.session_state.dom_content = r
        # Не сбрасываем pars_description при новом запуске, чтобы пользователь мог перезапустить и оставить уточнения

if st.session_state.dom_content:
    with st.expander("Посмотреть данные из источников"):
        st.text_area("Собранные данные", st.session_state.dom_content, height=300)

    # Поле ввода уточнений (необязательное)
    input_description = st.text_area(
        "Введи уточнения, которые помогут AI составить тест кейсы (необязательно)",
        value=st.session_state.pars_description,
        key="description_input"
    )
    st.session_state.pars_description = input_description

    if st.button("Сгенерировать"):
        st.write("Генерация...")
        # Вызов LLM для извлечения релевантной информации с учетом уточнений пользователя
        generated_result = parse_content(
            dom_content=st.session_state.dom_content, 
            user_request=st.session_state.pars_description
        )
        st.write("Результат:")
        st.text_area("Извлеченные данные", value=generated_result, height=400)
