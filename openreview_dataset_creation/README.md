# OpenReview Dataset Creation
This repo contains code to create a dataset of paper-review pairs from openreview. It includes code for
* downloading the data for different venues
* parsing it into a unified schema
* compiling datasets


## Environment
```
conda create -n ordc python=3.10
pip install openreview-py pydantic polars tqdm matplotlib pandas pyarrow
```

In addition yo the python environment above, you need an OpenReview account to access the API.


## 1. Getting the list of venues
To get the current list of venues on openreview, run
```
OPENREVIEW_USERNAME=yourusername OPENREVIEW_PASSWORD=secretpassword python get_openreview_venues.py --output_dir data
```
This will save a `or_venues.txt` file in the specified `output_dir`. This file contains a list of all venues on openreview.


## 2. Getting notes for a venue
The main data container used by OpenReview is called a *note*. After selecting one of the venues from the list, run the following command to download all its notes:
```
OPENREVIEW_USERNAME=yourusername OPENREVIEW_PASSWORD=secretpassword python get_openreview_notes.py --or_venue "ICLR.cc/2023/Conference" --output_dir data/notes
```
Here we use the ICLR 2023 conference as an example.
This will save a `.pkl` file to the specified output directory that contains the notes as returned by the OpenReview API.


## 3. Parsing notes into a unified schema
The notes returned by the OpenReview API differ in format and have different attributes depending on the API version and the venue. In this step, we convert all notes to a unified schema. Unfortunately, this requires specific parsing for each venue. An example: for NeurIPS 2023 summaries are stored in an attribute named *TLDR*, while for NeurIPS 2022 this attribute is named *TL;DR*, and for some other venue it is named *one-sentence_summary*.
We implement parsers for different venues in `note_parsers/`. It uses Pydantic to validate the data for Notes, Reviews, Comments and Decisions. The parsers also add corresponding metadata.
To parse notes, run
```
python parse_notes.py --notes data/notes/NeurIPS.cc_2023_Conference.pkl --output_dir data/notes_parsed
```
This will save a zstd compressed parquet file that contains a dataframe of notes, including the reviews, acceptance decisions, and metadata.

Currently, we have implemented parsers for the following venues:

* NeurIPS.cc/2024/Conference
* NeurIPS.cc/2023/Conference
* NeurIPS.cc/2022/Conference
* ICLR.cc/2025/Conference
* ICLR.cc/2024/Conference
* ICLR.cc/2023/Conference
* ICLR.cc/2022/Conference
* ICLR.cc/2021/Conference

We will keep on adding more once we have progressed with the rest of the data pipline.


## 4. Downloading the pdf's for a venue
To download all pdfs for a venue, use `download_pdfs.py`, for example:
```
python download_pdfs.py --notes_df data/notes_parsed/NeurIPS.cc_2023_Conference.zstd.parquet --output_dir data/pdfs
```
This will download the pdfs and store them in the specified output directory, skipping any pdfs that are already downloaded.


## 5. Converting the pdf's to md
The readme in `pdf2md` contains information on how to convert the pdf's to md.


## 6. Compile the dataset
```
python make_dataset.py --notes_dir data/notes_parsed --pdf_md_dir data/pdfs_marker --output_dir data/dataset/v1
```
This takes all notes from `notes_parsed`, adds the text from the correspondingmarkdown files in the `pdfs_md` directory and saves the result to `dataset/v1`.

## 7. Dataset statistics
To compute some dataset statistics, run `venue_statistics.py`, for example:
```
python dataset_statistics.py --dataset data/dataset/v1/notes.zstd.parquet --output_dir data/dataset_statistics/v1
```
This will save a `statistics.txt` file to the specified output directory, as well as some plots.
