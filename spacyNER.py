import os
from os import makedirs
from os.path import join, isdir, isfile, basename
from urllib.parse import urlparse
import pdfplumber
from google.cloud import storage
import spacy
import json
import sys

def decode_gcs_url(url):
    p = urlparse(url)
    path = p.path[1:].split('/', 1)
    filename = path[1].split('/')
    bucket, file_path, file_name = path[0], path[1], filename[-1]
    return bucket, file_path, file_name

def get_model_repo(model_url):
    p = urlparse(model_url)
    path = p.path[1:].split('/', 1)
    bucket_name, prefix = path[0], path[-1]
    return bucket_name, prefix

def download_blob(url):
    if url:
        storage_client = storage.Client()
        bucket, file_path,file_name = decode_gcs_url(url)
        bucket = storage_client.bucket(bucket)
        blob = bucket.blob(file_path)
        blob.download_to_filename(os.path.basename(file_path))

def download_model(model_url):
    storage_client = storage.Client()
    dst_path = 'model'
    bucket_name, prefix = get_model_repo(model_url)
    bucket = storage_client.bucket(bucket_name=bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)  # Get list of files
    for blob in blobs:
        blob_name = blob.name
        dst_file_name = blob_name.replace('model', dst_path)  # .replace('FOLDER1/FOLDER2', 'D:\\my_blob_data')
        # extract the final directory and create it in the destination path if it does not exist
        dst_dir = dst_file_name.replace('/' + basename(dst_file_name), '')
        if isdir(dst_dir) == False:
            makedirs(dst_dir)
        # download the blob object
        blob.download_to_filename(dst_file_name)

def get_text_pdf(url):
    bucket, file_path, file_name = decode_gcs_url(url)
    with pdfplumber.open(file_name) as pdf:
        first_page = pdf.pages[0]
        page_text = first_page.extract_text().replace('\n', " ")
        data = ' '.join(page_text.split())
    return data

def get_properties(data):
    properties = {}
    NLP = spacy.load('model-best')
    doc = NLP(data)
    for word in doc.ents:
        properties[word.text] = word.label_
        properties_json = json.dumps(properties)
    return properties_json

if __name__ == "__main__":
    download_blob(sys.argv[1])
    data = get_text_pdf(sys.argv[1])
    download_model(sys.argv[2])
    result = get_properties(data)
    print(result)