import json
import pytest
from review_contract import bind_response, result_record
from pruefworkflow import KiBefunde, Pruefkontext
from pruefung import vergleiche, referenz_extraktion_laden
from training_tools import pruefauftrag_laden


def response():
    order = pruefauftrag_laden("PR-001")
    context = Pruefkontext(**{k: order[k] for k in Pruefkontext.__dataclass_fields__})
    record = result_record(KiBefunde(context, vergleiche(referenz_extraktion_laden("1"), "1"), "referenz"))
    return {"id":"resp_test", "status":"completed", "agent_session_id":"public_session_test", "output":[{"content":[{"type":"output_text", "text":json.dumps(record)}]}]}


def test_completed_is_never_human_approval():
    bound = bind_response(response(), {"x-agent-session-id":"session_test"}, "PR-001")
    assert bound["result"]["human_approval_status"] == "not_requested"
    assert bound["result"]["dataverse_callback_status"] == "not_requested"
    assert bound["session_id"] == "public_session_test"
    assert bound["sandbox_id"] == "session_test"


@pytest.mark.parametrize("wrong", [None, "PR-999", "PR-201"])
def test_wrong_binding_fails_closed(wrong):
    with pytest.raises(ValueError): bind_response(response(), {}, wrong)


def test_explicit_rerun_gets_distinct_run_id():
    assert bind_response(response(), {}, "PR-001")["result"]["run_id"] != bind_response(response(), {}, "PR-001")["result"]["run_id"]


@pytest.mark.parametrize("field,value", [("asset_id", "A-200"), ("document_version", "2"),
    ("catalog_version", "99"), ("run_id", "not-a-uuid"), ("human_approval_status", "approved"),
    ("dataverse_callback_status", "created"), ("klaerungspunkte", []), ("befunde", [])])
def test_tampered_record_fails_closed(field, value):
    body = response()
    record = json.loads(body["output"][0]["content"][0]["text"])
    record[field] = value
    body["output"][0]["content"][0]["text"] = json.dumps(record)
    with pytest.raises(ValueError): bind_response(body, {}, "PR-001")


@pytest.mark.parametrize('field,value', [('agent_version',''),('agent_name',''),('befunde',[None]),('run_id','00000000-0000-0000-0000-000000000000')])
def test_malformed_identity_and_findings_fail_closed(field, value):
    body = response()
    record = json.loads(body['output'][0]['content'][0]['text'])
    record[field] = value
    body['output'][0]['content'][0]['text'] = json.dumps(record)
    with pytest.raises(ValueError): bind_response(body, {}, 'PR-001')


def test_wrong_agent_and_version_header_fail_closed():
    with pytest.raises(ValueError): bind_response(response(), {}, 'PR-001', expected_agent='kuenz-pruefung-trainer')
    with pytest.raises(ValueError): bind_response(response(), {'x-ms-agent-version':'other-version'}, 'PR-001')
