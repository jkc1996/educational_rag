from src.llms import get_openai_llm
llm = get_openai_llm()
print(llm.invoke("Say hello in one sentence"))