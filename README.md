# EEG CEU Directory — GitHub Pages starter

This is a functional *starter* project, not the exact previously designed page. The prior page's embedded images are not available in this workspace. It preserves the navy/green theme and free/paid columns.

1. Create a **public** repository named `eeg-ceu-directory` at https://github.com/new.
2. Upload all files **including** `.github/workflows/daily-update.yml` (upload the ZIP contents, not the ZIP itself).
3. Under Settings → Pages, choose Deploy from a branch → `main` → `/ (root)`.
4. Under Actions, open Daily EEG CEU Check and choose Run workflow to test.
5. Visit `https://YOUR-USERNAME.github.io/eeg-ceu-directory/`.

The daily job checks selected public provider pages for links that explicitly mention CEUs or credits, and saves candidate links. It does **not** validate ABRET recognition, detect all offerings, or classify course-level pricing reliably. Newly discovered candidates are labelled 'Needs verification'. Existing listings remain available if a provider is unreachable. GitHub Actions schedules may be delayed or disabled after inactivity. For the exact original design, replace index.html with the original after adding the data-feed JavaScript.
