
from pathlib import Path
from unittest.mock import patch




from src.batch_processor import process_invoice_folder

def test_batch_processing_success(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"

    input_folder.mkdir()

    (input_folder / "invoice1.pdf").touch()
    (input_folder / "invoice2.pdf").touch()

    def fake_process_invoice(input_path, output_path):
        Path(output_path).write_text("{}", encoding="utf-8")

        return {
            "is_valid": True,
            "output_path": output_path,
        }

    with patch(
        "src.batch_processor.process_invoice",
        side_effect=fake_process_invoice,
    ):
        results = process_invoice_folder(
            str(input_folder),
            str(output_folder),
        )

    assert len(results) == 2
    assert all(result["status"] == "Success" for result in results)


def test_batch_processing_continues_after_failure(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"

    input_folder.mkdir()

    (input_folder / "broken.pdf").touch()
    (input_folder / "valid.pdf").touch()

    def fake_process_invoice(input_path, output_path):
        if Path(input_path).name == "broken.pdf":
            raise ValueError("Invalid PDF")

        Path(output_path).write_text("{}", encoding="utf-8")

        return {
            "is_valid": True,
            "output_path": output_path,
        }

    with patch(
        "src.batch_processor.process_invoice",
        side_effect=fake_process_invoice,
    ):
        results = process_invoice_folder(
            str(input_folder),
            str(output_folder),
        )

    assert len(results) == 2

    failed_results = [
        result for result in results
        if result["status"] == "Failed"
    ]

    successful_results = [
        result for result in results
        if result["status"] == "Success"
    ]

    assert len(failed_results) == 1
    assert len(successful_results) == 1
    assert failed_results[0]["file"] == "broken.pdf"
    assert successful_results[0]["file"] == "valid.pdf"
