# Reciprocity

Reciprocity is a CLI and daemon for converting recipe scans to Markdown.

## Motivation

I have a lot of cookbooks. Among those cookbooks are a far fewer number of recipes that I consider go-tos, and which I want to have on-hand. I have been scanning recipes that I like and dumping them into my notes as PDFs for a long time, but eventually I end up needing to transcribe them into Markdown by hand so that I can add notes and tweaks.

Reciprocity provides a pipeline for converting PDF recipes to a consistent Markdown format. Once converted to Markdown, I can manually edit my recipes as part of my own note-taking system.

I know that there are a number of other FOSS recipe management solutions available. I have not taken a comprehensive look at the options, but my understanding is that most of them take a heavyweight database + web-UI approach rather than simply treating recipes as notes. Those other solutions may be more suited to most peoples' personal needs; this is the tool that suits mine.

## Dependencies

1. [Poppler](https://poppler.freedesktop.org/) (specifically `pdftoppm`) is needed for converting PDFs into images
2. [Tesseract OCR](https://tesseract-ocr.github.io/) is needed for converting images into plaintext
3. [Ollama](https://ollama.com/) is needed for running a locally-hosted LLM to coerce plaintext recipes into templated Markdown
   - Note that Reciprocity does not support cloud models, and that it builds its own model automatically by pairing `qwen3:1.7b` with a system prompt

You can run `reciprocity setup` to confirm that your environment has all the required dependencies available.

## Installation

Reciprocity is not currently published to any package repositories, but there is a `flake.nix` file in this repository that you can use to install it.

You can run Reciprocity directly via `nix run github:ciarandg/reciprocity`, or install it by adding the repository to your config as a Flake input and then adding `inputs.reciprocity.packages.<system>.reciprocity` to your `environment.systemPackages` or `home.packages`.

Another option is to clone this repo and use `uv` directly to run Reciprocity, e.g. `uv run reciprocity`.

## Usage

Reciprocity provides three subcommands:

1. `setup`: Confirms that external dependencies are available, and builds the custom Ollama model if not yet available
2. `read`: Takes one or more `-i <path>` options to PDF or image files that comprise a single recipe, uses [Tesseract OCR](https://tesseract-ocr.github.io/) via [pytesseract](https://pypi.org/project/pytesseract/) to convert them into plaintext, and writes them to `stdout`
3. `format`: Takes plaintext via `stdin` or reads from a file provided via a `-i <path>` option, builds a custom Ollama model if not yet available, and then uses that model to coerce the input plaintext into the [built-in Markdown template](./reciprocity/data/template.txt)
3. `watch`: Launches a daemon that monitors an input directory at `-i <path>` for new files, reads them via OCR, formats them with an Ollama model, and writes them to an output directory at `-o <path>`.

## Examples

```bash
# Check dependencies and build Ollama model if necessary
reciprocity setup

# Run OCR on a two-page recipe and write plaintext to stdout
reciprocity read -i ~/recipes/cake-1.png -i ~/recipes/cake-2.png

# Convert a recipe PDF to plaintext and write it to a text file
reciprocity read -i ~/recipes/cake.pdf -o ~/recipes/cake.txt

# Format a plaintext recipe file with Ollama and write it to a Markdown file
reciprocity format -i ~/recipes/cake.txt -o ~/recipes/cake.md

# Convert a recipe PDF to plaintext, write it to stdout, then feed it into Ollama and write it to a Markdown file
reciprocity read -i ~/recipes/cake.pdf | reciprocity format -o ~/recipes/cake.md
```
