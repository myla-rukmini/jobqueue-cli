# JobQueue-CLI - Background Job Queue System

A CLI-based background job queue system with worker processes, retry mechanism, and Dead Letter Queue.

## Features

- ✅ Job enqueueing and management
- ✅ Multiple worker processes
- ✅ Exponential backoff retry mechanism
- ✅ Dead Letter Queue (DLQ)
- ✅ Persistent job storage
- ✅ Graceful worker shutdown
- ✅ Configurable retry counts and backoff

## Installation

```bash
# Navigate to the project directory
cd C:\Users\itsme\Downloads\jobqueue-cli

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install click