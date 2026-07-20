from agents.copilot_agent import ExpertCopilotAgent

def test_copilot_refuses_without_grounded_evidence():
    response = ExpertCopilotAgent().run({"query": "What is the shutdown procedure?", "retrieved_chunks": []})["final_response"]
    assert response["answer"] == "Insufficient documentation found to answer safely."
    assert response["citations"] == [] and response["confidence"] == 0.0
