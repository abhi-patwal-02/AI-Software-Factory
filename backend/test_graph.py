from app.database import SessionLocal
from app.graph.workflow import build_factory_graph


db = SessionLocal()

try:
    graph = build_factory_graph(db)

    result = graph.invoke({
        "project_id": 3
    })

    print("\n===== GRAPH RESULT =====")
    print(result)

    if result.get("decision"):
        print("\n===== DECISION =====")
        print(
            result["decision"].model_dump_json(
                indent=2
            )
        )

finally:
    db.close()