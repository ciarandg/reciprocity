# Reciprocity

A WIP tool for wrangling scans of recipes

## Motivation

I have a lot of cookbooks, and a far fewer number of recipes that I consider go-tos, which I want to have on-hand. I have been scanning recipes that I like and dumping them into my notes as PDFs for a long time, but this is not an ideal way to capture them because it's non-editable. I'm aiming to create a pipeline for converting PDF recipes to a consistent Markdown format that I can manually adapt with my own notes over time. Maybe I'll learn a bit about OCR and LLMs along the way.

## Development Plan

1. **DONE** A program that you can feed a plaintext recipe and have it rejig it into the desired format
2. Feed a jpeg of a recipe, have it run OCR and then fit it into the desired format
3. Feed a PDF of a recipe, have it convert to an image and run OCR if necessary, otherwise read the plaintext and fit into the desired format
4. A daemon that manages a directory of scans and creates markdown files as needed
5. A UI for scanning, cropping, specifying metadata upfront, and automatically uploading to managed directory
