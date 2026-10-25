from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from .nodes import create_agent_node
from .state import StylistState

def create_stylist_graph(llm, tools):
    ## create graph
    graph = StateGraph(StylistState)

    # create nodes

    agent_node = create_agent_node(llm=llm, tools=tools)
    tools_node = ToolNode(tools=tools, handle_tool_errors=False)

    print("agent_node: ",agent_node)
    print("tool_node: ", tools_node)
    # add nodes & edges

    graph.add_node("assistant", agent_node)
    graph.add_node("tools", tools_node)

    graph.add_edge(START, "assistant")
    graph.add_conditional_edges(
        "assistant",
        tools_condition,
        {
            "tools":"tools",
            "__end__":END
        }
    )
    print("graph created")
    graph.add_edge("tools", "assistant")

    print(graph)
    # compile

    return graph.compile()
