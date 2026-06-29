from pathlib import Path

from typer.testing import CliRunner

from rgen.cli import app


runner = CliRunner()


def test_stats_command_works(tmp_path: Path):
    path = tmp_path / "tasks.jsonl"
    result = runner.invoke(app, ["generate", "--n", "8", "--seed", "42", "--out", str(path)])
    assert result.exit_code == 0
    result = runner.invoke(app, ["stats", str(path)])
    assert result.exit_code == 0
    assert "Dataset Statistics" in result.output


def test_split_command_creates_files(tmp_path: Path):
    path = tmp_path / "tasks.jsonl"
    out_dir = tmp_path / "splits"
    result = runner.invoke(app, ["generate", "--n", "10", "--seed", "42", "--out", str(path)])
    assert result.exit_code == 0
    result = runner.invoke(app, ["split", str(path), "--out-dir", str(out_dir)])
    assert result.exit_code == 0
    assert (out_dir / "train.jsonl").exists()
    assert (out_dir / "val.jsonl").exists()
    assert (out_dir / "test.jsonl").exists()


def test_report_command_creates_markdown_file(tmp_path: Path):
    path = tmp_path / "tasks.jsonl"
    report = tmp_path / "report.md"
    result = runner.invoke(app, ["generate", "--n", "12", "--seed", "42", "--out", str(path)])
    assert result.exit_code == 0
    result = runner.invoke(app, ["report", str(path), "--out", str(report)])
    assert result.exit_code == 0
    assert report.exists()
    assert "RGen Dataset Report" in report.read_text(encoding="utf-8")
