from fastapi import APIRouter

from backend.workflows.ecommerce_graph import graph

router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)

@router.get("")
def get_insights():

    result = graph.invoke(
        {
            "query": "Show executive dashboard",
            "history": []
        }
    )

    print("=" * 80)
    print("GRAPH RESULT:")
    print(result)
    print("=" * 80)

    analysis = result.get("analysis")

    if analysis is None:
        raise Exception(f"Analysis missing. Result = {result}")

    analysis = result["analysis"]

    insights = [

        f"{analysis['delayed_orders']} delayed orders require attention.",

        f"{analysis['top_warehouse']} is currently the most affected warehouse.",

        f"{analysis['top_product']} has the highest delivery delays.",

        f"{analysis['top_complaint']} is the leading complaint category."
    ]

    return {
        "insights": insights
    }