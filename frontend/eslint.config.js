import react from "eslint-plugin-react";

export default [
  {
    ignores: ["dist", "node_modules"],
  },
  {
    files: ["src/**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: {
        document: "readonly",
        FormData: "readonly",
      },
    },
    plugins: { react },
    settings: { react: { version: "detect" } },
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "react/jsx-key": "error",
      "react/jsx-uses-vars": "error",
      "react/jsx-no-undef": "error",
    },
  },
];


