import pytest
import requests

def test_fetchemplleaverequestlist(base_url):
    url = f"{base_url}/rest/v2/dailybiz"
    headers = {"Content-Type": "application/json"}
    params = {}
    response = requests.get(url, headers=headers, params=params)

    # Assertions
    assert response.status_code in [200, 200, 201], f'Expected 200/200/201, got {response.status_code}'
    assert "{'employeeLeavesResult': {'employeeId': '927', 'labelList': [{'labelName': 'Pending', 'labelValue': 4}, {'labelName': 'Recommend', 'labelValue': 0}, {'labelName': 'Verified', 'labelValue': 6}, {'labelName': 'Approved', 'labelValue': 5}, {'labelName': 'Rejected', 'labelValue': 0}, {'labelName': 'Created', 'labelValue': 0}, {'labelName': 'All', 'labelValue': 15}], 'leaveList': [{'leaveTypeDesc': 'Casual Leave', 'partyId': '1061', 'partyName': 'RAGHU D R', 'leaveTypeId': 'CL', 'leaveStatus': 'Approved', 'leaveFromDate': 'Dec 05, 2025', 'leaveThruDate': 'Dec 05, 2025', 'comment': None, 'emplLeaveApplId': '35736', 'appliedDate': 'Dec 06, 2025', 'leaveCountDays': 1.0, 'status': 'Approved', 'nextLevelStatusList': [{'id': 'LEAVE_REJECTED', 'description': 'REJECTED'}, {'id': 'LEAVE_REJECTED', 'description': 'REJECTED'}]}]}}" in response.text, 'Expected response to contain "{'employeeLeavesResult': {'employeeId': '927', 'labelList': [{'labelName': 'Pending', 'labelValue': 4}, {'labelName': 'Recommend', 'labelValue': 0}, {'labelName': 'Verified', 'labelValue': 6}, {'labelName': 'Approved', 'labelValue': 5}, {'labelName': 'Rejected', 'labelValue': 0}, {'labelName': 'Created', 'labelValue': 0}, {'labelName': 'All', 'labelValue': 15}], 'leaveList': [{'leaveTypeDesc': 'Casual Leave', 'partyId': '1061', 'partyName': 'RAGHU D R', 'leaveTypeId': 'CL', 'leaveStatus': 'Approved', 'leaveFromDate': 'Dec 05, 2025', 'leaveThruDate': 'Dec 05, 2025', 'comment': None, 'emplLeaveApplId': '35736', 'appliedDate': 'Dec 06, 2025', 'leaveCountDays': 1.0, 'status': 'Approved', 'nextLevelStatusList': [{'id': 'LEAVE_REJECTED', 'description': 'REJECTED'}, {'id': 'LEAVE_REJECTED', 'description': 'REJECTED'}]}]}}"'
