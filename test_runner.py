#!/usr/bin/env python3
from investment_assistant.graph import investment_graph

def test_interactive():
    print("=== Investment Assistant - Step 5 Test ===")
    print("Try these example queries:")
    print("1. 'I'm 25 and want to start investing'")
    print("2. 'What is compound interest?'")
    print("3. 'Explain diversification'")
    print("4. 'Analyze Apple stock'")
    print("5. 'How does dollar cost averaging work?'")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'quit':
            break

        try:
            result = investment_graph.invoke({
                "user_message": user_input,
                "conversation_history": []
            })

            print(f"\nIntent: {result.get('intent', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")

            # Profile Analysis Results
            if result.get('intent') == 'profile_analysis':
                print(f"\n--- PROFILE ANALYSIS ---")
                print(f"Risk Tolerance: {result.get('risk_tolerance', 'unknown')}")
                print(f"Investment Horizon: {result.get('investment_horizon', 'unknown')}")
                print(f"Age Range: {result.get('age_range', 'unknown')}")
                print(f"Income Level: {result.get('income_level', 'unknown')}")
                print(f"Goals: {result.get('investment_goals', [])}")
                if result.get('reasoning'):
                    print(f"Analysis: {result.get('reasoning')}")

            # Portfolio Creation Results
            elif result.get('intent') == 'portfolio_creation':
                print(f"\n--- PORTFOLIO RECOMMENDATION ---")
                allocation = result.get('recommended_allocation', {})
                if allocation:
                    print("Asset Allocation:")
                    for asset_class, percentage in allocation.items():
                        print(f"  {asset_class.title()}: {percentage*100:.1f}%")
                etfs = result.get('etf_selection', [])
                if etfs:
                    print(f"\nETF Selection:")
                    total_weight = 0
                    for etf in etfs:
                        weight_pct = etf['weight'] * 100
                        price = etf.get('price', 0)
                        print(f"  {etf['ticker']}: {weight_pct:.1f}% @ ${price:.2f}")
                        total_weight += etf['weight']
                    print(f"  Total Weight: {total_weight*100:.1f}%")
                reasoning = result.get('builder_reasoning')
                if reasoning:
                    print(f"\nReasoning: {reasoning}")

            # Market Research Results
            elif result.get('intent') == 'market_research':
                print(f"\n--- MARKET RESEARCH ANALYSIS ---")
                symbol = result.get('stock_symbol', 'N/A')
                price = result.get('current_price', 0)
                change = result.get('price_change_pct', 0)
                print(f"Stock: {symbol}")
                print(f"Current Price: ${price:.2f} ({change:+.2f}%)")
                tech_signals = result.get('technical_signals', {})
                if tech_signals:
                    print(f"\nTechnical Signals:")
                    for indicator, signal in tech_signals.items():
                        print(f"  {indicator}: {signal.upper()}")
                ratios = result.get('fundamental_ratios', {})
                if ratios:
                    print(f"\nKey Ratios:")
                    print(f"  P/E Ratio: {ratios.get('PE_Ratio', 0):.1f}")
                    print(f"  ROE: {ratios.get('ROE', 0)*100:.1f}%")
                    print(f"  Debt/Equity: {ratios.get('Debt_To_Equity', 0):.2f}")
                rec = result.get('recommendation', 'HOLD')
                confidence = result.get('confidence_score', 0) * 100
                print(f"\nRecommendation: {rec} (Confidence: {confidence:.0f}%)")
                analysis = result.get('market_analysis', '')
                if analysis:
                    print(f"\nAnalysis Summary:")
                    lines = analysis.split('\n')
                    for line in lines:
                        if line.startswith('THESIS:'):
                            print(f"  {line}")
                            break

            # Educational Q&A Results
            elif result.get('intent') == 'question_answering':
                print(f"\n--- INVESTMENT EDUCATION ---")
                response = result.get('response', 'No response available.')
                print(f"\n{response}")
                concept = result.get('concept_explained')
                if concept:
                    print(f"\n📖 Concept Covered: {concept.replace('_', ' ').title()}")
                    related = result.get('related_concepts', [])
                    if related:
                        related_formatted = [c.replace('_', ' ').title() for c in related]
                        print(f"🔗 Related Topics: {', '.join(related_formatted)}")
                suggestion = result.get('suggestion')
                if suggestion:
                    print(f"\n💡 {suggestion}")

            # Other intents
            else:
                print(f"Intent '{result.get('intent')}' - Handler not yet implemented")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        print("-" * 60)

if __name__ == "__main__":
    test_interactive()
