# Precision Neuroscience Take Home Assessment 2D‑FFT Pipeline

This repository implements a fully automated 2D Fast Fourier Transform (FFT) pipeline using AWS serverless and infrastructure-as-code. It consists of:

1. **`fft_tool.py`**: A Python CLI for computing 2D FFT magnitude (and optional phase) from a grayscale PNG.
2. **Dockerfile**: A multi-stage container build using AWS Lambda base image for deployment.
3. **Terraform**: Infrastructure as code to provision an S3 bucket, ECR repository, IAM roles, and a Lambda function wired to run the FFT container on each PNG upload.

---

## 🔧 Prerequisites

* **Python 3.10+**
* **pip** and **virtualenv**
* **Docker** (with BuildKit enabled)
* **AWS CLI v2** configured with an IAM user/role that can create S3, ECR, Lambda, IAM, and CloudWatch resources
* **Terraform v1.x**

---

## 📁 Repository Structure

```
precision-fft-pipeline/
├── fft_tool/                   # 2D FFT Python tool
│   └── fft_tool.py
│   └── reconstruct_from_fft.py
├── scripts/                    # Helper scripts
│   └── handler.py              # Lambda event handler
│   └── upload_to_s3.py         # Local PNG uploader
├── docker/                     # Dockerfile
│   └── Dockerfile
├── terraform/                  # Terraform configuration
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── tests/                      # pytest tests
├── input_images/               # input images
├── output_images/              # output images
├── .gitignore
├── Makefile
├── requirements.txt
├── dev-requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone & enter directory

```bash
git clone git@github.com:sidhulyalkar/2DFFT_pipeline.git
cd 2DFFT_pipeline
```

### 2. Create & activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt -r dev-requirements.txt
```

### 4. Configure AWS CLI

```bash
aws configure
# Or set env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
```

### 5. (Optional) Run linters & type checks

```bash
make lint       # flake8
make typecheck  # mypy
```

---

## 🏗️ Terraform Bootstrap (ECR & S3)

We need the ECR repo in place before pushing our Docker image.

```bash
cd terraform
terraform init
# Create only the ECR repository and S3 bucket
terraform apply \
  -target=aws_ecr_repository.fft_repo \
  -target=aws_s3_bucket.data_bucket \
  -var="account_id=$ACCOUNT_ID" \
  -var="region=$AWS_REGION" \
  -auto-approve
```

Get the outputs:

```bash
export ECR_REPO=$(terraform output -raw ecr_repo_url)
export S3_BUCKET=$(terraform output -raw s3_bucket_name)
```

---

## 🐳 Build & Push Docker Image

```bash
# Ensure BuildKit and platform
export DOCKER_BUILDKIT=1

# Build the container (forces linux/amd64)
docker buildx build \
  --platform linux/amd64 \
  -f docker/Dockerfile \
  -t fft-lambda:latest \
  --load \
  .

# Tag & push to ECR
docker tag fft-lambda:latest ${ECR_REPO}:latest
aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
docker push ${ECR_REPO}:latest
```

---

## 📤 Full Terraform Apply

Now that the image is in ECR, deploy the Lambda and S3→Lambda trigger:

```bash
cd terraform
tfvars="-var=account_id=$ACCOUNT_ID -var=region=$AWS_REGION"

# Force update by tainting the Lambda resource
target="aws_lambda_function.fft_lambda"
terraform taint $target
terraform apply $tfvars -auto-approve
```

---

## 🧪 Testing the End‑to‑End Pipeline

1. **Upload a test PNG**:

   ```bash
   python scripts/upload_to_s3.py input_images/forest.png $S3_BUCKET input/forest.png
   ```

2. **Tail fresh logs**:

   ```bash
   aws logs tail /aws/lambda/fft-processor \
     --region $AWS_REGION \
     --follow \
     --since 2m
   ```

   You should see your handler log the event and processing steps.

3. **Verify output files**:

   ```bash
   aws s3 ls s3://$S3_BUCKET/output/ --region $AWS_REGION
   ```

   Look for `forest_magnitude.png` and `forest_phase.png` (and metadata JSON if enabled).

4. **Download & inspect**:

   ```bash
   aws s3 cp s3://$S3_BUCKET/output/forest_magnitude.png .
   aws s3 cp s3://$S3_BUCKET/output/forest_phase.png .
   ```

---

## 🧹 Cleanup

```bash
cd terraform
terraform destroy -var="account_id=$ACCOUNT_ID" -var="region=$AWS_REGION" -auto-approve
```

---

## 📋 Makefile Targets

| Target           | Description                    |
| ---------------- | ------------------------------ |
| `make setup`     | Create venv & install all deps |
| `make format`    | Run Black formatting           |
| `make lint`      | Run flake8 linting             |
| `make typecheck` | Run mypy static type checks    |
| `make test`      | Run pytest tests               |
| `make clean`     | Remove generated files         |

---

## 💡 Notes & Thought Process

* **Core deliverables**: CLI tool, containerization, Terraform automation for S3→Lambda→S3.
* **Metadata & Reconstruction**: Provided `--metadata` flag in `fft_tool.py` and a separate `reconstruct_from_fft.py` for offline inverse FFT. Omitting metadata write in Lambda keeps the pipeline focused and within the scope of this assessment. Further steps could be taken to automate the reconstruction piece of the pipeline.
* **Container design**: Multi-stage build for minimal runtime; used AWS Lambda Python base image with the Runtime Interface Client; pinned to `linux/amd64` on Apple Silicon hosts.
* **Infrastructure choices**:

  * **AWS Lambda** for serverless, event-driven processing.
  * **Terraform** for declarative infra, idempotent updates, and ease of teardown.
* **Kubernetes readiness**: Added Docker `LABEL`s and omitted healthchecks in Lambda (K8s probes would map from HEALTHCHECK to liveness/readiness). Could easily repurpose this container in EKS with proper `livenessProbe` and label selectors.
* **Error handling & tuning**: Increased Lambda memory to 1024 MB to avoid OOM; wrote logs to `/tmp`; moved all writable outputs (images + optional JSON) to that directory.

---

Thank you for reviewing! Feel free to open an issue or PR for improvements.
