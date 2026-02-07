# Project Setup & Execution Guidelines

## Important: Use `uv` for Everything

This project uses **`uv`** as the package manager and task runner. Please follow these guidelines:

### Installation
- **Install dependencies**: Use `uv add <package_name>` instead of `pip install`
- **Remove dependencies**: Use `uv remove <package_name>` instead of `pip uninstall`
- **View dependencies**: Check `pyproject.toml` for project dependencies

### Execution
- **Run scripts**: Always use `uv run python <script_name>` instead of `python <script_name>`
- **Run commands**: Use `uv run <command>` for any project-related commands
- **Development mode**: Dependencies are automatically managed through `pyproject.toml`

### Why `uv`?
- Faster dependency resolution
- Consistent environments across all developers
- Better project isolation
- Simplified dependency management

### Project Dependencies
All project dependencies are specified in `pyproject.toml`. When adding new dependencies:
```bash
uv add package_name
```

This will automatically update `pyproject.toml` and create/update the lock file.
