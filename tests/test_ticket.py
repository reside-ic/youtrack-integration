from unittest.mock import MagicMock, patch
from flask import json
from src.app.Ticket import Ticket
from src.app.YouTrackAPI import YouTrackAPI

requested_payload = json.loads("""{
    "action": "review_requested",
    "number": 2,
    "pull_request": {
        "url": "https://api.github.com/repos/Codertocat/Hello-World/pulls/2",
        "html_url": "https://github.com/Codertocat/Hello-World/pull/2",
        "state": "open",
        "user": {
            "login": "Codertocat"
        },
        "head": {
            "label": "Codertocat:changes",
            "ref": "RESIDE-11"
        },
        "requested_reviewers": [
            {
                "login": "Octocat"
            }
        ]
    }
}""")

approved_payload = json.loads("""{
  "action": "submitted",
  "review": {
    "id": 237895671,
    "node_id": "MDE3OlB1bGxSZXF1ZXN0UmV2aWV3MjM3ODk1Njcx",
    "user": {
      "login": "Octocat"
    },
    "state": "approved",
    "html_url": "https://github.com/Codertocat/Hello-World/pull/2#pullrequestreview-237895671"
  },
  "pull_request": {
      "url": "https://api.github.com/repos/Codertocat/Hello-World/pulls/2",
      "html_url": "https://github.com/Codertocat/Hello-World/pull/2",
      "user": {
            "login": "Codertocat"
      },
      "head": {
            "label": "Codertocat:changes",
            "ref": "RESIDE-11"
        }
  }
}""")

closed_payload = json.loads("""{
  "action": "closed",
  "review": {
    "id": 237895671,
    "node_id": "MDE3OlB1bGxSZXF1ZXN0UmV2aWV3MjM3ODk1Njcx",
    "user": {
      "login": "Octocat"
    },
    "state": "commented",
    "html_url": "https://github.com/Codertocat/Hello-World/pull/2#pullrequestreview-237895671"
  },
  "pull_request": {
     "merged": false,
     "url": "https://api.github.com/repos/Codertocat/Hello-World/pulls/2",
     "html_url": "https://github.com/Codertocat/Hello-World/pull/2",
     "user": {
        "login": "Codertocat"
     },
     "head": {
        "label": "Codertocat:changes",
        "ref": "RESIDE-11"
     }
  }
}""")


commented_payload = json.loads("""{
  "action": "submitted",
  "review": {
    "id": 237895671,
    "node_id": "MDE3OlB1bGxSZXF1ZXN0UmV2aWV3MjM3ODk1Njcx",
    "user": {
      "login": "Octocat"
    },
    "state": "commented",
    "html_url": "https://github.com/Codertocat/Hello-World/pull/2#pullrequestreview-237895671"
  },
  "pull_request": {
     "merged": false,
     "url": "https://api.github.com/repos/Codertocat/Hello-World/pulls/2",
     "html_url": "https://github.com/Codertocat/Hello-World/pull/2",
     "user": {
        "login": "Codertocat"
     },
     "head": {
        "label": "Codertocat:changes",
        "ref": "RESIDE-11"
     }
  }
}""")


own_reviewer_payload = json.loads("""{
  "action": "submitted",
  "review": {
    "id": 237895671,
    "node_id": "MDE3OlB1bGxSZXF1ZXN0UmV2aWV3MjM3ODk1Njcx",
    "user": {
      "login": "Octocat"
    },
    "state": "commented",
    "html_url": "https://github.com/Codertocat/Hello-World/pull/2#pullrequestreview-237895671"
  },
  "pull_request": {
     "url": "https://api.github.com/repos/Codertocat/Hello-World/pulls/2",
     "html_url": "https://github.com/Codertocat/Hello-World/pull/2",
     "user": {
        "login": "Octocat"
     },
     "head": {
        "label": "Codertocat:changes",
        "ref": "RESIDE-11"
     }
  }
}""")

