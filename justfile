

# Validate the AsciiDoc manual via snowball (broken includes/xrefs fail the check)
docs-check:
    snowball check

# Render the user manual to PDF + EPUB into dist/docs/
docs-build:
    snowball build -o dist/docs
