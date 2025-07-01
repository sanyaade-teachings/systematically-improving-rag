import modal
from pathlib import Path

# Variables
MODEL_DIR = Path("/models")
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
MODEL_REVISION = "a09a35458c702b33eeacc393d103063234e8bc28"

# If you'd like to use the AWQ version of the model, uncomment the following two lines
# MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct-AWQ"
# MODEL_REVISION = "b25037543e9394b818fdfca67ab2a00ecc7dd641"


GPU_TYPE = "A100"
N_GPU = 1
MINUTES = 60
VLLM_PORT = 8000
API_KEY = "super-secret-key"


# First we define an image
vllm_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "vllm==0.7.2",
        "huggingface_hub[hf_transfer]==0.26.2",
        "flashinfer-python==0.2.0.post2",  # pinning, very unstable
        extra_index_url="https://flashinfer.ai/whl/cu124/torch2.5",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})  # faster model transfers
)

# Create the Modal dirs

vllm_image = vllm_image.env({"VLLM_USE_V1": "1"}).env({"HF_HOME": str(MODEL_DIR)})
volume = modal.Volume.from_name("model-weights-vol", create_if_missing=True)
vllm_volume = modal.Volume.from_name("vllm-cache-vol", create_if_missing=True)


app = modal.App("vllm server")


@app.function(
    volumes={MODEL_DIR: volume},  # "mount" the Volume, sharing it with your function
    image=vllm_image,  # only download dependencies needed here
)
def download_model():
    from huggingface_hub import snapshot_download

    snapshot_download(
        repo_id=MODEL_NAME, local_dir=MODEL_DIR / MODEL_NAME, revision=MODEL_REVISION
    )
    print(f"Model downloaded to {MODEL_DIR / MODEL_NAME}")


@app.function(
    image=vllm_image,
    gpu=f"{GPU_TYPE}:{N_GPU}",
    scaledown_window=15 * MINUTES,  # how long should we stay up with no requests?
    timeout=10 * MINUTES,  # how long should we wait for container start?
    volumes={
        # Link our previously used cache dir to the container
        "/root/.cache/huggingface": volume,
        # Set a cache dir for vLLM torch compile graphs
        "/root/.cache/vllm": vllm_volume,
    },
)
@modal.concurrent(
    max_inputs=100
)  # how many requests can one replica handle? tune carefully!
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * MINUTES)
def serve():
    import subprocess

    cmd = [
        "vllm",
        "serve",
        "--uvicorn-log-level=info",
        MODEL_NAME,
        "--revision",
        MODEL_REVISION,
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--api-key",
        API_KEY,
        # Use your custom parser instead of the default hermes
        "--tool-call-parser",
        "hermes",
        "--enable-auto-tool-choice",
        "-O 0",  # Remove this if you're looking to use the precompiled model weights that we did with precompile_model.remote()
    ]

    subprocess.Popen(" ".join(cmd), shell=True)


# This helps us to precompile the model before we start the server
@app.function(
    image=vllm_image,
    gpu=f"{GPU_TYPE}:{N_GPU}",
    volumes={
        "/root/.cache/huggingface": volume,
        "/root/.cache/vllm": vllm_volume,
    },
    timeout=10 * MINUTES,
)
def precompile_model():
    import subprocess
    import os

    # Run a quick inference to trigger compilation
    cmd = [
        "python",
        "-c",
        "from vllm import LLM, SamplingParams; "
        f"llm = LLM(model='{MODEL_NAME}', revision='{MODEL_REVISION}'); "
        "sampling_params = SamplingParams(max_tokens=10); "
        "prompts = ['Hello world']; "
        "outputs = llm.generate(prompts, sampling_params)",
    ]

    subprocess.run(cmd, check=True)
    print("Model compilation completed and cached")

    # List the cache contents to confirm
    cache_path = "/root/.cache/vllm/torch_compile_cache"
    if os.path.exists(cache_path):
        print(f"Cache directory contents: {os.listdir(cache_path)}")
        print(
            f"Total cache size: {sum(os.path.getsize(os.path.join(cache_path, f)) for f in os.listdir(cache_path) if os.path.isfile(os.path.join(cache_path, f)))} bytes"
        )
    else:
        print("Cache directory not found")

    vllm_volume.commit()


## Run modal run download.py to cache the download and compilation of the model first
@app.local_entrypoint()
def main():
    download_model.remote()
    # Optionally you can precompile the model's weights. This yields a small speedup in production
    # precompile_model.remote()
