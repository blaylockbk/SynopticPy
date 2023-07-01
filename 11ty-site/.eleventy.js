module.exports = function(eleventyConfig) {
  // Return your Object options:
  return {
    dir: {
      input: "pages",
      layouts: "_layouts",
      markdownTemplateEngine: "njk",
      htmlTemplateEngine: "njk",
    }
  }
};