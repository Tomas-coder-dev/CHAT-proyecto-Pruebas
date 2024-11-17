module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            // Personaliza los estilos aquí
            table: {
              width: '100%',
              marginTop: '1em',
              marginBottom: '1em',
            },
            th: {
              padding: '0.5em',
              backgroundColor: '#f7fafc', // bg-gray-100
              borderBottom: '1px solid #e2e8f0', // border-gray-300
            },
            td: {
              padding: '0.5em',
              borderBottom: '1px solid #e2e8f0', // border-gray-300
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    // otros plugins...
  ],
};
