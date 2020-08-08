import glob
import click
from indexer import index_file, search as index_search


@click.group()
def cli():
    pass


@cli.command()
@click.option('--dry-run', default=False, help='dry-run, does not index')
@click.argument('index_name')
@click.argument('directory')
def load(index_name, directory, dry_run):
    for text_file in glob.iglob(f"{directory}/*.txt"):
        index_file(index_name, text_file, index=not dry_run)


@cli.command()
@click.argument('index_name')
@click.argument('words')
def search(index_name, words):
    words = words.split(' ')
    data = index_search(index_name, words)
    for doc in data:
        print(doc)


if __name__ == '__main__':
    cli()
