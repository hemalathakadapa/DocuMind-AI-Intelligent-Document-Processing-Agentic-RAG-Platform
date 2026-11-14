from pathlib import Path


from src.pipeline import process_invoice


def process_invoice_folder(
    input_folder: str,
    output_folder: str,
) -> list:

    input_path = Path(input_folder)
    output_path = Path(output_folder)

    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    pdf_files = list(input_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:

        json_file = output_path / f"{pdf_file.stem}.json"

        try:
            result = process_invoice(
                str(pdf_file),
                str(json_file),
            )

            results.append({
                "file": pdf_file.name,
                "status": "Success",
                "valid": result["is_valid"],
                "output": str(json_file),
            })

        except Exception as error:
            results.append({
                "file": pdf_file.name,
                "status": "Failed",
                "error": str(error),
            })

    return results