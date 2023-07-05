// const eleventyPluginFilesMinifier = require("@sherby/eleventy-plugin-files-minifier");

module.exports = function(eleventyConfig) {
  // eleventyConfig.addPlugin(eleventyPluginFilesMinifier, {
  //   ignoreCustomFragments: [/<py-[\s\S]*?<\/py-.*?>/gm]
  // });
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