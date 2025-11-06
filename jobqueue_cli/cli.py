import click
import json
import sys
from jobqueue_cli.core import QueueManager
from jobqueue_cli.storage import JSONStorage
from jobqueue_cli.worker import WorkerManager
from jobqueue_cli.config import ConfigManager
from jobqueue_cli.models import Job

@click.group()
@click.pass_context
def cli(ctx):
    """JobQueue-CLI - Background Job Queue System"""
    storage = JSONStorage()
    queue_manager = QueueManager(storage)
    worker_manager = WorkerManager(queue_manager)
    config_manager = ConfigManager(storage)
    
    ctx.obj = {
        'queue_manager': queue_manager,
        'worker_manager': worker_manager,
        'config_manager': config_manager
    }

@cli.command()
@click.argument('job_spec')
@click.pass_context
def enqueue(ctx, job_spec):
    """Enqueue a new job"""
    try:
        # Try to parse as JSON first
        if job_spec.startswith('{'):
            job_data = json.loads(job_spec)
            job_id = job_data.get('id')
            command = job_data['command']
            max_retries = job_data.get('max_retries', 3)
        else:
            # Treat as plain command
            job_id = None
            command = job_spec
            max_retries = 3
        
        queue_manager = ctx.obj['queue_manager']
        job = queue_manager.enqueue_job(command, job_id, max_retries)
        
        click.echo(f"Enqueued job: {job.id}")
        click.echo(f"Command: {job.command}")
        click.echo(f"State: {job.state}")
        
    except Exception as e:
        click.echo(f"Error enqueueing job: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--count', default=1, help='Number of workers to start')
@click.pass_context
def start(ctx, count):
    """Start worker processes"""
    worker_manager = ctx.obj['worker_manager']
    worker_manager.start_workers(count)

@cli.command()
@click.pass_context
def stop(ctx):
    """Stop all worker processes"""
    worker_manager = ctx.obj['worker_manager']
    worker_manager.stop_workers()

@cli.command()
@click.pass_context
def status(ctx):
    """Show queue status and active workers"""
    queue_manager = ctx.obj['queue_manager']
    worker_manager = ctx.obj['worker_manager']
    
    stats = queue_manager.get_stats()
    worker_status = worker_manager.get_worker_status()
    
    click.echo("=== Queue Status ===")
    click.echo(f"Total jobs: {stats['total']}")
    click.echo(f"Pending: {stats['pending']}")
    click.echo(f"Processing: {stats['processing']}")
    click.echo(f"Completed: {stats['completed']}")
    click.echo(f"Failed: {stats['failed']}")
    click.echo(f"Dead: {stats['dead']}")
    
    click.echo("\n=== Worker Status ===")
    click.echo(f"Active workers: {worker_status['active_workers']}")
    for worker in worker_status['workers']:
        current_job = worker['current_job'] or "idle"
        click.echo(f"  {worker['id']}: {current_job}")

@cli.command()
@click.option('--state', type=click.Choice(['pending', 'processing', 'completed', 'failed', 'dead']), 
              help='Filter jobs by state')
@click.pass_context
def list(ctx, state):
    """List jobs, optionally filtered by state"""
    queue_manager = ctx.obj['queue_manager']
    storage = queue_manager.storage
    
    if state:
        jobs = storage.get_jobs_by_state(state)
    else:
        jobs = storage.get_all_jobs()
    
    for job in jobs:
        click.echo(f"{job.id}: {job.command} [{job.state}] (attempts: {job.attempts})")

@cli.group()
def dlq():
    """Dead Letter Queue operations"""
    pass

@dlq.command()
@click.pass_context
def list(ctx):
    """List jobs in Dead Letter Queue"""
    queue_manager = ctx.obj['queue_manager']
    storage = queue_manager.storage
    
    dead_jobs = storage.get_jobs_by_state("dead")
    
    if not dead_jobs:
        click.echo("No jobs in Dead Letter Queue")
        return
    
    for job in dead_jobs:
        click.echo(f"{job.id}: {job.command}")
        click.echo(f"  Last error: {job.last_error}")
        click.echo(f"  Attempts: {job.attempts}/{job.max_retries}")
        click.echo()

@dlq.command()
@click.argument('job_id')
@click.pass_context
def retry(ctx, job_id):
    """Retry a job from Dead Letter Queue"""
    queue_manager = ctx.obj['queue_manager']
    
    if queue_manager.retry_dead_job(job_id):
        click.echo(f"Job {job_id} moved back to pending queue")
    else:
        click.echo(f"Job {job_id} not found in DLQ or not dead", err=True)
        sys.exit(1)

@cli.group()
def config():
    """Configuration management"""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set(ctx, key, value):
    """Set a configuration value"""
    config_manager = ctx.obj['config_manager']
    config_manager.set_config(key, value)
    click.echo(f"Set {key} = {value}")

@config.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    """Get a configuration value"""
    config_manager = ctx.obj['config_manager']
    value = config_manager.get_config(key)
    click.echo(f"{key} = {value}")

@config.command()
@click.pass_context
def list(ctx):
    """List all configuration values"""
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_all_config()
    
    for key, value in config.items():
        click.echo(f"{key} = {value}")

if __name__ == '__main__':
    cli()