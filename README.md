# JobQueue-CLI

A CLI-based background job queue system with worker processes, retry mechanism, and Dead Letter Queue.

## Features

- ✅ Enqueue and manage background jobs
- ✅ Multiple worker processes
- ✅ Exponential backoff retry mechanism
- ✅ Dead Letter Queue (DLQ) for failed jobs
- ✅ Persistent job storage
- ✅ Configuration management
- ✅ Clean CLI interface

## Demo Video

[Demo](https://drive.google.com/file/d/1yI4XEFolvlHOAoZivmcSH_B71DShEd53/view?usp=sharing)

*Click the image above to watch the demo video*

## Installation

```bash
# Clone the repository
git clone https://github.com/myla-rukmini/jobqueue-cli.git
cd jobqueue-cli

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install package
pip install -e .
