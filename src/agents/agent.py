from langchain_core.messages import HumanMessage
from .graph import create_stylist_graph
from .tools.tool_factory import ToolFactory

class StylistAgent:

    def __init__(self, llm,dependencies):
        self.tools  = ToolFactory(dependencies=dependencies).create_tools()
        self.graph = create_stylist_graph(llm=llm, tools=self.tools)


    async def chat(self, message:str)->str:
        config = {"configurable": {"thread_id": "1"},
                "recursion_limit": 16}
        for tool in self.tools:
            print("Tool:", tool.name)
            print("Schema:", tool.args)

        result = await self.graph.ainvoke(
            {
            "messages" : [HumanMessage(content=message)]
            },
            config=config
        )
        print("\n=== FINAL GRAPH STATE ===")

        for msg in result["messages"]:
            print("Type:", msg.type)
            print("Content:", msg.content)
            print("Tool calls:", getattr(msg, "tool_calls", None))
            print("-----------------")

        return result["messages"][-1].content
    
    