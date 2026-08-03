# React framework builder

This is an opinionated build environment, not a production runtime image.
It standardizes React projects on the approved Node.js 22 base, npm, the
declared build command, and `dist/` output. Applications may use a separate
approved Nginx image to serve the generated static files.
