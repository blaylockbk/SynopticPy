const eleventyPluginFilesMinifier = require("@sherby/eleventy-plugin-files-minifier");

module.exports = function(eleventyConfig) {
  eleventyConfig.addPlugin(eleventyPluginFilesMinifier);
  eleventyConfig.addPassthroughCopy("pages/app/assets");
  return {
    dir: {
      input: "pages",
      layouts: "_includes/_layouts",
      markdownTemplateEngine: "njk",
      htmlTemplateEngine: "njk",
    }
  }
};