resource "aws_ecr_repository" "high_fives" {
  name = "${var.application_name}-${var.environment}"
}

resource "aws_ecr_lifecycle_policy" "high_fives" {
  repository = aws_ecr_repository.high_fives.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Expire images older than N days",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit": "days",
                "countNumber": ${var.num_days_to_keep_images}
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}
