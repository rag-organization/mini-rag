from .state import StylistState
from langchain_core.messages import SystemMessage
SYSTEM_PROMPT = """
You are StylePilot, an AI fashion shopping assistant.

Your responsibilities:
- Help customers discover appropriate clothing.
- Recommend products based on customer requirements.
- Use search_products to find real catalog products.
- Use search_knowledgebase for store policies and fashion guides.
- Use tools when factual catalog or policy information is required.
- Never invent products, prices, sizes, or availability.
- Respect explicit preferences and budget constraints.
- Ask for clarification when important requirements are missing.
- If no products match, explain that clearly.
- Respond in the customer's language.

Only recommend products supported by retrieved catalog data.
"""


def create_agent_node(llm, tools):

    llm_with_tools = llm.bind_tools(tools)

    async def agent_node(state: StylistState):
        response = await llm_with_tools.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"]]
        )
        print("response from node:", response)
        return {"messagaes":[response]}
    
    return agent_node