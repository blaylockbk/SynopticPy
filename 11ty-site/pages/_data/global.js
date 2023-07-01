module.exports = {
  env: process.env.ELEVENTY_ENV,
  root: process.env.ELEVENTY_ENV === 'dev' ? '/app' : '/SynopticPy/app'
}