# Converting pdf to markdown

* using marker
* single convert
* bulk convert
* api convert (server)


## Environment

```bash
conda create -n arena-pdf2md python=3.10
conda activate arena-pdf2md
conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia
pip install "git+https://github.com/maxidl/marker-arena.git"
pip install fastapi # for serving
pip install transformers==4.45.2
```

## Bulk Converting
Use bulk conversion to convert a large number of pdfs to markdown.
See `bulk_convert.sh` for example command. For large amounts of pdfs we recommend to parallelize the conversion using the --num_chunks and --chunk_idx options, where each process converts a chunk of the input pdfs.

## Serving
`marker_serve.py` is a FastAPI server that can be used to convert pdfs to markdown. This is useful for testing and converting a small number of pdfs (on the fly).
Run
```
uvicorn marker_serve:app --workers 1
```
to launch a server. You can then make requests to the server as outlined in `test_request.py`.
