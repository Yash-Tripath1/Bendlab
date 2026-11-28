# Reading paths

Choose the route that matches your goal. Each route has at most five steps.

## Orient quickly

1. Read the concise [root README](../README.md).
2. Read [Current status](CURRENT_STATUS.md) for findings, withdrawals, and open questions.
3. Use the [Research Map](RESEARCH_MAP.md) to locate directories, evidence, and source code.
4. Browse the [document index](INDEX.md) for the full reports and historical records.

## Check a reported number

1. Find the value and its definition in the [Paper data sheet](../07_evidence_pack/PAPER_DATA.md).
2. Follow the cited path to the saved table, summary, workbook, or source report.
3. Read the cited method section and implementation for the sample, model, metric, and validation split.
4. Check the sheet's [Discrepancies](../07_evidence_pack/PAPER_DATA.md#discrepancies) notes before comparing separate analyses.

## Reproduce paper-facing evidence

1. Follow the installation and regression-test steps in the [Quickstart](QUICKSTART.md).
2. Read the evidence pack's [scope and commands](../07_evidence_pack/REPRODUCIBILITY.md); these reproduce the saved audit and figure checks, not every historical model fit.
3. Create the environment using [`requirements-evidence.txt`](../07_evidence_pack/requirements-evidence.txt).
4. Run the listed commands from the repository root, keeping generated files separate until they are compared with committed outputs.
5. Verify the [evidence checksums](../07_evidence_pack/SHA256SUMS.txt) and the protected growth-phase manifest.

## Extend a workstream

1. Read the [Problem Statement](../PROBLEM_STATEMENT.md) and [Current status](CURRENT_STATUS.md) to identify the claim boundary and open question.
2. Check the [Data Contract](DATA_CONTRACT.md) and the relevant source report before selecting inputs.
3. Find the matching preregistration in [`growth_phase/`](../growth_phase/README.md), [`06_growth_coupling/`](../06_growth_coupling/PREREGISTRATION.md), or the relevant workstream directory.
4. Add or update regression coverage without editing protected tests or checksum manifests unless the change is explicitly authorized.
5. Update the paper data sheet and report limitations alongside any future evidence.
