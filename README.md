# almo-cli

almo-cli is a command line interface for the [almo](https://github.com/abap34/almo).

⚠️ This project is still in development and not ready for production use.

## Installation

```bash
pip install almo-cli@git+git+https://github.com/abap34/almo-cli.git
```


## Usage

almo-cli offers two commands: `almo-cli preview` and `almo-cli build`

`almo-cli preview` starts a local server to preview your article.

`almo-cli build` builds your article to a static html file.


```bash
almo-cli preview [-h] [-t TEMPLATE] [-s STYLE] [--editor_theme EDITOR_THEME] [--syntax_theme SYNTAX_THEME] [--config CONFIG] [-o OUTPUT] [--port PORT] [--allow-sharedarraybuffer] target
```

```bash
almo-cli build [-h] [-t TEMPLATE] [-s STYLE] [--editor_theme EDITOR_THEME] [--syntax_theme SYNTAX_THEME] [--config CONFIG] [-o OUTPUT] target
```

### Common options

| Argument | Description | 
| --- | --- |
| target | The target file or directory to preview. |
| -h, --help | Show this help message and exit. |
| -t TEMPLATE, --template TEMPLATE | The template to use. |
| -s STYLE, --style STYLE | The style to use. |
| --editor_theme EDITOR_THEME | The editor theme to use. |
| --syntax_theme SYNTAX_THEME | The syntax theme to use. |
| --config CONFIG | The configuration file to use. |
| -o OUTPUT, --output OUTPUT | The output directory. |
| --allow-sharedarraybuffer | Allow SharedArrayBuffer to terminate the worker. |

### `almo-cli preview` options

| Argument | Description |
| --- | --- |
| --port PORT | The port to use. |



