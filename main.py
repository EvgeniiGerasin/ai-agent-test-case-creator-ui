import streamlit as st
from scrape import get_page_html, extract_body_content, clean_body_content, split_dom_content
from parse import parse_content

# Инициализация переменных в session_state, если они не существуют
if "dom_content" not in st.session_state:
    st.session_state.dom_content = ""
if "pars_description" not in st.session_state:
    st.session_state.pars_description = None
if "urls" not in st.session_state:
    st.session_state.urls = [""]  # Инициализируем с одним пустым URL

st.title("AI")

# Добавляем кнопку "+" для добавления новых полей ввода URL
col1, col2 = st.columns([10, 1])
with col1:
    # Динамически создаем поля ввода URL
    for i in range(len(st.session_state.urls)):
        st.session_state.urls[i] = st.text_input(
            f"Источник данных url {i+1}", 
            value=st.session_state.urls[i], 
            key=f"url_input_{i}"
        )

with col2:
    # Кнопка для добавления новых полей ввода
    if st.button("➕", key="add_url"):
        st.session_state.urls.append("")  # Добавляем новое пустое поле

if st.button("Запуск"):
    # Обработка всех непустых URL и объединение их содержимого
    all_content = []
    source_number = 1
    for url in st.session_state.urls:
        if url.strip():  # Проверяем, что URL не пустой
            r = get_page_html(url=url)
            r = extract_body_content(r)
            r = clean_body_content(r)
            # Добавляем разделение фрагментов с указанием источника
            source_header = f"\n\n=== Источник {source_number} ===\n"
            all_content.append(source_header + r)
            source_number += 1
    st.session_state.dom_content = "\n".join(all_content)
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
