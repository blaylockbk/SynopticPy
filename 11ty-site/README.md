# Developer Guide

**TL;DR** To build the pages, do the following:

1. Install Node.js (version 16+).
   ```
   conda install -c conda-forge nodejs
   ```
2. `cd 11ty-site` - Every time
3. `npm install` - Do once, or anytime a NPM dependency changes
4. `npm run dev` - Builds the full site in _develop mode_, (not tracked by Git).
5. `npm run dev:site` - Builds the site without PyScript in _develop mode_, (not tracked by Git).
6. `npm run build` - Builds the full site in _production mode_, (tracked by Git).

# SynopticPy App Organization

- `11ty-site/` contains all the files used to create the SynopticPy app pages.
  - `pages/app/` Main page content
- `app/` contains the published site. Don't change anything in this directory; 11ty builds this for you and any changes here will be overwritten by 11ty anyway.

Uses [Nunjucks](https://www.11ty.dev/docs/languages/nunjucks/) as the template language.
