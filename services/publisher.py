from github import Github, InputGitTreeElement
from config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH, GITHUB_MENU_PATH

def publish_menu_json(content: str) -> str:
    """
    Updates menu.json on GitHub using the Contents API.
    Returns the commit SHA or error message.
    """
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)

    try:
        # Get current file to get its SHA
        file = repo.get_contents(GITHUB_MENU_PATH, ref=GITHUB_BRANCH)
        current_sha = file.sha

        result = repo.update_file(
            path=GITHUB_MENU_PATH,
            message=f"chore: update menu.json via Telegram Bot ({datetime_now()})",
            content=content,
            sha=current_sha,
            branch=GITHUB_BRANCH
        )
        return f"✅ Published successfully\nCommit: `{result['commit'].sha[:7]}`"
    except Exception as e:
        return f"❌ Publish failed: {str(e)}"

def datetime_now():
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")