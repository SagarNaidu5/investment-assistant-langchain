from typing import Dict, List
from ..knowledge.financial_concepts import FinancialKnowledgeBase
from ..config import get_llm
from langchain.prompts import ChatPromptTemplate

EDUCATIONAL_PROMPT = ChatPromptTemplate.from_template("""
You are a patient, knowledgeable investment educator. A user has asked about a financial concept, and you have access to educational content to help them understand.

User Question: {user_question}

Relevant Financial Concept Information:
{concept_info}

Your task is to:
1. Provide a clear, beginner-friendly explanation of the concept
2. Include a practical example if available
3. Mention related concepts they might want to learn about
4. Use encouraging, educational tone

Keep your response informative but accessible, around 200-300 words. Focus on helping the user understand rather than overwhelming them with details.
""")

GENERAL_QUERY_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful investment education assistant. The user has asked a general investment question that doesn't match a specific concept in your knowledge base.

User Question: {user_question}

Provide a helpful, educational response based on your knowledge of investment fundamentals. Keep it:
- Clear and beginner-friendly
- Around 150-250 words
- Practical and actionable
- Encouraging for new investors

If the question is too complex or requires personalized advice, recommend consulting with a financial advisor.
""")

def extract_financial_concepts(query: str) -> List[str]:
    """Extract potential financial concepts from user query"""
    concept_keywords = {
        'compound interest': ['compound', 'compounding', 'growth'],
        'diversification': ['diversify', 'diversification', 'spread risk'],
        'pe_ratio': ['p/e ratio', 'pe ratio', 'price earnings', 'price to earnings'],
        'stocks': ['stock', 'shares', 'equity', 'share market'],
        'bonds': ['bond', 'fixed income', 'debt securities'],
        'mutual_funds': ['mutual fund', 'mutual funds', 'fund'],
        'etf': ['etf', 'exchange traded fund', 'index fund'],
        'risk_return_relationship': ['risk return', 'risk vs return', 'risk reward'],
        'dollar_cost_averaging': ['dollar cost', 'sip', 'systematic investment'],
        'asset_allocation': ['asset allocation', 'portfolio allocation'],
        'inflation': ['inflation', 'purchasing power'],
        'market_volatility': ['volatility', 'market fluctuation'],
        'roe': ['roe', 'return on equity'],
        'time_value_of_money': ['time value', 'present value', 'future value']
    }
    
    query_lower = query.lower()
    found_concepts = []
    
    for concept, keywords in concept_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            found_concepts.append(concept)
    
    return found_concepts

def format_concept_info(concept_data: Dict) -> str:
    """Format concept data for the LLM prompt"""
    if not concept_data:
        return "No specific concept information found."
    
    formatted = f"Definition: {concept_data.get('definition', 'N/A')}\n\n"
    
    if 'key_points' in concept_data:
        formatted += "Key Points:\n"
        for point in concept_data['key_points']:
            formatted += f"• {point}\n"
        formatted += "\n"
    
    if 'example' in concept_data:
        formatted += f"Example: {concept_data['example']}\n\n"
    
    if 'formula' in concept_data:
        formatted += f"Formula: {concept_data['formula']}\n\n"
    
    if 'types' in concept_data:
        formatted += "Types:\n"
        if isinstance(concept_data['types'], dict):
            for type_name, description in concept_data['types'].items():
                formatted += f"• {type_name}: {description}\n"
        elif isinstance(concept_data['types'], list):
            for type_item in concept_data['types']:
                formatted += f"• {type_item}\n"
        formatted += "\n"
    
    if 'related_concepts' in concept_data:
        related = ', '.join(concept_data['related_concepts'])
        formatted += f"Related Concepts: {related}\n"
    
    return formatted

def question_answerer_node(state: Dict) -> Dict:
    """Handle general investment education questions"""
    
    user_message = state.get("user_message", "")
    kb = FinancialKnowledgeBase()
    
    # Try to find matching financial concepts
    concept_matches = extract_financial_concepts(user_message)
    
    if concept_matches:
        # Found specific concept(s) - provide detailed educational response
        primary_concept = concept_matches[0]  # Use the first match
        concept_info = kb.get_concept(primary_concept)
        
        llm = get_llm()
        chain = EDUCATIONAL_PROMPT | llm
        
        response = chain.invoke({
            "user_question": user_message,
            "concept_info": format_concept_info(concept_info)
        })
        
        # Suggest related concepts
        related_suggestions = []
        if 'related_concepts' in concept_info:
            related_suggestions = concept_info['related_concepts'][:3]
        
        return {
            "response": response.content,
            "concept_explained": primary_concept,
            "related_concepts": related_suggestions,
            "education_type": "concept_explanation"
        }
    
    else:
        # General investment question - provide general guidance
        llm = get_llm()
        chain = GENERAL_QUERY_PROMPT | llm
        
        response = chain.invoke({
            "user_question": user_message
        })
        
        return {
            "response": response.content,
            "education_type": "general_guidance",
            "suggestion": "For more specific concepts, try asking about topics like 'compound interest', 'diversification', or 'asset allocation'."
        }

def get_random_learning_tip() -> str:
    """Provide a random investment learning tip"""
    tips = [
        "💡 Start early: Time is your biggest ally in building wealth through compound interest.",
        "📚 Learn continuously: The investment landscape evolves, so keep educating yourself.",
        "🎯 Set clear goals: Know what you're investing for before you start investing.",
        "⚖️ Balance is key: Diversification helps manage risk without sacrificing returns.",
        "📈 Think long-term: The stock market rewards patient investors over time.",
        "💰 Invest regularly: Dollar-cost averaging can smooth out market volatility.",
        "🔍 Understand what you buy: Never invest in something you don't understand.",
        "📊 Review periodically: Check your portfolio quarterly, not daily."
    ]
    import random
    return random.choice(tips)
