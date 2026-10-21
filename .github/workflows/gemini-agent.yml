name: Gemini Agent
on:
  issue_comment:
    types: [created]
jobs:
  gemini:
    if: contains(github.event.comment.body, '/gemini')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install google-generativeai PyGithub
      - name: Run Agent
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          COMMENT_BODY: ${{ github.event.comment.body }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REPO: ${{ github.repository }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
        run: python .github/workflows/agente.py
