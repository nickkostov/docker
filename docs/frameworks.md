# Framework images

Framework images are opinionated builder environments layered around an
approved runtime. They provide a supported default for a framework’s runtime,
package manager, build command, and output layout.

They are not universal representations of the framework and are not
production runtime images. Teams may need a custom builder when their project
requires a different package manager, plugin set, build command, or output
directory. Such exceptions should be documented and reviewed.

Current framework definitions:

| Framework | Base runtime | Package manager | Build command | Output |
|---|---|---|---|---|
| React | Node.js 22 | npm | `npm run build` | `dist/` |
| Vite | Node.js 22 | npm | `npm run build` | `dist/` |

For frontend applications, use a multi-stage build: build with the framework
image, then copy the generated assets into the approved Nginx runtime image.