merged_payload = json.loads("""{
  "action": "closed",
  "review": {
    "id": 237895671,
    "node_id": "MDE3OlB1bGxSZXF1ZXN0UmV2aWV3MjM3ODk1Njcx",
    "user": {
      "login": "Octocat"
    },
    "state": "commented",
    "html_url": "https://github.com/Codertocat/Hello-World/pull/2#pullrequestreview-237895671"
  },
  "pull_request": {
     "merged": true,
     "url": "https://api.github.com/repos/Codertocat/Hello-World/pulls/2",
     "html_url": "https://github.com/Codertocat/Hello-World/pull/2",
     "user": {
        "login": "Codertocat"
     },
     "head": {
        "label": "Codertocat:changes",
        "ref": "RESIDE-11"
     }
  }
}""")

mock_user_dict = {
    "Codertocat": "cc",
    "Octocat": "oc"
}


def test_ticket_exists():
    mock_api = YouTrackAPI("instance", "token")
    sut = Ticket(requested_payload, mock_api, {})
    assert sut.exists() is True


def test_ticket_does_not_exist():
    mock_api = YouTrackAPI("instance", "token")
    requested_payload["pull_request"]["head"]["ref"] = "someotherbranch"
    sut = Ticket(requested_payload, mock_api, {})
    assert sut.exists() is False
    requested_payload["pull_request"]["head"]["ref"] = "RESIDE-11"


def test_update_does_nothing_on_approval():
    mock_api = YouTrackAPI("instance", "token")
    mock_api.update_ticket = MagicMock(return_value=(True, {}))
    sut = Ticket(approved_payload, mock_api, mock_user_dict)
    result = sut.update()
    assert mock_api.update_ticket.called is False
    assert result == ('', 200)


def test_update_does_nothing_if_reviewer_is_author():
    mock_api = YouTrackAPI("instance", "token")
    mock_api.update_ticket = MagicMock(return_value=(True, {}))
    sut = Ticket(own_reviewer_payload, mock_api, mock_user_dict)
    result = sut.update()
    assert mock_api.update_ticket.called is False
    assert result == ('', 200)


def test_update_reopens_ticket_if_not_approved():
    mock_api = YouTrackAPI("instance", "token")
    mock_api.update_ticket = MagicMock(return_value=(True, {}))
    sut = Ticket(commented_payload, mock_api, mock_user_dict)
    result = sut.update()
    mock_api.update_ticket.assert_called_with("RESIDE-11",
                                                     commands=['state Reopened', 'for cc'],
                                                     comment="https://github.com/Codertocat/Hello-World/pull/2#pullrequestreview-237895671")
    assert result == ('', 200)


def test_submits_ticket():
    mock_api = YouTrackAPI("instance", "token")
    mock_api.update_ticket = MagicMock(return_value=(True, {}))
    sut = Ticket(requested_payload, mock_api, mock_user_dict)
    result = sut.update()
    mock_api.update_ticket.assert_called_with("RESIDE-11",
                                                     commands=['state Submitted', 'for oc'],
                                                     comment="https://github.com/Codertocat/Hello-World/pull/2")
    assert result == ('', 200)


def test_closes_ticket():
    mock_api = YouTrackAPI("instance", "token")
    mock_api.update_ticket = MagicMock(return_value=(True, {}))
    sut = Ticket(merged_payload, mock_api, mock_user_dict)
    result = sut.update()
    mock_api.update_ticket.assert_called_with("RESIDE-11",
                                                     commands=['state Ready to deploy', 'for Unassigned'])
    assert result == ('', 200)


def test_does_not_close_ticket_if_not_merged():
    mock_api = YouTrackAPI("instance", "token")
    mock_api.update_ticket = MagicMock(return_value=(True, {}))
    sut = Ticket(closed_payload, mock_api, mock_user_dict)
    result = sut.update()
    assert mock_api.update_ticket.called is False
    assert result == ('', 200)
