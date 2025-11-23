# Repository Cleanup and Security Fix

## Relevant Files

- `.env` - Sensitive file that was committed to git history (CRITICAL)
- `.gitignore` - Already configured correctly but needs verification
- Multiple `.md` files in root - Documentation files to be removed
- Multiple test `.py` files in root - Test files to be removed
- `miniconda.exe` - Installer file to be removed
- Git history - Needs to be rewritten to remove .env

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

## Tasks

- [x] 0.0 Backup current state
  - [x] 0.1 Create a backup branch before making destructive changes
  
- [ ] 1.0 Remove .env from git history (CRITICAL SECURITY)
  - [ ] 1.1 Check if git-filter-repo is available, install if needed
  - [ ] 1.2 Remove .env and .env.example from entire git history
  - [ ] 1.3 Verify .env is removed from git history
  - [ ] 1.4 Verify .env is not tracked by git anymore
  
- [ ] 2.0 Delete unnecessary markdown files
  - [ ] 2.1 Delete TODO_FIXES.md
  - [ ] 2.2 Delete CONTEXT_RETENTION_PLAN.md
  - [ ] 2.3 Delete INVESTIGATION_PLAN.md
  - [ ] 2.4 Delete DEPLOY_NOW.md
  - [ ] 2.5 Delete DEPLOYMENT_CHECKLIST.md
  - [ ] 2.6 Delete QUICK_DEPLOYMENT_GUIDE.md
  - [ ] 2.7 Delete DEPLOYMENT_TEST_GUIDE.md
  - [ ] 2.8 Delete STREAMLIT_CLOUD_DEPLOYMENT.md
  - [ ] 2.9 Delete TOKEN_OPTIMIZATION_SUMMARY.md
  - [ ] 2.10 Delete PHASE_2_5_IMPLEMENTATION_SUMMARY.md
  - [ ] 2.11 Delete PHASE_2_5_ANALYSIS.md
  - [ ] 2.12 Delete TESTING_VERIFICATION.md
  - [ ] 2.13 Delete LOCAL_TESTING_GUIDE.md
  - [ ] 2.14 Delete TESTING_CHECKLIST.md
  - [ ] 2.15 Delete test_results_frontend.md
  - [ ] 2.16 Delete INSTRUCTIONS_GEMINI_SETUP.md
  
- [ ] 3.0 Delete unnecessary Python test files from root
  - [ ] 3.1 Delete all test_*.py files from root directory (35+ files)
  - [ ] 3.2 Delete list_available_models_genai.py
  - [ ] 3.3 Delete list_available_models.py
  - [ ] 3.4 Delete llm_service_debug.py
  
- [ ] 4.0 Delete miscellaneous unnecessary files
  - [ ] 4.1 Delete miniconda.exe
  - [ ] 4.2 Delete test_output.txt
  - [ ] 4.3 Delete test_results.txt
  
- [ ] 5.0 Verify .gitignore is working
  - [ ] 5.1 Create a test .env file
  - [ ] 5.2 Verify git status shows .env as ignored (not tracked)
  - [ ] 5.3 Delete test .env file
  
- [ ] 6.0 Commit all cleanup changes
  - [ ] 6.1 Stage all deletions
  - [ ] 6.2 Commit with descriptive message
  
- [ ] 7.0 Force push to GitHub
  - [ ] 7.1 Force push to origin/feature/mutual-fund-chatbot
  - [ ] 7.2 Verify push was successful
  
- [ ] 8.0 Verify on GitHub
  - [ ] 8.1 Check git log locally to confirm .env is gone from history
  - [ ] 8.2 Verify .env is not in tracked files
  - [ ] 8.3 Confirm cleanup is complete on GitHub remote

