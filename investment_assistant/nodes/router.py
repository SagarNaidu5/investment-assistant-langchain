from langchain.prompts import ChatPromptTemplate
from ..config import get_llm

ROUTER_PROMPT = ChatPromptTemplate.from_template("""
You are an investment assistant router. Analyze the user's message and determine their primary intent.

User Message: "{user_message}"

Classify into one of these categories:
1. profile_analysis - User wants to discuss their investment profile, risk tolerance, goals
2. portfolio_creation - User wants portfolio recommendations or asset allocation advice  
3. market_research - User asks about specific stocks, market trends, economic analysis
4. question_answering - General investment education, explaining concepts, how-to questions

Examples for question_answering:
- "What is compound interest?"
- "How does diversification work?"
- "Explain P/E ratio"
- "What's the difference between stocks and bonds?"
- "How to start investing?"
- "What is dollar cost averaging?"

Respond with ONLY the category name and a confidence score (0-1).
Format: category_name|confidence_score

Examples:
- "I'm 30 years old and want to start investing" → profile_analysis|0.95
- "What stocks should I buy?" → portfolio_creation|0.85
- "How is Tesla performing?" → market_research|0.90
- "What is a P/E ratio?" → question_answering|0.95
""")

def router_node(state):
    llm = get_llm()
    chain = ROUTER_PROMPT | llm
    
    result = chain.invoke({"user_message": state["user_message"]})
    
    try:
        intent, confidence = result.content.strip().split("|")
        confidence = float(confidence)
    except:
        # Fallback for parsing errors
        intent = "question_answering"
        confidence = 0.5
    
    return {
        "intent": intent,
        "confidence": confidence
    }
