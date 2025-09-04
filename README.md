# DarwinCore to DataHub Metadata Translator

This tool translates metadata from DarwinCore Archive EML files to DataHub metadata template format. It can process both local DarwinCore archives and remote URLs from IPT (Integrated Publishing Toolkit) servers.

## Features

- **EML Parsing**: Extracts metadata from Ecological Metadata Language (EML) files
- **Template Population**: Populates DataHub Excel templates with translated metadata
- **Multiple Input Sources**: Supports local files and remote URLs
- **Creator Information**: Extracts and maps author/creator information
- **Geographic and Temporal Coverage**: Handles spatial and temporal metadata

## Installation

1. Create a conda environment:
```bash
conda env create -f conda-env.yml
conda activate TREC-eml-translator
```

## Usage

### Basic Usage

```bash
python trec_to_eml_translator.py <input> -o <output.xlsx>
```

### Examples

**Local DarwinCore archive:**
```bash
python trec_to_eml_translator.py data/dummy_dataset.zip -o output.xlsx
```

**Remote IPT URL:**
```bash
python trec_to_eml_translator.py "https://ipt.vliz.be/eurobis/resource?r=phytoplankton_in_the_western_north_sea_between_1976_and_1977" -o output.xlsx
```

### Command Line Options

- `input`: Input DarwinCore archive file or URL
- `-o, --output`: Output Excel file (default: datahub_metadata.xlsx)
- `-t, --template`: Template file (default: data/template.xlsx)

## Input Formats

### Local Files
- **DarwinCore Archive (.zip)**: Standard DarwinCore archive containing EML metadata
- **EML File (.xml)**: Direct EML metadata file

### Remote URLs
- **IPT URLs**: URLs from Integrated Publishing Toolkit servers (e.g., ipt.vliz.be)
- **Direct EML URLs**: URLs pointing directly to EML files

## Output Format

The translator populates the Excel template with multiple sheets:

1. **dataset**: Main dataset metadata (title, description, keywords, etc.)
2. **author**: Author/creator information

## Supported EML Elements

The translator extracts the following metadata from EML files:

### Dataset Information
- Title
- PID
- Abstract/Description
- Language
- Publication date
- License/Intellectual rights
- Keywords
- Acknowledgements

### Geographic Coverage
- Geographic description
- Bounding coordinates (latitude/longitude min/max)

### Temporal Coverage
- Start and end dates

### Creator Information
- Individual names (given name, surname)
- Organization affiliation
- Email addresses
- ORCID identifiers

## Testing

Run the full test suite with unit tests:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

This includes:
- Unit tests for each module
- Integration tests
- Command line interface tests

## License

This tool is provided as-is for the TREC to EML metadata translation project.

## Contributing

We use the **fork and pull request** workflow.

1. Fork this repository to your GitHub account.  
2. Create a new branch for your changes.
3. Make and commit your changes with clear messages.
4. Open a Pull Request from your forked branch to the main repository’s `main` branch.
5. Ensure (1) your PR description explains the purpose and scope of your changes and (2) the tests are passing.
