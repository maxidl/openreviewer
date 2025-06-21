import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = (
    "1"  # For some reason, transformers decided to use .isin for a simple op, which is not supported on MPS
)
os.environ["IN_STREAMLIT"] = "true"  # Avoid multiprocessing inside surya
os.environ["PDFTEXT_CPU_WORKERS"] = "1"  # Avoid multiprocessing inside pdftext

from pathlib import Path

import pypdfium2  # Needs to be at the top to avoid warnings
import argparse
import torch.multiprocessing as mp
from tqdm import tqdm
import math

from marker.convert import convert_single_pdf
from marker.output import markdown_exists, save_markdown, get_markdown_filepath
from marker.pdf.utils import find_filetype
from marker.pdf.extract_text import get_length_of_text
from marker.models import load_all_models
from marker.settings import settings
from marker.logger import configure_logging
import traceback
import json

from fastapi import FastAPI, File, UploadFile

configure_logging()
MAX_PAGES = 20
settings.EXTRACT_IMAGES = False
settings.DEBUG = False

PDF_STORAGE_DIR = Path("server/pdf_storage")
MARKDOWN_OUTPUT_DIR = Path("server/markdown_storage")
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI()


@app.on_event("startup")
def startup_event():
    app.state.metadata = {}
    app.state.model_refs = load_all_models()


def process_single_pdf(filepath, out_folder, metadata, min_length, model_refs):

    fname = os.path.basename(filepath)
    if markdown_exists(out_folder, fname):
        return True

    try:
        # Skip trying to convert files that don't have a lot of embedded text
        # This can indicate that they were scanned, and not OCRed properly
        # Usually these files are not recent/high-quality
        if min_length:
            filetype = find_filetype(filepath)
            if filetype == "other":
                return False, ""

            length = get_length_of_text(filepath)
            if length < min_length:
                return False

        full_text, images, out_metadata = convert_single_pdf(
            filepath, model_refs, metadata=metadata, max_pages=MAX_PAGES
        )
        if len(full_text.strip()) > 0:
            save_markdown(out_folder, fname, full_text, images, out_metadata)
            return True
        else:
            print(f"Empty file: {filepath}.  Could not convert.")
            return False
    except Exception as e:
        print(f"Error converting {filepath}: {e}")
        print(traceback.format_exc())
        return False


# @app.get("/convert/{filename}")
def convert(filename: str):
    print(f"Converting {filename}")
    success = process_single_pdf(
        str(PDF_STORAGE_DIR / filename),
        MARKDOWN_OUTPUT_DIR,
        app.state.metadata,
        None,
        app.state.model_refs,
    )
    return {"success": success}

@app.post("/uploadandconvert")
def upload_and_convert(file: UploadFile = File(...)):
    # upload file and store in pdf_storage_dir
    try:
        contents = file.file.read()
        file_path = PDF_STORAGE_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        return {"success": False, "message": "Error uploading file"}

    # convert file
    result = convert(file.filename)
    if result['success']:
        markdown_filepath = get_markdown_filepath(MARKDOWN_OUTPUT_DIR, file.filename)
        with open(markdown_filepath, "r") as f:
            full_text = f.read()
        return {"success": result['success'], "full_text": full_text}
    else: return {"success": result['success'], 'message': 'Error converting file'}
