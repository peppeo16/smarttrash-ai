import { useState } from 'react'
import { Camera, Upload, RefreshCw, CheckCircle, AlertTriangle, HelpCircle } from 'lucide-react'
import './App.css'

function App() {
  const [image, setImage] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setImage(imageUrl);
      setSelectedFile(file);
      setResult(null); 
    }
  };

  const analyzeImage = async () => {
    if (!selectedFile) {
      alert("Nessun file selezionato!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("https://smarttrash-ai.onrender.com/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Errore server");

      const data = await response.json();
      console.log("Dati Backend:", data);

      // --- LOGICA DI SICUREZZA ---
      // Se la confidenza è bassa (< 0.60), attiviamo la modalità "Incerto"
      const confidenceValue = data.confidence; // Es. 0.35
      const isLowConfidence = confidenceValue < 0.60;

      setResult({
        label: data.material,
        confidence: (confidenceValue * 100).toFixed(1) + "%",
        bin: data.bin,
        color: data.color,
        tip: data.tip,
        // Nuovi campi per gestire l'incertezza
        isLowConfidence: isLowConfidence 
      });

    } catch (error) {
      console.error(error);
      alert("Errore di connessione col server.");
    } finally {
      setLoading(false);
    }
  };

  const resetApp = () => {
    setImage(null);
    setSelectedFile(null);
    setResult(null);
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>🌱 SmartTrash AI</h1>
      </header>

      <main className="main-content">
        
        {/* SEZIONE 1: Caricamento */}
        {!result && (
          <>
            <div className="image-preview">
              {image ? (
                <img src={image} alt="Preview" className="uploaded-image" />
              ) : (
                <div className="placeholder">
                  <Upload size={48} color="#bdc3c7" />
                  <p>Carica una foto del rifiuto</p>
                </div>
              )}
            </div>

            <div className="controls">
              {!image ? (
                <>
                  <input type="file" id="file-upload" accept="image/*" onChange={handleImageUpload} hidden />
                  <label htmlFor="file-upload" className="btn btn-secondary">
                    <Upload size={20} /> Carica Foto
                  </label>
                  <button className="btn btn-primary" onClick={() => document.getElementById('file-upload').click()}>
                    <Camera size={20} /> Scatta Foto
                  </button>
                </>
              ) : (
                !loading && (
                  <button className="btn btn-analyze" onClick={analyzeImage}>
                    Analizza Rifiuto ✨
                  </button>
                )
              )}
            </div>
            {loading && <div className="loader">🧠 Analisi in corso...</div>}
          </>
        )}

        {/* SEZIONE 2: RISULTATO */}
        {result && (
          // Se la confidenza è BASSA, mostriamo lo stile "Warning" (Arancione)
          // Altrimenti mostriamo lo stile normale (Colore del bidone)
          <div className="result-card" style={{ 
            borderColor: result.isLowConfidence ? '#e67e22' : result.color 
          }}>
            
            <div className="result-header" style={{ 
              backgroundColor: result.isLowConfidence ? '#e67e22' : result.color 
            }}>
              {result.isLowConfidence ? (
                <HelpCircle size={32} color="white" />
              ) : (
                <CheckCircle size={32} color="white" />
              )}
              
              <h2>
                {result.isLowConfidence ? "Non sono sicuro..." : result.label}
              </h2>
            </div>
            
            <div className="result-body">
              {result.isLowConfidence ? (
                // --- MESSAGGIO DI ERRORE SE BASSA CONFIDENZA ---
                <div className="low-confidence-msg">
                  <p>Ho trovato <strong>{result.label}</strong>, ma la sicurezza è solo del <strong>{result.confidence}</strong>.</p>
                  <hr />
                  <p>⚠️ <strong>Consigli per una foto migliore:</strong></p>
                  <ul style={{textAlign: 'left', margin: '10px 0'}}>
                    <li>Avvicinati all'oggetto</li>
                    <li>Usa uno sfondo neutro (muro bianco o tavolo pulito)</li>
                    <li>Evita ombre forti o riflessi</li>
                  </ul>
                  <p>Nel dubbio, controlla l'etichetta!</p>
                </div>
              ) : (
                // --- RISULTATO NORMALE ---
                <>
                  <p className="confidence">Sicurezza IA: <strong>{result.confidence}</strong></p>
                  
                  <div className="bin-info">
                    <span>Buttalo nel bidone:</span>
                    <strong style={{ color: result.color, fontSize: '1.2rem' }}>{result.bin}</strong>
                  </div>

                  <div className="tip-box">
                    <AlertTriangle size={18} color="#e67e22" />
                    <p>{result.tip}</p>
                  </div>
                </>
              )}

              <button className="btn btn-secondary" onClick={resetApp}>
                <RefreshCw size={18} /> {result.isLowConfidence ? "Riprova Foto" : "Analizza un altro"}
              </button>
            </div>
          </div>
        )}

      </main>
    </div>
  )
}

export default App