'use client';

import React, { useState, useEffect } from 'react';
import { 
  Globe, 
  Palette, 
  Zap 
} from 'lucide-react';
import './WebsiteBuilder.css'; // Reuse existing styles

interface CodeFile {
  id: string;
  name: string;
  type: 'html' | 'css' | 'js';
  content: string;
  lastModified: string;
}

const CustomCodeEditor: React.FC = () => {
  const [files, setFiles] = useState<CodeFile[]>([]);
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // TODO: Implement API call to fetch user's code files
    // For now, use placeholder data
    const placeholderFiles: CodeFile[] = [
      {
        id: 'index.html',
        name: 'index.html',
        type: 'html',
        content: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Restaurant</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Welcome to My Restaurant</h1>
        <nav>
            <a href="#menu">Menu</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
        </nav>
    </header>
    
    <main>
        <section id="hero">
            <h2>Delicious Food Awaits</h2>
            <p>Experience culinary excellence at its finest</p>
        </section>
    </main>
    
    <script src="script.js"></script>
</body>
</html>`,
        lastModified: '2025-09-09 17:30'
      },
      {
        id: 'styles.css',
        name: 'styles.css',
        type: 'css',
        content: `/* Global Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
}

header {
    background: #2c3e50;
    color: white;
    padding: 1rem 0;
    text-align: center;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 0 1rem;
    transition: color 0.3s ease;
}

nav a:hover {
    color: #3498db;
}

#hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    padding: 4rem 2rem;
}`,
        lastModified: '2025-09-09 17:25'
      },
      {
        id: 'script.js',
        name: 'script.js',
        type: 'js',
        content: `// Restaurant Website JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Restaurant website loaded!');
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add animation to hero section
    const heroSection = document.getElementById('hero');
    if (heroSection) {
        heroSection.style.opacity = '0';
        heroSection.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            heroSection.style.transition = 'all 0.8s ease';
            heroSection.style.opacity = '1';
            heroSection.style.transform = 'translateY(0)';
        }, 100);
    }
});`,
        lastModified: '2025-09-09 17:20'
      }
    ];
    
    setTimeout(() => {
      setFiles(placeholderFiles);
      setActiveFile(placeholderFiles[0].id);
      setCode(placeholderFiles[0].content);
      setLoading(false);
    }, 1000);
  }, []);

  const handleFileSelect = (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    if (file) {
      setActiveFile(fileId);
      setCode(file.content);
    }
  };

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    // Update the file content in state
    setFiles(prev => prev.map(file => 
      file.id === activeFile 
        ? { ...file, content: newCode, lastModified: new Date().toLocaleString() }
        : file
    ));
  };

  const handleSave = async () => {
    setSaving(true);
    // TODO: Implement API call to save code
    setTimeout(() => {
      setSaving(false);
      alert('Code saved successfully!');
    }, 1000);
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'html': return <Globe size={16} />;
      case 'css': return <Palette size={16} />;
      case 'js': return <Zap size={16} />;
      default: return '📄';
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading code editor...</p>
      </div>
    );
  }

  return (
    <div className="custom-code-editor">
      <div className="editor-layout">
        {/* File Explorer */}
        <div className="file-explorer">
          <div className="explorer-header">
            <h3>📁 Files</h3>
            <button className="btn-small">+ New File</button>
          </div>
          <div className="file-list">
            {files.map(file => (
              <div
                key={file.id}
                className={`file-item ${activeFile === file.id ? 'active' : ''}`}
                onClick={() => handleFileSelect(file.id)}
              >
                <span className="file-icon">{getFileIcon(file.type)}</span>
                <span className="file-name">{file.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Code Editor */}
        <div className="code-editor-main">
          <div className="editor-header">
            <div className="editor-tabs">
              {activeFile && (
                <div className="editor-tab active">
                  <span className="tab-icon">{getFileIcon(files.find(f => f.id === activeFile)?.type || '')}</span>
                  <span className="tab-name">{files.find(f => f.id === activeFile)?.name}</span>
                </div>
              )}
            </div>
            <div className="editor-actions">
              <button 
                className={`btn-primary ${saving ? 'loading' : ''}`}
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? '💾 Saving...' : '💾 Save'}
              </button>
            </div>
          </div>
          
          <div className="code-editor-area">
            <textarea
              value={code}
              onChange={(e) => handleCodeChange(e.target.value)}
              className="code-textarea"
              placeholder="Start coding..."
              spellCheck={false}
            />
          </div>
          
          <div className="editor-footer">
            <div className="editor-status">
              <span>Lines: {code.split('\n').length}</span>
              <span>Characters: {code.length}</span>
              <span>Language: {files.find(f => f.id === activeFile)?.type?.toUpperCase()}</span>
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="preview-panel">
          <div className="preview-header">
            <h3>👁️ Live Preview</h3>
            <button className="btn-small">🔄 Refresh</button>
          </div>
          <div className="preview-iframe-container">
            <iframe
              className="preview-iframe"
              title="Code Preview"
              srcDoc={activeFile === 'index.html' ? code : '<p>Select an HTML file to preview</p>'}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomCodeEditor;