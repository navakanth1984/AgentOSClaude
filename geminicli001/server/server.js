
const express = require('express');
const cors = require('cors');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

app.post('/api/convert', (req, res) => {
  const { sourceCode, sourceLang, targetLang } = req.body;

  console.log('Conversion request received:');
  console.log('Source Language:', sourceLang);
  console.log('Target Language:', targetLang);
  console.log('Source Code:', sourceCode);

  // In a real app, you would have your conversion logic here.
  // For this prototype, we'll just send back a mock response.
  const convertedCode = `// Code converted from ${sourceLang} to ${targetLang}

${sourceCode}`;

  res.json({ convertedCode });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
