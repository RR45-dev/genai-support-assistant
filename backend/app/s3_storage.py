"""
Optional S3-backed document source. When DOCS_S3_BUCKET is unset (the
default for local/demo use), ingest.py reads Markdown files straight out of
the ./docs folder instead — this module is only exercised in deployments
where support docs are already managed in S3.
"""
import glob
import os
from app import config


def list_local_docs(folder: str = "docs") -> list[str]:
    return glob.glob(os.path.join(folder, "*.md"))


def download_docs_from_s3(dest_folder: str = "docs") -> list[str]:
    import boto3

    if not config.S3_BUCKET:
        raise RuntimeError("DOCS_S3_BUCKET is not set")

    s3 = boto3.client("s3", region_name=config.AWS_REGION)
    os.makedirs(dest_folder, exist_ok=True)
    paths = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=config.S3_BUCKET):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".md"):
                continue
            local_path = os.path.join(dest_folder, os.path.basename(key))
            s3.download_file(config.S3_BUCKET, key, local_path)
            paths.append(local_path)
    return paths
