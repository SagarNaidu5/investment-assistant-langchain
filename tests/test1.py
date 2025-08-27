from investment_assistant.config import get_llm
llm = get_llm()
print(llm.invoke("Say hello in one sentence"))
