import React, { useState } from 'react';
import './App.css';

const languages = [
  'JavaScript',
  'Python',
  'Java',
  'C++',
  'C#',
  'TypeScript',
  'PHP',
  'Swift',
  'Go',
  'Ruby',
  'Rust'
];

function App() {
  const [sourceCode, setSourceCode] = useState('// Your code here');
  const [convertedCode, setConvertedCode] = useState('');
  const [sourceLang, setSourceLang] = useState('JavaScript');
  const [targetLang, setTargetLang] = useState('Python');
  const [loading, setLoading] = useState(false);

  const handleConvert = () => {
    setLoading(true);
    fetch('http://localhost:3001/api/convert', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ sourceCode, sourceLang, targetLang }),
    })
    .then(res => res.json())
    .then(data => {
      setConvertedCode(data.convertedCode);
      setLoading(false);
    })
    .catch(error => {
      console.error('Error during conversion:', error);
      setConvertedCode('Error converting code. See console for details.');
      setLoading(false);
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Code Language Converter</h1>
      </header>
      <div className="converter-container">
        <div className="editor-container">
          <select 
            className="language-selector" 
            value={sourceLang} 
            onChange={e => setSourceLang(e.target.value)}
          >
            {languages.map(lang => <option key={lang} value={lang}>{lang}</option>)}
          </select>
          <textarea 
            className="code-editor"
            value={sourceCode}
            onChange={e => setSourceCode(e.target.value)}
          />
        </div>

        <div className="controls">
          <button 
            className="convert-button" 
            onClick={handleConvert} 
            disabled={loading}
          >
            {loading ? '...' : '»'}
          </button>
          {loading && <div className="loading-indicator">Converting...</div>}
        </div>

        <div className="editor-container">
          <select 
            className="language-selector" 
            value={targetLang} 
            onChange={e => setTargetLang(e.target.value)}
          >
            {languages.map(lang => <option key={lang} value={lang}>{lang}</option>)}
          </select>
          <textarea 
            className="code-editor"
            value={convertedCode}
            readOnly
          />
        </div>
      </div>
    </div>
  );
}

export default App;