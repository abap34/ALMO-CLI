import argparse
import logging
import pathlib

import almo
import jinja2
import yaml

from almo_cli import utils
from almo_cli.preview import PreviewRunner
from almo_cli.runner import loader


def parse_args():
    parser = argparse.ArgumentParser(
        description="almo-cli: A command line interface for ALMO"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments for both 'preview' and 'build' commands
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-t", "--template", type=str, help="Path to the template file", default=None
    )
    common_parser.add_argument(
        "-s", "--style", type=str, help="Path to the style file", default=None
    )
    common_parser.add_argument(
        "--editor_theme",
        type=str,
        help="Specify the editor theme",
        default="ace/theme/monokai",
    )
    common_parser.add_argument(
        "--syntax_theme",
        type=str,
        help="Specify the syntax theme",
        default="atom-one-dark",
    )

    common_parser.add_argument(
        "--config", type=str, help="Path to the configuration file", default=None
    )

    common_parser.add_argument(
        "-o", "--output", type=str, help="Path to the output file", default=None
    )

    # 'preview' command
    preview_parser = subparsers.add_parser(
        "preview", parents=[common_parser], help="Preview the HTML"
    )

    preview_parser.add_argument(
        "target",
        type=str,
        help="Path to the markdown file or directory to convert",
    )

    preview_parser.add_argument(
        "--port", help="Port for the preview server", type=int, default=5500
    )

    preview_parser.add_argument(
        "--allow-sharedarraybuffer",
        action="store_true",
        help="Allow SharedArrayBuffer in the preview",
        default=False,
    )

    # 'build' command
    build_parser = subparsers.add_parser(
        "build", parents=[common_parser], help="build the conversion"
    )
    build_parser.add_argument(
        "target",
        type=str,
        help="Path to the markdown file or directory to convert",
    )

    # 'version' argument
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s 0.0.1 (ALMO {almo.__version__})",
    )

    return parser.parse_args()


def fix_config(command_args: argparse.Namespace, config_from_file: dict) -> dict:
    """
    Fix the configuration by using the command line arguments if there is a conflict.
    If the configuration file is specified and the command line arguments are also specified,
    use the command line arguments with a warning.

    Args:
        command_args (argparse.Namespace): The command line arguments.
        config_from_file (dict): The configuration dictionary from the file.

    Returns:
        dict: The fixed configuration dictionary.
    """
    result = config_from_file.copy()

    # if command arg is not None, use it.
    for key in command_args.__dict__.keys():
        if command_args.__dict__[key] is not None:
            result[key] = vars(command_args)[key]

    # warn it.
    for key in config_from_file.keys():
        if command_args.__dict__[key] is not None:
            logging.warning(
                f"Warning: {key} is specified in both the configuration file and the command line arguments. Using the command line arguments."
            )

    return result


def build_hook(
    template_path: pathlib.Path,
    style_path: pathlib.Path,
    md_path: pathlib.Path,
    editor_theme: str,
    syntax_theme: str,
    output_path: pathlib.Path,
):
    def hook():
        md_content = md_path.read_text()

        try:
            front, content = utils.split_front_matter(md_content)
        except ValueError as e:
            logging.warning(
                f"Error in splitting front matter: {e}. Skipping conversion..."
            )

            return
        try:
            ast = almo.parse(content)

            need_pyodide = almo.required_pyodide(ast)

            almo.move_footnote_to_end(ast)
            
            content_html = ast.to_html()

        except Exception as e:
            logging.warning(f"Error in converting markdown to HTML: {e}")
            logging.warning("Skipping conversion...")
            return

        front_dict = yaml.safe_load(front)

        replace_dict = {
            "content": content_html,
            "editor_theme": editor_theme,
            "syntax_theme": syntax_theme,
        }

        if need_pyodide:
            replace_dict["runner"] = (
                '<script src="https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.js"></script> \n <script>\n'
                + loader
                + "\n</script>"
            )

        replace_dict.update(front_dict)

        template = template_path.read_text()
        style = style_path.read_text()

        replace_dict["style"] = style

        env = jinja2.Environment(loader=jinja2.BaseLoader())

        template = env.from_string(template)

        html = template.render(replace_dict)

        # Write to index.html
        output_path.write_text(html)

    return hook


def main():
    args = parse_args()

    # if config file is specified, load it and fix conflicts with command line arguments.
    if args.config:
        config: dict = fix_config(args, yaml.safe_load(open(args.config)))
    # if no config file is specified, use the command line arguments as the configuration.
    else:
        config: dict = vars(args)

    hook = build_hook(
        template_path=pathlib.Path(config["template"]),
        style_path=pathlib.Path(config["style"]),
        md_path=pathlib.Path(config["target"]),
        editor_theme=config["editor_theme"],
        syntax_theme=config["syntax_theme"],
        output_path=pathlib.Path(config["output"]),
    )

    if args.command == "preview":
        # add targets to the template and style.
        # to add these files to the watch list, we can develop template or style with livepreview.
        targets = [
            pathlib.Path(config["template"]),
            pathlib.Path(config["style"]),
            pathlib.Path(config["target"]),
        ]

        # Run first to generate the initial HTML file
        hook()

        preview_runner = PreviewRunner(
            hook=hook,
            port=args.port,
            targets=targets,
        )

        preview_runner.run()

    elif args.command == "build":
        hook()
