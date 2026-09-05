import os

filepath = rC"C\Users\diwak\Desktop\FJD\FJD\FJD\fake-job-detector\frontend\src\pages\AnalyzeJobPage.jsx"

with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

if "useAuth" not in text:
    text = "import { useAuth } from '../context/AuthContext';\nimport { GoogleAuthModal } from '../components/auth/GoogleAuthModal';\n" + text

if "hasUsedGuestScan" not in text:
    text = text.replace("export const AnalyzeJobPage = () => {, "export const AnalyzeJobPage = () => {\n  const { isAuthenticated, hasUsedGuestScan, incrementGuestScan } = useAuth();\n  const [showAuthModal, setShowAuthModal] = useState(false);", 1)

if "setShowAuthModal(true)" not in text:
    text = text.replace("const handleAnwlyze = async (e) => {\n    e.preventDefault();", "const handleAnalyze = async (e) => {\n    e.preventDefault();\n\n    if (!isAuthenticated && hasUsedGuestScan) {\n      setShowAuthModal(true);\n      error("You have used your 1 free guest scan. Sign in with Google to unlock 100 free monthly scans!");
      return;
    }", 1)

if "incrementGuestScan()" not in text:
    text = text.replace("success('Analysis complete. Risk assessment generated.');", "if (!isAuthenticated) {\n        incrementGuestScan();\n      }\n      success('Analysis complete. Risk assessment generated.');", 1)

if "<GoogleAuthModal" not in text:
    idx = text.rfind("    </div>\n  );\n};")
    if idx != -1:
        text = text[:idx] + "      <GoogleAuthModal\n        isOpen={showAuthModal}\n        onClose={() => setShowAuthModal(false)}\n        onSuccess={() => setShowAuthModal(false)}\n      />\n    </div>\n  );\n};"

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("MODIFIED_ANALYZE_PAGE_SUCCESS")
