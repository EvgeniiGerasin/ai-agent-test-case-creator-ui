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


# Добавляем CSS стили для адаптивного подстраивания страницы под контент
st.markdown("""
<style>
    .stTextInput > label {
        display: none;
    }
    
    .add-url-button {
        margin-top: 25px;
    }
    
    /* Адаптивная высота для текстовой области результата */
    .result-textarea {
        width: 100% !important;
        min-height: 300px;
        max-height: 80vh;  /* Максимальная высота 80% от высоты экрана */
        overflow-y: auto;  /* Вертикальный скролл, если контент превышает высоту */
    }
    
    /* Обертка для адаптивности */
    .main-container {
        width: 100%;
        max-width: 100%;
        padding: 1rem;
    }
    
    /* Адаптивность для текстовых полей */
    .stTextArea textarea, .stTextInput input {
        width: 100% !important;
    }
    
    /* Адаптивность для колонок */
    .stColumn {
        flex: 1;
    }
    
    /* Адаптивность для текста результата */
    .result-content {
        white-space: pre-wrap;  /* Сохраняем переносы строк */
        word-wrap: break-word;  /* Переносим длинные строки */
        overflow-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

st.title("Генератор проверок. Alpha0.1")

# Отдельная кнопка для добавления новых полей ввода URL
if st.button("➕ Добавить источник данных", key="add_url_main"):
    st.session_state.urls.append("")  # Добавляем новое пустое поле

# Добавляем поля ввода URL
for i in range(len(st.session_state.urls)):
    col1, col2 = st.columns([10, 1])
    with col1:
        st.session_state.urls[i] = st.text_input(
            f"Источник данных url {i+1}", 
            value=st.session_state.urls[i], 
            key=f"url_input_{i}",
            label_visibility="collapsed"  # Скрываем лейблы
        )

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
        # st.write("Результат:")
        # Адаптивная высота текстовой области в зависимости от размера контента
        # content_lines = len(generated_result.split('\n'))
        # calculated_height = min(max(300, content_lines * 20), 800)  # Высота от 300 до 800 пикселей
        # Используем текстовую область для прокрутки при большом объеме данных
        st.markdown(generated_result)
