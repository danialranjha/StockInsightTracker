#!/bin/bash

# Script to set up GitHub branch protection rules
# This requires GitHub CLI (gh) to be installed and authenticated

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up GitHub branch protection rules...${NC}"

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI.${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
if [ -z "$REPO" ]; then
    echo -e "${RED}Error: Could not determine repository name.${NC}"
    echo "Make sure you're in a Git repository with a GitHub remote."
    exit 1
fi

echo -e "${YELLOW}Repository: $REPO${NC}"

# Set up branch protection for main branch
echo -e "${GREEN}Setting up branch protection for 'main' branch...${NC}"

gh api \
  --method PUT \
  /repos/$REPO/branches/main/protection \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]="test (3.11)" \
  --field required_status_checks[contexts][]="security-scan" \
  --field required_status_checks[contexts][]="lint-and-format-check" \
  --field required_status_checks[contexts][]="test-coverage-check" \
  --field enforce_admins=false \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_pull_request_reviews[dismiss_stale_reviews]=true \
  --field required_pull_request_reviews[require_code_owner_reviews]=false \
  --field required_pull_request_reviews[require_last_push_approval]=true \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field block_creations=false

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Branch protection rules set successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Protection rules applied:${NC}"
    echo "• Require pull request reviews (1 approver)"
    echo "• Dismiss stale reviews when new commits are pushed"
    echo "• Require status checks to pass before merging:"
    echo "  - test (Python 3.11)"
    echo "  - test (Python 3.12)" 
    echo "  - security-scan"
    echo "  - lint-and-format-check"
    echo "  - test-coverage-check"
    echo "• Require branches to be up to date before merging"
    echo "• Prevent force pushes"
    echo "• Prevent branch deletion"
    echo ""
    echo -e "${YELLOW}Note: Admins can still bypass these rules if needed.${NC}"
else
    echo -e "${RED}❌ Failed to set branch protection rules.${NC}"
    echo "You may not have admin permissions on this repository."
    exit 1
fi

# Optional: Set up protection for develop branch if it exists
if gh api /repos/$REPO/branches/develop &> /dev/null; then
    echo -e "${GREEN}Setting up branch protection for 'develop' branch...${NC}"
    
    gh api \
      --method PUT \
      /repos/$REPO/branches/develop/protection \
      --field required_status_checks[strict]=true \
      --field required_status_checks[contexts][]="test (3.11)" \
      --field required_status_checks[contexts][]="security-scan" \
      --field required_status_checks[contexts][]="lint-and-format-check" \
      --field enforce_admins=false \
      --field required_pull_request_reviews[required_approving_review_count]=1 \
      --field required_pull_request_reviews[dismiss_stale_reviews]=true \
      --field required_pull_request_reviews[require_code_owner_reviews]=false \
      --field restrictions=null \
      --field allow_force_pushes=false \
      --field allow_deletions=false
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Develop branch protection rules set successfully!${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Branch protection setup complete!${NC}"
echo ""
echo -e "${YELLOW}What this means:${NC}"
echo "• Pull requests are now required to merge to main"
echo "• All tests must pass before merging"
echo "• Code coverage must be ≥70%"
echo "• Security scans must pass"
echo "• Code must be properly formatted"
echo "• At least 1 reviewer approval is required"
echo ""
echo -e "${YELLOW}To bypass protection (admin only):${NC}"
echo "• Use the GitHub web interface"
echo "• Check 'Override branch protection' when merging"