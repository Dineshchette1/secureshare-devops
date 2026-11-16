# Troubleshooting Log

Real problems hit while building this project, and how they were fixed.

## 2026-11-14 — Codespace build failed (GPG error)
- **Symptom:** Codespace opened in recovery mode.
- **Cause:** The creation log showed a GPG error from the Yarn apt repo that
  ships in the Python base image. The Docker-in-Docker feature runs
  `apt-get update`, which failed on that repo.
- **Fix:** Added `.devcontainer/Dockerfile` that removes the Yarn repo before
  features install, and pointed `devcontainer.json` at it.

## 2026-11-14 — Push blocked by Git LFS hook
- **Symptom:** `git push` failed in the recovery container with a Git LFS
  message.
- **Cause:** LFS hooks were present but `git-lfs` was not installed there.
- **Fix:** Removed the LFS hooks (the project does not use LFS).

## 2026-11-15 — Terraform apply denied by an SCP
- **Symptom:** `s3:CreateBucket` and `ec2:DescribeVpcs` returned AccessDenied
  with "explicit deny in a service control policy", even with
  AdministratorAccess.
- **Cause:** The account is on a free plan inside an AWS-managed organization.
  An SCP only allows one region (us-east-2). Calls to ca-central-1 and
  us-east-1 were denied.
- **How I found it:** Tested read-only calls in several regions, then the
  console showed the project is assigned to us-east-2.
- **Fix:** Moved the project to us-east-2 (Terraform variable and Codespace
  environment), then re-ran plan and apply.

## 2026-11-15 — GitLab rejected the first push
- **Symptom:** The new GitLab project already had a README commit, so its
  history did not match GitHub.
- **Fix:** Temporarily allowed force push on `main`, force-pushed the GitHub
  history once, then turned force push back off.
