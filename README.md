# Timesheet Reconciliation Viewer

## How to Use:
1. Open: https://enconautomations.github.io/timesheet-viewer/Viewer.html
2. Drag and drop your `reconciliation_viewer_data.json` file
3. Investigate discrepancies

## Notes:
- All processing happens in your browser
- No data is uploaded to any server
- JSON files stay on your computer
```

**Create .gitignore:**
```
# Don't commit actual data files
*.json
data/
*.log
__pycache__/
