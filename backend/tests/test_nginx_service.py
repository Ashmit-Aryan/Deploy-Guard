from app.services.nginx_service import NginxService


def test_switch_to_blue(tmp_path, monkeypatch):
    config_file = tmp_path / "upstream.conf"

    nginx_service = NginxService(str(config_file))

    monkeypatch.setattr(
        nginx_service,
        "test_config",
        lambda: True
    )

    monkeypatch.setattr(
        nginx_service,
        "reload",
        lambda: None
    )

    nginx_service.switch_traffic("blue")

    content = config_file.read_text()

    assert "127.0.0.1:8001" in content


def test_switch_to_green(tmp_path, monkeypatch):
    config_file = tmp_path / "upstream.conf"

    nginx_service = NginxService(str(config_file))

    monkeypatch.setattr(
        nginx_service,
        "test_config",
        lambda: True
    )

    monkeypatch.setattr(
        nginx_service,
        "reload",
        lambda: None
    )

    nginx_service.switch_traffic("green")

    content = config_file.read_text()

    assert "127.0.0.1:8002" in content


def test_invalid_environment(tmp_path):
    config_file = tmp_path / "upstream.conf"

    nginx_service = NginxService(str(config_file))

    try:
        nginx_service.switch_traffic("red")
        assert False
    except ValueError:
        assert True