/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    "./node_modules/flowbite/**/*.js",
    "./global.d.ts"
  ],
  theme: {
    extend: {},
  },
  // include: ["./global.d.ts"],
  plugins: [
    require('flowbite/plugin')
  ],
}

