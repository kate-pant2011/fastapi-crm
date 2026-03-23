from rich.console import Console
from rich.tree import Tree
from pathlib import Path

console = Console()

def build_tree(directory: Path, tree: Tree):
    for path in sorted(directory.iterdir()):
        if path.name in {"__pycache__", ".git", "venv", ".idea"}:
            continue
        
        branch = tree.add(f"[bold blue]{path.name}" if path.is_dir() else path.name)
        
        if path.is_dir():
            build_tree(path, branch)

root_path = Path(".")
tree = Tree(f"[bold]{root_path.resolve()}")

build_tree(root_path, tree)

console.print(tree)