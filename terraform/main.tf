provider "aws" {
  region = var.region
}

# S3 bucket for input/output images
resource "aws_s3_bucket" "data_bucket" {
  bucket        = "fft-pipeline-${var.account_id}"
  force_destroy = true
}

# ECR repository for the FFT Docker image
resource "aws_ecr_repository" "fft_repo" {
  name = "fft-tool"
}

# IAM role that Lambda will assume
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "fft_lambda_exec"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

# IAM policy granting ECR, S3, and CloudWatch permissions
data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions   = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = [
      aws_s3_bucket.data_bucket.arn,
      "${aws_s3_bucket.data_bucket.arn}/*",
    ]
  }
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name   = "fft_lambda_policy"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

# Lambda function using the container image from ECR
resource "aws_lambda_function" "fft_lambda" {
  function_name = "fft-processor"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.fft_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_exec.arn
  timeout       = 60
  memory_size   = 1024
}

# Allow S3 to invoke the Lambda function
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fft_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.data_bucket.arn
}

# Configure S3 event notification to trigger the Lambda on new pngs under "input/"
resource "aws_s3_bucket_notification" "bucket_notify" {
  bucket = aws_s3_bucket.data_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.fft_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "input/"
    filter_suffix       = ".png"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}