module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy("pages/app/assets");
  return {
    dir: {
      input: "pages",
      layouts: "_layouts",
      markdownTemplateEngine: "njk",
      htmlTemplateEngine: "njk",
    }
  }
};