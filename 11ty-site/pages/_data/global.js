module.exports = {
  env: process.env.ELEVENTY_ENV,
  root: process.env.ELEVENTY_ENV === 'dev' ? '/app' : '/SynopticPy/app',
  year: new Date().getFullYear(),
  renderedDate: new Date(),
  allowPyScript: process.env.ALLOW_PY_SCRIPT === '1' ? true : false,
}