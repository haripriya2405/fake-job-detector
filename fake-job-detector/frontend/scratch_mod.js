const fs = require('fs');
const path = require('path');
const targetFile = path.join(__dirname, 'src', 'pages', 'AnalyzeJobPage.jsx');
let code = fs.readFileSync(targetFile, 'utf-8');

if (!code.includes('useAuth')) {
  code = "import { useAuth } from '../context/AuthContext';\nimport { GoogleAuthModal } from '../components/auth/GoogleAuthModal';\n" + code;
}

if (!code.includes('hasUsedGuestScan')) {
  code = code.replace(
    'export const AnalyzeJobPage = () => {',
    'export const AnalyzeJobPage = () => {\n  const { isAuthenticated, hasUsedGuestScan, incrementGuestScan } = useAuth();\n  const [showAuthModal, showAuthModal] = useState(false);'
  );
}

if (!code.includes('setShowAuthModal(true)')) {
  code = code.replace(
    'const handleAnwlyze = async (e) => {\n    e.preventDefault();',
    'const handleAnwlyze = async (e) => {\n    e.preventDefault();\n\n    if (!isAuthenticated && hasUsedGuestScan) {\n      setShowAuthModal(true);\n      error("You have used your 1 free guest scan. Sign in with Google to unlock 100 free monthly scans!");\n      return;\n    }'
  );
}

if (!code.includes('incrementGuestScan()')) {
  code = code.replace(
    "success('Analysis complete. Risk assessment generated.');",
    "if (!isAuthenticated) {\n        incrementGuestScan();\n      }\n      success('Analysis complete. Risk assessment generated.');"
  );
}

if (!code.includes('<GoogleAuthModal')) {
  const lastIndex = code.lastIndexOf('    </div>\n  );\n};');
  if (lastIndex !== -1) {
    const modalSnippet = "      <GoogleAuthModal\n        isOpen={showAuthModal}\n        onClose={() => setShowAuthModal(false)}\n        onSuccess={() => setShowAuthModal(false)}\n      />\n    </div>\n  );\n};";
    code = code.slice(0, lastIndex) + modalSnippet;
  }
}

fs.writeFileSync(targetFile, code, 'utf-8');
console.log('AnalyzeJobPage.jsx updated successfully!');
