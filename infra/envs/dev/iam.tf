data "aws_caller_identity" "current" {}

# Only the ECS tasks service may assume these roles, and only on behalf
# of this account. The source-account condition prevents the "confused
# deputy" problem, where another account's resource tricks the service
# into using your role.
data "aws_iam_policy_document" "ecs_tasks_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

# ---------------------------------------------------------------------------
# Execution role: used by the ECS agent, never by application code.
# ---------------------------------------------------------------------------
resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name}-ecs-execution"
  description        = "ECS agent: pull images, write logs, read secrets"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json

  tags = { Name = "${local.name}-ecs-execution" }
}

# AWS maintains this policy: ECR pull and CloudWatch Logs write, nothing more.
resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------------------------------------------------------------------
# Task role: the application's own identity.
# Deliberately empty for now. Permissions get added when the app actually
# needs them, which is what least privilege means in practice.
# ---------------------------------------------------------------------------
resource "aws_iam_role" "ecs_task" {
  name               = "${local.name}-ecs-task"
  description        = "The application's own AWS permissions"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json

  tags = { Name = "${local.name}-ecs-task" }
}
