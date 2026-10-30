from langchain_core.messages import HumanMessage
from .graph import create_stylist_graph
from .tools.tool_factory import ToolFactory
from deepeval.integrations.langchain import CallbackHandler
class StylistAgent:

    def __init__(self, llm,dependencies, checkpointer):
        self.tools  = ToolFactory(dependencies=dependencies).create_tools()
        self.graph = create_stylist_graph(llm=llm, tools=self.tools, checkpointer=checkpointer)


    async def chat(self, message:str, conversation_id:str)->str:
        config = {
                "configurable": {"thread_id": conversation_id},
                "recursion_limit": 16,
                "callbacks": [CallbackHandler()],
        }
        # for tool in self.tools:
        #     print("Tool:", tool.name)
        #     print("Schema:", tool.args)

        result = await self.graph.ainvoke(
            {
            "messages" : [HumanMessage(content=message)]
            },
            config=config
        )
        # print("\n=== FINAL GRAPH STATE ===")

        # for msg in result["messages"]:
        #     print("Type:", msg.type)
        #     print("Content:", msg.content)
        #     print("Tool calls:", getattr(msg, "tool_calls", None))
        #     print("-----------------")

        return result
    
    