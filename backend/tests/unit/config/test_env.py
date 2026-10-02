from pathlib import Path

from config import env


def test_repo_env_file_skipped_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")

    assert env.repo_env_file() is None


def test_repo_env_file_uses_absolute_repo_path(monkeypatch, tmp_path):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setattr(env, "_REPO_ROOT", tmp_path)
    missing = env.repo_env_file()
    assert missing is None

    dotenv = tmp_path / ".env"
    dotenv.write_text("X=1\n", encoding="utf-8")
    found = env.repo_env_file()
    assert found == dotenv
    assert found.is_absolute()


def test_settings_config_points_at_repo_env(monkeypatch, tmp_path):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.setattr(env, "_REPO_ROOT", tmp_path)
    (tmp_path / ".env").write_text("X=1\n", encoding="utf-8")

    config = env.settings_config()
    assert Path(config["env_file"]) == tmp_path / ".env"
