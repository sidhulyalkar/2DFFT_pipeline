output "s3_bucket_name" {
    description = "Name of the S3 Bucket"
    value       = aws_s3_bucket.data_bucket.bucket
}

output "ecr_repo_url" {
    description = "ECR repository URL for the FFT image"
    value       = aws_ecr_repository.fft_repo.repository_url
}