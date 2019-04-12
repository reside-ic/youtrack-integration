from src.app.YouTrackHelper import YouTrackHelper


def test_can_match_old_branch_names():
    result = YouTrackHelper.get_issue_id("i637")
    assert result == "VIMC-637"

    result = YouTrackHelper.get_issue_id("i123_something")
    assert result == "VIMC-123"


def test_can_match_new_branch_names():
    result = YouTrackHelper.get_issue_id("VIMC-637")
    assert result == "VIMC-637"

    result = YouTrackHelper.get_issue_id("mrc-123_something")
    assert result == "mrc-123"


def test_does_not_match_arbitrary_branch_names():
    result = YouTrackHelper.get_issue_id("refactor")
    assert result is None
