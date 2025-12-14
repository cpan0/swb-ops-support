import pandas as pd
from graph import build_graph  # imports your LangGraph app
from pathlib import Path


def main(
    input_dir: str = "data",
    output_dir: str = "data/extracted",
):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    app = build_graph()

    # Loop over each csv file
    for input_csv in sorted(input_path.glob("*.csv")):
        output_csv = output_path / f"{input_csv.stem}_extracted.csv"

        # Load input CSV
        df = pd.read_csv(input_csv)

        if "name" not in df.columns:
            raise ValueError(f"{input_csv.name} must have a 'name' column.")

        extracted_rows = []

        # Loop over each NGO and call the graph
        for idx, row in df.iterrows():
            name = row["name"]
            print(f"[{input_csv.name}] Processing {idx + 1}/{len(df)}: {name}")

            try:
                state = app.invoke({"name": name})
            except Exception as e:
                print(f"Error processing '{name}' in {input_csv.name}: {e}")
                # If there's an error, record a row with empty fields
                extracted_rows.append(
                    {
                        "Your Name": "CP",
                        "Organization Name": name,
                        "Type of organization": "",
                        "Website URL": "",
                        "Contact name": "",
                        "Email of contact": "",
                        "Area of activity": "",
                        "Revenue": "",
                        "Number of employees": "",
                        "Countries served or impacted by the services of the organization (not necessarily where the org is located)": "",
                        "Done? (Y/N)": "Y",
                        "Comments": "",
                    }
                )
                continue

            extracted = state.get("extracted", {}) or {}

            # Build the row with the extracted info
            extracted_row = {
                "Your Name": "CP",
                "Organization Name": name,
                "Type of organization": extracted.get("Type of organization", ""),
                "Website URL": extracted.get("Website URL", ""),
                "Contact name": extracted.get("Contact name", ""),
                "Email of contact": extracted.get("Email of contact", ""),
                "Area of activity": extracted.get("Area of activity", ""),
                "Revenue": extracted.get("Revenue", ""),
                "Number of employees": extracted.get("Number of employees", ""),
                "Countries served or impacted by the services of the organization (not necessarily where the org is located)": extracted.get(
                    "Countries served or impacted by the services of the organization (not necessarily where the org is located)", ""
                ),
                "Done? (Y/N)": "Y",
                "Comments": extracted.get("Comments", ""),
            }

            extracted_rows.append(extracted_row)

        # Save to a new csv
        out_df = pd.DataFrame(extracted_rows)
        out_df.to_csv(output_csv, index=False)
        print(f"\nSaved extracted data to {output_csv}\n")


if __name__ == "__main__":
    main()
