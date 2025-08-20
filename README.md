# Lambda Layer Generator

A Python tool to automatically create AWS Lambda layers from Python packages and return their ARNs.

## Features

- ✅ **Create Lambda layers from package specifications**
- ✅ **Return layer ARNs for immediate use** 
- ✅ Parse comma-separated packages with version specifiers
- ✅ Support for all Python versions (3.8-3.12)
- ✅ Clean layer naming and descriptions
- ✅ Optimized layers with automatic cleanup
- ✅ Rich progress logging with timestamps
- ✅ CLI interface
- ✅ Robust error handling and validation

## Setup

### Prerequisites

- Python 3.8+
- AWS credentials configured via:
  - Environment variables, OR
  - `.env` file in project root

**Required AWS Environment Variables:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY` 
- `AWS_DEFAULT_REGION` or `AWS_REGION`

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

1. **Option 1: Environment Variables**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

2. **Option 2: .env File (Recommended)**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env with your credentials
   nano .env
   ```
   
   Your `.env` file should contain:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_DEFAULT_REGION=us-east-1
   ```

## Usage

### Generate Lambda Layers

```bash
# Create a layer with specific packages
python main.py "requests,pydantic==2.5.0"

# Use version specifiers
python main.py "boto3>=1.26.1,requests<=2.30.0"

# Specify Python runtime version
python main.py "requests==2.28.0,pymongo" --python-version python3.12

# Get JSON output with layer ARN
python main.py "boto3>=1.26.1" --json

# Quiet mode (no progress logs)
python main.py "requests,pydantic" --json --quiet
```

**Output:** Layer ARN ready to use in your Lambda functions!



## Input Format

### Package Specifications
- Single package: `"requests"`
- With exact version: `"requests==2.28.0"`
- With minimum version: `"boto3>=1.26.1"`
- With maximum version: `"requests<=2.30.0"`
- With compatible version: `"pymongo~=4.0.0"`
- With exclusion: `"pandas!=1.5.0"`
- Multiple packages: `"boto3>=1.26.1,requests==2.28.0,pydantic>=2.5.0"`

**Supported Version Specifiers:**
- `==` (exact version)
- `>=` (minimum version) 
- `>` (greater than)
- `<=` (maximum version)
- `<` (less than)
- `~=` (compatible release)
- `!=` (not equal)

### Python Versions
- `python3.8`
- `python3.9` 
- `python3.10`
- `python3.11`
- `python3.12`

## Layer Naming Convention

- Single package: `layer-{package-name}`
- Multiple packages: `layer-{package1}-{package2}-{package3}` (sorted, max 3)
- Only alphanumeric characters, hyphens, and underscores
- Versions excluded from layer names

## Error Handling

The application provides comprehensive error handling for:
- Invalid package specifications
- Missing AWS credentials or region
- Package installation failures
- AWS API errors
- Network connectivity issues

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── package_parser.py      # Package specification parsing
│   ├── layer_builder.py       # Layer creation and packaging
│   ├── aws_client.py          # AWS Lambda API client
│   ├── layer_generator.py     # Main orchestration logic
│   └── logger.py              # Pretty logging and progress tracking
├── main.py                    # CLI tool to generate layers
├── requirements.txt           # Dependencies
├── env.example                # Example environment file
├── .env                       # Your AWS credentials (create this)
└── README.md                  # This file
```

## License

MIT License 