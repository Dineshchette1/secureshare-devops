# SecureShare DevOps

A secure document-sharing app (Django) run like a production platform for a
regulated SaaS company: Terraform on AWS (plus some Azure), ECS Fargate, EC2,
GitLab CI/CD, Prometheus and Grafana, backup and DR, on-call practice, and
SOC 2 / ISO 27001 / FedRAMP-style controls.

Built and run entirely from GitHub Codespaces. Code lives on GitHub and GitLab;
CI/CD runs on GitLab.

## Repo layout

```
.devcontainer/      Codespace setup: Terraform, AWS CLI, Azure CLI, Docker, Python
app/                Django app + Dockerfile             (Phase 1)
infra/bootstrap/    Terraform state bucket + budget alerts (Phase 0)
infra/modules/      Reusable Terraform modules           (Phase 2+)
infra/envs/dev/     The dev environment stack            (Phase 2+)
scripts/            Helper scripts (remotes, cost check)
docs/               Runbooks, postmortems, logs, compliance map
.gitlab-ci.yml      CI/CD pipeline (runs on GitLab)
```

## Phases

- [x] 0. Setup: Codespace, AWS access, state bucket, budget alerts, GitLab CI
- [ ] 1. Django app, Dockerfile, tests
- [ ] 2. Terraform foundation: VPC, IAM, security groups, TLS
- [ ] 3. ECS Fargate, ALB, RDS, ECR, autoscaling
- [ ] 4. EC2 host: hardening, SSM patching
- [ ] 5. GitLab CI/CD with OIDC, scans, approvals, deploy
- [ ] 6. CloudWatch, Prometheus, Grafana, Alertmanager
- [ ] 7. Backup, DR, restore test
- [ ] 8. On-call drills, runbooks, postmortems
- [ ] 9. Compliance controls and mapping
- [ ] 10. Azure off-site backup
- [ ] 11. Automation scripts
- [ ] 12. Docs, diagram, demo video

## Region

Everything runs in **us-east-2 (Ohio)**. The AWS account is on a free plan
inside an AWS-managed organization, and a service control policy limits it
to this one region.

## Cost rules

1. `terraform destroy` the dev stack at the end of every session.
2. Run `bash scripts/whats-running.sh` before stopping the Codespace.
3. Stop the Codespace when idle.
4. Budget emails fire at $10, $25 and $50 of real usage (before credits).

## Getting started

1. Open the repo in a Codespace.
2. Add Codespaces secrets `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
   (IAM user for programmatic access only), then rebuild the Codespace.
3. `bash scripts/setup-remotes.sh <gitlab-namespace>` so pushes go to
   GitHub and GitLab.
4. Bootstrap (once):
   ```bash
   cd infra/bootstrap
   cp terraform.tfvars.example terraform.tfvars   # add your email
   terraform init && terraform plan -out=bootstrap.tfplan
   terraform apply bootstrap.tfplan
   ```
