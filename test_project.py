from unittest import mock
from io import StringIO
from pytest import mark
import requests
from project import get_novel_title, search_requester, get_search_results, novel_picker

def test_get_novel_title(monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO('Harry Potter\n'))
    assert get_novel_title() == 'harry potter'


@mock.patch('requests.get')
def test_search_requester(mock_get):
    mock_response = mock.Mock()
    mock_response.content = 'test content'
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Test 1: Successful search request
    assert search_requester('harry potter') == 'test content'

    # Test 2: HTTP Error
    mock_get.side_effect = requests.exceptions.HTTPError
    assert search_requester('harry potter') is None

    # Test 3: Connection Error
    mock_get.side_effect = requests.exceptions.ConnectionError
    assert search_requester('harry potter') is None

    # Test 4: Timeout Error
    mock_get.side_effect = requests.exceptions.Timeout
    assert search_requester('harry potter') is None

    # Test 5: Unexpected Error
    mock_get.side_effect = requests.exceptions.RequestException
    assert search_requester('harry potter') is None


def test_novel_picker(capfd):
    search_results = [
        {'title': 'Harry Potter and the Philosopher’s Stone', 'link': '/novel/harry-potter-and-the-philosophers-stone/', 'chapters': 'Chapter 127'},
        {'title': 'Harry Potter and the Chamber of Secrets', 'link': '/novel/harry-potter-and-the-chamber-of-secrets/', 'chapters': 'Chapter 101'},
        {'title': 'Harry Potter and the Prisoner of Azkaban', 'link': '/novel/harry-potter-and-the-prisoner-of-azkaban/', 'chapters': 'Chapter 129'},
    ]
    
    # Test 1: Successful pick
    with mock.patch('builtins.input', side_effect=['2']):
        result = novel_picker(search_results)
        assert result['title'] == 'Harry Potter and the Chamber of Secrets'

    # Test 2: Invalid input
    with mock.patch('builtins.input', side_effect=['abc', '0']):
        result = novel_picker(search_results)
        out, err = capfd.readouterr()
        assert "Invalid input." in out

    # Test 3: Invalid index
    with mock.patch('builtins.input', side_effect=['5', '0']):
        result = novel_picker(search_results)
        out, err = capfd.readouterr()
        assert "Invalid input." in out


