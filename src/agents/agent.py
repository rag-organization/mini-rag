from langchain_core.messages import HumanMessage
from .graph import create_stylist_graph
from .tools.tool_factory import ToolFactory

class StylistAgent:

    def __init__(self, llm,dependencies,query):
        self.tools  = ToolFactory(dependencies=dependencies, query=query).create_tools()
        self.graph = create_stylist_graph(llm=llm, tools=self.tools)



    async def chat(self, message:str)->str:

        result = await self.graph.ainvoke(
            {
            "messages" : [HumanMessage(content=message)]
            },
            config={
                "recursion_limit": 16
            }
        )
        print(result)
        return result["messages"][-1].content
    
    