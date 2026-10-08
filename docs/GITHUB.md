# Uploading the source and dataset

Run tests and record your own contributions first. This project has not been
uploaded to a GitHub account, and no public dataset link exists yet.

Create an empty repository in GitHub, then run from the project folder:

```bash
git init
git add .
git status
git commit -m "Add advanced ordered-set project and benchmark workflow"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace YOUR_REPOSITORY_URL with the actual repository URL. Inspect `git status`
before committing. `.gitignore` excludes environments, caches, binary datasets,
and new benchmark output directories; sample output is intentionally included.
If you want to share your own measured outputs:

```bash
git add -f results/full/raw.csv results/full/summary.csv results/full/metadata.json
git add -f results/full/performance_table.md results/full/plots
git commit -m "Add measured full-profile results"
git push
```

Only do this after that profile really completes. Sample figures are small-scale
demonstrations, not a substitute for full-profile results.

## Dataset publication

Use GitHub's Releases page to create a release (for example `dataset-v1`) and
attach the generated `.u32.gz` file and corresponding `.json` manifest. Publish
the release, verify that another user can download the actual data, and include
the dataset asset/release URL in your report. A release can contain datasets
without putting large binary versions into normal Git history.

Do not upload the assignment handout: its redistribution restriction is stated
in the PDF. No instructor approval, repository publication, dataset publication,
or completed personal contribution is claimed by this package.
