from app.utils import extract_json_payload

def test_extract():
    mock_supervisor = """```json\n{"status": "ok", "needs_policy": true, "needs_data": false, "clarification_question": null}\n```"""
    res1 = extract_json_payload(mock_supervisor)
    assert res1.get("status") == "ok"
    assert res1.get("needs_policy") is True
    print("test_extract passed")

if __name__ == "__main__":
    test_extract()
