import argparse
import yaml
import logging  

from almo_cli.preview import PreviewRunner

version_config = yaml.safe_load(open("almo_cli/version.yaml"))
almo_cli_version = version_config["almo-cli"]
almo_version = version_config["almo"]
__version__ = almo_cli_version

def parse_args():
    parser = argparse.ArgumentParser(description="almo-cli: A command line interface for ALMO")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments for both 'preview' and 'run' commands
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('-t', '--template', type=str, help="Path to the template file")
    common_parser.add_argument('-s', '--style', type=str, help="Path to the style file")
    common_parser.add_argument('--editortheme', type=str, help="Specify the editor theme")

    # 'preview' command
    preview_parser = subparsers.add_parser('preview', parents=[common_parser], help="Preview the HTML")
    preview_parser.add_argument('--config', type=str, help="Path to the configuration file")
    preview_parser.add_argument('--port', help="Port for the preview server", type=int)
    preview_parser.add_argument('--allow-sharedarraybuffer', action='store_true', help="Allow SharedArrayBuffer in the preview")

    # 'run' command
    run_parser = subparsers.add_parser('run', parents=[common_parser], help="Run the conversion")
    run_parser.add_argument('-o', '--output', type=str, help="Path to the output file")
    run_parser.add_argument('--json', action='store_true', help="Output the intermediate representation in JSON")
    run_parser.add_argument('--dot', action='store_true', help="Output the intermediate representation in DOT language")

    # 'version' argument
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__} (ALMO {almo_version})')

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
    for key, value in config_from_file.items():
        if key in vars(command_args):
            print(f"Warning: {key} is specified in both the configuration file and the command line arguments. Using the command line arguments.")
        config_from_file.update(vars(command_args))

    return config_from_file


def hook():
    logging.info("File changed. Reloading...")

def main():
    logger = logging.getLogger(__name__)
    args = parse_args()

    if args.command == 'preview':
        # if config file is specified, load it and fix conflicts with command line arguments.
        if args.config:
            config = yaml.safe_load(open(args.config))
            config = fix_config(args, config)
        # if no config file is specified, use the command line arguments as the configuration.
        else:
            config = vars(args)

        # remove `command` from the configuration
        config.pop('command')

        # add targets to the template and style.
        # to add these files to the watch list, we can develop template or style with livepreview.
        targets = []
        if args.template:
            targets.append(args.template)
            
        if args.style:
            targets.append(args.style)        
            
        preview_runner = PreviewRunner(hook=hook, targets=targets)
        preview_runner.run()

    elif args.command == 'run':
        print(f"Run conversion with template {args.template}, style {args.style}, and editor theme {args.editortheme}")
        if args.output:
            print(f"Output file: {args.output}")
        if args.json:
            print("Output intermediate representation in JSON")
        if args.dot:
            print("Output intermediate representation in DOT language")

