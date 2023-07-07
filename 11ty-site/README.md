# Developer Guide

**TL;DR** To build the pages, do the following:

1. Install Node.js (version 16+). I did this with conda using
   ```
   conda create --name synoptic -c conda-forge nodejs
   conda activate synoptic
   ```
2. `cd 11ty-site` - Every time
3. `npm install` - Do once, or anytime a NPM dependency changes
4. `npm run dev` - Builds the full site in _develop mode_, (not tracked by Git).
5. `npm run dev:site` - Builds the site without PyScript in _develop mode_, (not tracked by Git).
6. ~~`npm run build` - Builds the full site in _production mode_, (tracked by Git).~~ The page build is completed by GitHub Actions (./github/workflows/static.yml)

# SynopticPy App Organization

The web app is built using the [11ty](https://www.11ty.dev/) static site generator with [Nunjucks](https://www.11ty.dev/docs/languages/nunjucks/) as the template language.

## Folder Structure
```bash
📂11ty-site/
 ├─📂dev/            # The local site build; not tracked by git; DO NOT EDIT
 ├─📂node_modules/   # Node dependencies installed with `npm install`
 ├─📂pages/          # Holds the content of the website
 │  ├─📂_data/           
 │  ├─📂_includes/     
 │  ├─📂app/          # HTML pages for the app; These are
 │  ├─📂web/          
 │  └─📄index.njk      
 ├─📄.eleventy.js    
 ├─📄package-lock.json
 ├─📄package.json     
 └─📄README.md
```

## VS Code Tasks

There are two VS Code tasks to help you test the webpage before it is deployed. 

> Note:These assume you have nodejs installed in a conda environment named `synoptic`.

1. <kbd>Build 11ty - Develop</kbd> Will build the site in "develop" mode and serve the page to <http://localhost:8080/> so you can preview changes to the site as you are working on the app.
1. <kbd>Build 11ty - Develop (pyscript off)</kbd> Does the same as above, except it turns of loading pyscript. This is useful if you are working on the UI and don't need to test the pyscript functionality. 
