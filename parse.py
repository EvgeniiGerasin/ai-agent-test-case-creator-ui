from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

llm = ChatOpenAI(model="openai/gpt-oss-120b", base_url="https://integrate.api.nvidia.com/v1")


def parse_content(dom_content: str, user_request: str = None) -> str:
    """
    Parse content using LLM to extract relevant information based on user request.
    
    Args:
        dom_content (str): The raw HTML content to parse
        user_request (str, optional): User's specific request or clarification
        
    Returns:
        str: The parsed and filtered content relevant to the user's request
    """
    # Base prompt to extract only relevant information
    base_prompt = """Извлеки всю релевантную информацию из следующего содержимого страницы.
    При этом исключи всю ненужную информацию типа рекламы, ссылок, навигационных элементов, 
    и других элементов, не относящихся к основному содержанию страницы.
    Оставь только ценную и релевантную информацию.
    
    Содержимое страницы:
    {dom_content}
    """
    
    # If user provided a specific request, incorporate it into the prompt
    if user_request and user_request.strip():
        full_prompt = base_prompt + f"\n\nКроме того, пользователь уточнил, что ему нужно следующее: {user_request}\nУчитывай это уточнение при извлечении информации."
    else:
        full_prompt = base_prompt
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Ты помощник, который извлекает полезную информацию из веб-страниц."),
        ("human", full_prompt)
    ])
    
    # Create the chain with the prompt and LLM
    chain = prompt | llm | StrOutputParser()
    
    # Invoke the chain to get the parsed content
    result = chain.invoke({"dom_content": dom_content})
    
    return result