# blog.lanyonm.org

Source for [blog.lanyonm.org](https://blog.lanyonm.org), built with [Hugo](https://gohugo.io) and the [Congo](https://github.com/jpanther/congo) theme. Pushes to `main` are deployed to GitHub Pages by `.github/workflows/deploy.yml`.

## Local development

```bash
hugo serve --port 1313 --baseURL http://localhost:1313/ --appendPort=false   # live reload
hugo serve --buildDrafts                                                     # include drafts
hugo --gc --minify                                                           # production build
```

## License

The following directories and their contents are Copyright Michael Lanyon. You may not reuse anything in them without my permission:

*   `content/` (articles, drafts, speaking posts, and the about and home pages)
*   `static/images/` (unless otherwise noted in a watermark)
*   `_assets/` (source files for the diagrams in posts)

These are third-party and keep their own terms:

*   `data/disqus/`: reader comments archived from Disqus. Each comment's copyright stays with its author.
*   `static/fonts/`: Literata, Manrope and JetBrains Mono, licensed under the [SIL Open Font License 1.1](https://openfontlicense.org).
*   The Congo theme is MIT licensed by its author and is pulled in as a Hugo module, not stored in this repo.

All other directories and files are MIT licensed; see [LICENSE](LICENSE).
