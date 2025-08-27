from langchain.prompts import ChatPromptTemplate
from ..config import get_llm

PROFILE_ANALYSIS_PROMPT = ChatPromptTemplate.from_template("""
You are an investment profile analyzer. Extract key investment characteristics from the user's message.

User Message: "{user_message}"
Previous Context: {conversation_history}

Extract and classify the following information:

1. Risk Tolerance (conservative/moderate/aggressive):
   - Conservative: Capital preservation, low volatility preference
   - Moderate: Balanced growth and income, some volatility tolerance  
   - Aggressive: Growth-focused, high volatility tolerance

2. Investment Horizon (short/medium/long):
   - Short: < 3 years
   - Medium: 3-10 years
   - Long: > 10 years

3. Age Range: young (18-35), middle-aged (36-55), senior (55+)

4. Income Level: low, medium, high (based on context clues)

5. Investment Goals: List specific goals mentioned (retirement, house, education, etc.)

Respond in this exact format:
RISK_TOLERANCE: [conservative/moderate/aggressive]
INVESTMENT_HORIZON: [short/medium/long]  
AGE_RANGE: [young/middle-aged/senior]
INCOME_LEVEL: [low/medium/high]
INVESTMENT_GOALS: [goal1, goal2, goal3]
REASONING: [2-3 sentence explanation of your analysis]
""")

def profile_analyzer_node(state):
    llm = get_llm()
    chain = PROFILE_ANALYSIS_PROMPT | llm
    
    result = chain.invoke({
        "user_message": state["user_message"],
        "conversation_history": state.get("conversation_history", [])
    })
    
    # Parse the structured response
    lines = result.content.strip().split("\n")
    parsed_data = {}
    
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower().replace("_", "_")
            value = value.strip()
            
            if key == "risk_tolerance":
                parsed_data["risk_tolerance"] = value
            elif key == "investment_horizon":
                parsed_data["investment_horizon"] = value
            elif key == "age_range":
                parsed_data["age_range"] = value
            elif key == "income_level":
                parsed_data["income_level"] = value
            elif key == "investment_goals":
                parsed_data["investment_goals"] = [g.strip() for g in value.split(",")]
            elif key == "reasoning":
                parsed_data["reasoning"] = value
    
    return parsed_data
