import yaml

with open("version.txt") as f:
    version = f.read().strip()

version_config = yaml.safe_load(open("almo_cli/version.yaml"))
version_config["almo"] = version

with open("almo_cli/version.yaml", "w") as f:
    yaml.dump(version_config, f)
